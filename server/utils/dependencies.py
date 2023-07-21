from typing import Optional


class Paginator:
    def __init__(self, page: int = 1, size: int = 10, category: Optional[str] = None):
        self.page = page
        self.size = size
        self.category = category

    def dict(self):
        return {
            "page": self.page,
            "size": self.size,
            "category": self.category
        }
