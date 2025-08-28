"""Search presenter for find functionality in PDF viewer.

This presenter manages search operations following the MVP pattern.
"""

import re
import time
from enum import Enum
from typing import Any, Optional

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtPdf import QPdfDocument

from momovu.lib.logger import get_logger
from momovu.models.search import SearchModel, SearchResult
from momovu.presenters.base import BasePresenter

logger = get_logger(__name__)


class SearchError(Enum):
    """Search error types."""

    ENCRYPTED_PDF = "encrypted_pdf"
    NO_TEXT_LAYER = "no_text_layer"
    MEMORY_EXHAUSTED = "memory_exhausted"
    INVALID_REGEX = "invalid_regex"
    UNICODE_ERROR = "unicode_error"


class SearchOptions:
    """Options for search operation."""

    def __init__(
        self,
        case_sensitive: bool = False,
        whole_words: bool = False,
        use_regex: bool = False,
    ) -> None:
        """Initialize search options.

        Args:
            case_sensitive: Whether search is case-sensitive
            whole_words: Whether to match whole words only
            use_regex: Whether to use regex patterns
        """
        self.case_sensitive = case_sensitive
        self.whole_words = whole_words
        self.use_regex = use_regex


class SearchThread(QThread):
    """Background thread for search operations."""

    # Signals - include search ID to filter old results
    results_ready = Signal(list, int)  # list[SearchResult], search_id
    search_complete = Signal(int)  # search_id
    search_error = Signal(str, int)  # error_msg, search_id
    progress_update = Signal(int, int)  # current_page, total_pages

    def __init__(
        self,
        document: QPdfDocument,
        query: str,
        options: SearchOptions,
        visible_pages: list[int],
        total_pages: int,
        search_id: int = 0,  # Unique ID to identify this search
    ) -> None:
        """Initialize search thread.

        Args:
            document: PDF document to search
            query: Search query
            options: Search options
            visible_pages: Currently visible pages (search these first)
            total_pages: Total number of pages
            search_id: Unique ID for this search
        """
        super().__init__()
        self.document = document
        self.query = query
        self.options = options
        self.visible_pages = visible_pages
        self.total_pages = total_pages
        self.cancelled = False
        self.search_id = search_id  # Store search ID to tag results

    def run(self) -> None:
        """Execute search in background."""
        try:
            # Compile search pattern
            pattern = self._compile_pattern(self.query, self.options)
            if not pattern:
                self.search_error.emit("Invalid search pattern")
                return

            # Track if we found any results
            found_any_results = False

            # Search visible pages first for immediate feedback
            for page_num in self.visible_pages:
                if self.cancelled:
                    return

                results = self._search_page(page_num, pattern)
                if results:
                    self.results_ready.emit(results, self.search_id)
                    found_any_results = True

                self.progress_update.emit(page_num + 1, self.total_pages)

            # Then search remaining pages
            remaining_pages = [
                p for p in range(self.total_pages) if p not in self.visible_pages
            ]

            for page_num in remaining_pages:
                if self.cancelled:
                    return

                results = self._search_page(page_num, pattern)
                if results:
                    self.results_ready.emit(results, self.search_id)
                    found_any_results = True

                self.progress_update.emit(page_num + 1, self.total_pages)

            # If no results found on any page, emit empty results to clear old search
            if not found_any_results:
                self.results_ready.emit([], self.search_id)

            self.search_complete.emit(self.search_id)

        except Exception as e:
            logger.error(f"Search thread error: {e}", exc_info=True)
            self.search_error.emit(str(e), self.search_id)

    def cancel(self) -> None:
        """Cancel the search operation."""
        self.cancelled = True

    def _compile_pattern(
        self, query: str, options: SearchOptions
    ) -> Optional[re.Pattern[str]]:
        """Compile search pattern based on options.

        Args:
            query: Search query
            options: Search options

        Returns:
            Compiled regex pattern or None if invalid
        """
        try:
            # Build pattern based on options
            pattern_str = query if options.use_regex else re.escape(query)

            if options.whole_words:
                pattern_str = r"\b" + pattern_str + r"\b"

            # Compile with appropriate flags
            flags = 0 if options.case_sensitive else re.IGNORECASE

            return re.compile(pattern_str, flags)

        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
            return None

    def _search_page(
        self, page_num: int, pattern: re.Pattern[str]
    ) -> list[SearchResult]:
        """Search a single page for matches.

        OPTIMIZED: Only stores text positions, bounds calculated on-demand.

        Args:
            page_num: Page number to search
            pattern: Compiled regex pattern

        Returns:
            List of search results for this page
        """
        results: list[SearchResult] = []

        try:
            # Extract text from page
            start_time = time.time()
            selection = self.document.getAllText(page_num)
            if not selection:
                return results

            text = selection.text()
            if not text:
                return results
            text_time = time.time() - start_time

            # Track unique matches to avoid duplicates
            seen_matches = set()

            # Find all matches - FAST: Just store positions, no bounds calculation
            match_count = 0

            for match in pattern.finditer(text):
                # Check for cancellation frequently during page processing
                if self.cancelled:
                    return results  # Return partial results

                match_count += 1
                # Get match position
                start_pos = match.start()
                end_pos = match.end()
                matched_text = match.group()

                # Create unique key for this match
                match_key = (page_num, start_pos, end_pos)
                if match_key in seen_matches:
                    continue
                seen_matches.add(match_key)

                # OPTIMIZATION: Don't calculate bounds here!
                # Just store the match with None bounds - will be calculated on-demand
                results.append(
                    SearchResult(
                        page_num=page_num,
                        text=matched_text,
                        char_start=start_pos,
                        char_end=end_pos,
                        bounds=None,  # Defer bounds calculation!
                    )
                )

            # Log timing info
            if match_count > 0:
                logger.debug(
                    f"Page {page_num}: Found {match_count} matches in {text_time:.3f}s "
                    f"(text extraction only, no bounds calculation)"
                )

        except Exception as e:
            logger.error(f"Error searching page {page_num}: {e}")

        return results

    def _get_text_selection(
        self, page_num: int, start_char: int, end_char: int, full_text: str
    ) -> Any:  # Returns QPdfSelection
        """Get PDF selection for a character range.

        This method uses QPdfDocument's getSelectionAtIndex for FAST and ACCURATE selection.
        No more grid search nonsense!

        Args:
            page_num: Page number
            start_char: Start character index
            end_char: End character index
            full_text: Full text of the page (not used anymore but kept for compatibility)

        Returns:
            QPdfSelection object or None
        """
        try:
            # SIMPLE AND FAST: Use QPdfDocument's built-in selection by character index!
            # This is what should have been used from the beginning
            selection = self.document.getSelectionAtIndex(
                page_num, start_char, end_char - start_char  # length of selection
            )

            if selection and selection.isValid():
                return selection

            # If getSelectionAtIndex doesn't work (older Qt?), fall back to a simpler approach
            # Get the full page text selection to get bounds
            full_selection = self.document.getAllText(page_num)
            if not full_selection:
                return None

            # For fallback, just return the full selection
            # The bounds might not be perfect but at least it's fast
            # and the search will still work
            return full_selection

        except Exception as e:
            logger.error(f"Error getting text selection: {e}")
            return None


