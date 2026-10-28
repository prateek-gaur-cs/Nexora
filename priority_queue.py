
import heapq
from itertools import count


class PriorityQueue:
    """
    Smaller priority numbers are processed first.
    Example: priority 1 = urgent, priority 5 = low priority.
    """

    def __init__(self):
        self._heap = []
        self._counter = count()

    def enqueue(self, order_id, priority, description=""):
        item = (
            int(priority),
            next(self._counter),
            str(order_id),
            str(description)
        )
        heapq.heappush(self._heap, item)

    def dequeue(self):
        if not self._heap:
            return None

        priority, _, order_id, description = heapq.heappop(self._heap)
        return {
            "order_id": order_id,
            "priority": priority,
            "description": description
        }

    def peek(self):
        if not self._heap:
            return None

        priority, _, order_id, description = self._heap[0]
        return {
            "order_id": order_id,
            "priority": priority,
            "description": description
        }

    def get_all(self):
        return [
            {
                "order_id": item[2],
                "priority": item[0],
                "description": item[3]
            }
            for item in sorted(self._heap)
        ]

    def is_empty(self):
        return len(self._heap) == 0

    def __len__(self):
        return len(self._heap)
