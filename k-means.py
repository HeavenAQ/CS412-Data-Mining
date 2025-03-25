import random
import sys
from collections import defaultdict

# CONSTANT
K = 3

# extract data from the file
data: list[tuple] = []
with open("./test.txt") as file:
    while output := file.readline():
        data.append(
            tuple(
                map(
                    lambda x: float(x),
                    output.strip().split(",", 1),
                )
            )
        )


# Helpers
def euclidean(p1, p2):
    return sum((a - b) ** 2 for a, b in zip(p1, p2))


def kmeans_plus_plus_init(data, k):
    centroids = []
    centroids.append(random.choice(data))

    for _ in range(1, k):
        distances = []

        for point in data:
            min_dist_sq = min(euclidean(point, c) for c in centroids)
            distances.append(min_dist_sq)

        # weighted random choice based on squared distances
        total = sum(distances)
        probs = [d / total for d in distances]

        # a random threshold for CMP
        r = random.random()
        cumulative = 0
        for point, prob in zip(data, probs):
            cumulative += prob
            if r < cumulative:
                centroids.append(point)
                break
    return centroids


centroids = kmeans_plus_plus_init(data, K)
sse_record = sys.float_info.max
tmp_records = [0] * len(data)
final_records = [0] * len(data)

# update the data list
while True:
    # cluster it
    cur_list = defaultdict(list)
    for i, datum in enumerate(data):
        cluster = min(
            enumerate(
                map(lambda centroid: euclidean(datum, centroid), centroids),
            ),
            key=lambda x: x[1],
        )[0]
        tmp_records[i] = cluster
        cur_list[cluster].append(datum)

    # update the centroid
    for key, value in cur_list.items():
        avg_x = sum(map(lambda x: x[0], value)) / len(value)
        avg_y = sum(map(lambda x: x[1], value)) / len(value)
        centroids[key] = (avg_x, avg_y)

    # calculate the sse
    sse = 0
    for key, value in cur_list.items():
        for point in value:
            sse += euclidean(point, centroids[key])

    # use sse as threshold to stop the loop
    if sse >= sse_record:
        break
    else:
        sse_record = sse
        for i, record in enumerate(tmp_records):
            final_records[i] = record

with open("clusters.txt", "w") as f:
    for i, record in enumerate(final_records):
        f.write(f"{i} {record}\n")
