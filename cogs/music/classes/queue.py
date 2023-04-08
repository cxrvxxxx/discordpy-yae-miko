from typing import List, Union
from .song import Song

class Queue(object):
    def __init__(self) -> None:
        self.items: List[Song] = []

    def enqueue(self, song: Song) -> None:
        self.items.append(song)

    def dequeue(self, index: int=0) -> Union[Song, None]:
        if self.is_empty(): return
        return self.items.pop(index)

    def is_empty(self) -> bool:
        return True if self.size() == 0 else False

    def size(self) -> int:
        return len(self.items)
