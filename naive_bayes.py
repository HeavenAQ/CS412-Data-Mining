# Submit this file to Gradescope
import math
from typing import Dict, List, Tuple
# You may use any built-in standard Python libraries
# You may NOT use any non-standard Python libraries such as numpy, scikit-learn, etc.

num_C = 7  # Represents the total number of classes


class Solution:
    def get_class_count(self, Y_train: List[int]) -> List[int]:
        # count samples in classes
        class_counts = [0] * num_C
        for label in Y_train:
            class_counts[label - 1] += 1
        return class_counts

    def prior(self, X_train: List[List[int]], Y_train: List[int]) -> List[float]:
        """Calculate the prior probabilities of each class
        Args:
          X_train: Row i represents the i-th training datapoint
          Y_train: The i-th integer represents the class label for the i-th training datapoint
        Returns:
          A list of length num_C where num_C is the number of classes in the dataset
        """
        class_counts = self.get_class_count(Y_train)
        N = len(Y_train)
        return [(count + 0.1) / (N + 0.1 * num_C) for count in class_counts]

    def label(
        self, X_train: List[List[int]], Y_train: List[int], X_test: List[List[int]]
    ) -> List[int]:
        """Calculate the classification labels for each test datapoint
        Args:
          X_train: Row i represents the i-th training datapoint
          Y_train: The i-th integer represents the class label for the i-th training datapoint
          X_test: Row i represents the i-th testing datapoint
        Returns:
          A list of length M where M is the number of datapoints in the test set
        """
        # calculate the counts of attributes
        attr_counts = [{} for _ in range(len(X_train[0]))]
        possible_values = [set() for i in range(len(X_train[0]))]
        for label, datapoint in zip(Y_train, X_train):
            for i, attr in enumerate(datapoint):
                # the key for the dict
                key = (label, attr)

                # for counting the frequencies of x_i given y
                attr_counts[i][key] = attr_counts[i].get(key, 0) + 1

                # for counting possible values
                possible_values[i].add(attr)

        # calculate the conditional probabilities of x_i given y
        class_counts = self.get_class_count(Y_train)
        for i, attr_count in enumerate(attr_counts):
            # iterate through the counting dicts and calculate the probabilities
            for (label, attr), count in attr_count.items():
                attr_count[label, attr] = (count + 0.1) / (
                    class_counts[label - 1] + 0.1 * len(possible_values[i])
                )

        # calculate the result for the test set
        results = []
        priors = self.prior(X_train, Y_train)
        for datapoint in X_test:
            best_prob = float("-inf")
            best_label = -1

            # iterate over all the labels to test out all the x give y (label)
            for label in range(1, num_C + 1):
                prob = priors[label - 1]
                # iterate over all the attributes
                for i, attr in enumerate(datapoint):
                    attr_count = attr_counts[i]
                    prob *= attr_count.get(
                        (label, attr),
                        # in case there the attr-label comb is unseen before
                        0.1 / (class_counts[label - 1] + 0.1 * len(possible_values[i])),
                    )

                # update it to the best possible label
                if prob > best_prob:
                    best_prob = prob
                    best_label = label
            results.append(best_label)

        return results
