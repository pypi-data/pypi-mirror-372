"""Main window for the Momovu PDF viewer application.

This refactored version delegates functionality to specialized components,
keeping the main window clean and focused on coordination only.
"""

from typing import TYPE_CHECKING, Optional, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QBrush, QCloseEvent, QKeyEvent, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsScene,
    QMainWindow,
    QMessageBox,
    QSpinBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.constants import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MM_TO_POINTS,
)
from momovu.lib.exceptions import PageRenderError
from momovu.lib.logger import get_logger
from momovu.models.configuration import ConfigurationModel
from momovu.models.search import SearchModel
from momovu.presenters.configuration import ConfigurationPresenter
from momovu.presenters.search import SearchOptions, SearchPresenter
from momovu.views.components.calculator_dialog import SpineWidthCalculatorDialog
from momovu.views.components.cleanup_coordinator import CleanupCoordinator
from momovu.views.components.dialog_manager import DialogManager
from momovu.views.components.document_operations import (
    create_error_message,
    extract_filename_from_path,
    format_window_title,
    safe_document_operation,
    should_show_error_dialog,
)
from momovu.views.components.find_bar import FindBar
from momovu.views.components.graphics_view import GraphicsView
from momovu.views.components.menu_builder import MenuBuilder
from momovu.views.components.navigation_controller import NavigationController
from momovu.views.components.page_renderer import PageRenderer
from momovu.views.components.signal_connections import SignalConnections
from momovu.views.components.state_saver import StateSaver
from momovu.views.components.toggle_manager import ToggleManager
from momovu.views.components.toolbar_builder import ToolbarBuilder
from momovu.views.components.ui_state_manager import UIStateManager
from momovu.views.components.window_setup import WindowSetup
from momovu.views.components.zoom_controller import ZoomController

