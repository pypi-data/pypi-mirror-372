"""Calculator dialog for book production."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.constants import (
    GUTTER_SIZE_THRESHOLDS,
    MINIMUM_COVER_PAGES,
    MINIMUM_DUSTJACKET_PAGES,
)
from momovu.lib.logger import get_logger
from momovu.lib.sizes.book_interior_sizes import BOOK_INTERIOR_SIZES
from momovu.lib.spine_calculator import (
    calculate_spine_width,
    validate_page_count_range,
)

logger = get_logger(__name__)


def format_value_with_precision(value: float) -> str:
    """Format value to 3 decimal places, removing trailing zeros.

    Args:
        value: Value in millimeters

    Returns:
        Formatted string without unnecessary trailing zeros
    """
    # Format to 3 decimal places, then remove trailing zeros
    formatted = f"{value:.3f}".rstrip("0").rstrip(".")
    return formatted


def format_spine_width(width: float) -> str:
    """Format spine width removing unnecessary trailing zeros.

    Args:
        width: Spine width in millimeters

    Returns:
        Formatted string without trailing zeros
    """
    return format_value_with_precision(width)


class SpineWidthCalculatorDialog(QDialog):
    """Dialog for calculating spine width based on page count and document type.

    Uses official Lulu formulas or Lightning Source formulas based on user preference:
    - Covers (Paperback): Formula-based calculation
    - Dustjackets (Hardcover): Lookup table for Lulu, formula for Lightning Source
    """

    def __init__(
        self, parent: Optional[QWidget] = None, initial_pages: int = 100
    ) -> None:
        """Initialize the calculator dialog.

        Args:
            parent: Parent widget for the dialog
            initial_pages: Initial page count to display
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Calculator"))
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        # Set a reasonable default size to avoid scrollbars
        self.resize(750, 800)  # Increased height for better visibility
        self.initial_pages = initial_pages

        # Get configuration manager instance
        self.config_manager = ConfigurationManager()

        self._setup_ui()
        self._connect_signals()

        # Calculate initial values
        self._calculate_spine_width()
        self._update_document_sizes()
        self._update_production_details()

        logger.debug(f"Calculator dialog initialized with {initial_pages} pages")

    def _setup_ui(self) -> None:
        """Build the dialog layout with input controls and result display."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Reduced spacing to remove extra gaps

        # Page count input
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel(self.tr("Number of Pages:")))

        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(999)
        self.page_spinbox.setValue(self.initial_pages)
        self.page_spinbox.setToolTip(self.tr("Enter the total number of pages (1-999)"))
        page_layout.addWidget(self.page_spinbox)
        page_layout.addStretch()

        layout.addLayout(page_layout)

        # Document type selection
        type_group = QGroupBox(self.tr("Document Type"))
        type_layout = QVBoxLayout()
        type_layout.setContentsMargins(
            9, 9, 9, 0
        )  # Reduced bottom margin to match spacing

        self.cover_radio = QRadioButton(self.tr("Cover"))
        self.cover_radio.setChecked(True)  # Default selection
        type_layout.addWidget(self.cover_radio)

        self.dustjacket_radio = QRadioButton(self.tr("Dustjacket"))
        type_layout.addWidget(self.dustjacket_radio)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Info label for validation messages
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 11px; color: #666;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Document dimensions table
        dimensions_group = QGroupBox(self.tr("Document Dimensions"))
        dimensions_layout = QVBoxLayout()

        self.dimensions_table = self._setup_document_size_table()
        dimensions_layout.addWidget(self.dimensions_table)

        dimensions_group.setLayout(dimensions_layout)
        layout.addWidget(dimensions_group)

        # Production details table
        production_group = QGroupBox(self.tr("Production Details"))
        production_layout = QVBoxLayout()

        self.production_table = self._setup_production_details_table()
        production_layout.addWidget(self.production_table)

        production_group.setLayout(production_layout)
        layout.addWidget(production_group)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        # Set focus to OK button
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFocus()

    def _connect_signals(self) -> None:
        """Connect UI signals to calculation methods."""
        self.page_spinbox.valueChanged.connect(self._calculate_spine_width)
        self.page_spinbox.valueChanged.connect(self._update_document_sizes)
        self.page_spinbox.valueChanged.connect(self._update_production_details)
        self.cover_radio.toggled.connect(self._calculate_spine_width)
        self.cover_radio.toggled.connect(self._update_document_sizes)
        self.cover_radio.toggled.connect(self._update_production_details)
        self.dustjacket_radio.toggled.connect(self._calculate_spine_width)
        self.dustjacket_radio.toggled.connect(self._update_document_sizes)
        self.dustjacket_radio.toggled.connect(self._update_production_details)

    def _calculate_spine_width(self) -> None:
        """Calculate and display spine width based on current inputs."""
        page_count = self.page_spinbox.value()

        # Get printer preference and paper weight from configuration
        printer = self.config_manager.get_printer_formula()
        paper_weight = None
        if printer == "lightning_source":
            paper_weight = self.config_manager.get_lightning_source_paper_weight()

        # Determine document type
        document_type = "cover" if self.cover_radio.isChecked() else "dustjacket"

        if document_type == "cover" and page_count < MINIMUM_COVER_PAGES:
            self.info_label.setText(
                self.tr("Minimum {pages} pages required for covers").format(
                    pages=MINIMUM_COVER_PAGES
                )
            )
            return
        elif document_type == "dustjacket" and page_count < MINIMUM_DUSTJACKET_PAGES:
            self.info_label.setText(
                self.tr("Minimum {pages} pages required for dustjackets").format(
                    pages=MINIMUM_DUSTJACKET_PAGES
                )
            )
            return

        # Validate page count range for maximum limits
        is_valid, error_msg = validate_page_count_range(
            page_count, printer, document_type
        )

        if not is_valid and error_msg:
            # Only show error for maximum page count violations
            if "exceeds maximum" in error_msg.lower():
                self.info_label.setText(self.tr(error_msg))
            return

        try:
            # Calculate spine width using the centralized calculator
            spine_width = calculate_spine_width(
                page_count=page_count,
                printer=printer,
                document_type=document_type,
                paper_weight=paper_weight,
            )

            # Clear any previous info message
            self.info_label.setText("")

            logger.debug(
                f"Calculated spine width: {spine_width}mm for {page_count} pages "
                f"({document_type}, printer: {printer})"
            )

        except Exception as e:
            logger.error(f"Error calculating spine width: {e}")
            self.info_label.setText(self.tr("Error calculating spine width"))

    def _setup_document_size_table(self) -> QTableWidget:
        """Create and configure the document dimensions table.

        Returns:
            Configured QTableWidget for displaying document dimensions
        """
        num_formats = len(BOOK_INTERIOR_SIZES)
        table = QTableWidget(num_formats, 3)
        table.setHorizontalHeaderLabels(
            [
                self.tr("Book Format"),
                self.tr("Trim Size"),
                self.tr("Total Document Size"),
            ]
        )

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Set size policy to expand vertically (this table should grow with window)
        table.setSizePolicy(
            table.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Expanding
        )

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)

        # Set font-based row height
        font_metrics = table.fontMetrics()
        row_height = int(font_metrics.height() * 1.25)
        table.verticalHeader().setDefaultSectionSize(row_height)

        for row, format_key in enumerate(BOOK_INTERIOR_SIZES):
            format_name = self._format_book_name(format_key)
            table.setItem(row, 0, QTableWidgetItem(format_name))

        return table

    def _format_book_name(self, key: str) -> str:
        """Convert book format key to display name.

        Args:
            key: Format key from BOOK_INTERIOR_SIZES (e.g., 'POCKET_BOOK')

        Returns:
            Formatted display name (e.g., 'Pocket Book')
        """
        if key.startswith("US_"):
            return "US " + key[3:].replace("_", " ").title()
        return key.replace("_", " ").title()

    def _get_spine_width_for_table(self) -> float:
        """Get spine width for table calculations.

        Always returns a valid spine width, even when page count
        is outside normal ranges.

        Returns:
            Spine width in millimeters
        """
        page_count = self.page_spinbox.value()

        # Get printer preference and paper weight from configuration
        printer = self.config_manager.get_printer_formula()
        paper_weight = None
        if printer == "lightning_source":
            paper_weight = self.config_manager.get_lightning_source_paper_weight()

        # Determine document type
        document_type = "cover" if self.cover_radio.isChecked() else "dustjacket"

        try:
            spine_width = calculate_spine_width(
                page_count=page_count,
                printer=printer,
                document_type=document_type,
                paper_weight=paper_weight,
            )
            return spine_width
        except Exception as e:
            logger.warning(f"Error calculating spine width for table: {e}")
            return 6.0 if document_type == "dustjacket" else 3.0

    def _calculate_document_size(
        self, trim_width: float, trim_height: float
    ) -> tuple[float, float]:
        """Calculate total document dimensions for a book format.

        Args:
            trim_width: Trim width in millimeters
            trim_height: Trim height in millimeters

        Returns:
            Tuple of (total_width, total_height) in millimeters
        """
        spine_width = self._get_spine_width_for_table()

        if self.cover_radio.isChecked():
            cover_bleed = self.config_manager.get_cover_bleed_mm()
            total_width = (trim_width * 2) + spine_width + (cover_bleed * 2)
            total_height = trim_height + (cover_bleed * 2)
        else:
            dustjacket_bleed = self.config_manager.get_dustjacket_bleed_mm()
            flap_width = self.config_manager.get_dustjacket_flap_width_mm()
            fold_safety_margin = (
                self.config_manager.get_dustjacket_fold_safety_margin_mm()
            )
            total_width = (
                (trim_width * 2)
                + spine_width
                + (flap_width * 2)
                + (dustjacket_bleed * 2)
                + (fold_safety_margin * 3)
            )
            total_height = trim_height + (dustjacket_bleed * 2) + fold_safety_margin

        return (total_width, total_height)

    def _format_dimension(self, width: float, height: float) -> str:
        """Format dimensions as a display string.

        Args:
            width: Width in millimeters
            height: Height in millimeters

        Returns:
            Formatted string like '210.00 × 297.00 mm'
        """
        return f"{width:.2f} × {height:.2f} mm"

    def _setup_production_details_table(self) -> QTableWidget:
        """Create and configure the production details table.

        Returns:
            Configured QTableWidget for displaying production details
        """
        # Create table with 3 columns
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(
            [
                self.tr("Dimension"),
                self.tr("Value"),
                self.tr("Notes"),
            ]
        )

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Set size policy to NOT expand (this table should stay compact)
        table.setSizePolicy(
            table.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Minimum
        )

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # Set font-based row height (same as document dimensions table)
        font_metrics = table.fontMetrics()
        row_height = int(font_metrics.height() * 1.25)
        table.verticalHeader().setDefaultSectionSize(row_height)

        return table

    def _calculate_gutter_width(self, page_count: int) -> float:
        """Calculate gutter width based on page count for interior documents.

        This uses the same logic as MarginPresenter._calculate_gutter_width()
        but returns the value in mm instead of points.

        Args:
            page_count: Number of pages in the document

        Returns:
            Gutter width in millimeters
        """
        if page_count <= 0:
            page_count = 100  # Default

        # Find appropriate gutter size from thresholds
        gutter_width_mm = 0.0
        for threshold, width in GUTTER_SIZE_THRESHOLDS:
            if page_count <= threshold:
                gutter_width_mm = width
                break

        return gutter_width_mm

    def _update_production_details(self) -> None:
        """Update the production details table based on document type."""
        # Clear existing rows
        self.production_table.setRowCount(0)

        page_count = self.page_spinbox.value()

        # Calculate spine width for display
        spine_width = self._get_spine_width_for_table()
        spine_width_str = f"{format_value_with_precision(spine_width)} mm"

        # Calculate gutter width
        gutter_width = self._calculate_gutter_width(page_count)
        gutter_width_str = f"{format_value_with_precision(gutter_width)} mm"

        # Get configuration values
        safety_margin = self.config_manager.get_safety_margin_mm()
        barcode_width = self.config_manager.get_barcode_width_mm()
        barcode_height = self.config_manager.get_barcode_height_mm()

        # Build rows list - all rows will be alphabetized including Spine Width
        all_rows = []

        if self.cover_radio.isChecked():
            cover_bleed = self.config_manager.get_cover_bleed_mm()
            # Add cover-specific details with English keys for sorting
            all_rows = [
                (
                    "Barcode Area",
                    self.tr("Barcode Area"),
                    f"{format_value_with_precision(barcode_width)} × {format_value_with_precision(barcode_height)} mm",
                    self.tr("ISBN barcode placement area"),
                ),
                (
                    "Bleed Area",
                    self.tr("Bleed Area"),
                    f"{format_value_with_precision(cover_bleed)} mm",
                    self.tr("Extends beyond trim edge"),
                ),
                (
                    "Gutter Width (per page)",
                    self.tr("Gutter Width (per page)"),
                    gutter_width_str,
                    self.tr("Added to safety margin for binding"),
                ),
                (
                    "Safety Margin",
                    self.tr("Safety Margin"),
                    f"{format_value_with_precision(safety_margin)} mm",
                    self.tr("Minimum distance from trim edge"),
                ),
                (
                    "Spine Width",
                    self.tr("Spine Width"),
                    spine_width_str,
                    self.tr("Calculated based on {pages} pages").format(
                        pages=page_count
                    ),
                ),
            ]
        else:
            dustjacket_bleed = self.config_manager.get_dustjacket_bleed_mm()
            flap_width = self.config_manager.get_dustjacket_flap_width_mm()
            fold_safety_margin = (
                self.config_manager.get_dustjacket_fold_safety_margin_mm()
            )
            # Add dustjacket-specific details with English keys for sorting
            all_rows = [
                (
                    "Barcode Area",
                    self.tr("Barcode Area"),
                    f"{format_value_with_precision(barcode_width)} × {format_value_with_precision(barcode_height)} mm",
                    self.tr("ISBN barcode placement area"),
                ),
                (
                    "Bleed Area",
                    self.tr("Bleed Area"),
                    f"{format_value_with_precision(dustjacket_bleed)} mm",
                    self.tr("Extends beyond trim edge"),
                ),
                (
                    "Flap Width",
                    self.tr("Flap Width"),
                    f"{format_value_with_precision(flap_width)} mm",
                    self.tr("Width of front and back flaps"),
                ),
                (
                    "Fold Safety Margin",
                    self.tr("Fold Safety Margin"),
                    f"{format_value_with_precision(fold_safety_margin)} mm",
                    self.tr("Safety margin at fold lines"),
                ),
                (
                    "Gutter Width (per page)",
                    self.tr("Gutter Width (per page)"),
                    gutter_width_str,
                    self.tr("Added to safety margin for binding"),
                ),
                (
                    "Safety Margin",
                    self.tr("Safety Margin"),
                    f"{format_value_with_precision(safety_margin)} mm",
                    self.tr("Minimum distance from trim edge"),
                ),
                (
                    "Spine Width",
                    self.tr("Spine Width"),
                    spine_width_str,
                    self.tr("Calculated based on {pages} pages").format(
                        pages=page_count
                    ),
                ),
            ]

        # Sort all_rows alphabetically by English key (first element of tuple)
        all_rows.sort(key=lambda x: x[0])

        # Extract display values from tuples for the table
        rows = [(row[1], row[2], row[3]) for row in all_rows]

        # Add rows to table
        for row_data in rows:
            row_position = self.production_table.rowCount()
            self.production_table.insertRow(row_position)

            dimension_item = QTableWidgetItem(row_data[0])
            value_item = QTableWidgetItem(row_data[1])
            notes_item = QTableWidgetItem(row_data[2])

            # Don't make value column bold - keep normal weight

            self.production_table.setItem(row_position, 0, dimension_item)
            self.production_table.setItem(row_position, 1, value_item)
            self.production_table.setItem(row_position, 2, notes_item)

        # Don't resize rows - use the default consistent height set in _setup_production_details_table
        # This keeps row heights consistent with the document dimensions table

        # Calculate and set fixed height for production table
        row_count = self.production_table.rowCount()
        row_height = self.production_table.verticalHeader().defaultSectionSize()
        total_height = (
            (row_count * row_height)
            + self.production_table.horizontalHeader().height()
            + 2
        )

        # Set both minimum and maximum height to keep table compact
        self.production_table.setMinimumHeight(total_height)
        self.production_table.setMaximumHeight(total_height)

        logger.debug(
            f"Updated production details for "
            f"{'cover' if self.cover_radio.isChecked() else 'dustjacket'} document"
        )

    def _update_document_sizes(self) -> None:
        """Update all rows in the document dimensions table."""
        for row, (_format_key, (trim_width, trim_height)) in enumerate(
            BOOK_INTERIOR_SIZES.items()
        ):
            # Set trim size column
            trim_size_str = self._format_dimension(trim_width, trim_height)
            self.dimensions_table.setItem(row, 1, QTableWidgetItem(trim_size_str))

            # Calculate and set total document size
            total_width, total_height = self._calculate_document_size(
                trim_width, trim_height
            )
            total_size_str = self._format_dimension(total_width, total_height)
            self.dimensions_table.setItem(row, 2, QTableWidgetItem(total_size_str))

        logger.debug(
            f"Updated document sizes for all formats "
            f"({'cover' if self.cover_radio.isChecked() else 'dustjacket'} mode)"
        )
