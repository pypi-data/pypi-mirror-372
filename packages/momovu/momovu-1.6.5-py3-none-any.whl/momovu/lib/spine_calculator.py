"""Spine width calculator module providing unified spine calculations."""

from typing import Optional

from momovu.lib.constants import (
    MINIMUM_COVER_PAGES,
    MINIMUM_DUSTJACKET_PAGES,
    SPINE_WIDTH_DIVISOR,
    SPINE_WIDTH_OFFSET,
)
from momovu.lib.sizes.dustjacket_spine_widths import get_dustjacket_spine_width

# Lightning Source paper weight constants (pages per inch)
LIGHTNING_SOURCE_PPI = {
    38: 444,
    50: 400,
    70: 360,
}

# Lightning Source adjustments in mm
LIGHTNING_SOURCE_COVER_ADJUSTMENT = 0.635  # 0.025 inches
LIGHTNING_SOURCE_HARDCOVER_BOARDS = 5.0


def calculate_spine_width(
    page_count: int,
    printer: str = "lulu",
    document_type: str = "cover",
    paper_weight: Optional[int] = None,
) -> float:
    """Calculate spine width using the specified printer's formula.

    This is the main function for calculating spine width. It supports both
    Lulu and Lightning Source formulas, maintaining exact backward compatibility
    with existing Lulu calculations.

    Args:
        page_count: Number of pages in the book (must be positive)
        printer: Printer to use formula for ("lulu" or "lightning_source")
        document_type: Type of document ("cover" for paperback, "dustjacket" for hardcover)
        paper_weight: Paper weight in pounds (required for Lightning Source, ignored for Lulu)
                     Valid values: 38, 50, or 70

    Returns:
        Spine width in millimeters, rounded to 3 decimal places

    Raises:
        ValueError: If page_count is less than 1
        ValueError: If printer is "lightning_source" and paper_weight is not provided
        ValueError: If paper_weight is not a valid value (38, 50, or 70)

    Examples:
        >>> # Lulu paperback with 100 pages (default)
        >>> calculate_spine_width(100)
        7.245

        >>> # Lightning Source paperback with 100 pages on 50lb paper
        >>> calculate_spine_width(100, printer="lightning_source", paper_weight=50)
        6.985

        >>> # Lulu hardcover with 200 pages
        >>> calculate_spine_width(200, document_type="dustjacket")
        19.0
    """
    # Validate inputs
    if page_count < 1:
        raise ValueError(f"Page count must be at least 1, got {page_count}")

    if printer == "lulu":
        if document_type == "cover":
            spine_width = (page_count / SPINE_WIDTH_DIVISOR) + SPINE_WIDTH_OFFSET
            return round(spine_width, 3)
        else:  # dustjacket
            return get_dustjacket_spine_width(page_count)

    elif printer == "lightning_source":
        # Lightning Source formulas
        if paper_weight is None:
            raise ValueError(
                "Paper weight is required for Lightning Source calculations. "
                "Valid values are 38, 50, or 70."
            )

        if paper_weight not in LIGHTNING_SOURCE_PPI:
            raise ValueError(
                f"Invalid paper weight: {paper_weight}. "
                f"Valid values are: {', '.join(map(str, LIGHTNING_SOURCE_PPI.keys()))}"
            )

        ppi = LIGHTNING_SOURCE_PPI[paper_weight]
        spine_inches = page_count / ppi
        spine_mm = spine_inches * 25.4

        if document_type == "cover":
            spine_mm += LIGHTNING_SOURCE_COVER_ADJUSTMENT
        else:  # dustjacket
            spine_mm += LIGHTNING_SOURCE_HARDCOVER_BOARDS

        return round(spine_mm, 3)

    else:
        raise ValueError(
            f"Unknown printer: {printer}. Valid values are 'lulu' or 'lightning_source'"
        )


def calculate_dustjacket_spine_width(
    page_count: int,
    printer: str = "lulu",
    paper_weight: Optional[int] = None,
) -> float:
    """Calculate spine width specifically for dustjackets (hardcover books).

    This is a convenience function that calls calculate_spine_width with
    document_type="dustjacket". For Lulu, it uses the existing lookup table.
    For Lightning Source, it uses the formula plus 5mm for hardcover boards.

    Args:
        page_count: Number of pages in the book (must be positive)
        printer: Printer to use formula for ("lulu" or "lightning_source")
        paper_weight: Paper weight in pounds (required for Lightning Source)
                     Valid values: 38, 50, or 70

    Returns:
        Spine width in millimeters for dustjacket/hardcover

    Raises:
        ValueError: If page_count is less than 1
        ValueError: If printer is "lightning_source" and paper_weight is not provided
        ValueError: If paper_weight is not a valid value

    Examples:
        >>> # Lulu hardcover with 200 pages
        >>> calculate_dustjacket_spine_width(200)
        19.0

        >>> # Lightning Source hardcover with 200 pages on 50lb paper
        >>> calculate_dustjacket_spine_width(200, printer="lightning_source", paper_weight=50)
        17.7
    """
    return calculate_spine_width(
        page_count=page_count,
        printer=printer,
        document_type="dustjacket",
        paper_weight=paper_weight,
    )


def get_minimum_page_count(
    document_type: str = "cover",
) -> int:
    """Get the minimum page count requirement for a given document type.

    All printers use the same minimum page requirements for binding.

    Args:
        document_type: Type of document

    Returns:
        Minimum number of pages required

    Examples:
        >>> get_minimum_page_count("cover")
        32
        >>> get_minimum_page_count("dustjacket")
        24
    """
    if document_type == "cover":
        return MINIMUM_COVER_PAGES
    else:  # dustjacket
        return MINIMUM_DUSTJACKET_PAGES


def validate_page_count_range(
    page_count: int,
    printer: str = "lulu",
    document_type: str = "cover",
) -> tuple[bool, Optional[str]]:
    """Validate if page count is within acceptable range for printer and document type.

    Args:
        page_count: Number of pages to validate
        printer: Printer to validate for
        document_type: Type of document

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None

    Examples:
        >>> validate_page_count_range(100, "lulu", "cover")
        (True, None)
        >>> validate_page_count_range(10, "lulu", "cover")
        (False, 'Page count 10 is below minimum of 32 for lulu cover')
    """
    min_pages = get_minimum_page_count(document_type)

    if page_count < min_pages:
        return (
            False,
            f"Page count {page_count} is below minimum of {min_pages} "
            f"for {printer} {document_type}",
        )

    if printer == "lulu" and document_type == "dustjacket" and page_count > 800:
        return (
            False,
            f"Page count {page_count} exceeds maximum of 800 for Lulu dustjackets",
        )
    elif printer == "lightning_source" and page_count > 2000:
        return (
            False,
            f"Page count {page_count} exceeds maximum of 2000 for Lightning Source",
        )

    return (True, None)


def calculate_cover_spine_width(page_count: int) -> float:
    """Calculate spine width for covers using Lulu formula (backward compatibility).

    Args:
        page_count: Number of pages in the book

    Returns:
        Spine width in millimeters, rounded to 3 decimal places
    """
    return calculate_spine_width(page_count, printer="lulu", document_type="cover")