class SearchPresenter(QObject, BasePresenter):
    """Presenter for search operations following MVP pattern."""

    # Signals for UI updates
    search_started = Signal()
    search_completed = Signal()
    results_found = Signal(int)  # Total number of results
    current_result_changed = Signal(int)  # Current result index
    search_error_occurred = Signal(str)  # Error message

    def __init__(
        self,
        model: SearchModel,
        document_presenter: Any,  # DocumentPresenter
        navigation_presenter: Any,  # NavigationPresenter
        main_window: Any = None,  # MainWindow
    ) -> None:
        """Initialize search presenter.

        Args:
            model: Search model
            document_presenter: Document presenter for PDF access
            navigation_presenter: Navigation presenter for page navigation
            main_window: Reference to main window for navigation
        """
        QObject.__init__(self)
        BasePresenter.__init__(self)
        self._model = model
        self._document_presenter = document_presenter
        self._navigation_presenter = navigation_presenter
        self._main_window = main_window
        self._search_thread: Optional[SearchThread] = None
        self._qt_document: Optional[QPdfDocument] = None

        # Track search generation to filter out old results
        self._current_search_id = 0
        self._active_search_id = 0

        # Debounce timer for search-as-you-type
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._execute_debounced_search)
        self._pending_search: Optional[tuple[str, SearchOptions]] = None

        # Connect to model changes
        self._model.add_observer(self._on_model_changed)

    def set_qt_document(self, qt_document: QPdfDocument) -> None:
        """Set the Qt PDF document for search operations.

        Args:
            qt_document: The QPdfDocument instance
        """
        self._qt_document = qt_document

    def search(self, query: str, options: Optional[SearchOptions] = None) -> None:
        """Execute search with cancellation support.

        Args:
            query: Search query
            options: Search options (uses defaults if None)
        """
        # Increment search ID for new search to distinguish from old ones
        self._current_search_id += 1

        # Cancel any existing search
        self.cancel_search()

        # Validate input
        if not query or not self._document_presenter.is_document_loaded():
            self._model.clear_results()
            self.results_found.emit(0)
            return

        if not self._qt_document:
            logger.error("No Qt document available for search")
            return

        # Use default options if none provided
        if options is None:
            options = SearchOptions(
                case_sensitive=self._model.case_sensitive,
                whole_words=self._model.whole_words,
                use_regex=self._model.use_regex,
            )

        # Update model
        self._model.set_search_query(query)
        self._model.reset_search_state()

        # Set active search ID to track which results to accept
        self._active_search_id = self._current_search_id

        # Start async search
        self._start_search_thread(query, options)

    def search_with_debounce(
        self, query: str, options: Optional[SearchOptions] = None, delay_ms: int = 300
    ) -> None:
        """Execute search with debouncing for search-as-you-type.

        Args:
            query: Search query
            options: Search options
            delay_ms: Debounce delay in milliseconds
        """
        # Store pending search
        self._pending_search = (query, options or SearchOptions())

        # Reset timer
        self._debounce_timer.stop()
        self._debounce_timer.start(delay_ms)

    def _execute_debounced_search(self) -> None:
        """Execute the pending debounced search."""
        if self._pending_search:
            query, options = self._pending_search
            self._pending_search = None
            self.search(query, options)

    def cancel_search(self) -> None:
        """Cancel any ongoing search operation."""
        # Cancel debounce timer
        self._debounce_timer.stop()
        self._pending_search = None

        # Cancel search thread
        if self._search_thread and self._search_thread.isRunning():
            self._search_thread.cancel()
            self._search_thread.wait(1000)  # Wait up to 1 second
            if self._search_thread.isRunning():
                self._search_thread.terminate()  # Force terminate if still running

        self._model.cancel_search()

    def navigate_next(self) -> None:
        """Navigate to the next search result."""
        logger.debug(
            f"Navigate next: current index {self._model.current_result_index} of {self._model.total_results_found}"
        )
        result = self._model.navigate_to_next_result()
        if result:
            self._navigate_to_result(result)
            self.current_result_changed.emit(self._model.current_result_index)

    def navigate_previous(self) -> None:
        """Navigate to the previous search result."""
        logger.debug(
            f"Navigate previous: current index {self._model.current_result_index} of {self._model.total_results_found}"
        )
        result = self._model.navigate_to_previous_result()
        if result:
            self._navigate_to_result(result)
            self.current_result_changed.emit(self._model.current_result_index)

    def clear_search(self) -> None:
        """Clear all search results and state."""
        self.cancel_search()
        self._model.clear_results()
        self._model.clear_cache()
        self.results_found.emit(0)

    def get_results_for_page(self, page_num: int) -> list[SearchResult]:
        """Get all search results for a specific page.

        OPTIMIZED: Only calculates bounds for the current result, not all results.

        Args:
            page_num: Page number

        Returns:
            List of search results for the page
        """
        # Get results for this page
        page_results = [r for r in self._model.results if r.page_num == page_num]

        # PERFORMANCE FIX: Only calculate bounds for the CURRENT result
        # All other results will have bounds calculated on-demand when needed
        current_result = self._model.get_current_result()

        if current_result and current_result.page_num == page_num:
            # Only calculate bounds for the current result on this page
            self._calculate_bounds_for_result(current_result)

        return page_results

    def get_current_result(self) -> Optional[SearchResult]:
        """Get the current search result.

        Returns:
            Current SearchResult or None
        """
        return self._model.get_current_result()

    def _start_search_thread(self, query: str, options: SearchOptions) -> None:
        """Start background search thread.

        Args:
            query: Search query
            options: Search options
        """
        if not self._qt_document:
            return

        # Get visible pages
        visible_pages = self._get_visible_pages()
        total_pages = self._document_presenter.get_page_count()

        # Create and configure thread with search ID
        self._search_thread = SearchThread(
            self._qt_document,
            query,
            options,
            visible_pages,
            total_pages,
            self._active_search_id,
        )

        # Connect signals
        self._search_thread.results_ready.connect(self._on_results_ready)
        self._search_thread.search_complete.connect(self._on_search_complete)
        self._search_thread.search_error.connect(self._on_search_error)
        self._search_thread.progress_update.connect(self._on_progress_update)

        # Start search
        self.search_started.emit()
        self._search_thread.start()

    def _get_visible_pages(self) -> list[int]:
        """Get currently visible page numbers.

        Returns:
            List of visible page numbers
        """
        if not self._navigation_presenter:
            return []

        current_page = self._navigation_presenter.get_current_page()
        view_mode = self._navigation_presenter.model.view_mode

        # In side-by-side mode, two pages are visible
        if view_mode == "side_by_side":
            # Even page on left, odd page on right
            if current_page % 2 == 0:
                return [
                    current_page,
                    min(
                        current_page + 1, self._document_presenter.get_page_count() - 1
                    ),
                ]
            else:
                return [max(0, current_page - 1), current_page]
        else:
            return [current_page]

    def _on_results_ready(
        self, results: list[SearchResult], search_id: int = 0
    ) -> None:
        """Handle results from search thread.

        Args:
            results: List of new search results
            search_id: ID of the search that produced these results
        """
        # CRITICAL FIX: Ignore results from old searches
        if search_id != self._active_search_id:
            # Results from a cancelled search - ignore them
            return

        # Handle empty results to clear old search
        if len(results) == 0:
            self._model.clear_results()
            self.results_found.emit(0)
            return

        logger.debug(f"Received {len(results)} new search results")
        self._model.add_results(results)
        self.results_found.emit(self._model.total_results_found)

        # Auto-navigate to first result
        if self._model.current_result_index == -1 and self._model.results:
            self._model.set_current_result(0)
            result = self._model.get_current_result()
            if result:
                # Calculate bounds for first result only
                self._calculate_bounds_for_result(result)
                logger.debug(
                    f"Auto-navigating to first result on page {result.page_num}"
                )
                self._navigate_to_result(result)
                self.current_result_changed.emit(0)

    def _on_search_complete(self, search_id: int = 0) -> None:
        """Handle search completion.

        Args:
            search_id: ID of the completed search
        """
        # Ignore completion from old searches
        if search_id != self._active_search_id:
            return

        self._model.set_searching(False)
        self.search_completed.emit()

        # Show message if no results
        if self._model.total_results_found == 0:
            logger.info("No results found for search query")

    def _on_search_error(self, error_msg: str, search_id: int = 0) -> None:
        """Handle search error.

        Args:
            error_msg: Error message
            search_id: ID of the search that errored
        """
        # Ignore errors from old searches
        if search_id != self._active_search_id:
            return

        logger.error(f"Search error: {error_msg}")
        self._model.set_searching(False)
        self.search_error_occurred.emit(error_msg)

    def _on_progress_update(self, current_page: int, total_pages: int) -> None:
        """Handle search progress update.

        Args:
            current_page: Current page being searched
            total_pages: Total number of pages
        """
        # Could emit progress signal here if needed for UI
        pass

    def _calculate_bounds_for_result(self, result: SearchResult) -> None:
        """Calculate bounds for a search result on-demand.

        Args:
            result: Search result to calculate bounds for
        """
        if result.bounds is not None:
            return  # Already calculated

        if not self._qt_document:
            return

        try:
            # Get the selection for this specific match
            selection = self._qt_document.getSelectionAtIndex(
                result.page_num, result.char_start, result.char_end - result.char_start
            )

            if selection and selection.isValid():
                result.bounds = selection.boundingRectangle()
                logger.debug(
                    f"Calculated bounds for result at page {result.page_num}, "
                    f"chars {result.char_start}-{result.char_end}"
                )
        except Exception as e:
            logger.error(f"Error calculating bounds for result: {e}")

    def _navigate_to_result(self, result: SearchResult) -> None:
        """Navigate to a search result and ensure it's visible.

        Args:
            result: Search result to navigate to
        """
        # Calculate bounds on-demand when navigating
        self._calculate_bounds_for_result(result)

        logger.debug(f"Navigating to search result on page {result.page_num}")

        if self._navigation_presenter and self._main_window:
            # Navigate to the page containing the result
            # go_to_page expects 0-based index
            current_page = self._navigation_presenter.get_current_page()

            # Only navigate if we're not already on the right page
            if current_page != result.page_num:
                logger.debug(
                    f"Changing from page {current_page} to page {result.page_num}"
                )

                # Use the main window's navigation controller to properly change pages
                # This ensures the page is actually rendered, not just the model updated
                if hasattr(self._main_window, "navigation_controller"):
                    # Convert to 1-based page number for navigate_to_page
                    self._main_window.navigation_controller.navigate_to_page(
                        result.page_num + 1
                    )
                else:
                    # Fallback: use presenter directly and force render
                    success = self._navigation_presenter.go_to_page(result.page_num)
                    if success and hasattr(self._main_window, "render_current_page"):
                        self._main_window.render_current_page()
            else:
                logger.debug(f"Already on page {result.page_num}")

            # Emit signal to scroll to the result bounds
            # This will be handled by the view to ensure the result is visible
            from PySide6.QtCore import QTimer

            # Use a small delay to ensure page is rendered before scrolling
            def scroll_to_result() -> None:
                # Find the graphics view and scroll to show the result
                if hasattr(self._main_window, "graphics_view"):
                    graphics_view = self._main_window.graphics_view
                    if graphics_view and graphics_view.scene():
                        # Find the page item
                        for item in graphics_view.scene().items():
                            if (
                                hasattr(item, "page_number")
                                and item.page_number == result.page_num
                            ):
                                # Ensure the result bounds are visible
                                # Map the bounds to scene coordinates
                                scene_rect = item.mapRectToScene(result.bounds)
                                graphics_view.ensureVisible(scene_rect, 50, 50)
                                break

            # Schedule the scroll after a brief delay to allow rendering
            QTimer.singleShot(
                200, scroll_to_result
            )  # Increased delay to ensure rendering completes

    def _on_model_changed(self, event: Any) -> None:
        """Handle model property changes.

        Args:
            event: Property changed event
        """
        # Update view if needed
        if self.has_view:
            self.update_view(**{event.property_name: event.new_value})

    def handle_search_error(self, error_type: SearchError) -> None:
        """Centralized error handling.

        Args:
            error_type: Type of search error
        """
        error_messages = {
            SearchError.ENCRYPTED_PDF: "Cannot search in encrypted PDF",
            SearchError.NO_TEXT_LAYER: "This PDF appears to be scanned. No searchable text found.",
            SearchError.MEMORY_EXHAUSTED: f"Too many results (>{self._model.MAX_RESULTS_IN_MEMORY}). Showing first {self._model.MAX_RESULTS_IN_MEMORY}.",
            SearchError.INVALID_REGEX: "Invalid search pattern",
            SearchError.UNICODE_ERROR: "Text encoding error. Trying alternative search method.",
        }

        message = error_messages.get(error_type, "Unknown search error")
        logger.error(f"Search error: {message}")
        self.search_error_occurred.emit(message)

    def cleanup(self) -> None:
        """Clean up resources."""
        self.cancel_search()
        self._model.remove_observer(self._on_model_changed)
        super().cleanup()

    @property
    def model(self) -> SearchModel:
        """Access the search model."""
        return self._model
