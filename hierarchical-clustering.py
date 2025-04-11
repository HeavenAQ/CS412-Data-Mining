# Submit this file to Gradescope
from typing import List, Callable
from enum import Enum
import math
# you may use other Python standard libraries, but not data
# science libraries, such as numpy, scikit-learn, etc.


class SimMethod(Enum):
    SINGLE = 0
    COMPLETE = 1
    AVERAGE = 2


class Solution:
    def hclus_single_link(self, X: List[List[float]], K: int) -> List[int]:
        """Single link hierarchical clustering
        Args:
          - X: 2D input data
          - K: the number of output clusters
        Returns:
          A list of integers (range from 0 to K - 1) that represent class labels.
          The number does not matter as long as the clusters are correct.
          For example: [0, 0, 1] is treated the same as [1, 1, 0]"""

        # implement this function
        def cluster_dist(c1: set[int], c2: set[int]) -> float:
            return min(euclidean(X[p1], X[p2]) for p1 in c1 for p2 in c2)

        return self.__hclus(X, K, cluster_dist)

    def hclus_average_link(self, X: List[List[float]], K: int) -> List[int]:
        """Average link hierarchical clustering"""

        # implement this function
        def cluster_dist(c1: set[int], c2: set[int]) -> float:
            dists = [euclidean(X[p1], X[p2]) for p1 in c1 for p2 in c2]
            return sum(dists) / len(dists)

        return self.__hclus(X, K, cluster_dist)

    def hclus_complete_link(self, X: List[List[float]], K: int) -> List[int]:
        """Complete link hierarchical clustering"""

        # implement this function
        def cluster_dist(c1: set[int], c2: set[int]) -> float:
            return max(euclidean(X[p1], X[p2]) for p1 in c1 for p2 in c2)

        return self.__hclus(X, K, cluster_dist)

    def __hclus(
        self,
        X: List[List[float]],
        K: int,
        dist_func: Callable[[set[int], set[int]], float],
    ):
        clusters = [{i} for i in range(len(X))]
        while len(clusters) != K:
            # find the clusters to be merged
            to_merge = (None, None)
            min_dist = math.inf
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    dist = dist_func(clusters[i], clusters[j])
                    if dist < min_dist:
                        min_dist = dist
                        to_merge = (i, j)

            # merge the two clusters
            i, j = to_merge
            if i is None or j is None:
                break
            clusters[i] = clusters[i] | clusters[j]
            del clusters[j]

        # assign the label under the correct index
        result = [0] * len(X)
        for i, cluster in enumerate(clusters):
            for index in cluster:
                result[index] = i
        return result


def euclidean(p1: List[float], p2: List[float]):
    return math.sqrt(sum((coord1 - coord2) ** 2 for coord1, coord2 in zip(p1, p2)))


# def hclus(X: List[List[float]], K: int, M: SimMethod) -> List[int]:
#     print("In hclus: ")
#     solution = Solution()
#     result = []
#     match M:
#         case SimMethod.SINGLE:
#             print("Starting single link...")
#             result = solution.hclus_single_link(X, K)
#         case SimMethod.COMPLETE:
#             print("Starting complete link...")
#             result = solution.hclus_complete_link(X, K)
#         case SimMethod.AVERAGE:
#             print("Starting average link...")
#             result = solution.hclus_average_link(X, K)
#     return result
#
#
# def main():
#     with open("../../sample_test_cases/input03.txt") as f:
#         n, k, m = map(lambda x: int(x), f.readline().split(" "))
#         data = f.readlines()
#         data = list(
#             map(
#                 lambda x: list(
#                     map(
#                         lambda x: float(x),
#                         x.split(" "),
#                     )
#                 ),
#                 data,
#             )
#         )
#         print(f"The number of data points: {n}")
#         print(f"The number of output clusters: {k}")
#         print(f"The similarity measure: {m}")
#         print("================ Data ===================")
#         print(list(data))
#         result = hclus(data, k, SimMethod(m))
#         print("================ Result ===================")
#         for r in result:
#             print(r)
#
#
# if __name__ == "__main__":
#     main()
