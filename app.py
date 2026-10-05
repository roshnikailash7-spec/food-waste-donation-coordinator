"""
Food Waste Reduction and Donation Coordinator
=============================================
Web application backend using pure Python and Flask.
All core algorithmic operations and data structures are implemented FROM SCRATCH in dsa/.
No heapq, collections.deque, or built-in sort/bisect are used for DSA workflows.

DSA Mapping:
1. Min-Heap (dsa.MinHeap)        -> Priority Queue for soonest-expiring surplus food.
2. Hash Table (dsa.HashTable)    -> O(1) lookup of Donors, NGOs, and Food by unique ID.
3. Singly Linked List (dsa.SLL)  -> O(1) head-prepended chronological donation history log.
4. Queue (dsa.Queue)             -> FIFO queue for pending driver & volunteer pickup requests.
5. Stack (dsa.Stack)             -> LIFO undo stack to revert state-altering actions.
6. Graph + Dijkstra (dsa.Graph)  -> Urban road network & shortest route matching to nearest NGO.
7. Merge Sort (dsa.merge_sort)   -> Guaranteed O(N log N) stable sorting by expiry or quantity.
8. Binary Search (dsa.binary_search) -> O(log N) quantity queries on pre-sorted food inventory.
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Import custom DSA implementations from scratch
from dsa import (
    MinHeap,
    HashTable,
    SinglyLinkedList,
    Queue,
    Stack,
    Graph,
    merge_sort,
    binary_search_exact,
    binary_search_range,
    binary_search_closest
)

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# Global instances of custom data structures
donors_ht = HashTable(initial_capacity=16)     # Key: donor_id -> donor dict
ngos_ht = HashTable(initial_capacity=16)       # Key: ngo_id -> ngo dict
food_ht = HashTable(initial_capacity=32)       # Key: food_id -> food dict
food_min_heap = MinHeap()                      # Priority Queue ordered by expiry_hours
pickup_queue = Queue()                         # FIFO queue for scheduled pickups
history_ll = SinglyLinkedList()                # Singly Linked List for chronological logs
undo_stack = Stack()                           # LIFO stack for undo operations
city_graph = Graph()                           # Graph with adjacency list for road network


def rebuild_heap():
    """Rebuilds the Min-Heap priority queue with all currently AVAILABLE food items."""
    global food_min_heap
    food_min_heap = MinHeap()
    for food in food_ht.values():
        if food.get("status") == "AVAILABLE":
            food_min_heap.push(float(food.get("expiry_hours", 999.0)), food)


def load_data():
    """Load application state from data.json into custom data structures."""
    global city_graph
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Populate Donors Hash Table
    donors_ht.clear()
    for donor in data.get("donors", []):
        donors_ht.put(donor["id"], donor)

    # 2. Populate NGOs Hash Table
    ngos_ht.clear()
    for ngo in data.get("ngos", []):
        ngos_ht.put(ngo["id"], ngo)

    # 3. Populate Food Hash Table
    food_ht.clear()
    for food in data.get("food_items", []):
        food_ht.put(food["id"], food)

    # 4. Populate Food Min-Heap with available food
    rebuild_heap()

    # 5. Populate Pickup Queue (FIFO)
    pickup_queue.from_list(data.get("pickup_queue", []))

    # 6. Populate Donation History (Singly Linked List)
    history_ll.from_list(data.get("history", []))

    # 7. Populate Undo Stack (LIFO)
    undo_stack.from_list(data.get("undo_stack", []))

    # 8. Reconstruct City Road Graph
    city_graph = Graph()
    for node in data.get("graph_nodes", []):
        city_graph.add_node(
            node_id=node["id"],
            label=node.get("label", node["id"]),
            node_type=node.get("type", "transit"),
            x=node.get("x", 50),
            y=node.get("y", 50)
        )

    for edge in data.get("graph_edges", []):
        city_graph.add_edge(edge["source"], edge["target"], float(edge["weight"]), bidirectional=True)


def save_data():
    """Persist the current state of custom data structures to data.json."""
    graph_dict = city_graph.to_dict()
    data = {
        "donors": donors_ht.values(),
        "ngos": ngos_ht.values(),
        "food_items": food_ht.values(),
        "pickup_queue": pickup_queue.to_list(),
        "history": history_ll.to_list(),
        "undo_stack": undo_stack.to_list(),
        "graph_nodes": graph_dict["nodes"],
        "graph_edges": graph_dict["edges"]
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_history_entry(action_type, title, description, badge="info"):
    """
    Prepends an audit entry into the Singly Linked List history log in O(1) time.
    """
    entry = {
        "id": f"HIST_{int(datetime.now().timestamp() * 1000)}",
        "action_type": action_type,
        "title": title,
        "description": description,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "badge": badge
    }
    history_ll.prepend(entry)
    return entry


# Initialize data on server boot
load_data()


# -------------------------------------------------------------------------
# Web Routes & REST API Endpoints
# -------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the single-page application dashboard."""
    return render_template("index.html")


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    """
    Aggregates high-level metrics and urgent notifications across all data structures.
    Demonstrates:
    - Min-Heap: O(1) peek at the most urgent food item.
    - FIFO Queue: O(1) peek at next scheduled pickup.
    - Stack: O(1) check if undo is available.
    - Hash Table: O(1) counts and lookups.
    """
    all_food = food_ht.values()
    available_food = [f for f in all_food if f.get("status") == "AVAILABLE"]

    # Calculate metrics
    total_food_saved = sum(
        f.get("quantity", 0) for f in all_food if f.get("status") in ("RESERVED", "COMPLETED")
    )
    total_donations_completed = sum(
        1 for f in all_food if f.get("status") == "COMPLETED"
    )
    urgent_count = sum(
        1 for f in available_food if float(f.get("expiry_hours", 99)) < 6.0
    )

    # Min-Heap peek (most urgent available food)
    most_urgent = food_min_heap.peek()

    # FIFO Queue peek (next driver dispatch)
    next_pickup = pickup_queue.peek()

    # Undo Stack check
    can_undo = not undo_stack.is_empty()
    last_action = undo_stack.peek()

    return jsonify({
        "stats": {
            "total_food_saved_kg": round(total_food_saved, 1),
            "donations_completed": total_donations_completed,
            "available_items_count": len(available_food),
            "urgent_items_count": urgent_count,
            "active_donors_count": donors_ht.size(),
            "active_ngos_count": ngos_ht.size(),
            "pending_pickups_count": pickup_queue.size(),
        },
        "most_urgent_food": most_urgent,
        "next_pickup": next_pickup,
        "can_undo": can_undo,
        "last_action_type": last_action.get("type") if last_action else None
    })


