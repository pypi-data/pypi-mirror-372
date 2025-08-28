"""Search model for find functionality in PDF viewer.

This model manages search state following the MVP pattern.
"""

from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QRectF

from momovu.lib.logger import get_logger
from momovu.models.base import BaseModel

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""

    page_num: int
    text: str
    char_start: int
    char_end: int
    bounds: Optional[QRectF] = None  # Made optional for deferred calculation

    def __hash__(self) -> int:
        """Make SearchResult hashable for use in sets."""
        return hash((self.page_num, self.char_start, self.char_end))


class SearchModel(BaseModel):
    """Model for search state following MVP pattern."""

    MAX_RESULTS_IN_MEMORY = 1000  # Hard limit
    MAX_CACHED_PAGES = 50  # Pages to keep text cached

    def __init__(self) -> None:
        """Initialize the search model."""
        super().__init__()

        # Search parameters
        self.search_query: str = ""
        self.case_sensitive: bool = False
        self.whole_words: bool = False
        self.use_regex: bool = False

        # Results storage with memory management
        self.results: list[SearchResult] = []
        self.current_result_index: int = -1
        self.total_results_found: int = 0  # May exceed MAX_RESULTS_IN_MEMORY

        # Text cache with LRU eviction
        self._text_cache: OrderedDict[int, str] = OrderedDict()

        # Search state
        self.is_searching: bool = False
        self.search_cancelled: bool = False
        self.last_search_time: float = 0

        # Initialize properties
        self._init_properties()

    def _init_properties(self) -> None:
        """Initialize model properties for change notification."""
        self.set_property("search_query", "")
        self.set_property("case_sensitive", False)
        self.set_property("whole_words", False)
        self.set_property("use_regex", False)
        self.set_property("is_searching", False)
        self.set_property("current_result_index", -1)
        self.set_property("total_results_found", 0)

    def set_search_query(self, query: str) -> None:
        """Set the search query.

        Args:
            query: The search query string
        """
        self.search_query = query
        self.set_property("search_query", query)

    def set_case_sensitive(self, value: bool) -> None:
        """Set case sensitivity option.

        Args:
            value: True for case-sensitive search
        """
        self.case_sensitive = value
        self.set_property("case_sensitive", value)

    def set_whole_words(self, value: bool) -> None:
        """Set whole words option.

        Args:
            value: True to match whole words only
        """
        self.whole_words = value
        self.set_property("whole_words", value)

    def set_use_regex(self, value: bool) -> None:
        """Set regex option.

        Args:
            value: True to use regex patterns
        """
        self.use_regex = value
        self.set_property("use_regex", value)

    def add_results(self, new_results: list[SearchResult]) -> None:
        """Add results with memory management and duplicate detection.

        Args:
            new_results: List of new search results to add
        """
        # Check for duplicates before adding
        for result in new_results:
            # Check if this exact result already exists
            is_duplicate = False
            for existing in self.results:
                if (
                    existing.page_num == result.page_num
                    and existing.char_start == result.char_start
                    and existing.char_end == result.char_end
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                if len(self.results) >= self.MAX_RESULTS_IN_MEMORY:
                    # Stop storing but continue counting
                    self.total_results_found += 1
                    logger.debug(
                        f"Result limit reached, counting only: {self.total_results_found}"
                    )
                    continue
                self.results.append(result)
                self.total_results_found += 1

        # Notify observers
        self.set_property("total_results_found", self.total_results_found)

    def cache_page_text(self, page_num: int, text: str) -> None:
        """Cache page text with LRU eviction.

        Args:
            page_num: Page number
            text: Extracted text from the page
        """
        if page_num in self._text_cache:
            # Move to end (most recently used)
            self._text_cache.move_to_end(page_num)
        else:
            if len(self._text_cache) >= self.MAX_CACHED_PAGES:
                # Remove least recently used
                self._text_cache.popitem(last=False)
                logger.debug(
                    f"Evicted oldest page from text cache, size: {len(self._text_cache)}"
                )
            self._text_cache[page_num] = text

    def get_cached_text(self, page_num: int) -> Optional[str]:
        """Get cached text for a page.

        Args:
            page_num: Page number

        Returns:
            Cached text or None if not in cache
        """
        if page_num in self._text_cache:
            # Move to end (most recently used)
            self._text_cache.move_to_end(page_num)
            return self._text_cache[page_num]
        return None

    def clear_results(self) -> None:
        """Clear all search results."""
        self.results.clear()
        self.current_result_index = -1
        self.total_results_found = 0

        # Notify observers
        self.set_property("current_result_index", -1)
        self.set_property("total_results_found", 0)

    def clear_cache(self) -> None:
        """Clear the text cache."""
        self._text_cache.clear()
        logger.debug("Text cache cleared")

    def set_current_result(self, index: int) -> None:
        """Set the current result index.

        Args:
            index: Index of the current result (-1 for none)
        """
        if -1 <= index < len(self.results):
            self.current_result_index = index
            self.set_property("current_result_index", index)

    def get_current_result(self) -> Optional[SearchResult]:
        """Get the current search result.

        Returns:
            Current SearchResult or None
        """
        if 0 <= self.current_result_index < len(self.results):
            return self.results[self.current_result_index]
        return None

    def navigate_to_next_result(self) -> Optional[SearchResult]:
        """Navigate to the next search result.

        Returns:
            The next SearchResult or None if no results
        """
        if not self.results:
            return None

        # Wrap around to first result
        new_index = (self.current_result_index + 1) % len(self.results)
        self.set_current_result(new_index)
        return self.get_current_result()

    def navigate_to_previous_result(self) -> Optional[SearchResult]:
        """Navigate to the previous search result.

        Returns:
            The previous SearchResult or None if no results
        """
        if not self.results:
            return None

        # Wrap around to last result
        new_index = (self.current_result_index - 1) % len(self.results)
        self.set_current_result(new_index)
        return self.get_current_result()

    def set_searching(self, is_searching: bool) -> None:
        """Set the searching state.

        Args:
            is_searching: True if currently searching
        """
        self.is_searching = is_searching
        self.set_property("is_searching", is_searching)

    def cancel_search(self) -> None:
        """Cancel the current search operation."""
        self.search_cancelled = True
        self.set_searching(False)

    def reset_search_state(self) -> None:
        """Reset search state for a new search."""
        self.search_cancelled = False
        self.clear_results()
        self.set_searching(True)
