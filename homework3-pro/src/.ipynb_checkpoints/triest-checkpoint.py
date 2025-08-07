from typing import Tuple, Callable, Set, DefaultDict, FrozenSet
from collections import defaultdict
from scipy.stats import bernoulli
from functools import reduce
import random


def _get_edge(line: str) -> FrozenSet[int]:
    return frozenset([int(vertex) for vertex in line.split()])


class Triest:
    def __init__(self, file: str, M: int):
        """
        file: the path to the file
        M: the size of the memory
        """
        self.file: str = file
        self.M: int = M
        self.S: Set[FrozenSet[int]] = set()
        self.t: int = 0 # num of edges have been handled
        self.tau_vertices: DefaultDict[int, int] = defaultdict(int) # dic recording every node's triangles num
        self.tau: int = 0 # total tri number

    @property
    def xi(self) -> float: # used to correct the estimate
        return max(
            1.0,
            (self.t * (self.t - 1) * (self.t - 2)) / (self.M * (self.M - 1) * (self.M - 2))
        )

    def _sample_edge(self, t: int) -> bool:
        """
        Determines if the new edge can be inserted in memory. 
        edge: the current sample under consideration
        t: the number of observed samples in the stream
        Return true if the new edge can be inserted in the memory, false otherwise
        """
        if t <= self.M:
            return True
        elif bernoulli.rvs(p=self.M / t): 
            # true, accept new edge
            edge_to_remove: FrozenSet[int] = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            self._update_counters(lambda x, y: x - y, edge_to_remove) # update the counter of triangles
            return True
        else:
            return False

    def _update_counters(self, operator: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        Updates the counters related to estimating the number of triangles. The update happens through
        the operator lambda and involves the edge and its neighbours.

        operator: the lambda used to update the counters
        edge: the edge interested in the update
        """
        common_neighbourhood: Set[int] = reduce(lambda a, b: a & b, # 取交集
            [
                {
                    node 
                    for link in self.S if vertex in link # 遍历 s 中与 vertex 相连的边
                    for node in link if node != vertex # 找到与 vertex 相连的另一个节点
                }
                for vertex in edge # 对于新边的两个 vertex
            ]
        )

        for vertex in common_neighbourhood:
            self.tau = operator(self.tau, 1)
            self.tau_vertices[vertex] = operator(self.tau_vertices[vertex], 1)

            for node in edge:
                self.tau_vertices[node] = operator(self.tau_vertices[node], 1)


class TriestBase(Triest):
    """
    The algorithm Triest in the paper from 'L. De Stefani, A. Epasto, M. Riondato, and E. Upfal, TRIÈST: Counting Local  and Global Triangles in Fully-Dynamic Streams with Fixed Memory Size, KDD'16.'
    An estimate of the number of triangles in a graph in a streaming environment.
    """
    def run(self) -> float:  # Return the estimated number of triangles
        with open(self.file, 'r') as f:
            for line in f:
                edge = _get_edge(line)
                self.t += 1
                if self._sample_edge(self.t): # determine if accept the edge
                    self.S.add(edge)
                    self._update_counters(lambda x, y: x + y, edge)
            return self.xi * self.tau


class TriestImproved(Triest):  # Improved Triest
    @property
    def eta(self) -> float:  # New correction factor
        return max(
            1.0,
            ((self.t - 1) * (self.t - 2)) / (self.M * (self.M - 1))
        )

    def _update_counters(self, operator: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        Updates the counters related to estimating the number of triangles. The update happens through
        the operator lambda and involves the edge and its neighbours.

        operator: the lambda used to update the counters
        edge: the edge interested in the update
        """
        common_neighbourhood: Set[int] = reduce(lambda a, b: a & b,
            [
                {
                    node
                    for link in self.S if vertex in link
                    for node in link if node != vertex
                }
                for vertex in edge
            ]
        )

        for vertex in common_neighbourhood:
            self.tau += self.eta  # Mapping of current samples to global quantities
            self.tau_vertices[vertex] += self.eta

            for node in edge:
                self.tau_vertices[node] += self.eta

    def _sample_edge(self, t: int) -> bool:
        """
        Determines if the new edge can be inserted in memory. 
        edge: the current sample under consideration
        t: the number of observed samples in the stream
        Return true if the new edge can be inserted in the memory, false otherwise
        """
        if t <= self.M:
            return True
        elif bernoulli.rvs(p=self.M / t):
            edge_to_remove: FrozenSet[int] = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            return True
        else:
            return False

    def run(self) -> float:
        """
        Return the estimated number of triangles
        """
        with open(self.file, 'r') as f:
            for line in f:
                edge = _get_edge(line)
                self.t += 1
                
                self._update_counters(lambda x, y: x + y, edge) 
                # update the counters first, even if the edge is not chosen, it also contributes to estimation

                if self._sample_edge(self.t):
                    self.S.add(edge)

            return self.tau


