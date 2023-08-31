import pygame
import math

import Common

def makeGraph():
    adjGraph = {}
    for node in Common.nodes:
        n = []
        for road in Common.edges:
            if road.start == node:
                n.append(road.end)
        adjGraph.update({node: n})
    
    return adjGraph

def A_Path(start, destination):
    graph = Common.graph
    start.f = start.cost(destination)
    open = [start]
    closed = []

    while len(open) > 0:
        t = open[0]
        for node in open:
            if t.cost(destination) > node.cost(destination):
                t = node
        closed.append(t)
        open.remove(t)
        if t == destination:
            route = [t]
            s = t
            while s is not start:
                route.append(s.parent)
                s = s.parent
            return list(reversed(route))

        else:
            leaves = []
            for ends in graph[t]:
                leaves.append(ends)
            for leaf in leaves:
                if leaf in closed:
                    pass
                elif leaf not in open:
                    open.append(leaf)
                    leaf.parent = t
                    leaf.f = leaf.cost(destination)
                else:
                    if leaf.parent.f > t.f:
                        leaf.parent = t
                        leaf.f = leaf.cost(destination)
