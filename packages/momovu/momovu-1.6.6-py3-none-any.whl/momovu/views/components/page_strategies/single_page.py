"""Single page rendering strategy."""

from typing import Callable, Optional

from momovu.lib.logger import get_logger
from momovu.views.components.page_strategies.base import BaseStrategy

logger = get_logger(__name__)


class SinglePageStrategy(BaseStrategy):
    """Strategy for rendering a single page."""

    def render(
        self,
        current_page: int,
        is_presentation_mode: bool,
        show_fold_lines: bool,
        fit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Display only the current page, optionally fitted to view.

        Args:
            current_page: Page index to display
            is_presentation_mode: Triggers fit_callback if True
            show_fold_lines: Whether to display fold indicators
            fit_callback: Function to scale page to viewport
        """
        logger.debug(
            f"SinglePageStrategy.render called - page: {current_page}, presentation: {is_presentation_mode}"
        )

        # Check document state
        if not self.document_presenter:
            logger.error("No document presenter!")
            return

        if not self.pdf_document:
            logger.error("No pdf_document!")
            return

        page_count = self.document_presenter.get_page_count()
        logger.debug(f"Document has {page_count} pages, requesting page {current_page}")

        if current_page >= page_count:
            logger.error(f"Page {current_page} out of range (max: {page_count - 1})")
            return

        # Clean up PageItems before clearing to ensure timers are stopped
        self.cleanup_page_items()
        self.graphics_scene.clear()
        logger.debug("Scene cleared")

        page_size = self.document_presenter.get_page_size(current_page)
        if not page_size:
            logger.error(f"Could not get size for page {current_page}")
            return

        page_width, page_height = page_size
        logger.debug(f"Page {current_page} size: {page_width}x{page_height}")

        page_item = self.create_page_item(current_page, 0, 0)
        if page_item:
            self.graphics_scene.addItem(page_item)
            logger.debug(f"PageItem created and added to scene for page {current_page}")

            # Draw overlays - single page view doesn't show gutters
            self.draw_overlays(0, 0, page_width, page_height, page_position="single")

            self.update_scene_rect()

            self.fit_to_view_if_needed(is_presentation_mode, fit_callback)

            logger.debug(f"Rendered single page {current_page} successfully")
        else:
            logger.error(f"Failed to create PageItem for page {current_page}")
