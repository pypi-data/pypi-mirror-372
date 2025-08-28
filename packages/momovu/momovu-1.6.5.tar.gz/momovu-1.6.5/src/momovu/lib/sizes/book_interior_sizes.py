"""Book interior trim size constants for various book formats.

This module defines the standard interior trim sizes for different book formats.
All measurements are in millimeters (mm) and represent the final trimmed page dimensions.

Data source: Lulu book sizes for interior pages
Note: These constants are prepared for future use in the application.
"""

# Book interior trim sizes in millimeters
# Format: (width_mm, height_mm)
BOOK_INTERIOR_SIZES = {
    "A4": (210.000, 297.000),
    "A4_LANDSCAPE": (297.000, 210.000),
    "A5": (148.000, 210.000),
    "DIGEST": (139.700, 215.900),
    "EXECUTIVE": (177.800, 254.000),
    "NOVELLA": (127.000, 203.200),
    "POCKET_BOOK": (107.950, 174.625),
    "SMALL_LANDSCAPE": (228.600, 177.800),
    "SMALL_SQUARE": (190.500, 190.500),
    "US_LETTER": (215.900, 279.400),
    "US_LETTER_LANDSCAPE": (279.400, 215.900),
    "US_TRADE": (152.400, 228.600),
}
