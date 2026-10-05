"""
Binary Search Implementation from Scratch
=========================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, NGOs and relief coordinators often have
precise storage capacities or logistical limits (e.g. an NGO van can transport at most 50 kg,
or a shelter specifically needs a donation parcel around 30 kg).

- Once the food inventory is sorted by quantity (using our custom Merge Sort), finding
  matching items using a linear scan takes O(N) comparisons.
- Binary Search achieves O(log N) logarithmic time complexity by inspecting the midpoint and
  discarding half of the remaining items at each step.
- For 1,000 food records, linear search tests up to 1,000 items, whereas Binary Search pinpoints
  the item in at most 10 comparisons.
- We implement three variants:
  1. `binary_search_exact`: Finds a food batch with the exact requested quantity.
  2. `binary_search_range`: Finds all batches within [min_qty, max_qty] using binary search boundary bounds.
  3. `binary_search_closest`: Finds the batch closest to a target threshold (best fit for an NGO's remaining capacity).

Data Structure Details:
-----------------------
- Implemented from scratch without using Python's `bisect` module.
- Assumes the input array has already been sorted in ascending order (via our Merge Sort).
"""

def binary_search_exact(arr, target_val, key=None):
    """
    Search for an exact target value in a sorted list.
    
    Parameters:
        arr (list): Pre-sorted list in ascending order.
        target_val (float/int): Value to search for.
        key (callable, optional): Key extraction function.
        
    Returns:
        tuple: (index, item) if found, else (-1, None)
        
    Time Complexity: O(log N)
    Space Complexity: O(1)
    """
    if not arr:
        return -1, None

    key_fn = key if key is not None else (lambda x: x)
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = key_fn(arr[mid])

        if mid_val == target_val:
            return mid, arr[mid]
        elif mid_val < target_val:
            low = mid + 1
        else:
            high = mid - 1

    return -1, None


def _lower_bound(arr, target_val, key_fn):
    """Finds the first index where key_fn(arr[i]) >= target_val. O(log N)"""
    low = 0
    high = len(arr)
    while low < high:
        mid = (low + high) // 2
        if key_fn(arr[mid]) < target_val:
            low = mid + 1
        else:
            high = mid
    return low


def _upper_bound(arr, target_val, key_fn):
    """Finds the first index where key_fn(arr[i]) > target_val. O(log N)"""
    low = 0
    high = len(arr)
    while low < high:
        mid = (low + high) // 2
        if key_fn(arr[mid]) <= target_val:
            low = mid + 1
        else:
            high = mid
    return low


def binary_search_range(arr, min_val, max_val, key=None):
    """
    Search for all items in sorted array whose key falls within [min_val, max_val].
    Uses binary search to locate boundaries in O(log N), then slices matches.
    
    Time Complexity: O(log N + K) where K is number of matching items.
    """
    if not arr:
        return []

    key_fn = key if key is not None else (lambda x: x)
    start_idx = _lower_bound(arr, min_val, key_fn)
    end_idx = _upper_bound(arr, max_val, key_fn)

    return arr[start_idx:end_idx]


def binary_search_closest(arr, target_val, key=None):
    """
    Find the item in a sorted array whose key is closest to target_val.
    Useful for finding a food parcel that best fits an NGO's remaining capacity.
    
    Time Complexity: O(log N)
    Space Complexity: O(1)
    """
    if not arr:
        return None

    key_fn = key if key is not None else (lambda x: x)
    n = len(arr)

    # Edge cases: target is outside array range
    if target_val <= key_fn(arr[0]):
        return arr[0]
    if target_val >= key_fn(arr[n - 1]):
        return arr[n - 1]

    low = 0
    high = n - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = key_fn(arr[mid])

        if mid_val == target_val:
            return arr[mid]

        if mid_val < target_val:
            low = mid + 1
        else:
            high = mid - 1

    # At termination, high and low are the two closest bounding candidates
    diff_low = abs(key_fn(arr[low]) - target_val)
    diff_high = abs(key_fn(arr[high]) - target_val)

    return arr[low] if diff_low < diff_high else arr[high]


if __name__ == "__main__":
    sample = [
        {"id": "F1", "qty": 10},
        {"id": "F2", "qty": 20},
        {"id": "F3", "qty": 35},
        {"id": "F4", "qty": 50},
        {"id": "F5", "qty": 80},
    ]

    # Exact search
    idx, item = binary_search_exact(sample, 35, key=lambda x: x["qty"])
    assert idx == 2 and item["id"] == "F3"

    idx, item = binary_search_exact(sample, 99, key=lambda x: x["qty"])
    assert idx == -1 and item is None

    # Range search
    in_range = binary_search_range(sample, 15, 60, key=lambda x: x["qty"])
    assert [x["qty"] for x in in_range] == [20, 35, 50]

    # Closest search
    closest = binary_search_closest(sample, 42, key=lambda x: x["qty"])
    assert closest["id"] == "F3"  # 35 is diff 7, 50 is diff 8 -> 35 is closest

    print("Binary Search self-test passed successfully!")
