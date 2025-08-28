"""Menu builder component for the main window.

This component handles all menu creation and setup.
"""

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMainWindow, QStyle

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class MenuBuilder:
    """Component responsible for building and managing the menu bar."""

    def __init__(self, main_window: QMainWindow) -> None:
        """Initialize the menu builder.

        Args:
            main_window: The main window to add menus to
        """
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()

        self.actions: dict[str, QAction] = {}

    def build_menus(self) -> None:
        """Create and populate all application menus in the menu bar."""
        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_document_menu()
        self._build_help_menu()
        logger.info("Menus built successfully")

    def _build_file_menu(self) -> None:
        """Create File menu with Open and Exit actions."""
        file_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("MainWindow", "&File")
        )
        style = self.main_window.style()

        self.actions["open"] = QAction(
            QCoreApplication.translate("MainWindow", "&Open..."), self.main_window
        )
        icon_names = [
            "document-open-symbolic",
            "document-open",
            "folder-open-symbolic",
            "folder-open",
        ]
        icon = None
        for icon_name in icon_names:
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                self.actions["open"].setIcon(icon)
                logger.debug(f"Using theme icon '{icon_name}' for Open action")
                break

        if icon is None or icon.isNull():
            logger.debug(
                f"Theme icons not available for Open action: {', '.join(icon_names)}"
            )
            icon = style.standardIcon(QStyle.SP_DirOpenIcon)  # type: ignore[attr-defined]
            if not icon.isNull():
                self.actions["open"].setIcon(icon)
                logger.debug("Using standard icon SP_DirOpenIcon for Open action")
            else:
                logger.debug("No suitable icon found for Open action, using text only")
        self.actions["open"].setToolTip(
            QCoreApplication.translate("MainWindow", "Open a PDF file (Ctrl+O)")
        )
        self.actions["open"].setShortcut("Ctrl+O")
        file_menu.addAction(self.actions["open"])

        # Add Recent Files submenu
        self.recent_files_menu = file_menu.addMenu(
            QCoreApplication.translate("MainWindow", "Open &Recent")
        )
        self.recent_files_menu.setToolTip(
            QCoreApplication.translate("MainWindow", "Open recently used files")
        )
        # Store reference in main window for updates
        if hasattr(self.main_window, "recent_files_menu"):
            self.main_window.recent_files_menu = self.recent_files_menu
        self._update_recent_files_menu()

        self.actions["close"] = QAction(
            QCoreApplication.translate("MainWindow", "&Close"), self.main_window
        )
        self.actions["close"].setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Close the current document (Ctrl+W)"
            )
        )
        self.actions["close"].setShortcut("Ctrl+W")
        self.actions["close"].setEnabled(
            False
        )  # Disabled by default until a document is loaded
        file_menu.addAction(self.actions["close"])

        file_menu.addSeparator()

        # Add Preferences action
        self.actions["preferences"] = QAction(
            QCoreApplication.translate("MainWindow", "&Preferences..."),
            self.main_window,
        )
        self.actions["preferences"].setToolTip(
            QCoreApplication.translate("MainWindow", "Open preferences dialog")
        )
        self.actions["preferences"].setShortcut("Ctrl+,")
        file_menu.addAction(self.actions["preferences"])

        file_menu.addSeparator()

        self.actions["exit"] = QAction(
            QCoreApplication.translate("MainWindow", "E&xit"), self.main_window
        )
        self.actions["exit"].setShortcut("Ctrl+Q")
        file_menu.addAction(self.actions["exit"])

    def _build_edit_menu(self) -> None:
        """Create Edit menu with copy and find actions."""
        edit_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("MainWindow", "&Edit")
        )

        # Copy action
        self.actions["copy"] = QAction(
            QCoreApplication.translate("MainWindow", "&Copy"), self.main_window
        )
        self.actions["copy"].setShortcut("Ctrl+C")
        self.actions["copy"].setToolTip(
            QCoreApplication.translate("MainWindow", "Copy selected text (Ctrl+C)")
        )
        self.actions["copy"].setEnabled(False)  # Will be enabled when text is selected

        # Try to use standard copy icon
        style = self.main_window.style()
        icon = style.standardIcon(QStyle.SP_FileDialogDetailedView)  # type: ignore[attr-defined]
        if not icon.isNull():
            self.actions["copy"].setIcon(icon)

        edit_menu.addAction(self.actions["copy"])

        # Add separator
        edit_menu.addSeparator()

        # Find action
        self.actions["find"] = QAction(
            QCoreApplication.translate("MainWindow", "&Find..."), self.main_window
        )
        self.actions["find"].setShortcut("Ctrl+F")
        self.actions["find"].setToolTip(
            QCoreApplication.translate("MainWindow", "Find text in document (Ctrl+F)")
        )

        # Try to use standard find icon
        find_icon = style.standardIcon(QStyle.SP_FileDialogContentsView)  # type: ignore[attr-defined]
        if not find_icon.isNull():
            self.actions["find"].setIcon(find_icon)

        edit_menu.addAction(self.actions["find"])

    def _build_view_menu(self) -> None:
        """Create View menu with display mode and overlay toggle options."""
        view_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("MainWindow", "&View")
        )

        self.actions["fullscreen"] = QAction(
            QCoreApplication.translate("MainWindow", "&Fullscreen"), self.main_window
        )
        self.actions["fullscreen"].setShortcut("F11")
        self.actions["fullscreen"].setCheckable(True)
        view_menu.addAction(self.actions["fullscreen"])

        self.actions["presentation"] = QAction(
            QCoreApplication.translate("MainWindow", "&Presentation Mode"),
            self.main_window,
        )
        self.actions["presentation"].setShortcut("F5")
        self.actions["presentation"].setCheckable(True)
        view_menu.addAction(self.actions["presentation"])

        view_menu.addSeparator()

        self.actions["side_by_side"] = QAction(
            QCoreApplication.translate("MainWindow", "&Side by Side"), self.main_window
        )
        self.actions["side_by_side"].setShortcut("Ctrl+D")
        self.actions["side_by_side"].setCheckable(True)
        view_menu.addAction(self.actions["side_by_side"])

        view_menu.addSeparator()

        self.actions["show_margins"] = QAction(
            QCoreApplication.translate("MainWindow", "Show &Margins"), self.main_window
        )
        self.actions["show_margins"].setShortcut("Ctrl+M")
        self.actions["show_margins"].setCheckable(True)
        self.actions["show_margins"].setChecked(True)
        view_menu.addAction(self.actions["show_margins"])

        self.actions["show_trim_lines"] = QAction(
            QCoreApplication.translate("MainWindow", "Show &Trim Lines"),
            self.main_window,
        )
        self.actions["show_trim_lines"].setShortcut("Ctrl+T")
        self.actions["show_trim_lines"].setCheckable(True)
        self.actions["show_trim_lines"].setChecked(True)
        view_menu.addAction(self.actions["show_trim_lines"])

        self.actions["show_barcode"] = QAction(
            QCoreApplication.translate("MainWindow", "Show &Barcode"), self.main_window
        )
        self.actions["show_barcode"].setShortcut("Ctrl+B")
        self.actions["show_barcode"].setCheckable(True)
        self.actions["show_barcode"].setChecked(True)
        view_menu.addAction(self.actions["show_barcode"])

        self.actions["show_fold_lines"] = QAction(
            QCoreApplication.translate("MainWindow", "Show Fo&ld Lines"),
            self.main_window,
        )
        self.actions["show_fold_lines"].setShortcut("Ctrl+L")
        self.actions["show_fold_lines"].setCheckable(True)
        self.actions["show_fold_lines"].setChecked(True)
        view_menu.addAction(self.actions["show_fold_lines"])

        self.actions["show_bleed_lines"] = QAction(
            QCoreApplication.translate("MainWindow", "Show Bl&eed Lines"),
            self.main_window,
        )
        self.actions["show_bleed_lines"].setShortcut("Ctrl+R")
        self.actions["show_bleed_lines"].setCheckable(True)
        self.actions["show_bleed_lines"].setChecked(True)
        self.actions["show_bleed_lines"].setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Show bleed lines at page edges (Ctrl+R)"
            )
        )
        view_menu.addAction(self.actions["show_bleed_lines"])

        self.actions["show_gutter"] = QAction(
            QCoreApplication.translate("MainWindow", "Show G&utter"),
            self.main_window,
        )
        self.actions["show_gutter"].setShortcut("Ctrl+U")
        self.actions["show_gutter"].setCheckable(True)
        self.actions["show_gutter"].setChecked(True)
        self.actions["show_gutter"].setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Show gutter margin for interior documents (Ctrl+U)"
            )
        )
        view_menu.addAction(self.actions["show_gutter"])

        view_menu.addSeparator()
        self.actions["go_to_page"] = QAction(
            QCoreApplication.translate("MainWindow", "&Go to Page..."), self.main_window
        )
        self.actions["go_to_page"].setShortcut("Ctrl+G")
        self.actions["go_to_page"].setEnabled(False)
        self.actions["go_to_page"].setToolTip(
            QCoreApplication.translate("MainWindow", "Go to a specific page (Ctrl+G)")
        )
        view_menu.addAction(self.actions["go_to_page"])

        self.actions["show_spine_line"] = self.actions["show_fold_lines"]

    def _build_document_menu(self) -> None:
        """Create Document menu for selecting document type (interior/cover/dustjacket)."""
        document_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("MainWindow", "&Document")
        )

        self.actions["interior"] = QAction(
            QCoreApplication.translate("MainWindow", "&Interior"), self.main_window
        )
        self.actions["interior"].setCheckable(True)
        document_menu.addAction(self.actions["interior"])

        self.actions["cover"] = QAction(
            QCoreApplication.translate("MainWindow", "&Cover"), self.main_window
        )
        self.actions["cover"].setCheckable(True)
        document_menu.addAction(self.actions["cover"])

        self.actions["dustjacket"] = QAction(
            QCoreApplication.translate("MainWindow", "&Dustjacket"), self.main_window
        )
        self.actions["dustjacket"].setCheckable(True)
        document_menu.addAction(self.actions["dustjacket"])

        document_menu.addSeparator()

        self.actions["spine_calculator"] = QAction(
            QCoreApplication.translate("MainWindow", "&Calculator..."),
            self.main_window,
        )
        self.actions["spine_calculator"].setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Calculate spine width and document dimensions"
            )
        )
        self.actions["spine_calculator"].setShortcut("Ctrl+K")
        document_menu.addAction(self.actions["spine_calculator"])

    def _build_help_menu(self) -> None:
        """Create Help menu with About and Keyboard Shortcuts options."""
        help_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("MainWindow", "&Help")
        )

        self.actions["about"] = QAction(
            QCoreApplication.translate("MainWindow", "&About"), self.main_window
        )
        help_menu.addAction(self.actions["about"])

        self.actions["shortcuts"] = QAction(
            QCoreApplication.translate("MainWindow", "&Keyboard Shortcuts"),
            self.main_window,
        )
        self.actions["shortcuts"].setShortcut("F1")
        help_menu.addAction(self.actions["shortcuts"])

    def update_initial_states(
        self,
        show_margins: bool,
        show_trim_lines: bool,
        show_barcode: bool,
        show_fold_lines: bool,
        show_bleed_lines: bool = True,
        show_gutter: bool = True,
    ) -> None:
        """Set initial checked states for View menu overlay toggles.

        Args:
            show_margins: Whether margins should be visible initially
            show_trim_lines: Whether trim lines should be visible initially
            show_barcode: Whether barcode area should be visible initially
            show_fold_lines: Whether fold lines should be visible initially
            show_bleed_lines: Whether bleed lines should be visible initially
            show_gutter: Whether gutter should be visible initially
        """
        self.actions["show_margins"].setChecked(show_margins)
        self.actions["show_trim_lines"].setChecked(show_trim_lines)
        self.actions["show_barcode"].setChecked(show_barcode)
        self.actions["show_fold_lines"].setChecked(show_fold_lines)
        self.actions["show_bleed_lines"].setChecked(show_bleed_lines)
        if "show_gutter" in self.actions:
            self.actions["show_gutter"].setChecked(show_gutter)

    def update_view_menu_for_document_type(self, document_type: str) -> None:
        """Show/hide View menu items based on what's relevant for the document type.

        Args:
            document_type: One of 'interior', 'cover', or 'dustjacket'
        """
        try:
            show_barcode_action = self.actions.get("show_barcode")
            side_by_side_action = self.actions.get("side_by_side")
            show_bleed_lines_action = self.actions.get("show_bleed_lines")
            show_gutter_action = self.actions.get("show_gutter")
            go_to_page_action = self.actions.get("go_to_page")

            if not show_barcode_action or not side_by_side_action:
                logger.warning("Required menu actions not found")
                return

            if document_type == "interior":
                show_barcode_action.setVisible(False)
                side_by_side_action.setVisible(True)
                if show_bleed_lines_action:
                    show_bleed_lines_action.setVisible(False)
                if show_gutter_action:
                    show_gutter_action.setVisible(True)
                # Enable go_to_page for interior documents if a document is loaded
                if (
                    go_to_page_action
                    and hasattr(self.main_window, "document_presenter")
                    and self.main_window.document_presenter
                    and self.main_window.document_presenter.is_document_loaded()
                ):
                    go_to_page_action.setEnabled(True)
            elif document_type == "cover" or document_type == "dustjacket":
                show_barcode_action.setVisible(True)
                side_by_side_action.setVisible(False)
                if side_by_side_action.isChecked():
                    side_by_side_action.setChecked(False)
                if show_bleed_lines_action:
                    show_bleed_lines_action.setVisible(True)
                if show_gutter_action:
                    show_gutter_action.setVisible(False)
                # Disable go_to_page for cover/dustjacket documents
                if go_to_page_action:
                    go_to_page_action.setEnabled(False)
            else:
                logger.warning(f"Unknown document type: {document_type}")

            logger.info(f"Updated View menu for document type: {document_type}")

        except Exception as e:
            logger.error(f"Error updating View menu: {e}", exc_info=True)

    def _update_recent_files_menu(self) -> None:
        """Update the recent files submenu with current recent files."""
        if not hasattr(self, "recent_files_menu"):
            return

        self.recent_files_menu.clear()

        # Get recent files from configuration
        if hasattr(self.main_window, "config_manager"):
            recent_files = self.main_window.config_manager.get_recent_files()

            if not recent_files:
                action = self.recent_files_menu.addAction(
                    QCoreApplication.translate("MainWindow", "No Recent Files")
                )
                action.setEnabled(False)
                return

            # Add recent files with keyboard shortcuts
            from pathlib import Path

            for i, file_info in enumerate(recent_files[:5]):  # Max 5 files
                path = file_info.get("path", "")
                if not path:
                    continue

                filename = Path(path).name

                # Add number prefix for keyboard shortcut
                action_text = f"&{i+1}. {filename}"
                if file_info.get("document_type"):
                    action_text += f" ({file_info['document_type']})"

                action = self.recent_files_menu.addAction(action_text)
                action.setData(path)
                action.triggered.connect(
                    lambda _, p=path: self.main_window.load_recent_file(p)  # type: ignore[attr-defined]
                )

                # Add tooltip with full path
                action.setToolTip(path)

            self.recent_files_menu.addSeparator()

            # Add clear action
            clear_action = self.recent_files_menu.addAction(
                QCoreApplication.translate("MainWindow", "&Clear Recent Files")
            )
            clear_action.triggered.connect(self._clear_recent_files)
        else:
            action = self.recent_files_menu.addAction(
                QCoreApplication.translate("MainWindow", "No Recent Files")
            )
            action.setEnabled(False)

    def _clear_recent_files(self) -> None:
        """Clear the recent files list."""
        if hasattr(self.main_window, "config_manager"):
            self.main_window.config_manager.clear_recent_files()
            self._update_recent_files_menu()
