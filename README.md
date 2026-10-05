# Food Waste Reduction and Donation Coordinator

A full-stack college Data Structures and Algorithms (DSA) project built in pure Python and Flask. All core algorithmic data structures are **implemented completely from scratch** without relying on built-in libraries like `heapq`, `collections.deque`, or built-in `sort`/`bisect`.

---

## 🚀 Exact Run Command

To start the application, open your terminal in the project directory and run:

```bash
python app.py
```

Then open your web browser at:
👉 **[http://localhost:5000](http://localhost:5000)** (or [http://127.0.0.1:5000](http://127.0.0.1:5000))

*(On Windows, you can also double-click `run.bat` or run `.\run.bat`)*

---

## 📁 Project Architecture & File Structure

```text
DSA ASSIGNMENT/
├── app.py                     # Flask server, business logic & REST API coordination
├── data.json                  # Persistent JSON storage (survives app restarts)
├── run.bat                    # One-click Windows runner
├── python.bat                 # Direct launcher wrapper
├── test_app.py                # Automated end-to-end test suite
├── dsa/                       # Custom Data Structures Implemented From Scratch
│   ├── __init__.py            # Package exports
│   ├── min_heap.py            # 1. Min-Heap Priority Queue (Expiry Urgency)
│   ├── hash_table.py          # 2. Hash Table with Chaining (O(1) Entity Lookup)
│   ├── linked_list.py         # 3. Singly Linked List (Chronological History Log)
│   ├── queue.py               # 4. FIFO Queue (Pending Pickup Requests)
│   ├── stack.py               # 5. LIFO Stack (Atomic Undo Rollback)
│   ├── graph.py               # 6. Graph + Dijkstra (Shortest Route to Nearest NGO)
│   ├── merge_sort.py          # 7. Merge Sort (Guaranteed O(N log N) Stable Sort)
│   └── binary_search.py       # 8. Binary Search (O(log N) Quantity Searches)
├── templates/
│   └── index.html             # Single-Page Application interface
└── static/
    ├── style.css              # Soft pastel green & cream modern aesthetic
    └── app.js                 # Dynamic UI controller & Canvas Dijkstra map visualizer
```

---

## 📊 Summary of All 8 Data Structures Implemented From Scratch

| # | Data Structure | Source File | Where It Is Used | Operations & Time Complexity | Space Complexity | Why It Was Chosen |
|---|---|---|---|---|---|---|
| **1** | **Min-Heap (Priority Queue)** | `dsa/min_heap.py` | Expiry urgency management for surplus food | Peek: $\mathcal{O}(1)$<br>Push: $\mathcal{O}(\log N)$<br>Pop: $\mathcal{O}(\log N)$<br>Extract Sorted: $\mathcal{O}(N \log N)$ | $\mathcal{O}(N)$ | Perishable food spoils quickly. Min-Heap guarantees immediate $\mathcal{O}(1)$ access to the most critically expiring batch without continuous $\mathcal{O}(N \log N)$ sorting. |
| **2** | **Hash Table (Chaining)** | `dsa/hash_table.py` | Instant lookup of Donors, NGOs, and Food by unique ID | Get: $\mathcal{O}(1)$ avg, $\mathcal{O}(N)$ worst<br>Put: $\mathcal{O}(1)$ avg<br>Remove: $\mathcal{O}(1)$ avg | $\mathcal{O}(N)$ | Custom DJB2 hashing with separate chaining eliminates linear scans. Verifying donor or NGO capacity takes expected $\mathcal{O}(1)$ constant time. |
| **3** | **Singly Linked List** | `dsa/linked_list.py` | Chronological donation history & audit trail | Prepend: $\mathcal{O}(1)$<br>Append: $\mathcal{O}(1)$<br>Pop Front: $\mathcal{O}(1)$<br>Traversal: $\mathcal{O}(N)$ | $\mathcal{O}(N)$ | Activity logs are write-heavy; prepending new events to the head takes $\mathcal{O}(1)$ time without shifting elements in memory. |
| **4** | **FIFO Queue** | `dsa/queue.py` | Pending driver & volunteer pickup requests | Enqueue: $\mathcal{O}(1)$<br>Dequeue: $\mathcal{O}(1)$<br>Peek: $\mathcal{O}(1)$ | $\mathcal{O}(N)$ | First-In, First-Out fairness prevents starvation of scheduled donations, ensuring drivers pick up orders in exact arrival order. |
| **5** | **LIFO Stack** | `dsa/stack.py` | Multi-level Undo mechanism | Push: $\mathcal{O}(1)$<br>Pop: $\mathcal{O}(1)$<br>Peek: $\mathcal{O}(1)$ | $\mathcal{O}(N)$ | Last-In, First-Out is the exact mathematical inverse of chronological execution, enabling clean atomic rollback of operations. |
| **6** | **Graph + Dijkstra** | `dsa/graph.py` | Urban road network & shortest route to nearest NGO | Dijkstra: $\mathcal{O}((V + E) \log V)$<br>Add Edge: $\mathcal{O}(1)$<br>Get Neighbors: $\mathcal{O}(1)$ | $\mathcal{O}(V + E)$ | Models city road segments. Adjacency list is memory-optimal for sparse maps. Coupled with our custom Min-Heap, Dijkstra finds the fastest delivery path. |
| **7** | **Merge Sort** | `dsa/merge_sort.py` | Multi-attribute catalog sorting (expiry, batch size) | Best/Avg/Worst: $\mathcal{O}(N \log N)$<br>Merge step: $\mathcal{O}(N)$ | $\mathcal{O}(N)$ | Unlike QuickSort ($\mathcal{O}(N^2)$ worst-case), Merge Sort never degrades and is stable, preserving FIFO arrival order for identical expiry timestamps. |
| **8** | **Binary Search** | `dsa/binary_search.py` | Quantity queries (exact, range, closest NGO fit) | Exact Match: $\mathcal{O}(\log N)$<br>Closest Batch: $\mathcal{O}(\log N)$<br>Range: $\mathcal{O}(\log N + K)$ | $\mathcal{O}(1)$ | Logarithmic search allows instant matching against shelter storage limits without iterating over every food record. |

---

## 🎓 Viva-Friendly Guide: How the Pieces Connect (For 2nd-Year Students)

When an examiner or professor asks: *"Explain your project's workflow and how the data structures interact with each other,"* here is the exact step-by-step narrative to present:

### The Complete Lifecycle of a Food Donation:

```text
[Donor lists Food]
       │
       ▼
1. Hash Table: Checks if Donor ID exists in O(1). Stores new Food record.
2. Min-Heap: Pushes food item with priority = expiry_hours in O(log N).
3. Singly Linked List: Prepends audit log entry in O(1).
4. Stack: Pushes {"type": "ADD_FOOD"} for undo in O(1).
       │
       ▼ [Auto-Match Triggered]
5. Min-Heap: Extracts root node (soonest-expiring food) in O(log N).
6. Hash Table: Looks up donor location and active NGOs in O(1).
7. Graph + Dijkstra: Runs Dijkstra using Min-Heap priority queue from donor's node,
   computing shortest distance to all candidate NGOs with remaining capacity.
8. FIFO Queue: Enqueues a pickup dispatch mission in O(1).
9. Stack: Pushes {"type": "AUTO_MATCH"} for undo in O(1).
       │
       ▼ [Driver Dispatched & Pickup Completed]
10. FIFO Queue: Dequeues the front pickup in O(1).
11. Hash Table: Updates food status to 'COMPLETED'.
12. Singly Linked List: Prepends completion record in O(1).
       │
       ▼ [Accidental Action? Click 'Undo']
13. Stack: Pops the top action in O(1) and executes inverse handler (restores capacity,
    re-pushes food into Min-Heap, removes pickup from queue).
```

---

## 🎯 Top Viva Questions & Answers

### Q1: Why did you use a Min-Heap instead of simply sorting an array?
> **Answer:** If we used a regular unsorted array, finding the minimum takes $\mathcal{O}(N)$ time. If we sorted the array every time a donor listed food, it would take $\mathcal{O}(N \log N)$ time, and inserting an element into a sorted array requires shifting elements in $\mathcal{O}(N)$ time. A **Min-Heap** provides the mathematically optimal middle ground: **$\mathcal{O}(1)$** to peek at the most urgent food item, and only **$\mathcal{O}(\log N)$** to insert or extract, which scales efficiently for high-throughput listing.

### Q2: Why implement Separate Chaining in your Hash Table?
> **Answer:** In open addressing (linear/quadratic probing), as the load factor approaches 1.0, primary clustering causes search times to degrade drastically and deletions require complex `tombstone` markers. With **separate chaining**, each bucket holds a linked chain of `HashEntry` nodes. Collisions are handled gracefully at the bucket head in $\mathcal{O}(1)$, and our table dynamically doubles its capacity when the load factor exceeds 0.75, preserving true $\mathcal{O}(1)$ average performance.

### Q3: Why choose Merge Sort over QuickSort?
> **Answer:** QuickSort has a worst-case time complexity of $\mathcal{O}(N^2)$ when the pivot is poorly chosen or when sorting nearly-sorted food lists. **Merge Sort** strictly guarantees **$\mathcal{O}(N \log N)$** time in all cases (best, average, and worst). Furthermore, Merge Sort is **stable**: if two food batches have the exact same expiry time (e.g. 4.0 hours), Merge Sort preserves their original arrival order, maintaining FIFO fairness.

### Q4: Why is a Singly Linked List used for History instead of a dynamic Python list?
> **Answer:** An activity log is primarily write-heavy, with the requirement that the newest event appears at the top (index 0). In a standard dynamic array/list, prepending at index 0 forces all $N$ existing elements to shift one position right, taking $\mathcal{O}(N)$ time. In our custom **Singly Linked List**, prepending at the head updates just two pointers (`newNode.next = head; head = newNode`), taking strictly **$\mathcal{O}(1)$** time.

### Q5: How does your FIFO Queue differ from a Python `list`?
> **Answer:** When using a Python `list` as a queue, calling `list.pop(0)` takes $\mathcal{O}(N)$ time because the entire array in memory must be shifted left. Our custom **Queue** is implemented with dedicated `front` and `rear` node pointers, guaranteeing that both `enqueue()` and `dequeue()` execute in strict **$\mathcal{O}(1)$** time without using `collections.deque`.

### Q6: How does Dijkstra's Algorithm use your custom Min-Heap?
> **Answer:** Dijkstra is an iterative greedy algorithm. Instead of doing an $\mathcal{O}(V)$ linear scan on every iteration to find the unvisited vertex with the minimum tentative distance, we push `(distance, node_id)` pairs into our custom `MinHeap`. The vertex with the smallest distance is popped in $\mathcal{O}(\log V)$ time, bringing the total time complexity down to $\mathcal{O}((V + E) \log V)$.

---

## 🧪 Verifying the Test Suite

A comprehensive automated test runner is included in `test_app.py`. You can execute it at any time with the server running:

```bash
python test_app.py
```

It validates:
1. Dashboard aggregation and initial statistics
2. Merge Sort ordering by expiry and quantity
3. Min-Heap priority extraction
4. Binary Search (exact, range, and closest fit)
5. Auto-matching with Dijkstra shortest route traversal
6. FIFO Queue enqueue and dequeue operations
7. Multi-level Undo stack rollback
8. Singly Linked List history head-prepending
9. City road network graph connectivity
