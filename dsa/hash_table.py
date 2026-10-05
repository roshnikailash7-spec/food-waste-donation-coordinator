"""
Hash Table with Separate Chaining Implementation from Scratch
=============================================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, core system entities (Donors, NGOs,
and Food Items) are referenced constantly by their unique identifiers (e.g. 'DONOR_01',
'NGO_03', 'FOOD_08').

- When a donor posts food, the server must verify the donor ID in O(1) time.
- When an auto-match matches food to an NGO, it needs instant O(1) access to that NGO's
  location coordinates, operating capacity, and contact info.
- If we stored entities in a list or array, every lookup would require an O(N) scan.
- With thousands of transactions, O(N) scans degrade response times severely.
- A Hash Table provides expected O(1) time complexity for lookup, insertion, and deletion.
- Separate chaining ensures that even when hash collisions occur, entries are stored in a
  linked chain within the corresponding bucket, maintaining reliability without infinite loops.

Data Structure Details:
-----------------------
- Implemented from scratch using fixed bucket arrays and singly-linked `HashEntry` nodes.
- Custom DJB2 hashing function converts string/numeric keys to deterministic 32-bit integers.
- Dynamic resizing: Doubles table capacity when load factor exceeds 0.75 to maintain O(1) efficiency.
"""

class HashEntry:
    """Represents a key-value node in a hash table bucket's collision chain."""
    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next = next_node

    def __repr__(self):
        return f"HashEntry({self.key}: {self.value})"


class HashTable:
    """
    Hash Table with Separate Chaining for collision resolution.
    Supports dynamic resizing when load factor exceeds 0.75.
    """

    def __init__(self, initial_capacity=16):
        self.capacity = initial_capacity
        self.count = 0
        self.buckets = [None] * self.capacity

    def _hash(self, key):
        """
        Custom DJB2 hash algorithm.
        Produces deterministic distribution across buckets.
        Time Complexity: O(K) where K is length of key.
        """
        key_str = str(key)
        hash_val = 5381
        for char in key_str:
            # hash * 33 + c
            hash_val = (((hash_val << 5) + hash_val) + ord(char)) & 0xFFFFFFFF
        return hash_val % self.capacity

    def _resize(self):
        """
        Doubles the bucket array capacity and rehashes all existing key-value pairs.
        Time Complexity: O(N) amortized.
        """
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        self.count = 0

        for head in old_buckets:
            curr = head
            while curr:
                self.put(curr.key, curr.value)
                curr = curr.next

    def put(self, key, value):
        """
        Insert or update a key-value pair.
        Time Complexity: O(1) average, O(N) worst case with massive collisions.
        """
        if (self.count / self.capacity) >= 0.75:
            self._resize()

        index = self._hash(key)
        head = self.buckets[index]

        # Check if key already exists in chain -> update value
        curr = head
        while curr:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next

        # Insert new entry at the head of the chain (O(1))
        new_entry = HashEntry(key, value, next_node=head)
        self.buckets[index] = new_entry
        self.count += 1

    def get(self, key, default=None):
        """
        Retrieve value associated with key, or default if key is not found.
        Time Complexity: O(1) average.
        """
        index = self._hash(key)
        curr = self.buckets[index]
        while curr:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return default

    def contains(self, key):
        """Check if key exists in hash table. Time Complexity: O(1) average."""
        return self.get(key) is not None

    def remove(self, key):
        """
        Delete key-value pair from hash table.
        Returns the removed value if found, or None.
        Time Complexity: O(1) average.
        """
        index = self._hash(key)
        curr = self.buckets[index]
        prev = None

        while curr:
            if curr.key == key:
                val = curr.value
                if prev is None:
                    self.buckets[index] = curr.next
                else:
                    prev.next = curr.next
                self.count -= 1
                return val
            prev = curr
            curr = curr.next
        return None

    def keys(self):
        """Return list of all keys stored in the hash table. Time Complexity: O(N)"""
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append(curr.key)
                curr = curr.next
        return result

    def values(self):
        """Return list of all values stored in the hash table. Time Complexity: O(N)"""
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append(curr.value)
                curr = curr.next
        return result

    def items(self):
        """Return list of (key, value) pairs. Time Complexity: O(N)"""
        result = []
        for head in self.buckets:
            curr = head
            while curr:
                result.append((curr.key, curr.value))
                curr = curr.next
        return result

    def size(self):
        """Return total number of key-value pairs stored. Time Complexity: O(1)"""
        return self.count

    def is_empty(self):
        """Return True if hash table is empty. Time Complexity: O(1)"""
        return self.count == 0

    def clear(self):
        """Reset hash table to initial state."""
        self.capacity = 16
        self.count = 0
        self.buckets = [None] * self.capacity

    def to_dict(self):
        """Export hash table contents as standard Python dict for JSON output."""
        out = {}
        for k, v in self.items():
            out[k] = v
        return out


if __name__ == "__main__":
    ht = HashTable(initial_capacity=4)
    ht.put("DONOR_01", {"name": "GreenBite Bakery", "city": "Downtown"})
    ht.put("NGO_01", {"name": "Hope Shelter", "capacity": 150})
    ht.put("DONOR_02", {"name": "Metro Market", "city": "North End"})

    assert ht.get("DONOR_01")["name"] == "GreenBite Bakery"
    assert ht.get("NGO_01")["capacity"] == 150
    assert ht.size() == 3
    assert ht.contains("DONOR_02")
    assert not ht.contains("NON_EXISTENT")

    removed = ht.remove("DONOR_01")
    assert removed["name"] == "GreenBite Bakery"
    assert ht.size() == 2
    assert not ht.contains("DONOR_01")
    print("HashTable self-test passed successfully!")
