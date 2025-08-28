import logging
import math
from typing import List, Optional, Union

from fastapi import Request
from sqlalchemy.orm import Query

from fastpluggy.core.widgets.mixins import RequestParamsMixin


class Pagination(RequestParamsMixin):
    def __init__(
        self,
        request: Optional[Request],
        query: Query,
        default_rows_per_page: int = 10,
        window: int = 3,
        rows_per_page_options: Optional[List[int]] = None
    ):
        self.error = None
        self.request = request
        self.query = query
        self.window = window
        self.rows_per_page_options = rows_per_page_options or [10, 25, 50, 100]
        self.total_items = None
        self.total_pages = None

        # Initialize pagination parameters
        self.current_page = self.get_query_param("current_page", 1, int)
        self.rows_per_page = self.get_query_param(
            "rows_per_page", default_rows_per_page, int
        )
        self.offset = max(0, (self.current_page - 1) * self.rows_per_page)

        # Calculate total items and pages based on the filtered query
        try:
            self.total_items = self.query.count()
            self.total_pages = math.ceil(self.total_items / self.rows_per_page) if self.rows_per_page else 1
        except Exception as e:
            logging.exception(f"Error calculating pagination: {e}")
            self.error = str(e)

        # Initialize pagination info attributes
        self.pages: List[Union[int, str]] = []

        # Calculate pagination structure
        self.calculate_pagination()


    def add_dots_for_pagination(self, pages: List[int]) -> List[Union[int, str]]:
        """
        Add ellipses (...) to the pagination range if there are skipped pages.
        """
        result = []
        for i in range(len(pages)):
            result.append(pages[i])
            # Add "..." if there is a gap in the sequence
            if i < len(pages) - 1 and pages[i] + 1 < pages[i + 1]:
                result.append("...")
        return result

    def calculate_pagination(self) -> None:
        """
        Calculate the range of page numbers to display and where to place ellipses.
        The results are stored directly in instance attributes.
        """
        if self.total_items :
            try:
                # Always show first two and last two pages
                first_pages = []
                if self.total_pages >= 1 :
                    first_pages.append(1)
                if self.total_pages >= 2:
                    first_pages.append(2)
    
                last_pages = [self.total_pages - 1, self.total_pages] if self.total_pages >= 2 else [self.total_pages]
    
                # Calculate sliding window
                sliding_start = max(self.current_page - self.window, 1)
                sliding_end = min(self.total_pages , self.current_page+ self.window)
    
                sliding_pages = list(range(sliding_start, sliding_end + 1))
    
                # Combine all pages
                combined_pages = first_pages + sliding_pages + last_pages
    
                # Remove duplicates and sort
                self.pages = self.add_dots_for_pagination(
                    sorted(set(combined_pages))
                )
            except Exception as e:
                logging.exception(f"Error calculating pagination: {e}")
                self.error = str(e)

    def process(self):
        """
        Recalculate pagination structure if needed.
        """
        self.calculate_pagination()
