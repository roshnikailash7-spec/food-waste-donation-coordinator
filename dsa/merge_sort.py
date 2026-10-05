"""
Merge Sort Implementation from Scratch
======================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, inventory managers and food dispatchers
frequently need to sort and view the food catalog according to multiple criteria:
1. By Expiry Hours (ascending: urgent items first; descending: long-lasting items first)
2. By Quantity (ascending: small parcels; descending: bulk pallet batches)

- Merge Sort is a divide-and-conquer algorithm with a strictly guaranteed O(N log N) time
  complexity across best, average, and worst-case scenarios.
- Unlike QuickSort, which can degrade to O(N^2) worst-case on already sorted inputs or
  arrays with duplicate keys, Merge Sort never degrades.
- Crucially, Merge Sort is a STABLE sort: if two food batches have the exact same expiry
  (e.g., both expire in 4.0 hours), Merge Sort preserves their relative original input order.
  This ensures FIFO fairness is preserved for equal-urgency food items.
- Provides the essential pre-requisite for Binary Search, which requires a sorted sequence.

Data Structure Details:
-----------------------
- Implemented purely from scratch without using Python's `.sort()` or `sorted()`.
- Recursively divides the array into halves, sorts each half, and merges the sorted sublists.
- Supports arbitrary key extractors and reverse sorting (ascending/descending).
"""

def merge_sort(arr, key=None, reverse=False):
    """
    Sorts a list using the Merge Sort divide-and-conquer algorithm from scratch.
    
    Parameters:
        arr (list): The list of items to sort.
        key (callable, optional): A function of one argument that extracts a comparison key.
        reverse (bool): If True, sorts in descending order; otherwise ascending.
        
    Returns:
        list: A new sorted list.
        
    Time Complexity: O(N log N) in all cases (best, average, worst).
    Space Complexity: O(N) auxiliary space.
    """
    if len(arr) <= 1:
        return list(arr)

    # Key extractor helper
    if key is None:
        key_fn = lambda x: x
    else:
        key_fn = key

    # Divide step: split array in half
    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid], key=key_fn, reverse=reverse)
    right_half = merge_sort(arr[mid:], key=key_fn, reverse=reverse)

    # Conquer / Combine step: merge the two sorted halves
    return _merge(left_half, right_half, key_fn, reverse)


def _merge(left, right, key_fn, reverse):
    """
    Merges two sorted lists into a single sorted list.
    Preserves stability.
    Time Complexity: O(len(left) + len(right))
    """
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        val_left = key_fn(left[i])
        val_right = key_fn(right[j])

        # Comparison logic considering reverse flag and stability
        if not reverse:
            # Ascending: left <= right maintains stability
            if val_left <= val_right:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        else:
            # Descending: left >= right maintains stability
            if val_left >= val_right:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

    # Append remaining elements from either half
    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged


if __name__ == "__main__":
    sample_food = [
        {"id": "F1", "name": "Rice", "qty": 50, "exp": 4},
        {"id": "F2", "name": "Milk", "qty": 15, "exp": 2},
        {"id": "F3", "name": "Bread", "qty": 30, "exp": 8},
        {"id": "F4", "name": "Apples", "qty": 70, "exp": 24},
        {"id": "F5", "name": "Soup", "qty": 20, "exp": 2},  # Same exp as Milk -> tests stability
    ]

    # Sort by expiry ascending
    by_exp = merge_sort(sample_food, key=lambda x: x["exp"])
    assert by_exp[0]["name"] == "Milk"
    assert by_exp[1]["name"] == "Soup", "Stability test: Milk then Soup"
    assert by_exp[-1]["name"] == "Apples"

    # Sort by quantity descending
    by_qty_desc = merge_sort(sample_food, key=lambda x: x["qty"], reverse=True)
    assert by_qty_desc[0]["qty"] == 70
    assert by_qty_desc[-1]["qty"] == 15
    print("Merge Sort self-test passed successfully!")