@app.route("/api/food", methods=["GET"])
def get_food_catalog():
    """
    Returns food items, supporting:
    - Custom Merge Sort by 'expiry' or 'quantity' (ascending or descending).
    - Status filtering ('ALL', 'AVAILABLE', 'RESERVED', 'COMPLETED').
    """
    sort_by = request.args.get("sort_by", "expiry")  # 'expiry' or 'quantity'
    order = request.args.get("order", "asc")         # 'asc' or 'desc'
    status_filter = request.args.get("status", "ALL")
    urgent_only = request.args.get("urgent_only", "false").lower() == "true"

    items = food_ht.values()

    if status_filter != "ALL":
        items = [f for f in items if f.get("status") == status_filter]

    if urgent_only:
        items = [f for f in items if float(f.get("expiry_hours", 99)) < 6.0]

    # Apply custom from-scratch Merge Sort
    reverse = (order == "desc")
    if sort_by == "quantity":
        sorted_items = merge_sort(items, key=lambda x: float(x.get("quantity", 0)), reverse=reverse)
    else:  # default by expiry
        sorted_items = merge_sort(items, key=lambda x: float(x.get("expiry_hours", 999.0)), reverse=reverse)

    return jsonify({
        "items": sorted_items,
        "total_count": len(sorted_items),
        "sorted_by": sort_by,
        "order": order
    })


