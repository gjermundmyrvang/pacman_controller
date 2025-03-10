from collections import defaultdict
from heapq import heappop, heappush

def astar(startnode, target):
    startnode.g = 0  
    dist = defaultdict(lambda: float('inf'))
    parents = {startnode: None}
    dist[startnode] = 0
    queue = [(0, startnode)]

    while queue:
        c, u = heappop(queue)
        if c != dist[u]:
            continue

        if u == target:
             return reconstruct_path(parents, startnode, target)

        neighbors = u.getNeighbors()
        for v in neighbors:
            cost = dist[u] + heuristic(u, v)
            if cost < dist[v]:
                dist[v] = cost
                v.g = cost 
                parents[v] = u
                heappush(queue, (cost, v)) 

    return []

def dijkstra_avoid(startnode, target, ghosts):
    dist = defaultdict(lambda: float('inf'))
    parents = {startnode: None}
    dist[startnode] = 0
    queue = [(0, startnode)]

    while queue:
        c, u = heappop(queue)
        if c != dist[u]:
            continue
        if u == target:
             return reconstruct_path(parents, startnode, target)
        neighbors = u.getNeighbors()
        for v in neighbors:
            extra_cost = 1000 if v in ghosts else 0
            cost = dist[u] + extra_cost
            if cost < dist[v]:
                dist[v] = cost
                parents[v] = u
                heappush(queue, (cost, v)) 
    return []

def dijkstra(startnode, target):
    dist = defaultdict(lambda: float('inf'))
    parents = {startnode: None}
    dist[startnode] = 0
    queue = [(0, startnode)]

    while queue:
        c, u = heappop(queue)
        if c != dist[u]:
            continue

        if u == target:
             return reconstruct_path(parents, startnode, target)

        neighbors = u.getNeighbors()
        for v in neighbors:
            cost = dist[u] + 1
            if cost < dist[v]:
                dist[v] = cost
                parents[v] = u
                heappush(queue, (cost, v)) 

    return reconstruct_path(parents, startnode, target)

def heuristic(node1, node2):
    return abs(node1.position.x - node2.position.x) + abs(node1.position.y - node2.position.y)

def reconstruct_path(parents, start, target):
        path = []
        while target != start:
            path.append(target)
            target = parents[target]
        path.append(start)    
        path.reverse()
        return path