"""
LIFO Stack Implementation from Scratch
======================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, operators handle rapid live updates:
listing surplus batches, executing auto-matches, and dispatching transport requests.
Mistakes like entering the wrong batch size, matching the wrong NGO, or premature completion
can happen.

- An Undo mechanism requires reversing events in the EXACT reverse chronological order of
  their execution.
- A Stack operates strictly on a Last-In, First-Out (LIFO) protocol.
- Every state-altering action pushes an inverse command / snapshot onto the stack in O(1).
- Clicking 'Undo' pops the top action from the stack in O(1) and executes its rollback handler.
- If multiple consecutive undos are performed, the system unwinds state step-by-step cleanly.

Data Structure Details:
-----------------------
- Implemented from scratch using linked `StackNode` elements.
- Does NOT use collections.deque or built-in stack libraries.
- Top pointer enables O(1) push, pop, and peek.
"""

class StackNode:
    """Node representing an action element in the LIFO stack."""
    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node

    def __repr__(self):
        return f"StackNode({self.data})"


class Stack:
    """
    Last-In First-Out (LIFO) Stack implemented using linked nodes.
    Maintains O(1) push and pop operations.
    """

    def __init__(self):
        self.top = None
        self.count = 0

    def push(self, action):
        """
        Push an action onto the top of the stack.
        Time Complexity: O(1)
        """
        new_node = StackNode(action, next_node=self.top)
        self.top = new_node
        self.count += 1

    def pop(self):
        """
        Remove and return the action at the top of the stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        action = self.top.data
        self.top = self.top.next
        self.count -= 1
        return action

    def peek(self):
        """
        Return the top action without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.top.data

    def is_empty(self):
        """Check if stack is empty. Time Complexity: O(1)"""
        return self.top is None

    def size(self):
        """Return the number of actions in the stack. Time Complexity: O(1)"""
        return self.count

    def clear(self):
        """Clear all actions in the stack."""
        self.top = None
        self.count = 0

    def to_list(self):
        """
        Return actions in top-to-bottom order (most recent first).
        Time Complexity: O(N)
        """
        result = []
        curr = self.top
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result

    def from_list(self, items):
        """
        Reconstruct stack from a list where index 0 was top.
        Reverses the list so first item becomes top.
        """
        self.clear()
        # To restore top-to-bottom order, push in reverse
        for item in reversed(items):
            self.push(item)


if __name__ == "__main__":
    stk = Stack()
    stk.push({"action": "ADD_FOOD", "id": "F1"})
    stk.push({"action": "AUTO_MATCH", "id": "PK1"})

    assert stk.size() == 2
    assert stk.peek()["action"] == "AUTO_MATCH"

    popped = stk.pop()
    assert popped["action"] == "AUTO_MATCH"
    assert stk.size() == 1
    assert stk.peek()["action"] == "ADD_FOOD"

    popped2 = stk.pop()
    assert popped2["action"] == "ADD_FOOD"
    assert stk.is_empty()
    print("Stack self-test passed successfully!")
