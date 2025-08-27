import time
from typing import Optional, override
from ..modeling.model_context import ModelContext


class LivingContext:
    def __init__(self, context):
        if not context.id:
            raise ValueError('ModelContext must have an id')
        self.context = context
        self.birth = int(time.time())


class ModelContextPool:
    def __init__(
        self,
        max_length: int = 3,
        max_age: int = 300,  # seconds
    ):
        self.max_length = max_length
        self.max_age = max_age
        self.items: list[LivingContext] = []

    def __getitem__(self, index):
        return self.items[index]

    def __setitem__(self, index):
        raise NotImplementedError('cannot set in ModelContextPool directly, use append() or insert()')

    def __delitem__(self, index):
        del self.items[index]

    def __len__(self):
        return len(self.items)

    def insert(self, index, value):
        if isinstance(value, ModelContext):
            value = LivingContext(value)
        self.items.insert(index, value)
        self._check_expires()

    def append(self, value):
        if isinstance(value, ModelContext):
            value = LivingContext(value)
        self.items.append(value)
        self._check_expires()

    def _check_expires(self):
        new_items = []
        now = int(time.time())
        for i in range(len(self.items)):
            item = self.items[i]
            if now - item.birth > self.max_age:
                continue
            new_items.append(item)
        if len(new_items) > self.max_length:
            new_items = new_items[-self.max_length :]
        if len(new_items) != len(self.items):
            self.items = new_items

    def find_context(self, id: str) -> Optional[ModelContext]:
        self._check_expires()
        for item in self.items:
            if item.context.id == id:
                return item.context

    def __iter__(self):
        return iter(self.items)

    @override
    def __repr__(self):
        return f'<{self.__class__.__name__}: {len(self)} contexts>'
