"""PDF page item for MVP viewer - renders dynamically based on zoom level."""

import time
from collections import OrderedDict
from typing import Any, Optional

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from momovu.lib.constants import (
    ZOOM_ACTIVE_THRESHOLD,
    ZOOM_BUFFER_FACTOR,
    ZOOM_BUFFER_REDUCTION_MAX,
    ZOOM_BUFFER_REDUCTION_THRESHOLD,
    ZOOM_CACHE_LEVELS,
    ZOOM_CACHE_MAX_ENTRIES,
    ZOOM_CACHE_MAX_MEMORY_MB,
    ZOOM_MAX_DIMENSION,
    ZOOM_MAX_RENDER_PIXELS,
    ZOOM_MAX_USEFUL_SCALE,
    ZOOM_PROGRESSIVE_RENDER_DELAY,
    ZOOM_QUALITY_THRESHOLD,
    ZOOM_SAFE_FALLBACK_SCALE,
)
from momovu.lib.logger import get_logger
from momovu.views.direct_pdf_selector import DirectPdfSelector

logger = get_logger(__name__)


class PageItem(QGraphicsItem):
    """PDF page graphics item that renders dynamically based on zoom level.

    This is a simplified version of PageItem specifically for the MVP viewer.
    It renders the PDF page at the appropriate resolution for the current zoom level.
    """

    # Use constants from config - can be overridden there
    MAX_CACHE_ENTRIES = ZOOM_CACHE_MAX_ENTRIES
    MAX_CACHE_MEMORY_MB = ZOOM_CACHE_MAX_MEMORY_MB
    BUFFER_FACTOR = ZOOM_BUFFER_FACTOR
    CACHE_ZOOM_LEVELS = ZOOM_CACHE_LEVELS
    MAX_USEFUL_SCALE = ZOOM_MAX_USEFUL_SCALE

    def __init__(
        self,
        document: QPdfDocument,
        page_number: int,
        page_width: float,
        page_height: float,
    ):
        """Initialize the PDF page item.

        Args:
            document: The PDF document
            page_number: Zero-based page number
            page_width: Page width in points
            page_height: Page height in points
        """
        super().__init__()

        self.document = document
        self.page_number = page_number
        self.page_width = page_width
        self.page_height = page_height
        self.bounding_rect = QRectF(0, 0, page_width, page_height)

        # Disable Qt's cache since we're doing our own
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)

        # Cache for rendered regions: (scale, x, y, w, h) -> QImage
        self._render_cache: OrderedDict[
            tuple[float, float, float, float, float], QImage
        ] = OrderedDict()
        self._cache_memory_usage: float = 0.0

        # Progressive rendering state
        self._last_rendered_image: Optional[QImage] = None
        self._last_rendered_rect: Optional[QRectF] = None
        self._is_rendering = False
        self._pending_render_timer: Optional[QTimer] = None
        self._last_paint_time: float = 0.0
        self._pending_render_params: Optional[
            tuple[QRectF, int, int, float, tuple[float, float, float, float, float]]
        ] = None
        self._is_cleaning_up = False

        # Text selection state
        self.selection_start: Optional[QPointF] = None
        self.selection_end: Optional[QPointF] = None
        self.is_selecting: bool = False
        self.page_rotation: float = 0.0  # Page rotation in degrees
        self.selection_rects: list[QRectF] = (
            []
        )  # Multiple rects for multi-line selection
        self.current_selection: Any = None  # Current QPdfSelection object

        # Enable mouse tracking for text selection
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setAcceptHoverEvents(True)

        # Initialize direct PDF selector (uses built-in QPdfDocument selection)
        self.direct_selector: Optional[DirectPdfSelector] = None
        if self.document:
            self.direct_selector = DirectPdfSelector(self.document, self.page_number)

        # Search highlights
        self.search_highlights: list[QRectF] = []  # All search results on this page
        self.current_search_highlight: Optional[QRectF] = None  # Current/active result
        self._search_results: list[Any] = []  # Store actual SearchResult objects
        self._current_search_result: Optional[Any] = None  # Current SearchResult object

    def boundingRect(self) -> QRectF:
        """Define item's scene space boundaries for Qt rendering."""
        return self.bounding_rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,  # noqa: ARG002
    ) -> None:
        """Render only the visible portion of the PDF page for optimal performance.

        Uses caching and buffer zones for smooth panning experience.
        """
        # Get the visible rectangle in item coordinates
        visible_rect = option.exposedRect  # type: ignore[attr-defined]
        if visible_rect.isEmpty():
            return

        # Check document validity first
        if not self.document:
            logger.error(
                f"PageItem {self.page_number}: No document available in paint!"
            )
            self._draw_error_placeholder(painter, self.bounding_rect)
            return

        # Get current scale first
        transform = painter.transform()
        scale = max(transform.m11(), transform.m22())

        # Check if we're in presentation mode
        is_presentation = self._is_presentation_mode()
        logger.debug(
            f"PageItem {self.page_number}: Painting, scale={scale:.2f}, presentation={is_presentation}"
        )

        # For normal viewing (low zoom) or presentation, use original high-quality rendering
        # Threshold is configurable in constants
        if scale <= ZOOM_QUALITY_THRESHOLD or is_presentation:
            # Original full-page rendering for best quality
            self._render_full_page_original(painter, scale)
            # Draw search highlights first (below selection)
            self._draw_search_highlights(painter)
            # Draw selection overlay after page content
            self._draw_selection_overlay(painter)
            return

        # High zoom - use optimized visible-area rendering
        # Snap scale early for cache consistency
        scale = self._snap_to_cache_level(scale)
        # Add buffer around visible area for smooth panning
        # Reduce buffer at high zoom to maintain quality
        buffer_factor = self.BUFFER_FACTOR
        if (
            scale > ZOOM_BUFFER_REDUCTION_THRESHOLD
            and ZOOM_BUFFER_REDUCTION_THRESHOLD > 0
        ):
            # At high zoom, reduce buffer to maintain render quality
            # Protected against division by zero
            buffer_factor = min(
                ZOOM_BUFFER_REDUCTION_MAX,
                self.BUFFER_FACTOR / (scale / ZOOM_BUFFER_REDUCTION_THRESHOLD),
            )

        buffer_width = visible_rect.width() * buffer_factor
        buffer_height = visible_rect.height() * buffer_factor
        render_rect = visible_rect.adjusted(
            -buffer_width, -buffer_height, buffer_width, buffer_height
        )

        # Clamp to page bounds
        render_rect = render_rect.intersected(self.bounding_rect)

        # Check cache - use rect coordinates as key since QRectF isn't hashable
        cache_key = (
            scale,
            render_rect.x(),
            render_rect.y(),
            render_rect.width(),
            render_rect.height(),
        )
        cached_image = self._get_from_cache(cache_key)

        if cached_image:
            # Use cached image with quality hints
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            painter.drawImage(
                render_rect,
                cached_image,
                QRectF(0, 0, cached_image.width(), cached_image.height()),
            )
            self._last_rendered_image = cached_image
            self._last_rendered_rect = QRectF(render_rect)  # Store a copy
            return

        # Need to render - calculate size
        render_width = int(render_rect.width() * scale)
        render_height = int(render_rect.height() * scale)

        # Check if render size is reasonable
        if render_width * render_height > ZOOM_MAX_RENDER_PIXELS:
            # Don't reduce quality! Instead, render without buffer
            logger.debug(
                f"Render size {render_width}x{render_height} exceeds limit, removing buffer"
            )
            # Just render the visible area without buffer
            render_rect = visible_rect
            render_width = int(render_rect.width() * scale)
            render_height = int(render_rect.height() * scale)

            # If still too large, we need to cap the scale
            if render_width * render_height > ZOOM_MAX_RENDER_PIXELS:
                max_scale = (
                    ZOOM_MAX_RENDER_PIXELS
                    / (render_rect.width() * render_rect.height())
                ) ** 0.5
                scale = min(scale, max_scale)
                render_width = int(render_rect.width() * scale)
                render_height = int(render_rect.height() * scale)
                logger.debug(
                    f"Even without buffer, size too large. Capping scale to {scale:.1f}x"
                )

            # Update cache key for the new rect
            cache_key = (
                scale,
                render_rect.x(),
                render_rect.y(),
                render_rect.width(),
                render_rect.height(),
            )

        # Check if we're actively zooming (multiple paints in quick succession)
        current_time = time.time()
        is_active_zoom = (current_time - self._last_paint_time) < ZOOM_ACTIVE_THRESHOLD
        self._last_paint_time = current_time

        if is_active_zoom and self._last_rendered_image:
            # Store local copy to avoid race condition
            last_rect = self._last_rendered_rect
            try:
                if last_rect and not last_rect.isNull():
                    # Progressive rendering: show stretched previous image immediately
                    source_rect = self._calculate_source_rect(render_rect, last_rect)
                    painter.drawImage(
                        render_rect, self._last_rendered_image, source_rect
                    )
            except (RuntimeError, AttributeError):
                # Rect was deleted or became invalid, skip progressive rendering
                pass

            # Queue high-quality render
            self._queue_high_quality_render(
                render_rect, render_width, render_height, scale, cache_key
            )
        else:
            # Not actively zooming - render normally but cap scale
            actual_scale = min(scale, self.MAX_USEFUL_SCALE)
            if actual_scale < scale:
                # Recalculate dimensions with capped scale
                render_width = int(render_rect.width() * actual_scale)
                render_height = int(render_rect.height() * actual_scale)
                # Update cache key to use actual scale
                cache_key = (
                    actual_scale,
                    render_rect.x(),
                    render_rect.y(),
                    render_rect.width(),
                    render_rect.height(),
                )

            # Render the visible region
            image = self._render_region(
                render_rect, render_width, render_height, actual_scale
            )

            if image and not image.isNull():
                # Cache the result with correct key
                self._add_to_cache(cache_key, image)

                # Draw the image with high quality hints
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
                painter.drawImage(
                    render_rect, image, QRectF(0, 0, image.width(), image.height())
                )

                # Update last rendered for progressive rendering
                self._last_rendered_image = image
                self._last_rendered_rect = QRectF(render_rect)  # Store a copy

                # Queue predictive renders
                self._queue_predictive_renders(scale)
            else:
                self._draw_error_placeholder(painter, render_rect)

        # Draw search highlights first (below selection)
        self._draw_search_highlights(painter)

        # Draw selection overlay after page content
        self._draw_selection_overlay(painter)

    def _draw_search_highlights(self, painter: QPainter) -> None:
        """Draw search result highlights.

        OPTIMIZED: Only calculate bounds for results that are actually visible.

        Args:
            painter: The QPainter to draw with
        """
        # Check if we have any results to draw
        if (
            not hasattr(self, "_search_results") or not self._search_results
        ) and not self.current_search_highlight:
            return

        painter.save()

        # Get the visible rect to only draw highlights that are visible
        visible_rect = painter.clipBoundingRect()
        if visible_rect.isEmpty():
            visible_rect = self.bounding_rect

        # Draw regular search highlights in yellow
        if hasattr(self, "_search_results") and self._search_results:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 0, 100))  # Semi-transparent yellow

            for result in self._search_results:
                # Skip the current result (drawn separately)
                if (
                    hasattr(self, "_current_search_result")
                    and result == self._current_search_result
                ):
                    continue

                # Only process if bounds exist and are visible
                if (
                    hasattr(result, "bounds")
                    and result.bounds is not None
                    and visible_rect.intersects(result.bounds)
                ):
                    painter.drawRect(result.bounds)

        # Draw current search highlight in orange with border
        if self.current_search_highlight:
            from PySide6.QtGui import QPen

            painter.setPen(QPen(QColor(255, 140, 0), 2))  # Orange border
            painter.setBrush(QColor(255, 165, 0, 150))  # Semi-transparent orange
            painter.drawRect(self.current_search_highlight)

        painter.restore()

    def _draw_selection_overlay(self, painter: QPainter) -> None:
        """Draw the text selection overlay if there's an active selection.

        Args:
            painter: The QPainter to draw with
        """
        # Draw multi-line selection if we have selection rectangles
        if self.selection_rects:
            # Set up the selection color (semi-transparent blue)
            selection_color = QColor(0, 120, 215, 100)

            # Save painter state
            painter.save()

            # Draw each selection rectangle
            for rect in self.selection_rects:
                painter.fillRect(rect, selection_color)

            # Restore painter state
            painter.restore()

        # Fallback to rectangular selection if direct selector not available
        elif self.selection_start and self.selection_end and not self.direct_selector:
            # Get the selection rectangle
            selection_rect = self.get_selection_rectangle()

            # Set up the selection color (semi-transparent blue)
            selection_color = QColor(0, 120, 215, 100)

            # Save painter state
            painter.save()

            # Set the fill color
            painter.fillRect(selection_rect, selection_color)

            # Restore painter state
            painter.restore()

    def get_selection_rectangle(self) -> QRectF:
        """Calculate the selection rectangle from start and end points.

        Returns:
            QRectF representing the selection area, normalized and clipped to page bounds
        """
        if not self.selection_start or not self.selection_end:
            return QRectF()

        # Create rectangle from the two points (normalize to handle any direction)
        left = min(self.selection_start.x(), self.selection_end.x())
        top = min(self.selection_start.y(), self.selection_end.y())
        right = max(self.selection_start.x(), self.selection_end.x())
        bottom = max(self.selection_start.y(), self.selection_end.y())

        selection_rect = QRectF(left, top, right - left, bottom - top)

        # Clip to page boundaries
        selection_rect = selection_rect.intersected(self.bounding_rect)

        return selection_rect

    def clear_selection(self) -> None:
        """Clear the current text selection and update the visual."""
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.selection_rects = []
        self.current_selection = None

        # Clear the selection in GraphicsView (which will also disable Copy action)
        if self.scene():
            views = self.scene().views()
            if views:
                graphics_view = views[0]
                if hasattr(graphics_view, "set_selected_text"):
                    graphics_view.set_selected_text("")
                elif hasattr(graphics_view, "selected_text"):
                    graphics_view.selected_text = ""

        # Trigger a repaint to clear the selection visual
        self.update()

    def _draw_error_placeholder(self, painter: QPainter, rect: QRectF) -> None:
        """Draw error placeholder when rendering fails."""
        painter.fillRect(rect, Qt.GlobalColor.red)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            f"Error\nPage {self.page_number + 1}",
        )

    def _render_region(
        self, region: QRectF, width: int, height: int, scale: float
    ) -> Optional[QImage]:
        """Render a specific region of the page.

        Since QPdfDocument doesn't support partial rendering, we render
        the full page and extract the needed region.
        """
        from PySide6.QtCore import QSize

        try:
            # We need to render enough of the page to include our region
            # For now, render the full page (QPdfDocument limitation)
            # In the future, we could optimize by rendering a smaller portion
            full_width = int(self.page_width * scale)
            full_height = int(self.page_height * scale)

            # Safety check - configurable for different systems
            if full_width * full_height > ZOOM_MAX_RENDER_PIXELS:
                # Too large, reduce scale
                max_scale = (
                    ZOOM_MAX_RENDER_PIXELS / (self.page_width * self.page_height)
                ) ** 0.5
                scale = min(scale, max_scale)
                full_width = int(self.page_width * scale)
                full_height = int(self.page_height * scale)
                logger.debug(
                    f"Reduced render scale to {scale:.1f}x to stay within memory limits"
                )

            # Additional safety check for extreme cases
            if full_width > ZOOM_MAX_DIMENSION or full_height > ZOOM_MAX_DIMENSION:
                logger.warning(
                    f"Extreme render size detected: {full_width}x{full_height}"
                )
                # Cap at max dimension
                if full_width > ZOOM_MAX_DIMENSION:
                    scale = scale * (ZOOM_MAX_DIMENSION / full_width)
                    full_width = ZOOM_MAX_DIMENSION
                    full_height = int(self.page_height * scale)
                if full_height > ZOOM_MAX_DIMENSION:
                    scale = scale * (ZOOM_MAX_DIMENSION / full_height)
                    full_height = ZOOM_MAX_DIMENSION
                    full_width = int(self.page_width * scale)

            # Render full page with exception handling
            try:
                full_image = self.document.render(
                    self.page_number, QSize(full_width, full_height)
                )

                if full_image.isNull():
                    raise RuntimeError("Render returned null image")
            except Exception as render_error:
                logger.error(
                    f"PDF render failed at {full_width}x{full_height}: {render_error}"
                )
                # Try one more time at a safe resolution
                if scale > ZOOM_SAFE_FALLBACK_SCALE:
                    safe_scale = ZOOM_SAFE_FALLBACK_SCALE  # Use local variable instead of modifying parameter
                    safe_width = int(self.page_width * safe_scale)
                    safe_height = int(self.page_height * safe_scale)
                    try:
                        full_image = self.document.render(
                            self.page_number, QSize(safe_width, safe_height)
                        )
                        if full_image.isNull():
                            return None
                        # Use safe_scale for extraction calculations
                        source_x = int(region.x() * safe_scale)
                        source_y = int(region.y() * safe_scale)
                        # Recalculate dimensions with safe scale
                        width = int(region.width() * safe_scale)
                        height = int(region.height() * safe_scale)
                        source_rect = QRectF(source_x, source_y, width, height)

                        # Ensure source rect is within image bounds
                        source_rect = source_rect.intersected(
                            QRectF(0, 0, full_image.width(), full_image.height())
                        )

                        # Copy the region
                        return full_image.copy(source_rect.toRect())
                    except Exception:
                        return None
                else:
                    return None

            else:
                # Normal case - extract the region we need
                source_x = int(region.x() * scale)
                source_y = int(region.y() * scale)
                source_rect = QRectF(source_x, source_y, width, height)

                # Ensure source rect is within image bounds
                source_rect = source_rect.intersected(
                    QRectF(0, 0, full_image.width(), full_image.height())
                )

                # Copy the region
                return full_image.copy(source_rect.toRect())

        except (RuntimeError, MemoryError, Exception) as e:
            logger.warning(
                f"Failed to render region at {scale:.1f}x for page {self.page_number + 1}: {e}"
            )

            # Try with reduced scale
            if scale > ZOOM_SAFE_FALLBACK_SCALE:
                try:
                    return self._render_region(
                        region,
                        int(width * ZOOM_SAFE_FALLBACK_SCALE / scale),
                        int(height * ZOOM_SAFE_FALLBACK_SCALE / scale),
                        ZOOM_SAFE_FALLBACK_SCALE,
                    )
                except Exception:
                    logger.error("Even fallback render failed")
                    return None
            return None

    def _get_from_cache(
        self, key: tuple[float, float, float, float, float]
    ) -> Optional[QImage]:
        """Get image from cache if available."""
        if key in self._render_cache:
            # Move to end (LRU)
            self._render_cache.move_to_end(key)
            return self._render_cache[key]
        return None

    def _add_to_cache(
        self, key: tuple[float, float, float, float, float], image: QImage
    ) -> None:
        """Add image to cache with memory management."""
        # Calculate image memory usage (approximate) with overflow protection
        width = min(image.width(), 65536)  # Cap at reasonable max
        height = min(image.height(), 65536)
        bytes_per_pixel = 4
        total_bytes = width * height * bytes_per_pixel
        image_size_mb = total_bytes / (1024.0 * 1024.0)

        # Remove old entries if needed
        while (
            len(self._render_cache) >= self.MAX_CACHE_ENTRIES
            or self._cache_memory_usage + image_size_mb > self.MAX_CACHE_MEMORY_MB
        ):
            if not self._render_cache:
                break
            # Remove oldest
            _, old_image = self._render_cache.popitem(last=False)
            old_size_mb = (old_image.width() * old_image.height() * 4) / (
                1024.0 * 1024.0
            )
            self._cache_memory_usage -= old_size_mb

        # Add new entry
        self._render_cache[key] = image
        self._cache_memory_usage += image_size_mb

    def _snap_to_cache_level(self, scale: float) -> float:
        """Snap scale to nearest cache level for better hit rate."""
        if scale <= self.CACHE_ZOOM_LEVELS[0]:
            return self.CACHE_ZOOM_LEVELS[0]
        if scale >= self.CACHE_ZOOM_LEVELS[-1]:
            return self.CACHE_ZOOM_LEVELS[-1]

        # Find nearest level
        for i in range(len(self.CACHE_ZOOM_LEVELS) - 1):
            if self.CACHE_ZOOM_LEVELS[i] <= scale < self.CACHE_ZOOM_LEVELS[i + 1]:
                # Return closer one
                if (scale - self.CACHE_ZOOM_LEVELS[i]) < (
                    self.CACHE_ZOOM_LEVELS[i + 1] - scale
                ):
                    return self.CACHE_ZOOM_LEVELS[i]
                else:
                    return self.CACHE_ZOOM_LEVELS[i + 1]
        return scale

    def _calculate_source_rect(
        self, target_rect: QRectF, source_rect: QRectF
    ) -> QRectF:
        """Calculate source rectangle for progressive rendering stretch."""
        if not self._last_rendered_image:
            return QRectF(0, 0, 1, 1)

        # Protect against division by zero
        if source_rect.width() == 0 or source_rect.height() == 0:
            return QRectF(0, 0, 1, 1)

        # Map target rect to source image coordinates
        scale_x = self._last_rendered_image.width() / source_rect.width()
        scale_y = self._last_rendered_image.height() / source_rect.height()

        # Calculate intersection
        intersect = target_rect.intersected(source_rect)
        if intersect.isEmpty():
            return QRectF(
                0,
                0,
                self._last_rendered_image.width(),
                self._last_rendered_image.height(),
            )

        # Map to source coordinates
        x = (intersect.x() - source_rect.x()) * scale_x
        y = (intersect.y() - source_rect.y()) * scale_y
        w = intersect.width() * scale_x
        h = intersect.height() * scale_y

        return QRectF(x, y, w, h)

    def _queue_high_quality_render(
        self,
        rect: QRectF,
        width: int,
        height: int,
        scale: float,
        cache_key: tuple[float, float, float, float, float],
    ) -> None:
        """Queue a high-quality render after a short delay."""
        # Don't queue if we're cleaning up
        if self._is_cleaning_up:
            return

        # Store parameters as copies to avoid reference issues
        self._pending_render_params = (QRectF(rect), width, height, scale, cache_key)

        # Create timer only once, reuse it
        if self._pending_render_timer is None:
            self._pending_render_timer = QTimer()
            self._pending_render_timer.setSingleShot(True)
            self._pending_render_timer.timeout.connect(self._execute_progressive_render)

        # Cancel previous and start new
        self._pending_render_timer.stop()
        self._pending_render_timer.start(ZOOM_PROGRESSIVE_RENDER_DELAY)

    def _execute_progressive_render(self) -> None:
        """Execute the queued progressive render."""
        # Safety checks
        if self._is_cleaning_up or not self._pending_render_params or not self.scene():
            return

        # Extract parameters
        rect, width, height, scale, cache_key = self._pending_render_params
        self._pending_render_params = None

        # Don't render if already rendering
        if self._is_rendering:
            return

        self._is_rendering = True
        try:
            # Cap scale for rendering
            actual_scale = min(scale, self.MAX_USEFUL_SCALE)
            if actual_scale < scale:
                # Recalculate dimensions
                width = int(rect.width() * actual_scale)
                height = int(rect.height() * actual_scale)
                # Update cache key
                cache_key = (
                    actual_scale,
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height(),
                )

            # Render the region
            image = self._render_region(rect, width, height, actual_scale)

            if image and not image.isNull() and not self._is_cleaning_up:
                self._add_to_cache(cache_key, image)
                self._last_rendered_image = image
                self._last_rendered_rect = QRectF(rect)  # Store copy

                # Only update if we still have a scene
                if self.scene():
                    self.update(rect)

        except Exception as e:
            logger.error(f"Progressive render error: {e}", exc_info=True)
        finally:
            self._is_rendering = False

    def _queue_predictive_renders(self, scale: float) -> None:
        """Queue predictive renders for likely next views."""
        # For now, just a placeholder - could pre-render adjacent areas
        # or next zoom levels in the future
        pass

    def _is_presentation_mode(self) -> bool:
        """Check if we're in presentation mode.

        The UIStateManager sets is_presentation_mode on the scene when entering/exiting
        presentation mode. We safely check for this attribute.
        """
        scene = self.scene()
        if scene:
            # Use getattr with default to handle case where attribute doesn't exist yet
            return getattr(scene, "is_presentation_mode", False)
        return False

    def _render_full_page_original(self, painter: QPainter, scale: float) -> None:
        """Render full page at original quality (no optimizations)."""
        # Don't snap scale - use exact value for best quality
        render_width = int(self.page_width * scale)
        render_height = int(self.page_height * scale)

        # Add safety limits to prevent crashes in presentation mode
        if render_width * render_height > ZOOM_MAX_RENDER_PIXELS:
            # Need to cap the scale
            max_scale = (
                ZOOM_MAX_RENDER_PIXELS / (self.page_width * self.page_height)
            ) ** 0.5
            scale = min(scale, max_scale)
            render_width = int(self.page_width * scale)
            render_height = int(self.page_height * scale)
            logger.debug(f"Capped full page render to {scale:.1f}x for safety")

        # Also check dimensions
        if render_width > ZOOM_MAX_DIMENSION or render_height > ZOOM_MAX_DIMENSION:
            if render_width > ZOOM_MAX_DIMENSION:
                scale = scale * (ZOOM_MAX_DIMENSION / render_width)
                render_width = ZOOM_MAX_DIMENSION
                render_height = int(self.page_height * scale)
            if render_height > ZOOM_MAX_DIMENSION:
                scale = scale * (ZOOM_MAX_DIMENSION / render_height)
                render_height = ZOOM_MAX_DIMENSION
                render_width = int(self.page_width * scale)

        from PySide6.QtCore import QSize

        try:
            # Render at exact scale
            image = self.document.render(
                self.page_number, QSize(render_width, render_height)
            )

            if image and not image.isNull():
                # Use high-quality scaling
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
                target_rect = QRectF(0, 0, self.page_width, self.page_height)
                painter.drawImage(target_rect, image)
            else:
                self._draw_error_placeholder(painter, self.bounding_rect)

        except (RuntimeError, MemoryError, Exception) as e:
            logger.warning(
                f"Full page render failed at {render_width}x{render_height}: {e}"
            )
            # Try at a safe resolution
            if scale > ZOOM_SAFE_FALLBACK_SCALE:
                try:
                    safe_width = int(self.page_width * ZOOM_SAFE_FALLBACK_SCALE)
                    safe_height = int(self.page_height * ZOOM_SAFE_FALLBACK_SCALE)
                    image = self.document.render(
                        self.page_number, QSize(safe_width, safe_height)
                    )
                    if image and not image.isNull():
                        painter.drawImage(
                            QRectF(0, 0, self.page_width, self.page_height), image
                        )
                    else:
                        self._draw_error_placeholder(painter, self.bounding_rect)
                except Exception:
                    self._draw_error_placeholder(painter, self.bounding_rect)
            else:
                self._draw_error_placeholder(painter, self.bounding_rect)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse press for text selection start."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Start text selection using DIRECT PDF selection
            self.is_selecting = True
            self.selection_start = (
                event.pos()
            )  # QGraphicsSceneMouseEvent.pos() returns QPointF
            self.selection_end = event.pos()

            # Store the current selection for visual feedback
            self.current_selection = None

            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse move for text selection drag."""
        if self.is_selecting and event.buttons() & Qt.MouseButton.LeftButton:
            # Update selection end point
            self.selection_end = event.pos()

            # Use DIRECT PDF selection - let QPdfDocument handle everything!
            if self.direct_selector and self.selection_start and self.selection_end:
                # Get selection directly from QPdfDocument
                self.current_selection = self.direct_selector.get_selection(
                    self.selection_start, self.selection_end
                )

                if self.current_selection:
                    # Get the visual bounds for drawing
                    bounds = self.direct_selector.get_selection_bounds(
                        self.current_selection
                    )
                    self.selection_rects = []

                    # Convert bounds to QRectF for drawing
                    for bound in bounds:
                        if hasattr(bound, "boundingRect"):
                            rect = bound.boundingRect()
                        else:
                            rect = bound
                        self.selection_rects.append(rect)
                else:
                    self.selection_rects = []

            # Trigger visual feedback update
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse release to finalize text selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_selecting:
                self.is_selecting = False

                # Check if we actually moved the mouse (not just a click)
                if self.selection_start and self.selection_end:
                    distance = (
                        (self.selection_end.x() - self.selection_start.x()) ** 2
                        + (self.selection_end.y() - self.selection_start.y()) ** 2
                    ) ** 0.5

                    if distance < 3:  # Just a click, not a drag
                        # Clear selection on single click
                        self.clear_selection()
                        event.accept()
                        return

                # Extract text from the selected region
                if self.current_selection:
                    try:
                        selected_text = self.current_selection.text()

                        # Update the graphics view's selected text if we got any
                        if selected_text:
                            self.update_graphics_view_selection(selected_text)
                        else:
                            # Clear selection if no text was selected
                            self.clear_selection()
                    except Exception as e:
                        logger.error(f"Error extracting text selection: {e}")
                        self.clear_selection()

            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle double-click to select word at cursor position."""
        if event.button() == Qt.MouseButton.LeftButton and self.document:
            # Always set selection points for double-click
            self.selection_start = event.pos()
            self.selection_end = event.pos()

            try:
                # Get click position in PDF coordinates
                zoom_scale = self._get_current_zoom_scale()
                pdf_point = self.scene_to_pdf_coords(event.pos(), zoom_scale)

                # For word selection, we'd need to:
                # 1. Find the character index at the click point
                # 2. Expand to word boundaries
                # 3. Use getSelectionAtIndex to select the word

                # Since QPdfDocument doesn't directly support point-to-index conversion,
                # we'll use a small region around the click point
                tolerance = 5.0  # pixels
                start_point = QPointF(
                    pdf_point.x() - tolerance, pdf_point.y() - tolerance
                )
                end_point = QPointF(
                    pdf_point.x() + tolerance, pdf_point.y() + tolerance
                )

                # Get selection for the small region
                selection = self.document.getSelection(
                    self.page_number, start_point, end_point
                )

                if selection:
                    selected_text = selection.text()
                    if selected_text:
                        # Extract the word from the selected text
                        # This is a simplified approach - a real implementation
                        # would need more sophisticated word boundary detection
                        words = selected_text.split()
                        if words:
                            word = words[0]  # Take the first word
                            self.update_graphics_view_selection(word)

            except Exception as e:
                logger.error(f"Error selecting word: {e}")

            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def scene_to_pdf_coords(self, scene_point: QPointF, zoom_scale: float) -> QPointF:
        """Transform scene coordinates to PDF page coordinates.

        Args:
            scene_point: Point in scene/item coordinates (which are scaled by zoom)
            zoom_scale: Current zoom scale factor

        Returns:
            Point in PDF page coordinates
        """
        # IMPORTANT: The mouse coordinates are in the item's coordinate space,
        # which is scaled by the zoom factor. We need to account for this scaling
        # to get the actual PDF coordinates.

        # When zoomed, the item is scaled, so mouse coordinates need to be unscaled
        # to get back to PDF coordinates
        pdf_x = scene_point.x()  # Item coordinates are already in PDF points
        pdf_y = (
            scene_point.y()
        )  # No Y-flip needed (Qt and PDF both use top-left origin)

        # Note: The item itself is scaled by the view transform, but the coordinates
        # we receive in mouse events are already in the item's local coordinate system,
        # which is in PDF points. So we don't need to divide by zoom_scale here.

        return QPointF(pdf_x, pdf_y)

    def pdf_to_scene_coords(self, pdf_point: QPointF, zoom_scale: float) -> QPointF:
        """Transform PDF page coordinates to scene coordinates.

        Args:
            pdf_point: Point in PDF page coordinates
            zoom_scale: Current zoom scale factor (not used - coordinates are already in PDF points)

        Returns:
            Point in scene/item coordinates
        """
        # Based on testing, PDF coordinates from QPdfDocument are already
        # in Qt orientation (top-left origin), so no transformation needed
        scene_x = pdf_point.x()
        scene_y = pdf_point.y()  # NO flip needed!

        return QPointF(scene_x, scene_y)

    def scene_to_pdf_coords_with_rotation(
        self, scene_point: QPointF, zoom_scale: float, page_rotation: float
    ) -> QPointF:
        """Transform scene coordinates to PDF coordinates considering rotation.

        Args:
            scene_point: Point in scene/item coordinates
            zoom_scale: Current zoom scale factor
            page_rotation: Page rotation in degrees

        Returns:
            Point in PDF page coordinates
        """
        # First remove zoom scaling
        pdf_point = self.scene_to_pdf_coords(scene_point, zoom_scale)

        # Apply rotation transformation
        # This is simplified - actual implementation would use QTransform
        if page_rotation == 90:
            # 90-degree rotation: x -> y, y -> (width - x)
            new_x = pdf_point.y()
            new_y = self.page_width - pdf_point.x()
            return QPointF(new_x, new_y)
        elif page_rotation == 180:
            # 180-degree rotation: x -> (width - x), y -> (height - y)
            new_x = self.page_width - pdf_point.x()
            new_y = self.page_height - pdf_point.y()
            return QPointF(new_x, new_y)
        elif page_rotation == 270:
            # 270-degree rotation: x -> (height - y), y -> x
            new_x = self.page_height - pdf_point.y()
            new_y = pdf_point.x()
            return QPointF(new_x, new_y)
        else:
            # No rotation or unsupported angle
            return pdf_point

    def clamp_to_page_bounds(self, point: QPointF) -> QPointF:
        """Clamp a point to stay within page boundaries.

        Args:
            point: Point to clamp

        Returns:
            Clamped point within page bounds
        """
        clamped_x = max(0, min(point.x(), self.page_width))
        clamped_y = max(0, min(point.y(), self.page_height))

        return QPointF(clamped_x, clamped_y)

    def update_graphics_view_selection(self, text: str) -> None:
        """Update the GraphicsView's selected_text attribute.

        Args:
            text: The selected text to store
        """
        # Get the graphics view from the scene
        if self.scene():
            views = self.scene().views()
            if views:
                # Assume the first view is our GraphicsView
                graphics_view = views[0]
                if hasattr(graphics_view, "set_selected_text"):
                    # Use the setter method which also updates Copy action state
                    graphics_view.set_selected_text(text)
                elif hasattr(graphics_view, "selected_text"):
                    # Fallback to direct setting if setter not available
                    graphics_view.selected_text = text

    def _get_current_zoom_scale(self) -> float:
        """Get the current zoom scale from the view.

        Returns:
            Current zoom scale factor
        """
        if self.scene():
            views = self.scene().views()
            if views:
                view = views[0]
                # Get the transformation matrix
                transform = view.transform()
                # Extract scale (assuming uniform scaling)
                scale = transform.m11()  # or m22() for vertical scale
                return scale

        # Default to 1.0 if we can't determine scale
        return 1.0

    def update_search_highlights(
        self, results: list[Any], current_result: Optional[Any] = None
    ) -> None:
        """Update search highlights for this page.

        OPTIMIZED: Store results directly, calculate bounds only when painting.

        Args:
            results: List of SearchResult objects for this page
            current_result: The currently active SearchResult (if any)
        """
        # Store the results themselves, not the bounds
        self._search_results = results
        self._current_search_result = current_result

        # Clear old highlight rects - they'll be recalculated when needed
        self.search_highlights = []
        self.current_search_highlight = None

        # Only calculate bounds for the current result (for immediate display)
        if (
            current_result
            and current_result in results
            and hasattr(current_result, "bounds")
            and current_result.bounds is not None
        ):
            self.current_search_highlight = current_result.bounds

        # Trigger repaint to show highlights
        self.update()

    def clear_search_highlights(self) -> None:
        """Clear all search highlights from this page."""
        self.search_highlights = []
        self.current_search_highlight = None
        self.update()

    def cleanup(self) -> None:
        """Clean up resources when page item is being removed.

        This is called when the scene is cleared or the item is removed.
        Ensures timers are stopped to prevent crashes.
        """
        # Set flag first to prevent new operations
        self._is_cleaning_up = True

        # Stop and clean up timer
        if self._pending_render_timer:
            try:
                self._pending_render_timer.stop()

                try:
                    self._pending_render_timer.timeout.disconnect()
                except (RuntimeError, TypeError):
                    # Already disconnected or deleted
                    pass

                self._pending_render_timer.deleteLater()

            except RuntimeError:
                # Timer was already deleted by Qt
                pass
            finally:
                self._pending_render_timer = None

        # Clear pending parameters
        self._pending_render_params = None

        # Clear cache and other resources
        self._render_cache.clear()
        self._cache_memory_usage = 0
        self._last_rendered_image = None
        self._last_rendered_rect = None

        # Clear search highlights
        self.search_highlights = []
        self.current_search_highlight = None
        self._search_results = []
        self._current_search_result = None

        # Clear document reference last
        self.document = None  # type: ignore[assignment]
