from typing import Union

from .song import Song

class Queue(object):
    def __init__(self) -> None:
        self.items = []

    def enqueue(self, item: Song) -> None:
        self.items.append(item)

    def dequeue(self, index: int=0) -> Union[Song, None]:
        return self.items.pop(index)

    def is_empty(self) -> bool:
        return False if self.size() > 0 else True

    def size(self) -> int:
        return len(self.items)
