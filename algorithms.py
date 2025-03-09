from collections import defaultdict
from heapq import heappop, heappush

def astar(nodes, startnode, target):
    dist = defaultdict(lambda: float('inf'))
    parents = {startnode: None}
    queue = [(0, startnode)]
    dist[startnode] = 0

    while queue:
        c, u = heappop(queue)
        if c != dist[u]:
            continue

        if u == target:
             return reconstruct_path(parents, u)

        neighbors = nodes.getNeighbors(u)
        print(neighbors) 
        for v in neighbors:
            cost = dist[u] + heuristic(u, v)        
            if cost < dist[v]:
                dist[v] = cost
                parents[v] = u
                heappush(queue, (cost, v))

    return []

def heuristic(node1, node2):
    return abs(node1.position.x - node2.position.x) + abs(node1.position.y - node2.position.y)

def reconstruct_path(parents, current):
        path = []
        while current in parents:
            path.append(current)
            current = parents[current]
        path.reverse()
        return path