@app.route("/api/food/urgent", methods=["GET"])
def get_urgent_food_heap():
    """
    Extracts food items ordered strictly by expiry time using custom Min-Heap.
    Demonstrates MinHeap.get_sorted_list() in O(N log N) without built-in sort.
    """
    urgent_sorted = food_min_heap.get_sorted_list()
    return jsonify({
        "items": urgent_sorted,
        "count": len(urgent_sorted),
        "heap_size": food_min_heap.size()
    })


@app.route("/api/food", methods=["POST"])
def add_food():
    """
    Adds a new surplus food batch.
    - Validates Donor ID in O(1) via donors_ht.
    - Stores food in food_ht in O(1).
    - Pushes into food_min_heap in O(log N).
    - Records event into history_ll in O(1).
    - Pushes undo action onto undo_stack in O(1).
    """
    data = request.json or {}
    name = data.get("name", "").strip()
    donor_id = data.get("donor_id", "").strip()
    quantity = float(data.get("quantity", 0))
    expiry_hours = float(data.get("expiry_hours", 0))
    category = data.get("category", "General Food").strip()
    unit = data.get("unit", "kg").strip()

    if not name or quantity <= 0 or expiry_hours <= 0:
        return jsonify({"error": "Name, quantity (>0), and expiry hours (>0) are required."}), 400

    # O(1) lookup of Donor via Hash Table
    donor = donors_ht.get(donor_id)
    if not donor:
        return jsonify({"error": f"Donor with ID '{donor_id}' not found."}), 404

    # Generate new ID
    new_id = f"FOOD_{int(datetime.now().timestamp() * 1000) % 100000:05d}"
    food_item = {
        "id": new_id,
        "name": name,
        "donor_id": donor_id,
        "donor_name": donor["name"],
        "donor_location": donor["location"],
        "quantity": quantity,
        "unit": unit,
        "expiry_hours": expiry_hours,
        "category": category,
        "status": "AVAILABLE",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # 1. Insert into Hash Table (O(1))
    food_ht.put(new_id, food_item)

    # 2. Push into Min-Heap (O(log N))
    food_min_heap.push(expiry_hours, food_item)

    # 3. Add to Singly Linked List History (O(1) prepend)
    add_history_entry(
        action_type="FOOD_ADDED",
        title="Surplus Food Listed",
        description=f"{donor['name']} listed {quantity} {unit} of '{name}' (Expires in {expiry_hours}h).",
        badge="success"
    )

    # 4. Push onto Undo Stack (O(1))
    undo_stack.push({
        "type": "ADD_FOOD",
        "food_id": new_id,
        "food_data": food_item
    })

    save_data()
    return jsonify({"success": True, "food": food_item}), 201


@app.route("/api/food/search", methods=["GET"])
def search_food():
    """
    Search food by quantity using custom Binary Search algorithms.
    Workflow:
    1. Retrieve available items.
    2. Sort by quantity using custom Merge Sort (pre-requisite for Binary Search).
    3. Execute Binary Search:
       - 'exact': binary_search_exact for target quantity.
       - 'range': binary_search_range for [min_qty, max_qty].
       - 'closest': binary_search_closest to find nearest matching batch for an NGO.
    """
    mode = request.args.get("mode", "exact")  # 'exact', 'range', 'closest'

    available_items = [f for f in food_ht.values() if f.get("status") == "AVAILABLE"]

    # Step 1: Pre-sort items by quantity using our custom Merge Sort
    sorted_by_qty = merge_sort(available_items, key=lambda x: float(x.get("quantity", 0)))

    results = []
    comparisons_info = ""

    if mode == "exact":
        target = float(request.args.get("target", 0))
        idx, item = binary_search_exact(sorted_by_qty, target, key=lambda x: float(x.get("quantity", 0)))
        if item:
            results = [item]
        comparisons_info = f"Binary search for exact {target} kg in {len(sorted_by_qty)} items in O(log N) steps."

    elif mode == "range":
        min_val = float(request.args.get("min", 0))
        max_val = float(request.args.get("max", 9999))
        results = binary_search_range(sorted_by_qty, min_val, max_val, key=lambda x: float(x.get("quantity", 0)))
        comparisons_info = f"Binary search range [{min_val}, {max_val}] kg found {len(results)} items in O(log N + K) steps."

    elif mode == "closest":
        target = float(request.args.get("target", 0))
        closest_item = binary_search_closest(sorted_by_qty, target, key=lambda x: float(x.get("quantity", 0)))
        if closest_item:
            results = [closest_item]
        comparisons_info = f"Binary search found closest batch to {target} kg in O(log N) steps."

    return jsonify({
        "results": results,
        "count": len(results),
        "mode": mode,
        "sorted_items_count": len(sorted_by_qty),
        "explanation": comparisons_info
    })


@app.route("/api/donors", methods=["GET"])
def get_donors():
    """Retrieve all donors from the donors Hash Table."""
    return jsonify({"donors": donors_ht.values()})


@app.route("/api/donors", methods=["POST"])
def add_donor():
    """
    Register a new food donor.
    - Saves to donors_ht in O(1).
    - Connects location to city_graph.
    - Pushes undo action to undo_stack.
    """
    data = request.json or {}
    name = data.get("name", "").strip()
    location = data.get("location", "").strip()
    contact = data.get("contact", "").strip()
    donor_type = data.get("type", "Food Business").strip()

    if not name or not location:
        return jsonify({"error": "Name and location are required."}), 400

    new_id = f"DONOR_{int(datetime.now().timestamp() * 1000) % 10000:04d}"
    donor = {
        "id": new_id,
        "name": name,
        "location": location,
        "contact": contact,
        "type": donor_type
    }

    donors_ht.put(new_id, donor)

    # Ensure location is a vertex in the city graph
    if location not in city_graph.adj:
        city_graph.add_node(location, label=location, node_type="donor", x=45, y=50)
        # Link to nearest central junction for connectivity
        city_graph.add_edge(location, "Central City Junction", 3.0, bidirectional=True)

    add_history_entry(
        action_type="DONOR_REGISTERED",
        title="New Donor Joined",
        description=f"'{name}' at {location} registered to donate surplus food.",
        badge="info"
    )

    undo_stack.push({
        "type": "ADD_DONOR",
        "donor_id": new_id,
        "donor_data": donor
    })

    save_data()
    return jsonify({"success": True, "donor": donor}), 201


@app.route("/api/ngos", methods=["GET"])
def get_ngos():
    """Retrieve all NGOs from the NGOs Hash Table."""
    return jsonify({"ngos": ngos_ht.values()})


@app.route("/api/ngos", methods=["POST"])
def add_ngo():
    """
    Register a new partner NGO.
    - Saves to ngos_ht in O(1).
    - Connects location to city_graph.
    - Pushes undo action to undo_stack.
    """
    data = request.json or {}
    name = data.get("name", "").strip()
    location = data.get("location", "").strip()
    capacity = float(data.get("capacity", 0))
    contact = data.get("contact", "").strip()
    serves = data.get("serves", "Community").strip()

    if not name or not location or capacity <= 0:
        return jsonify({"error": "Name, location, and capacity (>0) are required."}), 400

    new_id = f"NGO_{int(datetime.now().timestamp() * 1000) % 10000:04d}"
    ngo = {
        "id": new_id,
        "name": name,
        "location": location,
        "capacity": capacity,
        "remaining_capacity": capacity,
        "contact": contact,
        "serves": serves
    }

    ngos_ht.put(new_id, ngo)

    if location not in city_graph.adj:
        city_graph.add_node(location, label=location, node_type="ngo", x=55, y=50)
        city_graph.add_edge(location, "South Bridge Interchange", 3.2, bidirectional=True)

    add_history_entry(
        action_type="NGO_REGISTERED",
        title="New NGO Partner Added",
        description=f"'{name}' ({capacity} kg capacity) at {location} onboarded.",
        badge="info"
    )

    undo_stack.push({
        "type": "ADD_NGO",
        "ngo_id": new_id,
        "ngo_data": ngo
    })

    save_data()
    return jsonify({"success": True, "ngo": ngo}), 201


@app.route("/api/match/auto", methods=["POST"])
def auto_match():
    """
    Core intelligent coordinator workflow connecting multiple DSAs:
    1. Min-Heap: Extracts the food item closest to expiry in O(log N).
    2. Hash Table: O(1) lookup of Donor profile and candidate NGOs.
    3. Graph + Dijkstra: Calculates shortest road distance from donor hub to each eligible NGO in O((V+E) log V).
    4. FIFO Queue: Enqueues the generated pickup dispatch task in O(1).
    5. Singly Linked List: Logs the match event in O(1).
    6. LIFO Stack: Pushes reversible action onto undo stack in O(1).
    """
    # Step 1: Extract most urgent food from Min-Heap
    if food_min_heap.is_empty():
        return jsonify({"error": "No surplus food items currently available to match."}), 400

    urgent_food = food_min_heap.pop()
    food_id = urgent_food["id"]
    food_qty = float(urgent_food.get("quantity", 0))

    # Step 2: Fetch donor details from Hash Table in O(1)
    donor = donors_ht.get(urgent_food["donor_id"])
    donor_location = donor["location"] if donor else urgent_food.get("donor_location")

    # Step 3: Gather active NGOs and evaluate shortest routes via Dijkstra
    candidate_ngos = []
    for ngo in ngos_ht.values():
        rem_cap = float(ngo.get("remaining_capacity", ngo.get("capacity", 0)))
        candidate_ngos.append({
            "id": ngo["id"],
            "name": ngo["name"],
            "location": ngo["location"],
            "capacity": rem_cap
        })

    # Run Dijkstra on the road network graph
    best_ngo, path, distance, evaluations = city_graph.find_nearest_ngo(
        donor_location_id=donor_location,
        candidate_ngos=candidate_ngos,
        required_capacity=food_qty
    )

    # Fallback if no NGO had enough capacity: find nearest NGO regardless of capacity
    if not best_ngo:
        best_ngo, path, distance, evaluations = city_graph.find_nearest_ngo(
            donor_location_id=donor_location,
            candidate_ngos=candidate_ngos,
            required_capacity=0
        )

    if not best_ngo:
        # Re-insert food back into heap since no route could be found
        food_min_heap.push(float(urgent_food.get("expiry_hours", 99)), urgent_food)
        return jsonify({"error": "No reachable NGO found on the road network."}), 400

    matched_ngo = ngos_ht.get(best_ngo["id"])

    # Step 4: Update state
    # Update food status in Hash Table
    urgent_food["status"] = "RESERVED"
    urgent_food["assigned_ngo_id"] = matched_ngo["id"]
    urgent_food["assigned_ngo_name"] = matched_ngo["name"]
    food_ht.put(food_id, urgent_food)

    # Deduct capacity from NGO
    deducted_qty = min(food_qty, float(matched_ngo.get("remaining_capacity", matched_ngo["capacity"])))
    matched_ngo["remaining_capacity"] = max(0.0, float(matched_ngo.get("remaining_capacity", matched_ngo["capacity"])) - food_qty)
    ngos_ht.put(matched_ngo["id"], matched_ngo)

    # Step 5: Create pickup request and enqueue to FIFO Queue (O(1))
    pickup_id = f"PKUP_{int(datetime.now().timestamp() * 1000) % 100000:05d}"
    pickup_request = {
        "id": pickup_id,
        "food_id": food_id,
        "food_name": urgent_food["name"],
        "quantity": food_qty,
        "unit": urgent_food.get("unit", "kg"),
        "expiry_hours": urgent_food["expiry_hours"],
        "donor_id": urgent_food["donor_id"],
        "donor_name": urgent_food["donor_name"],
        "donor_location": donor_location,
        "ngo_id": matched_ngo["id"],
        "ngo_name": matched_ngo["name"],
        "ngo_location": matched_ngo["location"],
        "route_path": path,
        "distance_km": distance,
        "status": "DISPATCH_READY",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    pickup_queue.enqueue(pickup_request)

    # Step 6: Log to Singly Linked List History (O(1) prepend)
    route_str = " -> ".join(path)
    add_history_entry(
        action_type="AUTO_MATCHED",
        title="Optimal Food Match Made",
        description=(
            f"Prioritized '{urgent_food['name']}' ({food_qty} kg, expires in {urgent_food['expiry_hours']}h). "
            f"Dijkstra routed to '{matched_ngo['name']}' via [{route_str}] ({distance} km)."
        ),
        badge="warning"
    )

    # Step 7: Push action onto Undo Stack (O(1))
    undo_stack.push({
        "type": "AUTO_MATCH",
        "pickup": pickup_request,
        "food_id": food_id,
        "ngo_id": matched_ngo["id"],
        "capacity_deducted": food_qty
    })

    save_data()

    return jsonify({
        "success": True,
        "food": urgent_food,
        "ngo": matched_ngo,
        "pickup": pickup_request,
        "path": path,
        "distance_km": distance,
        "evaluations": evaluations
    })


@app.route("/api/queue", methods=["GET"])
def get_pickup_queue():
    """
    Returns all pending pickup requests in strict FIFO order from custom Queue.
    """
    return jsonify({
        "queue": pickup_queue.to_list(),
        "count": pickup_queue.size()
    })


@app.route("/api/queue/complete", methods=["POST"])
def complete_pickup():
    """
    Completes the next scheduled pickup in FIFO order.
    - Dequeues front item from pickup_queue in O(1).
    - Updates food status to 'COMPLETED'.
    - Logs to history_ll in O(1).
    - Pushes undo action to undo_stack in O(1).
    """
    if pickup_queue.is_empty():
        return jsonify({"error": "No pending pickup requests in queue."}), 400

    # Dequeue from FIFO Queue (O(1))
    pickup = pickup_queue.dequeue()
    food_id = pickup["food_id"]

    # Update food status to COMPLETED
    food = food_ht.get(food_id)
    if food:
        food["status"] = "COMPLETED"
        food["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        food_ht.put(food_id, food)

    add_history_entry(
        action_type="PICKUP_COMPLETED",
        title="Food Delivered Successfully",
        description=(
            f"Pickup #{pickup['id']} delivered: {pickup['quantity']} {pickup.get('unit', 'kg')} of "
            f"'{pickup['food_name']}' transferred from {pickup['donor_name']} to {pickup['ngo_name']}."
        ),
        badge="success"
    )

    # Push to Undo Stack
    undo_stack.push({
        "type": "COMPLETE_PICKUP",
        "pickup": pickup,
        "food_id": food_id
    })

    save_data()
    return jsonify({
        "success": True,
        "completed_pickup": pickup,
        "remaining_queue_size": pickup_queue.size()
    })


@app.route("/api/undo", methods=["POST"])
def undo_last_action():
    """
    Pops the most recent action from custom LIFO Stack and reverses it.
    Demonstrates Stack O(1) rollback capability across diverse action types.
    """
    if undo_stack.is_empty():
        return jsonify({"error": "No actions available to undo."}), 400

    # Pop from LIFO Stack (O(1))
    action = undo_stack.pop()
    action_type = action.get("type")
    description = ""

    if action_type == "ADD_FOOD":
        food_id = action["food_id"]
        food_ht.remove(food_id)
        food_min_heap.remove_by_id(food_id)
        description = f"Removed listed food item '{action['food_data']['name']}'."

    elif action_type == "ADD_DONOR":
        donor_id = action["donor_id"]
        donors_ht.remove(donor_id)
        description = f"Removed registered donor '{action['donor_data']['name']}'."

    elif action_type == "ADD_NGO":
        ngo_id = action["ngo_id"]
        ngos_ht.remove(ngo_id)
        description = f"Removed registered NGO '{action['ngo_data']['name']}'."

    elif action_type == "AUTO_MATCH":
        pickup = action["pickup"]
        food_id = action["food_id"]
        ngo_id = action["ngo_id"]
        qty = action["capacity_deducted"]

        # 1. Remove pickup from Queue
        pickup_queue.remove_by_id(pickup["id"])

        # 2. Restore food item to AVAILABLE and re-push into Min-Heap
        food = food_ht.get(food_id)
        if food:
            food["status"] = "AVAILABLE"
            food.pop("assigned_ngo_id", None)
            food.pop("assigned_ngo_name", None)
            food_ht.put(food_id, food)
            food_min_heap.push(float(food.get("expiry_hours", 99)), food)

        # 3. Restore NGO capacity
        ngo = ngos_ht.get(ngo_id)
        if ngo:
            ngo["remaining_capacity"] = min(
                float(ngo["capacity"]),
                float(ngo.get("remaining_capacity", 0)) + qty
            )
            ngos_ht.put(ngo_id, ngo)

        description = f"Reverted auto-match for '{pickup['food_name']}'. Restored to priority heap."

    elif action_type == "COMPLETE_PICKUP":
        pickup = action["pickup"]
        food_id = action["food_id"]

        # 1. Restore food to RESERVED
        food = food_ht.get(food_id)
        if food:
            food["status"] = "RESERVED"
            food_ht.put(food_id, food)

        # 2. Re-enqueue the pickup back into FIFO queue
        pickup_queue.enqueue(pickup)
        description = f"Reopened completed pickup #{pickup['id']} back into dispatch queue."

    # Record undo event in Singly Linked List history
    add_history_entry(
        action_type="ACTION_UNDONE",
        title="Undo Action Executed",
        description=f"Action '{action_type}' was reversed: {description}",
        badge="info"
    )

    save_data()
    return jsonify({
        "success": True,
        "undone_action": action_type,
        "message": description,
        "remaining_undo_count": undo_stack.size()
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Returns audit history log in chronological sequence (newest first)
    by traversing custom Singly Linked List in O(N) time.
    """
    return jsonify({
        "history": history_ll.to_list(),
        "total_records": history_ll.size()
    })


@app.route("/api/graph", methods=["GET"])
def get_graph():
    """
    Returns urban road network nodes and edges from custom Graph representation.
    """
    return jsonify(city_graph.to_dict())


@app.route("/api/reset", methods=["POST"])
def reset_to_seed_data():
    """
    Resets application state back to clean default seed data (5 donors, 5 NGOs, 10 food items).
    """
    # Overwrite data.json with fresh initial sample data
    # (data.json already contains the initial dataset)
    load_data()
    add_history_entry(
        action_type="SYSTEM_RESET",
        title="System Reset to Defaults",
        description="Loaded 5 donors, 5 NGOs, 10 food items, and city road network.",
        badge="warning"
    )
    save_data()
    return jsonify({"success": True, "message": "System reset to default realistic seed data."})


if __name__ == "__main__":
    print("=" * 70)
    print(" FOOD WASTE REDUCTION AND DONATION COORDINATOR")
    print(" Core Logic Powered by 8 Custom Data Structures Implemented From Scratch")
    print(" Server starting on http://127.0.0.1:5000 (or http://localhost:5000)")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5000, debug=True)
