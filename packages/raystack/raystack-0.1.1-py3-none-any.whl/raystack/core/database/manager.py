import asyncio
from raystack.core.database.query import QuerySet, should_use_async

class Manager:
    def __init__(self, model_class):
        self.model_class = model_class

    def filter(self, **kwargs):
        return QuerySet(self.model_class).filter(**kwargs)

    def all(self):
        return QuerySet(self.model_class).all()

    def create(self, **kwargs):
        # create usually creates object immediately, so we implement sync+async
        if should_use_async():
            return QuerySet(self.model_class)._create_async(**kwargs)
        else:
            return QuerySet(self.model_class)._create_sync(**kwargs)

    def get(self, **kwargs):
        # get = filter + first
        qs = QuerySet(self.model_class).filter(**kwargs)
        return qs.first()

    def count(self):
        return QuerySet(self.model_class).count()

    def exists(self):
        return QuerySet(self.model_class).exists()

    def delete(self, **kwargs):
        qs = QuerySet(self.model_class).filter(**kwargs)
        return qs.delete()

            # Support for lazy loading and iteration
    def iter(self):
        """Returns an iterable object with query results (lazy loading)."""
        return QuerySet(self.model_class).iter()

    def get_item(self, key):
        """Gets element by index or slice (lazy loading)."""
        return QuerySet(self.model_class).get_item(key)

    def __iter__(self):
        """Support for direct iteration over Manager (lazy loading)."""
        return self.iter()

    def __getitem__(self, key):
        """Support for Manager indexing (lazy loading)."""
        return self.get_item(key)

    def __aiter__(self):
        """Support for asynchronous iteration over Manager (lazy loading)."""
        return QuerySet(self.model_class).__aiter__()
