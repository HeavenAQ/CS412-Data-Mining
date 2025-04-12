# Submit this file to Gradescope
from typing import Dict, List, Tuple

# from enum import Enum
from collections import Counter, defaultdict
import math

# you may use other Python standard libraries, but not data
# science libraries, such as numpy, scikit-learn, etc.


class Solution:
    def confusion_matrix(
        self, true_labels: List[int], pred_labels: List[int]
    ) -> Dict[Tuple[int, int], int]:
        """Calculate the confusion matrix and return it as a sparse matrix in dictionary form.
        Args:
          true_labels: list of true labels
          pred_labels: list of predicted labels
        Returns:
          A dictionary of (true_label, pred_label): count
        """
        return dict(Counter(zip(true_labels, pred_labels)))

    def jaccard(self, true_labels: List[int], pred_labels: List[int]) -> float:
        """Calculate the Jaccard index.
        Args:
          true_labels: list of true cluster labels
          pred_labels: list of predicted cluster labels
        Returns:
          The Jaccard index. Do NOT round this value.
        """
        n = len(true_labels)
        tp, fn, fp = 0, 0, 0
        for i in range(n):
            for j in range(i + 1, n):
                is_g_equal = true_labels[i] == true_labels[j]
                is_c_equal = pred_labels[i] == pred_labels[j]
                if is_g_equal and is_c_equal:
                    tp += 1
                elif is_g_equal and not is_c_equal:
                    fn += 1
                elif not is_g_equal and is_c_equal:
                    fp += 1
        denominator = tp + fn + fp
        return tp / denominator if denominator else 0

    def nmi(self, true_labels: List[int], pred_labels: List[int]) -> float:
        """Calculate the normalized mutual information.
        Args:
          true_labels: list of true cluster labels
          pred_labels: list of predicted cluster labels
        Returns:
          The normalized mutual information. Do NOT round this value.
        """

        # helper for the entropy function
        def entropy(clusters: dict[int, int], total_data: int) -> float:
            return -sum(
                p * math.log(p) for v in clusters.values() if (p := v / total_data) != 0
            )

        n = len(true_labels)
        matrix = self.confusion_matrix(true_labels, pred_labels)

        # Get clusters and ground truth
        cs = defaultdict(int)
        gs = defaultdict(int)
        for (true, pred), count in matrix.items():
            gs[true] = gs[true] + count
            cs[pred] = cs[pred] + count

        # caluculate the mutual information
        mi = 0
        for (true, pred), count in matrix.items():
            p_ij = count / n
            p_gi = gs[true] / n
            p_ci = cs[pred] / n
            mi += p_ij * math.log(p_ij / (p_gi * p_ci))

        # calculate entropies for c and g
        h_c = entropy(cs, n)
        h_g = entropy(gs, n)
        denominator = math.sqrt(h_c * h_g)
        return mi / denominator if denominator else 0


#
# class Method(Enum):
#     JACCARD = 0
#     NMI = 1
#     CONFUSION = 2
#
#
# def main():
#     with open("../../sample_test_cases/input02.txt") as f:
#         test_case = Method(int(f.readline()))
#         true_labels, pred_labels = zip(
#             *(
#                 map(
#                     lambda x: int(x),
#                     line.split(" ", 1),
#                 )
#                 for line in f.readlines()
#             )
#         )
#         true_labels, pred_labels = list(true_labels), list(pred_labels)
#
#         print("================= True Labels ====================")
#         print(true_labels)
#         print("================= Predicted Labels ====================")
#         print(pred_labels)
#         print("Start Testing...")
#         solution = Solution()
#         match test_case:
#             case Method.JACCARD:
#                 ans = solution.jaccard(true_labels, pred_labels)
#                 print(ans)
#             case Method.NMI:
#                 ans = solution.nmi(true_labels, pred_labels)
#                 print(ans)
#             case Method.CONFUSION:
#                 ans = solution.confusion_matrix(true_labels, pred_labels)
#
#
# if __name__ == "__main__":
#     main()
