"""
Graph (Adjacency List) + Dijkstra's Algorithm Implementation from Scratch
========================================================================
Why this DSA was chosen:
-------------------------
In the Food Waste Reduction & Donation Coordinator, donors and NGOs are situated across
different geographic city zones connected by road networks.

- Perishable food requires minimum travel time so it can be delivered hot, fresh, and safely.
- A Graph is the natural, optimal mathematical representation of an urban transit network:
  Vertices (V) represent donor facilities, distribution hubs, and NGO shelters.
  Edges (E) represent road segments weighted by real-world distance or transit time in kilometers.
- An Adjacency List representation was chosen because urban road networks are sparse (each location
  connects to only a few neighboring intersections), using O(V + E) memory rather than the
  O(V^2) memory required by an adjacency matrix.
- Dijkstra's Algorithm computes the single-source shortest path from a donor to every destination.
  By coupling Dijkstra with our custom from-scratch Min-Heap priority queue, we achieve
  O((V + E) log V) optimal performance.
- When an auto-match is triggered, the system runs Dijkstra from the donor's hub, evaluates all
  active NGOs with sufficient remaining capacity, and selects the closest NGO while highlighting
  the precise turn-by-turn route on the interactive city map.

Data Structure Details:
-----------------------
- Implemented from scratch using dictionaries and lists for adjacency mapping.
- Uses our custom `MinHeap` from `dsa.min_heap` for Dijkstra's priority queue.
- Includes node coordinates (x, y) to render an interactive map visually.
"""

from .min_heap import MinHeap


