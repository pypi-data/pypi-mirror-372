"""Font information dialog for displaying PDF font details."""

from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class FontInfoDialog(QDialog):
    """Dialog for displaying font information from a PDF document.

    Shows a table with font details including name, type, embedded status,
    subset status, and encoding.
    """

    def __init__(
        self, parent: Optional[QWidget] = None, pdf_path: Optional[str] = None
    ) -> None:
        """Initialize the font information dialog.

        Args:
            parent: Parent widget for the dialog
            pdf_path: Path to the PDF file to extract font information from
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Font Information"))
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)
        self.resize(800, 500)

        self.pdf_path = pdf_path
        self._setup_ui()

        # Extract and display font information if PDF path is provided
        if self.pdf_path:
            self._load_font_information()

    def _setup_ui(self) -> None:
        """Build the dialog layout with table and controls."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Info label for status messages
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 11px; color: #666;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Create table for font information
        self.font_table = QTableWidget(0, 5)
        self.font_table.setHorizontalHeaderLabels(
            [
                self.tr("Font Name"),
                self.tr("Type"),
                self.tr("Embedded"),
                self.tr("Subset"),
                self.tr("Encoding"),
            ]
        )

        self.font_table.verticalHeader().setVisible(False)
        self.font_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.font_table.setAlternatingRowColors(True)
        self.font_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Configure column sizing
        header = self.font_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Font Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Embedded
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # Subset
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )  # Encoding

        layout.addWidget(self.font_table)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        # Set focus to OK button
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFocus()

    def _load_font_information(self) -> None:
        """Extract and display font information from the PDF."""
        try:
            # Try to import PyMuPDF
            try:
                import fitz  # type: ignore  # PyMuPDF
            except ImportError:
                self.info_label.setText(
                    self.tr(
                        "PyMuPDF is not installed. Please install it to view font information."
                    )
                )
                logger.warning(
                    "PyMuPDF not installed - cannot extract font information"
                )
                return

            # Open the PDF document
            try:
                doc = fitz.open(self.pdf_path)
            except Exception as e:
                self.info_label.setText(
                    self.tr("Failed to open PDF: {error}").format(error=str(e))
                )
                logger.error(f"Failed to open PDF for font extraction: {e}")
                return

            # Extract fonts from all pages
            all_fonts: dict[str, dict[str, Any]] = {}

            try:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    fonts = page.get_fonts(full=True)

                    for font in fonts:
                        # Font tuple structure from PyMuPDF:
                        # (xref, ext, type, basefont, name, encoding, subset_status)
                        if len(font) >= 7:
                            xref = font[0]
                            ext = font[1]
                            font_type = font[2]
                            basefont = font[
                                3
                            ]  # Actual font name (e.g., "BCDEEE+Calibri", "ArialMT")
                            name = font[
                                4
                            ]  # Internal PDF reference (e.g., "F129", "F37")
                            encoding = font[5] if font[5] else "Unknown"

                            # Clean up the basefont name by removing subset prefix if present
                            # Subset prefix is 6 uppercase letters followed by '+'
                            display_name = basefont
                            if (
                                basefont
                                and len(basefont) > 7
                                and basefont[6] == "+"
                                and all(
                                    c.isupper() or c.isdigit() for c in basefont[:6]
                                )
                            ):
                                display_name = basefont[7:]  # Remove the subset prefix

                            # Use basefont as display name, fallback to internal name if basefont is empty
                            if not display_name:
                                display_name = name if name else "Unknown"

                            # Create a unique key for the font
                            font_key = f"{xref}_{name}"

                            if font_key not in all_fonts:
                                all_fonts[font_key] = {
                                    "name": display_name,
                                    "type": ext.upper() if ext else "Unknown",
                                    "embedded": font_type
                                    != "Type3",  # Simplified check
                                    "subset": (
                                        basefont.startswith("+")
                                        if basefont and len(basefont) > 1
                                        else False
                                    ),
                                    "encoding": encoding,
                                    "xref": xref,
                                }

                doc.close()

            except Exception as e:
                doc.close()
                self.info_label.setText(
                    self.tr("Error extracting font information: {error}").format(
                        error=str(e)
                    )
                )
                logger.error(f"Error extracting font information: {e}")
                return

            # Populate the table with font information
            if not all_fonts:
                self.info_label.setText(self.tr("No fonts found in this PDF"))
                return

            self._populate_font_table(list(all_fonts.values()))

            # Update info label with count
            font_count = len(all_fonts)
            if font_count == 1:
                self.info_label.setText(self.tr("1 font found"))
            else:
                self.info_label.setText(
                    self.tr("{count} fonts found").format(count=font_count)
                )

        except Exception as e:
            logger.error(
                f"Unexpected error in font information extraction: {e}", exc_info=True
            )
            self.info_label.setText(
                self.tr("Unexpected error: {error}").format(error=str(e))
            )

    def _populate_font_table(self, fonts: list[dict[str, Any]]) -> None:
        """Populate the table with font information.

        Args:
            fonts: List of font dictionaries with font details
        """
        # Clear existing rows
        self.font_table.setRowCount(0)

        # Sort fonts by name for consistent display
        fonts.sort(key=lambda x: x.get("name", "").lower())

        # Add rows for each font
        for font_info in fonts:
            row_position = self.font_table.rowCount()
            self.font_table.insertRow(row_position)

            # Font Name
            name_item = QTableWidgetItem(font_info.get("name", "Unknown"))
            self.font_table.setItem(row_position, 0, name_item)

            # Type
            type_item = QTableWidgetItem(font_info.get("type", "Unknown"))
            self.font_table.setItem(row_position, 1, type_item)

            # Embedded
            embedded = font_info.get("embedded", False)
            embedded_text = self.tr("Yes") if embedded else self.tr("No")
            embedded_item = QTableWidgetItem(embedded_text)
            # Center align the embedded status
            embedded_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.font_table.setItem(row_position, 2, embedded_item)

            # Subset
            subset = font_info.get("subset", False)
            subset_text = self.tr("Yes") if subset else self.tr("No")
            subset_item = QTableWidgetItem(subset_text)
            # Center align the subset status
            subset_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.font_table.setItem(row_position, 3, subset_item)

            # Encoding
            encoding_item = QTableWidgetItem(font_info.get("encoding", "Unknown"))
            self.font_table.setItem(row_position, 4, encoding_item)

        # Resize rows to content
        self.font_table.resizeRowsToContents()