if TYPE_CHECKING:
    from PySide6.QtPdf import QPdfDocument

    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.margin import MarginPresenter
    from momovu.presenters.navigation import NavigationPresenter
    from momovu.views.components.page_spinbox import PageSpinBox

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main window for the MVP PDF viewer application."""

    # Signals
    zoom_changed = Signal(float)

    def __init__(
        self,
        pdf_path: Optional[str] = None,
        num_pages: Optional[int] = None,
        book_type: Optional[str] = None,
        side_by_side: bool = False,
        show_margins: Optional[bool] = None,
        show_trim_lines: Optional[bool] = None,
        show_barcode: Optional[bool] = None,
        show_fold_lines: Optional[bool] = None,
        show_bleed_lines: Optional[bool] = None,
        show_gutter: Optional[bool] = None,
        start_presentation: bool = False,
        start_fullscreen: bool = False,
        jump: Optional[int] = None,
    ) -> None:
        """Initialize the main window."""
        super().__init__()

        # Initialize configuration system FIRST
        self.config_manager = ConfigurationManager(self)
        self.config_model = ConfigurationModel()
        self.config_presenter = ConfigurationPresenter(
            self.config_model, self.config_manager
        )

        # Connect configuration signals
        self.config_manager.recent_files_changed.connect(self._update_recent_files_menu)
        self.config_manager.config_changed.connect(self._on_config_changed)

        # Load saved configuration
        self.config_presenter.load_configuration()

        # Load window state early
        window_state = self.config_manager.get_window_state()
        if window_state.get("geometry"):
            self.restoreGeometry(window_state["geometry"])

        self.pdf_document: Optional[QPdfDocument] = None
        self.document_presenter: Optional[DocumentPresenter] = None
        self.margin_presenter: Optional[MarginPresenter] = None
        self.navigation_presenter: Optional[NavigationPresenter] = None
        self.page_number_spinbox: Optional[Union[QSpinBox, PageSpinBox]] = None
        self.num_pages_spinbox: Optional[QSpinBox] = None
        self.toolbar: Optional[QToolBar] = None
        self.show_fold_lines_action: Optional[QAction] = None

        # Load saved overlay defaults or use provided CLI values
        saved_overlays = self.config_presenter.get_document_overlays(
            book_type or "interior"
        )

        # CLI arguments override saved configuration
        self._show_margins = (
            show_margins
            if show_margins is not None
            else saved_overlays.get("show_margins", True)
        )
        self._show_trim_lines = (
            show_trim_lines
            if show_trim_lines is not None
            else saved_overlays.get("show_trim_lines", True)
        )
        self._show_barcode = (
            show_barcode
            if show_barcode is not None
            else saved_overlays.get("show_barcode", True)
        )
        self._show_fold_lines = (
            show_fold_lines
            if show_fold_lines is not None
            else saved_overlays.get("show_fold_lines", True)
        )
        self._show_bleed_lines = (
            show_bleed_lines
            if show_bleed_lines is not None
            else saved_overlays.get("show_bleed_lines", True)
        )
        self._show_gutter = (
            show_gutter
            if show_gutter is not None
            else saved_overlays.get("show_gutter", True)
        )

        self._resources_initialized = False

        try:
            self.window_initializer = WindowSetup(self)

            self.window_initializer.init_models_and_presenters()

            self.window_initializer.store_init_params(
                pdf_path,
                num_pages,
                book_type,
                side_by_side,
                show_margins,
                show_trim_lines,
                show_barcode,
                show_fold_lines,
                show_bleed_lines,
                show_gutter,
                start_presentation,
                start_fullscreen,
                jump,
            )

            self._setup_ui()
            self._setup_components()

            self._resources_initialized = True

            self.window_initializer.apply_initial_settings()
            self.window_initializer.initialize_document()

        except Exception as e:
            logger.error(f"Failed to initialize main window: {e}", exc_info=True)
            self._cleanup_resources()
            raise

    def _setup_ui(self) -> None:
        """Set up the user interface with error handling."""
        try:
            self.setWindowTitle("Momovu")
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
            self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            self.graphics_view = GraphicsView(self)
            self.graphics_scene = QGraphicsScene()
            self.graphics_view.setScene(self.graphics_scene)
            self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.graphics_view.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
            layout.addWidget(self.graphics_view)

            # Add find bar at the bottom (initially hidden)
            self.find_bar = FindBar(self)
            layout.addWidget(self.find_bar)

        except Exception as e:
            logger.error(f"Failed to setup UI: {e}", exc_info=True)
            raise

    def _setup_components(self) -> None:
        """Set up UI components using builders."""
        self.menu_builder = MenuBuilder(self)
        self.menu_builder.build_menus()
        self.menu_builder.update_initial_states(
            self._show_margins,
            self._show_trim_lines,
            self._show_barcode,
            self._show_fold_lines,
            self._show_bleed_lines,
            self._show_gutter,
        )

        self.toolbar_builder = ToolbarBuilder(self)
        self.toolbar_builder.build_toolbar(
            self.menu_builder.actions, self.margin_presenter
        )

        if (
            self.pdf_document is None
            or self.document_presenter is None
            or self.margin_presenter is None
            or self.navigation_presenter is None
        ):
            logger.error("Required components not initialized for PageRenderer")
            raise RuntimeError(
                "Cannot create PageRenderer: required components not initialized. "
                "Ensure WindowSetup.init_models_and_presenters() was called."
            )

        self.page_renderer = PageRenderer(
            self.graphics_scene,
            self.pdf_document,
            self.document_presenter,
            self.margin_presenter,
            self.navigation_presenter,
            self.config_manager,  # Pass config manager for color preferences
        )

        self.ui_state_manager = UIStateManager(self)
        self.toggle_manager = ToggleManager(self)

        self.navigation_controller = NavigationController(self)

        self.dialog_manager = DialogManager(self)
        self.dialog_manager.set_file_load_callback(self.load_pdf)
        self.dialog_manager.set_page_navigation_callback(
            self.navigation_controller.navigate_to_page
        )

        self.zoom_controller = ZoomController(
            self.graphics_view, self.graphics_scene, self
        )
        self.zoom_controller.set_presenter_callbacks(
            lambda: self.margin_presenter,
            lambda: self.navigation_presenter,
            lambda: self.document_presenter,
        )
        self.zoom_controller.set_update_callback(self.update_page_label)

        self.cleanup_coordinator = CleanupCoordinator(self)

        # Create state saver for automatic state persistence
        self.state_saver = StateSaver(self)

        self.window_initializer.create_action_aliases()

        self.signal_connector = SignalConnections(self)
        self.signal_connector.connect_all_signals()

        # Connect state saver signals after all components are initialized
        self.state_saver.connect_signals()

        # Initialize search components
        self._setup_search_components()

    def load_pdf(self, file_path: str) -> None:
        """Load a PDF file with error handling."""
        if not self.document_presenter or not self.navigation_presenter:
            logger.error("Presenters not initialized")
            return

        def _load_document() -> bool:
            """Internal function to load the document."""
            if not self.document_presenter or not self.navigation_presenter:
                return False

            success = self.document_presenter.load_document(file_path)

            if success:
                filename = extract_filename_from_path(file_path)
                self.setWindowTitle(format_window_title(self.tr("Momovu"), filename))

                page_count = self.document_presenter.get_page_count()

                # Check if we should jump to a specific page (interior documents only)
                jump_page = None
                if (
                    hasattr(self, "window_initializer")
                    and hasattr(self.window_initializer, "_jump")
                    and self.window_initializer._jump is not None
                    and self.margin_presenter
                    and self.margin_presenter.model.document_type == "interior"
                ):
                    jump_page = self.window_initializer._jump
                    # Validate jump page is within bounds
                    if jump_page > page_count:
                        logger.warning(
                            f"Jump page {jump_page} exceeds document pages ({page_count}), starting at page 1"
                        )
                        jump_page = 1
                    # Clear the jump value so it only applies on initial load
                    self.window_initializer._jump = None

                # CRITICAL: Set total pages FIRST before any navigation
                # This ensures go_to_page() validation works correctly
                self.navigation_presenter.set_total_pages(page_count)

                if jump_page:
                    # Use go_to_page() which properly handles side-by-side alignment
                    # Convert from 1-based to 0-based index
                    success = self.navigation_presenter.go_to_page(jump_page - 1)

                    if success:
                        logger.info(f"Successfully jumped to page {jump_page}")
                    else:
                        logger.warning(
                            f"Failed to jump to page {jump_page} - staying at page 1"
                        )
                else:
                    # No jump requested - start at first page
                    # go_to_page(0) ensures proper alignment for side-by-side mode
                    self.navigation_presenter.go_to_page(0)

                # Update gutter width based on actual document page count (interior documents only)
                if (
                    self.margin_presenter
                    and self.margin_presenter.model.document_type == "interior"
                ):
                    self.margin_presenter.update_page_count(page_count)

                # Update UI elements
                if self.page_number_spinbox:
                    self.page_number_spinbox.setMaximum(
                        page_count if page_count > 0 else 1
                    )
                    self.page_number_spinbox.setEnabled(True)  # Re-enable after loading

                # Update page label AFTER resetting page
                self.update_page_label()

                # Update View menu based on current document type
                if (
                    hasattr(self, "menu_builder")
                    and self.menu_builder
                    and self.margin_presenter
                ):
                    current_doc_type = self.margin_presenter.get_document_type()
                    self.menu_builder.update_view_menu_for_document_type(
                        current_doc_type
                    )

                # NOW render - after all state is properly set
                self.render_current_page()

                # Enable close action now that a document is loaded
                if hasattr(self, "close_action"):
                    self.close_action.setEnabled(True)

                # Enable go to page action for interior documents
                if (
                    hasattr(self, "go_to_page_action")
                    and self.margin_presenter
                    and self.margin_presenter.get_document_type() == "interior"
                ):
                    self.go_to_page_action.setEnabled(True)

                # Enable font info action now that a document is loaded
                if hasattr(self, "font_info_action"):
                    self.font_info_action.setEnabled(True)

                # Automatically fit to page after loading to ensure proper centering
                # This fixes the initial view issue caused by scene padding
                from PySide6.QtCore import QTimer

                # Temporarily disable state saving during initial fit
                def fit_and_save() -> None:
                    # Check if the window is still valid before proceeding
                    try:
                        # Quick check to see if the window is still valid
                        if not self.isVisible():
                            logger.debug(
                                "Window is no longer visible, skipping fit_and_save"
                            )
                            return
                    except RuntimeError:
                        # Window has been deleted
                        logger.debug("Window has been deleted, skipping fit_and_save")
                        return

                    # Disable state saver temporarily using public interface
                    if hasattr(self, "state_saver"):
                        self.state_saver.disable_saves()

                    # Perform fit to page
                    try:
                        self.fit_to_page()
                    except RuntimeError as e:
                        logger.debug(f"Error during fit_to_page: {e}")
                        return

                    # Re-enable state saver and save the final state
                    def save_final_state() -> None:
                        # Check if window is still valid
                        try:
                            if not self.isVisible():
                                return
                        except RuntimeError:
                            return

                        if hasattr(self, "state_saver"):
                            self.state_saver.enable_saves()
                            # Now save the state with the correct zoom
                            self.state_saver.save_state()

                    # Save state after fit is complete
                    QTimer.singleShot(50, save_final_state)

                QTimer.singleShot(100, fit_and_save)

                logger.info(f"PDF loaded: {file_path}")
                return True
            else:
                logger.error(f"Failed to load PDF: {file_path}")
                return False

        result = safe_document_operation("load PDF", _load_document)

        if not result.success and should_show_error_dialog(Exception(result.message)):
            error_message = create_error_message(
                Exception(result.message), "loading PDF"
            )
            QMessageBox.critical(self, self.tr("Load Error"), error_message)

    def render_current_page(self, skip_fit: bool = False) -> None:
        """Render pages using the page renderer component with error handling.

        Args:
            skip_fit: If True, skip automatic fit-to-page (useful for overlay toggles)
        """
        try:
            current_page = (
                self.navigation_presenter.get_current_page()
                if self.navigation_presenter
                else -1
            )
            view_mode = (
                self.navigation_presenter.model.view_mode
                if self.navigation_presenter
                else "unknown"
            )
            logger.info(
                f"[DIAGNOSTIC] render_current_page called - page: {current_page}, view_mode: {view_mode}, presentation: {self.ui_state_manager.is_presentation_mode}"
            )

            self.page_renderer.set_presentation_mode(
                self.ui_state_manager.is_presentation_mode
            )
            if hasattr(self, "show_fold_lines_action") and self.show_fold_lines_action:
                self.page_renderer.set_show_fold_lines(
                    self.show_fold_lines_action.isChecked()
                )

            # Only pass fit callback if not skipping fit
            fit_callback = None if skip_fit else self.zoom_controller.fit_to_page
            self.page_renderer.render_current_page(fit_callback)
            self.update_page_label()

            # Update toolbar visibility based on document type
            # This ensures "Page" and "Pages" spinboxes are shown/hidden appropriately
            if hasattr(self, "toolbar_builder") and self.toolbar_builder:
                self.toolbar_builder.update_toolbar_visibility()

            logger.info("[DIAGNOSTIC] render_current_page completed")
        except PageRenderError as e:
            logger.error(f"Rendering error: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                self.tr("Rendering Error"),
                self.tr("Failed to render page:\n{error}").format(error=str(e)),
            )
        except Exception as e:
            logger.error(f"Unexpected error during rendering: {e}", exc_info=True)

    def update_page_label(self) -> None:
        """Update the page number spinbox."""
        if not self.navigation_presenter:
            return

        current = self.navigation_presenter.get_current_page() + 1

        if (
            hasattr(self, "page_number_spinbox")
            and self.page_number_spinbox is not None
        ):
            try:
                self.page_number_spinbox.blockSignals(True)
                self.page_number_spinbox.setValue(current)
                self.page_number_spinbox.blockSignals(False)
                # Force immediate update of the spinbox display
                self.page_number_spinbox.repaint()
            except RuntimeError:
                # Widget has been deleted, ignore
                logger.debug(
                    "page_number_spinbox widget has been deleted, skipping update"
                )
        else:
            logger.warning(
                f"page_number_spinbox not available when updating to page {current}"
            )

    def on_page_number_changed(self, value: int) -> None:
        """Handle page number spinbox change.

        Args:
            value: New page number (1-based)
        """
        # With setKeyboardTracking(False), this is only called when:
        # - User presses Enter after typing
        # - User clicks arrow buttons
        # - Spinbox loses focus after typing
        self.navigation_controller.on_page_number_changed(value)

    def on_num_pages_changed(self, value: int) -> None:
        """Handle number of pages spinbox change."""
        if not self.margin_presenter:
            return

        self.margin_presenter.set_num_pages(value)
        if self.margin_presenter.model.document_type in ["cover", "dustjacket"]:
            self.render_current_page()

        # Save state after num_pages change
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def open_file_dialog(self) -> None:
        """Open a file dialog to select a PDF with error handling."""
        try:
            self.dialog_manager.show_open_file_dialog()
        except Exception as e:
            logger.error(f"Error in file dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("File Dialog Error"),
                self.tr("Failed to open file dialog:\n{error}").format(error=str(e)),
            )

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        self.toggle_manager.toggle_fullscreen()

    @property
    def is_presentation_mode(self) -> bool:
        """Get current presentation mode state from ui_state_manager."""
        if hasattr(self, "ui_state_manager"):
            return self.ui_state_manager.is_presentation_mode
        return False

    def toggle_presentation(self, sync: bool = False) -> None:
        """Toggle presentation mode.

        Args:
            sync: If True, perform mode changes synchronously (for testing).
                  If False (default), use normal async behavior for production.
        """
        self.toggle_manager.toggle_presentation(sync=sync)

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

        # Save state after presentation mode change
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def enter_presentation_mode(self) -> None:
        """Enter presentation mode."""
        self.toggle_manager.enter_presentation_mode()

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

        # Save state after entering presentation mode
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def exit_presentation_mode(self, sync: bool = False) -> None:
        """Exit presentation mode.

        Args:
            sync: If True, set presentation mode state synchronously (for testing).
                  If False (default), use normal async behavior for production.
        """
        self.toggle_manager.exit_presentation_mode(sync=sync)

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

        # Save state after exiting presentation mode
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_side_by_side(self, sync: bool = False) -> None:
        """Toggle side-by-side view mode.

        Args:
            sync: If True, perform the toggle synchronously (for testing).
                  If False (default), use normal async behavior for production.
        """
        self.toggle_manager.toggle_side_by_side(sync=sync)

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

        # Save state after view mode change
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_margins(self) -> None:
        """Toggle margin visibility."""
        self.toggle_manager.toggle_margins()
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_trim_lines(self) -> None:
        """Toggle trim lines visibility."""
        self.toggle_manager.toggle_trim_lines()
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_barcode(self) -> None:
        """Toggle barcode visibility."""
        self.toggle_manager.toggle_barcode()
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_fold_lines(self) -> None:
        """Toggle fold lines visibility."""
        self.toggle_manager.toggle_fold_lines()
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_bleed_lines(self) -> None:
        """Toggle bleed lines visibility."""
        self.toggle_manager.toggle_bleed_lines()
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def toggle_gutter(self) -> None:
        """Toggle gutter visibility."""
        self.toggle_manager.toggle_gutter()
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def set_document_type(self, doc_type: str) -> None:
        """Set the document type."""
        self.toggle_manager.set_document_type(doc_type)

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

        # Save state after document type change
        if hasattr(self, "state_saver"):
            self.state_saver.save_state()

    def zoom_in(self) -> None:
        """Zoom in from viewport center."""
        self.zoom_controller.zoom_in()

    def zoom_out(self) -> None:
        """Zoom out from viewport center."""
        self.zoom_controller.zoom_out()

    def fit_to_page(self) -> None:
        """Fit the current page(s) to the view."""
        self.zoom_controller.fit_to_page()

    def show_shortcuts_dialog(self) -> None:
        """Show the keyboard shortcuts dialog."""
        self.dialog_manager.show_shortcuts_dialog()

    def show_about_dialog(self) -> None:
        """Show the about dialog."""
        self.dialog_manager.show_about_dialog()

    def show_go_to_page_dialog(self) -> None:
        """Show the go to page dialog."""
        self.dialog_manager.show_go_to_page_dialog_with_presenters(
            self.document_presenter, self.navigation_presenter
        )

    def show_spine_calculator_dialog(self) -> None:
        """Show the spine width calculator dialog."""
        # Get the appropriate page count based on document type
        initial_pages = 100  # Default

        if self.margin_presenter:
            doc_type = self.margin_presenter.get_document_type()

            if doc_type == "interior":
                # For interior documents, use the total page count
                if self.document_presenter:
                    page_count = self.document_presenter.get_page_count()
                    if page_count > 0:
                        initial_pages = page_count
            else:
                # For covers/dustjackets, use the Pages spinbox value
                if self.num_pages_spinbox:
                    initial_pages = self.num_pages_spinbox.value()

        dialog = SpineWidthCalculatorDialog(self, initial_pages)
        dialog.exec()

    def show_font_info_dialog(self) -> None:
        """Show the font information dialog."""
        from momovu.views.dialogs.font_info_dialog import FontInfoDialog

        # Check if a document is loaded
        if (
            not self.document_presenter
            or not self.document_presenter.is_document_loaded()
        ):
            QMessageBox.information(
                self,
                self.tr("No Document"),
                self.tr("Please open a PDF document first to view font information."),
            )
            return

        # Get the current PDF path
        pdf_path = getattr(self.document_presenter, "_file_path", None)
        if (
            not pdf_path
            and hasattr(self.document_presenter, "model")
            and hasattr(self.document_presenter.model, "file_path")
        ):
            pdf_path = self.document_presenter.model.file_path

        if not pdf_path:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Could not determine the PDF file path."),
            )
            return

        # Show the font information dialog
        dialog = FontInfoDialog(self, pdf_path)
        dialog.exec()

    def _setup_search_components(self) -> None:
        """Set up search-related components."""
        # Create search model and presenter
        self.search_model = SearchModel()
        self.search_presenter = SearchPresenter(
            self.search_model,
            self.document_presenter,
            self.navigation_presenter,
            self,  # Pass main window reference for navigation
        )

        # Set Qt document for search
        if hasattr(self, "pdf_document") and self.pdf_document:
            self.search_presenter.set_qt_document(self.pdf_document)

        # Connect find bar signals
        self.find_bar.search_requested.connect(self._on_search_requested)
        self.find_bar.next_requested.connect(self.search_presenter.navigate_next)
        self.find_bar.previous_requested.connect(
            self.search_presenter.navigate_previous
        )
        self.find_bar.close_requested.connect(self._on_find_bar_closed)
        self.find_bar.options_changed.connect(self._on_search_options_changed)

        # Connect search presenter signals
        self.search_presenter.results_found.connect(self._on_results_found)
        self.search_presenter.current_result_changed.connect(
            self._on_current_result_changed
        )
        self.search_presenter.search_error_occurred.connect(self._on_search_error)

    def show_find_bar(self) -> None:
        """Show the find bar for searching."""
        if hasattr(self, "find_bar") and self.find_bar:
            self.find_bar.show_bar()

            # If there's selected text, use it as the search query
            if hasattr(self, "graphics_view") and self.graphics_view:
                selected_text = getattr(self.graphics_view, "selected_text", "")
                if selected_text and selected_text.strip():
                    # Take only the first line if multi-line selection
                    first_line = selected_text.strip().split("\n")[0]
                    # Limit length for search box
                    if len(first_line) > 100:
                        first_line = first_line[:100]
                    self.find_bar.set_search_text(first_line)

    def navigate_search_result(self, previous: bool = False) -> None:
        """Navigate to next or previous search result.

        Args:
            previous: If True, navigate to previous result; otherwise next
        """
        if hasattr(self, "search_presenter"):
            if previous:
                self.search_presenter.navigate_previous()
            else:
                self.search_presenter.navigate_next()

    def _on_search_requested(self, query: str) -> None:
        """Handle search request from find bar.

        Args:
            query: Search query
        """
        if not query:
            # Clear search
            self.search_presenter.clear_search()
            self._clear_search_highlights()
            return

        # Get search options from find bar
        case_sensitive, whole_words, use_regex = self.find_bar.get_search_options()

        # Update model options
        self.search_model.set_case_sensitive(case_sensitive)
        self.search_model.set_whole_words(whole_words)
        self.search_model.set_use_regex(use_regex)

        # Execute search with debounce
        options = SearchOptions(case_sensitive, whole_words, use_regex)
        self.search_presenter.search_with_debounce(query, options)

    def _on_search_options_changed(
        self, case_sensitive: bool, whole_words: bool, use_regex: bool
    ) -> None:
        """Handle search options change.

        Args:
            case_sensitive: Case sensitive option
            whole_words: Whole words option
            use_regex: Regex option
        """
        # Options change will trigger a new search via find bar's internal logic
        pass

    def _on_results_found(self, total: int) -> None:
        """Handle search results found.

        Args:
            total: Total number of results
        """
        current = self.search_model.current_result_index
        self.find_bar.update_result_count(current, total)

        # Clear highlights when no results found, otherwise update them
        if total == 0:
            self._clear_search_highlights()
        else:
            self._update_search_highlights()

    def _on_current_result_changed(self, index: int) -> None:
        """Handle current search result change.

        Args:
            index: Current result index
        """
        total = self.search_model.total_results_found
        self.find_bar.update_result_count(
            index, min(total, self.search_model.MAX_RESULTS_IN_MEMORY)
        )

        # Update highlights to show current result
        self._update_search_highlights()

    def _on_search_error(self, error_msg: str) -> None:
        """Handle search error.

        Args:
            error_msg: Error message
        """
        # Could show error in status bar or dialog
        logger.error(f"Search error: {error_msg}")
        if hasattr(self, "statusBar") and callable(self.statusBar):
            self.statusBar().showMessage(f"Search error: {error_msg}", 5000)

    def _on_find_bar_closed(self) -> None:
        """Handle find bar close."""
        # Clear search when find bar is closed
        if hasattr(self, "search_presenter"):
            self.search_presenter.clear_search()
        self._clear_search_highlights()

    def _update_search_highlights(self) -> None:
        """Update search highlights on visible pages."""
        if not hasattr(self, "graphics_scene") or not self.graphics_scene:
            return

        # PERFORMANCE FIX: Only update highlights for VISIBLE pages
        # Get the current viewport to determine what's actually visible
        if not hasattr(self, "graphics_view") or not self.graphics_view:
            return

        viewport_rect = self.graphics_view.mapToScene(
            self.graphics_view.viewport().rect()
        ).boundingRect()

        # Get current page items that are actually visible
        for item in self.graphics_scene.items():
            # Check if this is a PageItem
            if hasattr(item, "page_number") and hasattr(
                item, "update_search_highlights"
            ):
                # CRITICAL: Only process if the page is visible in the viewport
                item_rect = item.sceneBoundingRect()
                if not viewport_rect.intersects(item_rect):
                    continue  # Skip pages not in view

                # Get search results for this page
                results = self.search_presenter.get_results_for_page(item.page_number)
                current_result = self.search_presenter.get_current_result()

                # Update highlights on the page
                item.update_search_highlights(results, current_result)

    def _clear_search_highlights(self) -> None:
        """Clear all search highlights from pages."""
        if not hasattr(self, "graphics_scene") or not self.graphics_scene:
            return

        # Clear highlights from all page items
        for item in self.graphics_scene.items():
            if hasattr(item, "clear_search_highlights"):
                item.clear_search_highlights()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events by delegating to GraphicsView.

        This exists for compatibility with tests and Qt's event system.
        All actual handling is in GraphicsView.
        """
        if hasattr(self, "graphics_view"):
            self.graphics_view.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def go_to_first_page(self) -> None:
        """Navigate to first page."""
        self.navigation_controller.navigate_first()

    def previous_page(self) -> None:
        """Navigate to previous page."""
        self.navigation_controller.navigate_previous()

    def next_page(self) -> None:
        """Navigate to next page."""
        self.navigation_controller.navigate_next()

    def go_to_last_page(self) -> None:
        """Navigate to last page."""
        self.navigation_controller.navigate_last()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event and cleanup resources."""
        logger.info("Main window closing, saving configuration")

        # CRITICAL: Save any pending state immediately before closing
        if hasattr(self, "state_saver"):
            self.state_saver.save_state_immediate()

        # Save window state
        self.config_manager.save_window_state(
            self.saveGeometry().data(),  # QByteArray.data() returns bytes
            self.saveState().data(),  # QByteArray.data() returns bytes
            self.isMaximized(),
            self.isFullScreen(),
        )

        # Save current overlay settings if document is loaded
        if self.margin_presenter:
            doc_type = self.margin_presenter.get_document_type()
            overlays = {
                "show_margins": self.margin_presenter.model.show_margins,
                "show_trim_lines": self.margin_presenter.model.show_trim_lines,
                "show_barcode": self.margin_presenter.model.show_barcode,
                "show_fold_lines": self.margin_presenter.model.show_fold_lines,
                "show_bleed_lines": self.margin_presenter.model.show_bleed_lines,
            }
            # Add gutter for interior documents
            if doc_type == "interior":
                overlays["show_gutter"] = self.margin_presenter.model.show_gutter
            self.config_presenter.save_document_overlays(doc_type, overlays)

        # Save configuration
        self.config_presenter.save_configuration()

        self._cleanup_resources()
        super().closeEvent(event)

    def copy_text(self) -> None:
        """Copy selected text to clipboard.

        This method delegates to the graphics view's copy handler.
        """
        if hasattr(self, "graphics_view") and self.graphics_view:
            # Call the graphics view's copy handler
            self.graphics_view._handle_copy_text()
        else:
            logger.warning("Graphics view not available for copy operation")

    def close_pdf(self) -> None:
        """Close the current PDF document without exiting the application."""
        # Check if a document is actually loaded
        if (
            not self.document_presenter
            or not self.document_presenter.is_document_loaded()
        ):
            logger.info("No document to close")
            return

        logger.info("Closing current PDF document")

        # Clear search if active
        if hasattr(self, "search_presenter"):
            self.search_presenter.clear_search()
        if hasattr(self, "find_bar") and self.find_bar.isVisible():
            self.find_bar.hide_bar()

        # Clear the graphics scene
        if hasattr(self, "graphics_scene") and self.graphics_scene:
            self.graphics_scene.clear()

        # Close the document
        if self.document_presenter:
            self.document_presenter.close_document()

        # Reset navigation
        if self.navigation_presenter:
            self.navigation_presenter.model.current_page = 0
            self.navigation_presenter.set_total_pages(0)

        # Update UI
        self.setWindowTitle(self.tr("Momovu"))

        if self.page_number_spinbox:
            self.page_number_spinbox.blockSignals(True)
            self.page_number_spinbox.setValue(1)  # Minimum value is 1
            self.page_number_spinbox.setMaximum(1)
            self.page_number_spinbox.setEnabled(False)
            self.page_number_spinbox.blockSignals(False)

        if hasattr(self, "close_action"):
            self.close_action.setEnabled(False)

        # Disable go to page action when document is closed
        if hasattr(self, "go_to_page_action"):
            self.go_to_page_action.setEnabled(False)

        # Disable Copy action when document is closed (no text to copy)
        if hasattr(self, "copy_action"):
            self.copy_action.setEnabled(False)

        # Disable font info action when document is closed
        if hasattr(self, "font_info_action"):
            self.font_info_action.setEnabled(False)

        # Clear any text selection in graphics view
        if hasattr(self, "graphics_view") and self.graphics_view:
            if hasattr(self.graphics_view, "set_selected_text"):
                self.graphics_view.set_selected_text("")
            elif hasattr(self.graphics_view, "selected_text"):
                self.graphics_view.selected_text = ""

        logger.info("PDF document closed successfully")

    def _cleanup_resources(self) -> None:
        """Clean up resources when closing or on error.

        This method delegates to the CleanupCoordinator for proper resource cleanup.
        """
        if hasattr(self, "cleanup_coordinator"):
            self.cleanup_coordinator.cleanup_resources()

    def _update_recent_files_menu(self) -> None:
        """Update the recent files submenu."""
        if hasattr(self, "menu_builder") and self.menu_builder:
            self.menu_builder._update_recent_files_menu()

    def _on_config_changed(self, key: str) -> None:
        """Handle configuration change signal.

        Args:
            key: Configuration key that changed
        """
        logger.debug(f"Configuration changed: {key}")

        # Check if we're in the middle of closing a preferences dialog
        # If so, skip handling to prevent accessing deleted objects
        if (
            hasattr(self, "_active_preferences_dialog")
            and self._active_preferences_dialog
        ):
            logger.debug("Skipping config change during preferences dialog lifecycle")
            return

        # If it's a full reset or batch update, reload configuration
        if key == "*":
            self.config_presenter.load_configuration()
            # Apply configuration to UI (skip window state to avoid issues)
            self.config_presenter.apply_configuration(self, skip_window_state=True)

    def show_preferences_dialog(self) -> None:
        """Show the preferences dialog with proper lifecycle management."""
        from momovu.views.components.preferences_dialog import PreferencesDialog

        # Check if a preferences dialog is already open
        if (
            hasattr(self, "_active_preferences_dialog")
            and self._active_preferences_dialog is not None
        ):
            logger.warning("Preferences dialog already open, ignoring request")
            # Bring the existing dialog to front
            self._active_preferences_dialog.raise_()
            self._active_preferences_dialog.activateWindow()
            return

        # Create dialog with proper parent
        dialog = PreferencesDialog(self.config_manager, self)

        # Ensure dialog is properly modal to prevent parent window interaction
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Store reference to prevent premature garbage collection and track active dialog
        self._active_preferences_dialog: Optional[PreferencesDialog] = dialog

        # Connect signal for preferences changes
        # Use Qt.ConnectionType.QueuedConnection to ensure signal is handled
        # after the dialog is fully closed
        dialog.preferences_changed.connect(
            self._on_preferences_changed, Qt.ConnectionType.QueuedConnection
        )

        # REMOVED: setUpdatesEnabled(False) - This was causing paint event issues
        # Qt properly handles modality without needing to disable updates

        # Show dialog modally - this blocks until dialog is closed
        result = dialog.exec()

        # Force a repaint of the main window after dialog closes
        # This ensures any visual artifacts are cleared
        self.update()
        self.repaint()

        # Log the result for debugging
        if result == QDialog.DialogCode.Accepted:
            logger.debug("Preferences dialog accepted")
        else:
            logger.debug("Preferences dialog cancelled")
            # Clean up the dialog reference if cancelled
            if (
                hasattr(self, "_active_preferences_dialog")
                and self._active_preferences_dialog is not None
            ):
                self._active_preferences_dialog.deleteLater()
                self._active_preferences_dialog = None

    def _on_preferences_changed(self) -> None:
        """Handle preferences change signal with proper cleanup."""
        logger.debug("Preferences changed signal received")

        try:
            # Apply preferences immediately since we're using QueuedConnection
            # The dialog is already closed at this point
            logger.debug("Applying preferences changes")

            # Reload configuration from disk
            self.config_presenter.load_configuration()

            # Apply configuration to UI but SKIP window state restoration
            # Restoring window geometry while preferences dialog is closing causes
            # the window duplication glitch where a smaller window appears
            self.config_presenter.apply_configuration(self, skip_window_state=True)

            # IMPORTANT: Defer the re-rendering to avoid event loop re-entrancy
            # This prevents window glitches by ensuring all dialog cleanup is complete
            if self.document_presenter and self.document_presenter.is_document_loaded():
                logger.debug("Scheduling page re-render with new preferences")
                from PySide6.QtCore import QTimer

                # Use a longer delay to ensure all dialog cleanup is complete
                QTimer.singleShot(100, lambda: self._safe_render_after_preferences())

        finally:
            # Clean up the dialog reference after handling the signal
            # This ensures the dialog is properly deleted
            if (
                hasattr(self, "_active_preferences_dialog")
                and self._active_preferences_dialog is not None
            ):
                self._active_preferences_dialog.deleteLater()
                self._active_preferences_dialog = None
                logger.debug("Preferences dialog cleaned up")

    def _safe_render_after_preferences(self) -> None:
        """Safely re-render the page after preferences change.

        This method is called after a delay to ensure all dialog cleanup
        is complete and avoid event loop re-entrancy issues.
        """
        try:
            if self.document_presenter and self.document_presenter.is_document_loaded():
                logger.debug("Re-rendering current page with new preferences")

                # IMPORTANT: Update margin presenter with new dimension settings
                if self.margin_presenter:
                    doc_type = self.margin_presenter.get_document_type()

                    # Re-apply safety margin from configuration
                    safety_margin_mm = self.config_manager.get_safety_margin_mm()
                    self.margin_presenter._model.safety_margin_points = (
                        safety_margin_mm * MM_TO_POINTS
                    )

                    # For dustjacket documents, update flap width and fold safety margin
                    if doc_type == "dustjacket":
                        flap_width_mm = (
                            self.config_manager.get_dustjacket_flap_width_mm()
                        )
                        self.margin_presenter._model.flap_width = (
                            flap_width_mm * MM_TO_POINTS
                        )

                        # Note: fold_safety_margin is handled internally by renderers
                        # using config_manager directly, not stored in the model

                    # Recalculate spine width for cover/dustjacket with new formula settings
                    if doc_type in ["cover", "dustjacket"]:
                        logger.debug(
                            f"Recalculating spine width for {doc_type} with new formula settings"
                        )
                        # Force recalculation by calling the private method directly
                        self.margin_presenter._calculate_spine_width()

                # Clear renderer caches to ensure new colors are loaded
                if hasattr(self, "page_renderer") and self.page_renderer:
                    self.page_renderer.clear_renderer_caches()
                self.render_current_page(skip_fit=True)
        except Exception as e:
            logger.error(
                f"Error re-rendering after preferences change: {e}", exc_info=True
            )

    def load_recent_file(self, file_path: str) -> None:
        """Load a recent file from the menu.

        Args:
            file_path: Path to the PDF file to load
        """
        from pathlib import Path

        # Check if file still exists
        if Path(file_path).exists():
            # Find the file info from recent files
            recent_files = self.config_manager.get_recent_files()
            doc_type = "interior"  # default
            overlays = None
            num_pages = None
            view_mode = None
            zoom_level = None
            current_page = None

            presentation_mode = False
            # Normalize the file path for comparison
            normalized_file_path = str(Path(file_path).resolve())
            for file_info in recent_files:
                # Compare normalized paths
                if (
                    str(Path(file_info.get("path", "")).resolve())
                    == normalized_file_path
                ):
                    doc_type = file_info.get("document_type", "interior")
                    overlays = file_info.get("overlays")
                    num_pages = file_info.get("num_pages")
                    view_mode = file_info.get("view_mode")
                    zoom_level = file_info.get("zoom_level")
                    current_page = file_info.get(
                        "last_page", 0
                    )  # Note: stored as "last_page" in config
                    presentation_mode = file_info.get("presentation_mode", False)
                    break

            # Load the PDF
            self.load_pdf(file_path)

            # Restore the document type after loading
            if self.margin_presenter:
                # Temporarily disable saves while setting document type
                if hasattr(self, "state_saver"):
                    self.state_saver.disable_saves()

                try:
                    self.set_document_type(doc_type)
                finally:
                    if hasattr(self, "state_saver"):
                        self.state_saver.enable_saves()

                # Restore num_pages for cover/dustjacket documents
                if num_pages and doc_type in ["cover", "dustjacket"]:
                    self.margin_presenter.set_num_pages(num_pages)
                    if self.num_pages_spinbox:
                        # Ensure value is within valid range
                        min_val = self.num_pages_spinbox.minimum()
                        max_val = self.num_pages_spinbox.maximum()
                        safe_value = max(min_val, min(num_pages, max_val))
                        self.num_pages_spinbox.setValue(safe_value)

                # Coordinate all restoration in a single function to avoid timing issues
                from PySide6.QtCore import QTimer

                def restore_all_state() -> None:
                    """Restore all state in the correct order."""
                    # Check all required components exist
                    if not all(
                        [
                            hasattr(self, "navigation_presenter"),
                            hasattr(self, "navigation_controller"),
                            hasattr(self, "graphics_view"),
                            hasattr(self, "zoom_controller"),
                            hasattr(self, "margin_presenter"),
                        ]
                    ):
                        logger.warning(
                            "Cannot restore state - required components missing"
                        )
                        return

                    # 1. Set view mode first (affects how pages are displayed)
                    if view_mode and self.navigation_presenter:
                        self.navigation_presenter.set_view_mode(view_mode)

                        # Update UI to match
                        if view_mode == "side_by_side":
                            if hasattr(self, "side_by_side_action"):
                                self.side_by_side_action.blockSignals(True)
                                self.side_by_side_action.setChecked(True)
                                self.side_by_side_action.blockSignals(False)
                            if self.page_number_spinbox:
                                self.page_number_spinbox.setSingleStep(2)
                        else:
                            if hasattr(self, "side_by_side_action"):
                                self.side_by_side_action.blockSignals(True)
                                self.side_by_side_action.setChecked(False)
                                self.side_by_side_action.blockSignals(False)
                            if self.page_number_spinbox:
                                self.page_number_spinbox.setSingleStep(1)

                    # 2. Navigate to the saved page
                    if current_page is not None and current_page >= 0:
                        try:
                            # Use a flag instead of monkey patching
                            if hasattr(self, "state_saver"):
                                self.state_saver.disable_saves()

                            try:
                                self.navigation_controller.navigate_to_page(
                                    current_page + 1
                                )
                            finally:
                                # Always re-enable even if navigation fails
                                if hasattr(self, "state_saver"):
                                    self.state_saver.enable_saves()
                        except Exception as e:
                            logger.error(
                                f"Failed to restore page position: {e}", exc_info=True
                            )

                    # 3. Apply zoom level
                    if zoom_level and zoom_level > 0 and self.graphics_view.scene():
                        try:
                            self.graphics_view.resetTransform()
                            if zoom_level != 1.0:
                                self.graphics_view.scale(zoom_level, zoom_level)
                            self.zoom_controller.set_zoom_level(
                                zoom_level, emit_signal=False
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to restore zoom level: {e}", exc_info=True
                            )

                    # 4. Apply presentation mode if needed
                    if presentation_mode and hasattr(self, "ui_state_manager"):
                        try:
                            # Use a flag instead of monkey patching
                            if hasattr(self, "state_saver"):
                                self.state_saver.disable_saves()

                            try:
                                self.enter_presentation_mode()
                            finally:
                                # Always re-enable even if entering presentation fails
                                if hasattr(self, "state_saver"):
                                    self.state_saver.enable_saves()
                        except Exception as e:
                            logger.error(
                                f"Failed to restore presentation mode: {e}",
                                exc_info=True,
                            )

                    # 5. Force a single render with everything set
                    try:
                        self.render_current_page(skip_fit=True)
                    except Exception as e:
                        logger.error(
                            f"Failed to render after state restore: {e}", exc_info=True
                        )

                # Restore all state after document is fully loaded
                QTimer.singleShot(200, restore_all_state)

                # Restore overlay settings if available
                if overlays and isinstance(overlays, dict) and self.margin_presenter:
                    # Store the original state to check if we need to re-render
                    original_state = {
                        "show_margins": self.margin_presenter.model.show_margins,
                        "show_trim_lines": self.margin_presenter.model.show_trim_lines,
                        "show_barcode": self.margin_presenter.model.show_barcode,
                        "show_fold_lines": self.margin_presenter.model.show_fold_lines,
                        "show_bleed_lines": self.margin_presenter.model.show_bleed_lines,
                    }

                    # Apply the saved overlay settings
                    # Block signals to prevent double-setting through toggle methods
                    if (
                        "show_margins" in overlays
                        and overlays["show_margins"] != original_state["show_margins"]
                    ):
                        self.margin_presenter.model.show_margins = overlays[
                            "show_margins"
                        ]
                        if hasattr(self, "show_margins_action"):
                            self.show_margins_action.blockSignals(True)
                            self.show_margins_action.setChecked(
                                overlays["show_margins"]
                            )
                            self.show_margins_action.blockSignals(False)
                    if (
                        "show_trim_lines" in overlays
                        and overlays["show_trim_lines"]
                        != original_state["show_trim_lines"]
                    ):
                        self.margin_presenter.model.show_trim_lines = overlays[
                            "show_trim_lines"
                        ]
                        if hasattr(self, "show_trim_lines_action"):
                            self.show_trim_lines_action.blockSignals(True)
                            self.show_trim_lines_action.setChecked(
                                overlays["show_trim_lines"]
                            )
                            self.show_trim_lines_action.blockSignals(False)

                    if (
                        "show_barcode" in overlays
                        and overlays["show_barcode"] != original_state["show_barcode"]
                    ):
                        self.margin_presenter.model.show_barcode = overlays[
                            "show_barcode"
                        ]
                        if hasattr(self, "show_barcode_action"):
                            self.show_barcode_action.blockSignals(True)
                            self.show_barcode_action.setChecked(
                                overlays["show_barcode"]
                            )
                            self.show_barcode_action.blockSignals(False)

                    if (
                        "show_fold_lines" in overlays
                        and overlays["show_fold_lines"]
                        != original_state["show_fold_lines"]
                    ):
                        self.margin_presenter.model.show_fold_lines = overlays[
                            "show_fold_lines"
                        ]
                        if (
                            hasattr(self, "show_fold_lines_action")
                            and self.show_fold_lines_action is not None
                        ):
                            self.show_fold_lines_action.blockSignals(True)
                            self.show_fold_lines_action.setChecked(
                                overlays["show_fold_lines"]
                            )
                            self.show_fold_lines_action.blockSignals(False)

                    if (
                        "show_bleed_lines" in overlays
                        and overlays["show_bleed_lines"]
                        != original_state["show_bleed_lines"]
                    ):
                        self.margin_presenter.model.show_bleed_lines = overlays[
                            "show_bleed_lines"
                        ]
                        if hasattr(self, "show_bleed_lines_action"):
                            self.show_bleed_lines_action.blockSignals(True)
                            self.show_bleed_lines_action.setChecked(
                                overlays["show_bleed_lines"]
                            )
                            self.show_bleed_lines_action.blockSignals(False)
                    # Only re-render if overlays actually changed
                    # The render in restore_all_state() will handle the display
                    # so we don't need to render here anymore
        else:
            QMessageBox.warning(
                self,
                self.tr("File Not Found"),
                self.tr("The file could not be found:\n{path}").format(path=file_path),
            )
