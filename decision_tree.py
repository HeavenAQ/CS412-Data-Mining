import collections
from typing import Counter, Dict, List, Tuple
import math


class Node:
    """
    This class, Node, represents a single node in a decision tree. It is designed to store information about the tree
    structure and the specific split criteria at each node. It is important to note that this class should NOT be
    modified as it is part of the assignment and will be used by the autograder.

    The attributes of the Node class are:
    - split_dim: The dimension/feature along which the node splits the data (-1 by default, indicating uninitialized)
    - split_point: The value used for splitting the data at this node (-1 by default, indicating uninitialized)
    - label: The class label assigned to this node, which is the majority label of the data at this node. If there is a tie,
      the numerically smaller label is assigned (-1 by default, indicating uninitialized)
    - left: The left child node of this node (None by default). Either None or a Node object.
    - right: The right child node of this node (None by default) Either None or a Node object.
    """

    def __init__(self):
        self.split_dim = -1
        self.split_point = -1.0
        self.label = -1
        self.left: Node | None = None
        self.right: Node | None = None


class Solution:
    """
    Example usage of the Node class to build a decision tree using a custom method called split_node():

    # In the fit method, create the root node and call the split_node() method to build the decision tree
      self.root = Node()
      self.split_node(self.root, data, ..., depth=0)

    def split_node(self, node, data, ..., depth):
        # Your implementation to calculate split_dim, split_point, and label for the given node and data
        # ...

        # Assign the calculated values to the node
        node.split_dim = split_dim
        node.split_point = split_point
        node.label = label

        # Recursively call split_node() for the left and right child nodes if the current node is not a leaf node
        # Remember, a leaf node is one that either only has data from one class or one that is at the maximum depth
        if not is_leaf:
            left_child = Node()
            right_child = Node()

            split_node(left_child, left_data, ..., depth+1)
            split_node(right_child, right_data, ..., depth+1)
    """

    def split_node(
        self, node: Node, data: List[List[float]], labels: List[int], depth: int
    ):
        # assign max label
        label_counts = collections.Counter(labels)
        node.label = min(
            k for k, v in label_counts.items() if v == max(label_counts.values())
        )

        # check if the node is leaf
        if len(data) == 0 or depth == 2 or len(label_counts) == 1:
            return

        # compute base entropy
        base_info = self.info([*label_counts.values()], len(labels))

        # search for best split and dim
        max_gain = float("-inf")
        max_dim_split = (0, 0.0)
        for i in range(len(data[0])):
            attr_vals = sorted(set(row[i] for row in data))
            midpoints = [(a + b) / 2 for a, b in zip(attr_vals, attr_vals[1:])]

            cur_best_gain = float("-inf")
            cur_best_mid = 0
            for m in midpoints:
                info_A = self.split_info(data, labels, i, m)
                gain = base_info - info_A
                if gain > cur_best_gain:
                    cur_best_gain, cur_best_mid = gain, m

            if cur_best_gain > max_gain:
                max_gain, max_dim_split = cur_best_gain, (i, cur_best_mid)

        node.split_dim, node.split_point = max_dim_split

        # partition data
        left_data, left_labels, right_data, right_labels = [], [], [], []
        for x, y in zip(data, labels):
            if x[node.split_dim] <= node.split_point:
                left_data.append(x)
                left_labels.append(y)
            else:
                right_data.append(x)
                right_labels.append(y)

        # go to next level
        node.left, node.right = Node(), Node()
        self.split_node(node.left, left_data, left_labels, depth + 1)
        self.split_node(node.right, right_data, right_labels, depth + 1)

    def info(self, train_label_counts: List[int], num_data: int):
        return -sum(
            (
                (p := label_count / num_data) * math.log2(p)
                for label_count in train_label_counts
                if label_count > 0
            )
        )

    def split_info(
        self,
        data: List[List[float]],
        label: List[int],
        split_dim: int,
        split_point: float,
    ) -> float:
        """
        Compute the information needed to classify a dataset if it's split
        with the given splitting dimension and splitting point, i.e. Info_A in the slides.

        Parameters:
        data (List[List]): A nested list representing the dataset.
        label (List): A list containing the class labels for each data point.
        split_dim (int): The dimension/attribute index to split the data on.
        split_point (float): The value at which the data should be split along the given dimension.

        Returns:
        float: The calculated Info_A value for the given split. Do NOT round this value
        """
        left_labels = []
        right_labels = []
        for i, datapoint in enumerate(data):
            if datapoint[split_dim] <= split_point:
                left_labels.append(label[i])
            else:
                right_labels.append(label[i])

        # set up lengths
        N = len(data)
        left_N = len(left_labels)
        right_N = len(right_labels)

        # count the frequencies for each labels
        left_counts = collections.Counter(left_labels)
        right_counts = collections.Counter(right_labels)

        # calculate the info_A
        info_A = 0.0
        if left_N > 0:
            info_A += left_N / N * self.info([*left_counts.values()], left_N)
        if right_N > 0:
            info_A += right_N / N * self.info([*right_counts.values()], right_N)

        return info_A

    def fit(self, train_data: List[List[float]], train_label: List[int]) -> None:
        """
        Fit the decision tree model using the provided training data and labels.

        Parameters:
        train_data (List[List[float]]): A nested list of floating point numbers representing the training data.
        train_label (List[int]): A list of integers representing the class labels for each data point in the training set.

        This method initializes the decision tree model by creating the root node. It then builds the decision tree starting
        from the root node

        It is important to note that for tree structure evaluation, the autograder for this assignment
        first calls this method. It then performs tree traversals starting from the root node in order to check whether
        the tree structure is correct.

        So it is very important to ensure that self.root is assigned correctly to the root node

        It is best to use a different method (such as in the example above) to build the decision tree.
        """
        self.root = Node()
        self.split_node(self.root, train_data, train_label, depth=0)

    def classify(
        self,
        train_data: List[List[float]],
        train_label: List[int],
        test_data: List[List[float]],
    ) -> List[int]:
        """
        Classify the test data using a decision tree model built from the provided training data and labels.
        This method first fits the decision tree model using the provided training data and labels by calling the
        'fit()' method.

        Parameters:
        train_data (List[List[float]]): A nested list of floating point numbers representing the training data.
        train_label (List[int]): A list of integers representing the class labels for each data point in the training set.
        test_data (List[List[float]]): A nested list of floating point numbers representing the test data.

        Returns:
        List[int]: A list of integer predictions, which are the label predictions for the test data after fitting
                   the train data and labels to a decision tree.
        """
        self.fit(train_data, train_label)

        def traverse(node: Node, datapoint: List[float]):
            while node.left and node.right:
                if datapoint[node.split_dim] <= node.split_point:
                    node = node.left
                else:
                    node = node.right
            return node.label

        return [traverse(self.root, datapoint) for datapoint in test_data]

    """
  Students are encouraged to implement as many additional methods as they find helpful in completing
  the assignment. These methods can be implemented either as class methods of the Solution class or as
  global methods, depending on design preferences.

  For instance, one essential method that must be implemented is a method to build out the decision tree recursively.
  """
