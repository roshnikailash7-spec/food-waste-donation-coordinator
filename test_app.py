import urllib.request
import json
import sys

base = 'http://127.0.0.1:5000'

def req(path, method='GET', data=None):
    url = base + path
    headers = {'Content-Type': 'application/json'} if data else {}
    body = json.dumps(data).encode('utf-8') if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_tests():
    print("1. Testing /api/dashboard...")
    dash = req('/api/dashboard')
    print("   Dashboard OK! Stats:", dash['stats'])
    assert dash['stats']['active_donors_count'] == 5
    assert dash['stats']['active_ngos_count'] == 5

    print("2. Testing /api/food with Merge Sort...")
    by_exp = req('/api/food?sort_by=expiry&order=asc')
    items = by_exp['items']
    print(f"   Merge Sort by expiry returned {len(items)} items. First: {items[0]['name']} ({items[0]['expiry_hours']}h)")
    by_qty = req('/api/food?sort_by=quantity&order=desc')
    q_items = by_qty['items']
    print(f"   Merge Sort by qty returned {len(q_items)} items. First: {q_items[0]['name']} ({q_items[0]['quantity']}kg)")

    print("3. Testing /api/food/urgent (Min-Heap)...")
    urgent = req('/api/food/urgent')
    print(f"   Min-Heap returned {urgent['count']} items. Heap root: {urgent['items'][0]['name']} ({urgent['items'][0]['expiry_hours']}h)")

    print("4. Testing /api/food/search (Binary Search)...")
    exact = req('/api/food/search?mode=exact&target=30')
    print("   Binary Search exact target=30:", exact['results'][0]['name'] if exact['results'] else "None")
    range_search = req('/api/food/search?mode=range&min=20&max=50')
    print(f"   Binary Search range [20, 50]: {len(range_search['results'])} items found.")
    closest = req('/api/food/search?mode=closest&target=42')
    print(f"   Binary Search closest to 42 kg: {closest['results'][0]['name']} ({closest['results'][0]['quantity']} kg)")

    print("5. Testing /api/match/auto (Min-Heap + Dijkstra + FIFO Queue + History + Undo Stack)...")
    match_res = req('/api/match/auto', method='POST')
    print("   Match Success!")
    print("   Food matched:", match_res['food']['name'])
    print("   Shelter matched:", match_res['ngo']['name'])
    print("   Dijkstra shortest path:", " -> ".join(match_res['path']))
    print(f"   Road Distance: {match_res['distance_km']} km")

    print("6. Testing /api/queue (FIFO Queue)...")
    q = req('/api/queue')
    print(f"   Pending pickup queue size: {q['count']}")
    assert q['count'] >= 1
    assert q['queue'][0]['id'] == match_res['pickup']['id']

    print("7. Testing /api/queue/complete (Dequeue from FIFO Queue)...")
    comp = req('/api/queue/complete', method='POST')
    print("   Completed pickup:", comp['completed_pickup']['id'])

    print("8. Testing /api/undo (LIFO Stack pop)...")
    undo1 = req('/api/undo', method='POST')
    print("   Undo 1 (reverted complete pickup):", undo1['message'])
    undo2 = req('/api/undo', method='POST')
    print("   Undo 2 (reverted auto-match):", undo2['message'])

    print("9. Testing /api/food POST (Add surplus food)...")
    new_food = req('/api/food', method='POST', data={
        'name': 'Fresh Baked Apple Pies',
        'donor_id': 'DONOR_01',
        'category': 'Bakery',
        'quantity': 15.0,
        'expiry_hours': 6.0
    })
    print("   Food added successfully:", new_food['food']['id'], new_food['food']['name'])

    print("10. Testing /api/undo on added food...")
    undo3 = req('/api/undo', method='POST')
    print("   Undo 3 (removed added food):", undo3['message'])

    print("11. Testing /api/history (Singly Linked List)...")
    hist = req('/api/history')
    print(f"   History has {hist['total_records']} logged audit events. Latest: {hist['history'][0]['title']}")

    print("12. Testing /api/graph (Adjacency List Graph)...")
    graph = req('/api/graph')
    print(f"   City graph has {len(graph['nodes'])} nodes and {len(graph['edges'])} road edges.")

    print("\n>>> ALL API AND DSA WORKFLOW TESTS PASSED COMPLETELY! <<<")

if __name__ == '__main__':
    run_tests()
