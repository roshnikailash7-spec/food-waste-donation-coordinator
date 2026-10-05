"""
Singly Linked List Implementation from Scratch
==============================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, completed food distributions and
audit events must be logged into a chronological history trail.

- Donation history logs are predominantly write-heavy: every time food is matched or
  picked up, an audit entry is prepended to the head of the log so that the most recent
  activity appears first.
- In a traditional array / dynamic list, prepending an item to index 0 requires shifting
  all N existing elements to the right (O(N) time).
- A Singly Linked List allows O(1) instantaneous prepend operations by simply updating the
  head pointer.
- Dynamic memory allocation ensures nodes are instantiated only when donations occur, with
  zero pre-allocated empty slots or memory reallocation overhead.

Data Structure Details:
-----------------------
- Built from scratch using `LinkedListNode` pointers (data and next).
- Maintains both `head` and `tail` references plus a running count for O(1) size queries.
- Provides conversion to/from standard Python lists for JSON persistence.
"""

class LinkedListNode:
    """A single node containing data payload and a pointer to the next node."""
    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node

    def __repr__(self):
        return f"Node({self.data})"


class SinglyLinkedList:
    """
    Singly Linked List with head and tail pointers.
    Optimized for O(1) prepend operations (audit logs).
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def prepend(self, data):
        """
        Insert new element at the very front (head) of the list.
        Time Complexity: O(1)
        """
        new_node = LinkedListNode(data, next_node=self.head)
        self.head = new_node
        if self.tail is None:
            self.tail = new_node
        self.count += 1

    def append(self, data):
        """
        Insert new element at the end (tail) of the list.
        Time Complexity: O(1)
        """
        new_node = LinkedListNode(data, next_node=None)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.count += 1

    def pop_front(self):
        """
        Remove and return the data at the front of the list.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        data = self.head.data
        self.head = self.head.next
        self.count -= 1
        if self.head is None:
            self.tail = None
        return data

    def peek_front(self):
        """Return the data of the first node without removing it. Time Complexity: O(1)"""
        if self.is_empty():
            return None
        return self.head.data

    def is_empty(self):
        """Check if list has no nodes. Time Complexity: O(1)"""
        return self.head is None

    def size(self):
        """Return total number of nodes in list. Time Complexity: O(1)"""
        return self.count

    def clear(self):
        """Reset the linked list."""
        self.head = None
        self.tail = None
        self.count = 0

    def to_list(self):
        """
        Traverse the list and return all items in head-to-tail order.
        Time Complexity: O(N)
        """
        items = []
        curr = self.head
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def from_list(self, items):
        """
        Populate the linked list from an iterable, preserving original sequence.
        Time Complexity: O(N)
        """
        self.clear()
        for item in items:
            self.append(item)


if __name__ == "__main__":
    ll = SinglyLinkedList()
    ll.prepend({"id": "H1", "event": "First Donation"})
    ll.prepend({"id": "H2", "event": "Second Donation"})
    ll.append({"id": "H0", "event": "Oldest Archive"})

    items = ll.to_list()
    assert items[0]["id"] == "H2", "Most recent should be H2"
    assert items[1]["id"] == "H1", "Second should be H1"
    assert items[2]["id"] == "H0", "Last should be H0"
    assert ll.size() == 3

    popped = ll.pop_front()
    assert popped["id"] == "H2"
    assert ll.size() == 2
    print("SinglyLinkedList self-test passed successfully!")
