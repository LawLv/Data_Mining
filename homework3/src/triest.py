from typing import Tuple, Callable, Set, DefaultDict, FrozenSet
from collections import defaultdict
from scipy.stats import bernoulli
from functools import reduce
import random


def parse_edge(line: str) -> FrozenSet[int]:
    """
    Parses a line from the input file and returns a frozenset representing an edge.
    """
    return frozenset([int(node) for node in line.split()])


class TriangleCounter:
    """
    Base class for implementing TRIÈST algorithms to estimate triangles in a graph.
    """

    def __init__(self, file_path: str, max_memory: int, verbose: bool = True):
        """
        Initialize the triangle counter with necessary parameters.

        :param file_path: Path to the input data file.
        :param max_memory: Maximum number of edges to store in memory.
        :param verbose: Whether to print detailed logs during execution.
        """
        self.file_path: str = file_path
        self.max_memory: int = max_memory
        self.verbose: bool = verbose
        self.edge_set: Set[FrozenSet[int]] = set()
        self.edge_count: int = 0
        self.vertex_triangle_map: DefaultDict[int, int] = defaultdict(int)
        self.global_triangle_count: int = 0

    @property
    def scale_factor(self) -> float:
        """
        Computes the scaling factor for triangle estimation.
        """
        return max(
            1.0,
            (self.edge_count * (self.edge_count - 1) * (self.edge_count - 2))
            / (self.max_memory * (self.max_memory - 1) * (self.max_memory - 2))
        )

    def should_store_edge(self, current_count: int) -> bool:
        """
        Determines whether a given edge should be stored in memory.

        :param current_count: Current index of the edge in the stream.
        :return: True if the edge should be stored, False otherwise.
        """
        if current_count <= self.max_memory:
            return True
        if bernoulli.rvs(p=self.max_memory / current_count):
            edge_to_remove: FrozenSet[int] = random.choice(list(self.edge_set))
            self.edge_set.remove(edge_to_remove)
            self.update_triangle_counters(lambda x, y: x - y, edge_to_remove)
            return True
        return False

    def update_triangle_counters(self, operation: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        Updates triangle counts for the edge and its neighbors.

        :param operation: The operation to apply to the counters (e.g., addition or subtraction).
        :param edge: The edge being processed.
        """
        common_neighbors: Set[int] = reduce(
            lambda a, b: a & b,
            [
                {neighbor for edge_pair in self.edge_set if vertex in edge_pair for neighbor in edge_pair if neighbor != vertex}
                for vertex in edge
            ],
        )

        for neighbor in common_neighbors:
            self.global_triangle_count = operation(self.global_triangle_count, 1)
            self.vertex_triangle_map[neighbor] = operation(self.vertex_triangle_map[neighbor], 1)
            for vertex in edge:
                self.vertex_triangle_map[vertex] = operation(self.vertex_triangle_map[vertex], 1)


class BasicTriangleCounter(TriangleCounter):
    """
    Implements the basic TRIÈST algorithm for triangle counting.
    """

    def execute(self) -> float:
        """
        Executes the basic TRIÈST algorithm on the input data.

        :return: Estimated number of triangles.
        """
        if self.verbose:
            print(f"Running the algorithm with memory size = {self.max_memory}.")

        with open(self.file_path, 'r') as data_file:
            if self.verbose:
                print("Reading input data...")

            for line in data_file:
                edge = parse_edge(line)
                self.edge_count += 1

                if self.verbose and self.edge_count % 1000 == 0:
                    print(f"Processed {self.edge_count} edges.")

                if self.should_store_edge(self.edge_count):
                    self.edge_set.add(edge)
                    self.update_triangle_counters(lambda x, y: x + y, edge)

                if self.verbose and self.edge_count % 1000 == 0:
                    print(f"Estimated triangle count: {self.scale_factor * self.global_triangle_count}")

            return self.scale_factor * self.global_triangle_count


class ImprovedTriangleCounter(TriangleCounter):
    """
    Implements the improved TRIÈST algorithm for triangle counting.
    """

    @property
    def adjustment_factor(self) -> float:
        """
        Computes the adjustment factor for improved triangle estimation.
        """
        return max(1.0, ((self.edge_count - 1) * (self.edge_count - 2)) / (self.max_memory * (self.max_memory - 1)))

    def update_triangle_counters(self, operation: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        Updates triangle counts using the improved estimation method.

        :param operation: The operation to apply to the counters.
        :param edge: The edge being processed.
        """
        common_neighbors: Set[int] = reduce(
            lambda a, b: a & b,
            [
                {neighbor for edge_pair in self.edge_set if vertex in edge_pair for neighbor in edge_pair if neighbor != vertex}
                for vertex in edge
            ],
        )

        for neighbor in common_neighbors:
            self.global_triangle_count += self.adjustment_factor
            self.vertex_triangle_map[neighbor] += self.adjustment_factor
            for vertex in edge:
                self.vertex_triangle_map[vertex] += self.adjustment_factor

    def execute(self) -> float:
        """
        Executes the improved TRIÈST algorithm on the input data.

        :return: Estimated number of triangles.
        """
        if self.verbose:
            print(f"Running the algorithm with memory size = {self.max_memory}.")

        with open(self.file_path, 'r') as data_file:
            if self.verbose:
                print("Reading input data...")

            for line in data_file:
                edge = parse_edge(line)
                self.edge_count += 1

                if self.verbose and self.edge_count % 1000 == 0:
                    print(f"Processed {self.edge_count} edges.")

                self.update_triangle_counters(lambda x, y: x + y, edge)

                if self.should_store_edge(self.edge_count):
                    self.edge_set.add(edge)

                if self.verbose and self.edge_count % 1000 == 0:
                    print(f"Estimated triangle count: {self.global_triangle_count}")

            return self.global_triangle_count


if __name__ == "__main__":
    ImprovedTriangleCounter(
        file_path='../data/facebook_combined.txt',
        max_memory=1000,
        verbose=True
    ).execute()
