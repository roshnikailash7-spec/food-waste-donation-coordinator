"""
Min-Heap (Priority Queue) Implementation from Scratch
=====================================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, surplus food is strictly time-sensitive.
Food items expire at different rates (from 2 hours for cooked buffet meals to several days for
canned produce). 

The system must constantly prioritize the batch closest to expiration for immediate matching
and dispatch. 

- A Min-Heap acts as an optimal Priority Queue where the node with the smallest expiry time
  always sits at the root (index 0).
- Peek (inspecting the most urgent food): O(1) time complexity.
- Insertion (a donor lists a new surplus item): O(log N) time complexity.
- Extraction (dispatching the most critical item): O(log N) time complexity.
- In contrast, an unsorted list would require O(N) linear scan to locate the minimum, and keeping
  a list sorted naively requires O(N) shift per insertion. Min-Heap is mathematically optimal.

Data Structure Details:
-----------------------
- Implemented as a 0-indexed binary heap inside a dynamic Python list without using heapq.
- Parent index: (i - 1) // 2
- Left child index: 2 * i + 1
- Right child index: 2 * i + 2
- Heap invariants are preserved via sift-up and sift-down operations.
"""

class MinHeapNode:
    """Represents a node in the min-heap containing priority and payload data."""
    def __init__(self, priority, data):
        self.priority = priority  # e.g., expiry_hours (float/int)
        self.data = data          # e.g., food dictionary

    def __repr__(self):
        return f"MinHeapNode(priority={self.priority}, data={self.data})"


class MinHeap:
    """
    Min-Heap Priority Queue.
    Stores MinHeapNode items ordered by ascending priority (smallest priority value at top).
    """

    def __init__(self):
        self.heap = []

    def _parent(self, i):
        return (i - 1) // 2

    def _left_child(self, i):
        return 2 * i + 1

    def _right_child(self, i):
        return 2 * i + 2

    def _has_parent(self, i):
        return self._parent(i) >= 0

    def _has_left_child(self, i):
        return self._left_child(i) < len(self.heap)

    def _has_right_child(self, i):
        return self._right_child(i) < len(self.heap)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _sift_up(self, index):
        """
        Restores min-heap property by bubbling the node at index up towards the root.
        Time Complexity: O(log N)
        """
        current = index
        while self._has_parent(current):
            p = self._parent(current)
            if self.heap[current].priority < self.heap[p].priority:
                self._swap(current, p)
                current = p
            else:
                break

    def _sift_down(self, index):
        """
        Restores min-heap property by bubbling the node at index down towards the leaves.
        Time Complexity: O(log N)
        """
        current = index
        while self._has_left_child(current):
            smallest_child = self._left_child(current)
            r = self._right_child(current)
            if self._has_right_child(current) and self.heap[r].priority < self.heap[smallest_child].priority:
                smallest_child = r

            if self.heap[current].priority > self.heap[smallest_child].priority:
                self._swap(current, smallest_child)
                current = smallest_child
            else:
                break

    def push(self, priority, data):
        """
        Insert an item with an associated numeric priority.
        Time Complexity: O(log N)
        """
        node = MinHeapNode(priority, data)
        self.heap.append(node)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        """
        Extract and return the item with the minimum priority value.
        Time Complexity: O(log N)
        """
        if self.is_empty():
            return None
        if len(self.heap) == 1:
            node = self.heap.pop()
            return node.data

        root = self.heap[0]
        # Move the last element to root and sift down
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root.data

    def peek(self):
        """
        Return the item with the minimum priority without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.heap[0].data

    def peek_priority(self):
        """Return the minimum priority value without removing it."""
        if self.is_empty():
            return None
        return self.heap[0].priority

    def is_empty(self):
        """Check if heap has 0 elements. Time Complexity: O(1)"""
        return len(self.heap) == 0

    def size(self):
        """Return the number of elements in the heap. Time Complexity: O(1)"""
        return len(self.heap)

    def to_list(self):
        """
        Return raw list of payloads currently in the heap.
        Note: The heap order is a partial order, not fully sorted.
        Time Complexity: O(N)
        """
        return [node.data for node in self.heap]

    def get_sorted_list(self):
        """
        Non-destructive extraction to return all elements sorted by priority.
        Clones the internal heap array and repeatedly pops minimums.
        Time Complexity: O(N log N)
        """
        # Save current heap
        saved = list(self.heap)
        sorted_items = []
        while not self.is_empty():
            sorted_items.append(self.pop())
        # Restore heap
        self.heap = saved
        return sorted_items

    def remove_by_id(self, item_id, id_key="id"):
        """
        Remove a specific item by its dictionary key (e.g. food['id'] == item_id).
        Time Complexity: O(N) to locate + O(log N) to restore heap invariant.
        """
        target_idx = -1
        for i, node in enumerate(self.heap):
            if isinstance(node.data, dict) and node.data.get(id_key) == item_id:
                target_idx = i
                break

        if target_idx == -1:
            return False

        if target_idx == len(self.heap) - 1:
            self.heap.pop()
            return True

        # Move the last element to the target index
        self.heap[target_idx] = self.heap.pop()
        # The replacement node might need to go up or down
        p = self._parent(target_idx)
        if target_idx > 0 and self.heap[target_idx].priority < self.heap[p].priority:
            self._sift_up(target_idx)
        else:
            self._sift_down(target_idx)
        return True


if __name__ == "__main__":
    # Self-test
    pq = MinHeap()
    pq.push(10, {"id": "F1", "name": "Bread", "exp": 10})
    pq.push(2, {"id": "F2", "name": "Milk", "exp": 2})
    pq.push(5, {"id": "F3", "name": "Salad", "exp": 5})
    assert pq.peek()["name"] == "Milk", "Peek should be Milk"
    assert pq.pop()["name"] == "Milk", "Pop should extract Milk"
    assert pq.pop()["name"] == "Salad", "Next should be Salad"
    assert pq.pop()["name"] == "Bread", "Last should be Bread"
    assert pq.is_empty(), "Heap should be empty"
    print("MinHeap self-test passed successfully!")
