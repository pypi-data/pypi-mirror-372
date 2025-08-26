class PagedQueryResult:
    """
    defines results of a paged query.
    :ivar str direction: 'asc' or 'desc' direction.
    :ivar int page: page number return on current result.
    :ivar list results: list of results records return by the query.
    :ivar int size: number of records per page.
    :ivar str sort: column name used in sorting.
    :ivar int total: total number of results on all pages.
    """

    def __init__(self,
                 total: int = None,
                 page: int = None,
                 size: int = None,
                 sort: str = None,
                 direction: str = None):
        self.total = total
        self.page = page
        if page < 0:
            raise ValueError("page must be a positive number")
        self.size = size
        if size < 0 or size > 100:
            raise ValueError("size is limited to 100")
        self.sort = sort
        if sort is None:
            raise ValueError("sort is mandatory")
        self.direction = direction
        if direction != 'asc' and direction != 'desc':
            raise ValueError("direction must be asc or desc")
        self.results = None
