"""
FIFO Queue Implementation from Scratch
======================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, when food is matched to an NGO, a
pickup dispatch task is generated and placed into a pending processing pipeline.

- Pickup logistics must operate on a strict First-In, First-Out (FIFO) discipline. The earliest
  matched requests must be processed and assigned to drivers/volunteers first to prevent food
  from sitting waiting for transport.
- Using a standard Python list as a queue leads to performance bottlenecks: `list.pop(0)` takes
  O(N) time because every subsequent element in memory must be shifted left by one slot.
- This custom Queue is built using linked nodes with dedicated `front` and `rear` pointers.
- Enqueue (scheduling a new pickup): O(1) time complexity.
- Dequeue (completing the next pickup in line): O(1) time complexity.
- Peek (viewing next pending driver mission): O(1) time complexity.

Data Structure Details:
-----------------------
- Implemented from scratch using `QueueNode` objects.
- Does NOT use collections.deque or built-in queue libraries.
- Supports serialization to list and queue restoration.
"""

class QueueNode:
    """Node representing an element in the FIFO queue."""
    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node

    def __repr__(self):
        return f"QueueNode({self.data})"


class Queue:
    """
    First-In First-Out (FIFO) Queue implemented via linked nodes.
    Maintains O(1) enqueue and dequeue operations.
    """

    def __init__(self):
        self.front = None
        self.rear = None
        self.count = 0

    def enqueue(self, item):
        """
        Add an item to the rear of the queue.
        Time Complexity: O(1)
        """
        new_node = QueueNode(item)
        if self.is_empty():
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.count += 1

    def dequeue(self):
        """
        Remove and return the item from the front of the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        data = self.front.data
        self.front = self.front.next
        self.count -= 1
        if self.front is None:
            self.rear = None
        return data

    def peek(self):
        """
        Return the item at the front without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.front.data

    def is_empty(self):
        """Check if queue is empty. Time Complexity: O(1)"""
        return self.front is None

    def size(self):
        """Return the number of items in the queue. Time Complexity: O(1)"""
        return self.count

    def clear(self):
        """Empty the queue. Time Complexity: O(1)"""
        self.front = None
        self.rear = None
        self.count = 0

    def to_list(self):
        """
        Convert queue to a Python list in FIFO order (front to rear).
        Time Complexity: O(N)
        """
        result = []
        curr = self.front
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result

    def from_list(self, items):
        """Populate the queue from an iterable in order."""
        self.clear()
        for item in items:
            self.enqueue(item)

    def remove_by_id(self, item_id, id_key="id"):
        """
        Remove an item anywhere in the queue matching item[id_key] == item_id.
        Useful if a pending pickup is cancelled or rolled back by undo.
        Time Complexity: O(N)
        """
        if self.is_empty():
            return False

        curr = self.front
        prev = None
        while curr:
            data = curr.data
            if isinstance(data, dict) and data.get(id_key) == item_id:
                if prev is None:
                    # Removing front
                    self.front = curr.next
                    if self.front is None:
                        self.rear = None
                else:
                    prev.next = curr.next
                    if curr == self.rear:
                        self.rear = prev
                self.count -= 1
                return True
            prev = curr
            curr = curr.next
        return False


if __name__ == "__main__":
    q = Queue()
    q.enqueue({"id": "PK1", "desc": "Pickup 1"})
    q.enqueue({"id": "PK2", "desc": "Pickup 2"})
    q.enqueue({"id": "PK3", "desc": "Pickup 3"})

    assert q.peek()["id"] == "PK1"
    assert q.size() == 3

    popped = q.dequeue()
    assert popped["id"] == "PK1"
    assert q.peek()["id"] == "PK2"
    assert q.size() == 2

    # Remove by id
    assert q.remove_by_id("PK3")
    assert q.size() == 1
    assert q.dequeue()["id"] == "PK2"
    assert q.is_empty()
    print("Queue self-test passed successfully!")