class Graph:
    """
    Weighted undirected graph using an Adjacency List.
    Implements Dijkstra's algorithm for shortest-path route matching.
    """

    def __init__(self):
        # Maps node_id -> list of (neighbor_id, weight)
        self.adj = {}
        # Maps node_id -> dict(label, type, x, y)
        self.nodes = {}

    def add_node(self, node_id, label=None, node_type="transit", x=0, y=0):
        """
        Add a vertex to the graph.
        node_type: 'donor', 'ngo', or 'transit'
        x, y: coordinate percentage or pixel location for visual rendering.
        """
        if node_id not in self.adj:
            self.adj[node_id] = []
        self.nodes[node_id] = {
            "id": node_id,
            "label": label if label else node_id,
            "type": node_type,
            "x": x,
            "y": y
        }

    def add_edge(self, u, v, weight, bidirectional=True):
        """
        Add an edge with a distance weight (e.g., kilometers).
        Time Complexity: O(1)
        """
        if u not in self.adj:
            self.add_node(u)
        if v not in self.adj:
            self.add_node(v)

        # Check if edge already exists to prevent duplicate weights
        for idx, (neighbor, _) in enumerate(self.adj[u]):
            if neighbor == v:
                self.adj[u][idx] = (v, weight)
                break
        else:
            self.adj[u].append((v, weight))

        if bidirectional:
            for idx, (neighbor, _) in enumerate(self.adj[v]):
                if neighbor == u:
                    self.adj[v][idx] = (u, weight)
                    break
            else:
                self.adj[v].append((u, weight))

    def get_neighbors(self, node_id):
        """Return list of (neighbor_id, weight) tuples for a given vertex."""
        return self.adj.get(node_id, [])

    def dijkstra(self, start_node):
        """
        Dijkstra's shortest path algorithm using custom Min-Heap.
        Returns:
            distances: dict mapping node_id -> shortest distance from start_node
            previous: dict mapping node_id -> previous node in optimal path
        Time Complexity: O((V + E) log V)
        """
        if start_node not in self.adj:
            return {}, {}

        distances = {node: float('inf') for node in self.adj}
        previous = {node: None for node in self.adj}
        distances[start_node] = 0.0

        # Min-Heap stores (distance, node_id)
        pq = MinHeap()
        pq.push(0.0, start_node)

        visited = set()

        while not pq.is_empty():
            curr_dist = pq.peek_priority()
            curr_node = pq.pop()

            if curr_node in visited:
                continue
            visited.add(curr_node)

            for neighbor, weight in self.adj.get(curr_node, []):
                distance_through_curr = curr_dist + weight
                if distance_through_curr < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance_through_curr
                    previous[neighbor] = curr_node
                    pq.push(distance_through_curr, neighbor)

        return distances, previous

    def get_shortest_path(self, start_node, target_node):
        """
        Reconstruct the shortest path from start_node to target_node.
        Returns:
            path: list of node_ids [start_node, ..., target_node]
            distance: total road distance (float)
        """
        if start_node not in self.adj or target_node not in self.adj:
            return [], float('inf')

        distances, previous = self.dijkstra(start_node)
        total_dist = distances.get(target_node, float('inf'))

        if total_dist == float('inf'):
            return [], float('inf')

        path = []
        curr = target_node
        while curr is not None:
            path.append(curr)
            curr = previous.get(curr)

        # Reverse path to start -> target
        path.reverse()
        return path, round(total_dist, 2)

    def find_nearest_ngo(self, donor_location_id, candidate_ngos, required_capacity=0):
        """
        Find the nearest eligible NGO to a donor using Dijkstra.
        candidate_ngos: list of dicts with keys: {'id', 'location_id', 'capacity', 'name'}
        required_capacity: minimum remaining capacity required for the batch.
        
        Returns:
            best_ngo: dict of closest NGO or None
            shortest_path: list of node IDs along the road network
            shortest_distance: distance in kilometers
            all_evaluations: list of evaluated NGOs with distances
        """
        if donor_location_id not in self.adj:
            return None, [], float('inf'), []

        distances, previous = self.dijkstra(donor_location_id)

        best_ngo = None
        min_dist = float('inf')
        evaluations = []

        for ngo in candidate_ngos:
            loc = ngo.get("location_id") or ngo.get("location")
            capacity = ngo.get("capacity", 0)

            # Check capacity requirement
            is_eligible = capacity >= required_capacity
            dist = distances.get(loc, float('inf'))

            eval_entry = {
                "ngo_id": ngo.get("id"),
                "ngo_name": ngo.get("name"),
                "location": loc,
                "distance": round(dist, 2) if dist != float('inf') else None,
                "capacity": capacity,
                "eligible": is_eligible
            }
            evaluations.append(eval_entry)

            if is_eligible and dist < min_dist:
                min_dist = dist
                best_ngo = ngo

        best_path = []
        if best_ngo:
            target_loc = best_ngo.get("location_id") or best_ngo.get("location")
            best_path, _ = self.get_shortest_path(donor_location_id, target_loc)

        return best_ngo, best_path, (round(min_dist, 2) if min_dist != float('inf') else float('inf')), evaluations

    def to_dict(self):
        """
        Export graph representation for UI rendering.
        Returns:
            nodes: list of node dicts with {id, label, type, x, y}
            edges: list of edge dicts with {source, target, weight}
        """
        nodes_list = list(self.nodes.values())
        edges_list = []
        seen = set()

        for u, neighbors in self.adj.items():
            for v, weight in neighbors:
                edge_id = tuple(sorted([u, v]))
                if edge_id not in seen:
                    seen.add(edge_id)
                    edges_list.append({
                        "source": u,
                        "target": v,
                        "weight": weight
                    })

        return {
            "nodes": nodes_list,
            "edges": edges_list
        }


if __name__ == "__main__":
    g = Graph()
    # Add locations
    g.add_node("D_Downtown", "Downtown Bakery", "donor", x=20, y=30)
    g.add_node("HUB_Central", "Central Junction", "transit", x=50, y=50)
    g.add_node("N_Shelter", "Hope Shelter", "ngo", x=80, y=30)
    g.add_node("N_Bank", "Grace Food Bank", "ngo", x=70, y=80)

    # Add edges
    g.add_edge("D_Downtown", "HUB_Central", 3.5)
    g.add_edge("HUB_Central", "N_Shelter", 4.2)
    g.add_edge("HUB_Central", "N_Bank", 6.0)
    g.add_edge("D_Downtown", "N_Shelter", 9.0)

    path, dist = g.get_shortest_path("D_Downtown", "N_Shelter")
    assert path == ["D_Downtown", "HUB_Central", "N_Shelter"], f"Path was {path}"
    assert dist == 7.7, f"Dist was {dist}"

    candidates = [
        {"id": "N1", "name": "Hope Shelter", "location": "N_Shelter", "capacity": 100},
        {"id": "N2", "name": "Grace Food Bank", "location": "N_Bank", "capacity": 200},
    ]
    best, best_path, best_dist, _ = g.find_nearest_ngo("D_Downtown", candidates, required_capacity=50)
    assert best["id"] == "N1"
    assert best_dist == 7.7
    print("Graph & Dijkstra self-test passed successfully!")
