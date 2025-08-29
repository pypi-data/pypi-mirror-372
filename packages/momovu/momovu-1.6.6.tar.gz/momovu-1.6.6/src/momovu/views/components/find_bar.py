"""Find bar widget for PDF search functionality.

This widget provides the UI for searching within PDF documents.
"""

from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class FindBar(QWidget):
    """Compact find bar that appears at bottom of window."""

    # Signals
    search_requested = Signal(str)  # Search query
    next_requested = Signal()
    previous_requested = Signal()
    close_requested = Signal()
    options_changed = Signal(bool, bool, bool)  # case_sensitive, whole_words, use_regex

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the find bar.

        Args:
            parent: Parent widget (usually MainWindow)
        """
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()

        # Debounce timer for search-as-you-type
        self._debounce_timer = QTimer()
        self._debounce_timer.timeout.connect(self._execute_search)
        self._debounce_timer.setSingleShot(True)

        # Hide by default
        self.hide()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setMaximumWidth(30)
        self.close_button.setToolTip(self.tr("Close find bar (Escape)"))
        layout.addWidget(self.close_button)

        # Search label
        search_label = QLabel(self.tr("Find:"))
        layout.addWidget(search_label)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.tr("Enter search text..."))
        self.search_input.setMinimumWidth(200)
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input)

        # Previous button
        self.prev_button = QPushButton("◀")
        self.prev_button.setMaximumWidth(30)
        self.prev_button.setToolTip(self.tr("Previous result (Shift+F3)"))
        self.prev_button.setEnabled(False)
        layout.addWidget(self.prev_button)

        # Next button
        self.next_button = QPushButton("▶")
        self.next_button.setMaximumWidth(30)
        self.next_button.setToolTip(self.tr("Next result (F3)"))
        self.next_button.setEnabled(False)
        layout.addWidget(self.next_button)

        # Result counter
        self.result_label = QLabel(self.tr("No results"))
        self.result_label.setMinimumWidth(100)
        layout.addWidget(self.result_label)

        # Separator
        separator = QLabel("|")
        layout.addWidget(separator)

        # Options
        self.case_checkbox = QCheckBox("Aa")
        self.case_checkbox.setToolTip(self.tr("Case sensitive"))
        layout.addWidget(self.case_checkbox)

        self.whole_word_checkbox = QCheckBox("W")
        self.whole_word_checkbox.setToolTip(self.tr("Whole words"))
        layout.addWidget(self.whole_word_checkbox)

        self.regex_checkbox = QCheckBox(".*")
        self.regex_checkbox.setToolTip(self.tr("Regular expression"))
        layout.addWidget(self.regex_checkbox)

        # Add stretch to push everything to the left
        layout.addStretch()

        self.setLayout(layout)

        # Style the widget
        self.setStyleSheet(
            """
            FindBar {
                background-color: #f0f0f0;
                border-top: 1px solid #d0d0d0;
            }
            QLineEdit {
                padding: 2px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
            }
            QPushButton {
                padding: 2px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                color: #a0a0a0;
                background-color: #f5f5f5;
            }
            QCheckBox {
                spacing: 2px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
        """
        )

    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Button clicks
        self.close_button.clicked.connect(self.hide_bar)
        self.prev_button.clicked.connect(self.previous_requested.emit)
        self.next_button.clicked.connect(self.next_requested.emit)

        # Search input
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self._on_return_pressed)

        # Options
        self.case_checkbox.toggled.connect(self._on_options_changed)
        self.whole_word_checkbox.toggled.connect(self._on_options_changed)
        self.regex_checkbox.toggled.connect(self._on_options_changed)

    def _on_text_changed(self, text: str) -> None:
        """Handle text change with debouncing.

        Args:
            text: Current text in search input
        """
        # Enable/disable navigation buttons based on text
        has_text = bool(text.strip())
        self.prev_button.setEnabled(has_text)
        self.next_button.setEnabled(has_text)

        # Debounce search (300ms delay)
        self._debounce_timer.stop()
        if has_text:
            self._debounce_timer.start(300)
        else:
            # Clear search immediately when text is cleared
            self.result_label.setText(self.tr("No results"))
            self.search_requested.emit("")

    def _on_return_pressed(self) -> None:
        """Handle Enter key - search immediately or go to next result."""
        self._debounce_timer.stop()
        text = self.search_input.text().strip()
        if text:
            # If we already have results, go to next
            # Otherwise, execute search
            if (
                "result" in self.result_label.text().lower()
                and "no" not in self.result_label.text().lower()
            ):
                self.next_requested.emit()
            else:
                self._execute_search()

    def _execute_search(self) -> None:
        """Execute the search with current text."""
        text = self.search_input.text().strip()
        if text:
            self.search_requested.emit(text)

    def _on_options_changed(self) -> None:
        """Handle search options change."""
        # Emit options changed signal
        self.options_changed.emit(
            self.case_checkbox.isChecked(),
            self.whole_word_checkbox.isChecked(),
            self.regex_checkbox.isChecked(),
        )

        # Re-execute search if we have text
        text = self.search_input.text().strip()
        if text:
            self._debounce_timer.stop()
            self._debounce_timer.start(100)  # Shorter delay for option changes

    def show_bar(self) -> None:
        """Show the find bar and focus the search input."""
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def hide_bar(self) -> None:
        """Hide the find bar and clear search."""
        self.hide()
        self.search_input.clear()
        self.result_label.setText(self.tr("No results"))
        self.close_requested.emit()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events.

        Args:
            event: Key press event
        """
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Escape:
            # Escape closes the find bar
            self.hide_bar()
            event.accept()
        elif key == Qt.Key.Key_F3:
            # F3 navigates results
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.previous_requested.emit()
            else:
                self.next_requested.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

    def update_result_count(self, current: int, total: int) -> None:
        """Update the result counter display.

        Args:
            current: Current result index (0-based, -1 for none)
            total: Total number of results
        """
        if total == 0:
            self.result_label.setText(self.tr("No results"))
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        elif current == -1:
            # Have results but none selected
            if total == 1:
                self.result_label.setText(self.tr("%n result", "", total))
            else:
                self.result_label.setText(self.tr("%n results", "", total))
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)
        else:
            # Show current position
            self.result_label.setText(
                self.tr("%1 of %2")
                .replace("%1", str(current + 1))
                .replace("%2", str(total))
            )
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)

    def set_search_text(self, text: str) -> None:
        """Set the search text programmatically.

        Args:
            text: Text to set in search input
        """
        self.search_input.setText(text)

    def get_search_text(self) -> str:
        """Get the current search text.

        Returns:
            Current text in search input
        """
        return self.search_input.text()

    def get_search_options(self) -> tuple[bool, bool, bool]:
        """Get current search options.

        Returns:
            Tuple of (case_sensitive, whole_words, use_regex)
        """
        return (
            self.case_checkbox.isChecked(),
            self.whole_word_checkbox.isChecked(),
            self.regex_checkbox.isChecked(),
        )

    def set_search_options(
        self, case_sensitive: bool, whole_words: bool, use_regex: bool
    ) -> None:
        """Set search options programmatically.

        Args:
            case_sensitive: Whether search is case-sensitive
            whole_words: Whether to match whole words only
            use_regex: Whether to use regex patterns
        """
        self.case_checkbox.setChecked(case_sensitive)
        self.whole_word_checkbox.setChecked(whole_words)
        self.regex_checkbox.setChecked(use_regex)

    def clear_search(self) -> None:
        """Clear the search input and results."""
        self.search_input.clear()
        self.result_label.setText(self.tr("No results"))
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
