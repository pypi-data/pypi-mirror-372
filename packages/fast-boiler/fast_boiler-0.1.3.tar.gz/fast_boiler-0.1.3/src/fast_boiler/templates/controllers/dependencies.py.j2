from typing import Annotated
from fastapi import Query

def parse_query_params(
    # 👇 CORRECTED: Default value is ONLY set with '='
    page: Annotated[int, Query(description="Page number, starting from 1.")] = 1,
    # 👇 CORRECTED: Default value is ONLY set with '='
    size: Annotated[int, Query(description="Number of items per page.")] = 50,
    
    # These were already correct, but are included for completeness
    sort_by: Annotated[str | None, Query(description="Field to sort by (e.g., 'id').")] = None,
    sort_order: Annotated[str | None, Query(description="Sort order: 'asc' or 'desc'.")] = "asc",
    filters: Annotated[list[str] | None, Query(
        description="Filter criteria in 'field:operator:value' format. Supported operators: eq, neq, gt, lt, gte, lte, like, in."
    )] = None,
    search: Annotated[str | None, Query(description="Full-text search query.")] = None
) -> dict:
    """
    Parses common query parameters for filtering, sorting, and pagination.
    This is used as a dependency in API endpoints.
    """
    return {
        "page": page,
        "size": size,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "filters": filters or [],
        "search": search,
    }