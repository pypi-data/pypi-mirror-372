"""Direct PDF text selection using QPdfDocument's built-in capabilities."""

from collections.abc import Sequence
from typing import Optional, Union

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPolygonF
from PySide6.QtPdf import QPdfDocument, QPdfSelection

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class DirectPdfSelector:
    """Direct text selection using QPdfDocument's native selection methods."""

    def __init__(self, document: QPdfDocument, page_number: int):
        """Initialize the selector.

        Args:
            document: The PDF document
            page_number: Zero-based page number
        """
        self.document = document
        self.page_number = page_number

    def get_selection(
        self, start_point: QPointF, end_point: QPointF
    ) -> Optional[QPdfSelection]:
        """Get text selection between two points.

        This directly uses QPdfDocument.getSelection() which handles all the
        coordinate transformations and text flow internally.

        Args:
            start_point: Start point in page coordinates
            end_point: End point in page coordinates

        Returns:
            QPdfSelection object or None if no text
        """
        # QPdfDocument.getSelection expects the rectangle corners
        # It handles text flow selection internally
        selection = self.document.getSelection(self.page_number, start_point, end_point)

        if selection and selection.isValid():
            return selection

        return None

    def get_selection_bounds(
        self, selection: QPdfSelection
    ) -> Sequence[Union[QRectF, QPolygonF]]:
        """Get the visual bounds for a selection.

        Args:
            selection: The QPdfSelection object

        Returns:
            List of QRectF/QPolygonF representing the selection bounds
        """
        if selection and selection.isValid():
            return selection.bounds()
        return []
