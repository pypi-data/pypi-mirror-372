"""Toggle manager component for handling all UI toggle operations."""

from typing import Any, Optional

from PySide6.QtCore import QTimer

from momovu.lib.constants import IMMEDIATE_DELAY
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class ToggleManager:
    """Manages all toggle operations for the main window."""

    def __init__(self, main_window: Any) -> None:
        """Initialize the toggle manager.

        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self._side_by_side_transition_in_progress = False
        self._side_by_side_timer: Optional[QTimer] = None

    def toggle_fullscreen(self) -> None:
        """Switch between fullscreen and windowed display modes."""
        self.main_window.ui_state_manager.toggle_fullscreen()
        logger.debug("Fullscreen toggled")

    def toggle_presentation(self, sync: bool = False) -> None:
        """Switch between presentation mode (fullscreen, no UI) and normal mode.

        Args:
            sync: If True, perform mode changes synchronously (for testing).
                  If False (default), use normal async behavior for production.
        """
        self.main_window.ui_state_manager.toggle_presentation(sync=sync)
        logger.debug(f"Presentation mode: {self.main_window.is_presentation_mode}")

    def enter_presentation_mode(self) -> None:
        """Enable presentation mode with fullscreen display and hidden UI elements."""
        self.main_window.ui_state_manager.enter_presentation_mode()
        logger.debug("Entered presentation mode")

    def exit_presentation_mode(self, sync: bool = False) -> None:
        """Return to normal viewing mode with visible UI elements.

        Args:
            sync: If True, set presentation mode state synchronously (for testing).
                  If False (default), use normal async behavior for production.
        """
        self.main_window.ui_state_manager.exit_presentation_mode(sync=sync)
        logger.debug("Exited presentation mode")

    def toggle_side_by_side(self, sync: bool = False) -> None:
        """Switch between single page and side-by-side page display for interior documents.

        Args:
            sync: If True, perform the toggle synchronously (for testing).
                  If False (default), use normal async behavior for production.
        """
        if not sync and self._side_by_side_transition_in_progress:
            logger.debug("Side-by-side transition already in progress, ignoring toggle")
            return

        if self._side_by_side_timer and self._side_by_side_timer.isActive():
            self._side_by_side_timer.stop()

        self._side_by_side_transition_in_progress = True

        current_page = self.main_window.navigation_presenter.get_current_page()
        logger.debug(f"Storing current page before view mode change: {current_page}")

        # Use the action's checked state to determine the new mode
        # This is set either by user interaction or programmatically before calling toggle
        if self.main_window.side_by_side_action.isChecked():
            # Action is checked, switch to side-by-side mode
            self.main_window.navigation_presenter.set_view_mode("side_by_side")
            # Set spinbox to increment by 2 in side-by-side mode
            if self.main_window.page_number_spinbox:
                self.main_window.page_number_spinbox.setSingleStep(2)
        else:
            # Action is unchecked, switch to single mode
            self.main_window.navigation_presenter.set_view_mode("single")
            # Reset spinbox to increment by 1 in single page mode
            if self.main_window.page_number_spinbox:
                self.main_window.page_number_spinbox.setSingleStep(1)

        # Prevent the flash by disabling viewport updates during the transition
        view = self.main_window.graphics_view

        # Note: Removed QApplication.processEvents() to prevent re-entrancy issues

        view.setViewportUpdateMode(view.ViewportUpdateMode.NoViewportUpdate)
        view.setUpdatesEnabled(False)

        self.main_window.render_current_page()
        logger.debug(
            f"Side-by-side: {self.main_window.side_by_side_action.isChecked()}"
        )

        def restore_page_position() -> None:
            """Restore the page position after view mode change."""
            try:
                if (
                    self.main_window.navigation_presenter.get_current_page()
                    != current_page
                ):
                    logger.warning(
                        f"Page changed during transition from {current_page} to {self.main_window.navigation_presenter.get_current_page()}"
                    )
                    self.main_window.navigation_presenter.set_current_page(current_page)

                # Use the zoom controller's fit logic instead of manual positioning
                # This ensures proper page positioning (first page on right, etc.)
                self.main_window.fit_to_page()

                logger.debug(f"Fitted to page {current_page} after view mode change")

                self.main_window.update_page_label()

            except Exception as e:
                logger.error(f"Error restoring page position: {e}")
            finally:
                self._side_by_side_transition_in_progress = False

        def restore_and_enable_updates() -> None:
            restore_page_position()
            view.setUpdatesEnabled(True)
            view.setViewportUpdateMode(view.ViewportUpdateMode.MinimalViewportUpdate)
            view.viewport().update()

        if sync:
            # In sync mode (for testing), execute immediately
            restore_and_enable_updates()
        else:
            # Normal async mode - use timer for next event loop
            self._side_by_side_timer = QTimer()
            self._side_by_side_timer.setSingleShot(True)
            self._side_by_side_timer.timeout.connect(restore_and_enable_updates)
            self._side_by_side_timer.start(IMMEDIATE_DELAY)  # Next event loop

    def toggle_margins(self) -> None:
        """Show or hide the safety margin overlays on pages."""
        show = self.main_window.show_margins_action.isChecked()
        self.main_window.margin_presenter.set_show_margins(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Margins visible: {show}")

    def toggle_trim_lines(self) -> None:
        """Show or hide the trim/cut lines at page edges."""
        show = self.main_window.show_trim_lines_action.isChecked()
        self.main_window.margin_presenter.set_show_trim_lines(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Trim lines visible: {show}")

    def toggle_barcode(self) -> None:
        """Show or hide the barcode area indicator on cover/dustjacket documents."""
        show = self.main_window.show_barcode_action.isChecked()
        self.main_window.margin_presenter.set_show_barcode(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Barcode visible: {show}")

    def toggle_fold_lines(self) -> None:
        """Show or hide the spine/flap fold lines on cover/dustjacket documents."""
        show = self.main_window.show_fold_lines_action.isChecked()
        self.main_window.margin_presenter.set_show_fold_lines(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Fold lines visible: {show}")

    def toggle_bleed_lines(self) -> None:
        """Show or hide the bleed lines at page edges on cover/dustjacket documents."""
        show = self.main_window.show_bleed_lines_action.isChecked()
        self.main_window.margin_presenter.set_show_bleed_lines(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Bleed lines visible: {show}")

    def toggle_gutter(self) -> None:
        """Show or hide the gutter margin on interior documents."""
        show = self.main_window.show_gutter_action.isChecked()
        self.main_window.margin_presenter.set_show_gutter(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Gutter visible: {show}")

    def set_document_type(self, doc_type: str) -> None:
        """Change the document type and update UI accordingly.

        Args:
            doc_type: One of 'interior', 'cover', or 'dustjacket'
        """
        self.main_window.interior_action.setChecked(doc_type == "interior")
        self.main_window.cover_action.setChecked(doc_type == "cover")
        self.main_window.dustjacket_action.setChecked(doc_type == "dustjacket")
        self.main_window.margin_presenter.set_document_type(doc_type)

        if hasattr(self.main_window, "menu_builder") and self.main_window.menu_builder:
            self.main_window.menu_builder.update_view_menu_for_document_type(doc_type)

        self.main_window.render_current_page()
        logger.info(f"Document type set to: {doc_type}")

        if (
            hasattr(self.main_window, "toolbar_builder")
            and self.main_window.toolbar_builder
        ):
            self.main_window.toolbar_builder.update_toolbar_visibility()
