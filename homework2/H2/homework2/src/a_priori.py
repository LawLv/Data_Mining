from collections import defaultdict, Counter
from typing import Dict, List, Set, KeysView, FrozenSet
from itertools import combinations
import numpy as np


def load_dataset(filename: str) -> List[Set[int]]:
    """
    Read .dat file. Every row is a basket of items.
    Returns the list of the baskets.[{set},{set},{set}...,{set}]
    """
    with open(filename, "r") as file_obj:
        baskets: List[Set[int]] = [
            {int(item) for item in line.split()}
            for line in file_obj.read().splitlines()  # make the file into a list split by rows
        ]
    return baskets


def get_frequent_singletons(baskets: List[Set[int]], min_support: int = 1) -> Dict[FrozenSet[int], int]:
    """
    Find all the singletons having a support greater than min_support.
    baskets: the list of all baskets
    min_support: the threshold
    Return the set of all frequent singletons
    """

    item_support_count = defaultdict(int)

    for basket in baskets:
        for item in basket:
            item_support_count[frozenset([item])] += 1

    print(f'Total unique items: {len(item_support_count)}')
    print(f'Average support: {np.mean(list(item_support_count.values())):.2f}')

    return {
        item_set: support
        for item_set, support in item_support_count.items()
        if support > min_support
    }


def create_candidate_itemsets(previous_itemsets: KeysView[FrozenSet[int]], set_size: int) -> Set[FrozenSet[int]]:
    """
    Step k+1: Find the set of candidate (new frequent itemsets), by combining the itemsets found at step k.
    previous_itemsets: the frequent itemsets found at time k
    set_size: the length of the next candidates to be returned
    Return a set of candidate frequent itemsets of length k+1
    """
    return {
        item_set1.union(item_set2)
        for item_set1, item_set2 in combinations(previous_itemsets, 2)
        if len(item_set1.union(item_set2)) == set_size
    }


def filter_frequent_itemsets(baskets: List[Set[int]], candidate_sets: Set[FrozenSet[int]], set_size: int, min_support: int = 1) -> Dict[FrozenSet[int], int]:
    """
    Find all the itemsets with a support greater than min_support.
    candidate_sets: the set of itemsets candidate
    set_size: the length of the itemsets
    min_support: the threshold
    Return the set of all frequent itemsets
    """
    candidate_support_count = Counter(
        frozenset(items)
        for basket in baskets
        for items in combinations(basket, set_size)
        if frozenset(items) in candidate_sets
    )  # 统计候选项集中每个项集的支持度（出现次数）

    return {
        item_set: count
        for item_set, count in candidate_support_count.items()
        if count > min_support
    }  # 从支持度字典中挑选出支持度大于阈值的项集


def find_frequent_itemsets(filename: str, min_support: int = 1) -> Dict[FrozenSet[int], int]:
    """
    Generates the set of frequent itemsets with (support >= min_support) and (maximum size = maximum_item_set_size).
    min_support: the minimum support required to consider an itemset frequent
    Return the set of all frequent itemsets, represented as frozensets, mapped to their support
    """

    baskets = load_dataset(filename=filename)

    # The first frequent itemsets are the frequent singletons
    frequent_itemsets: Dict[FrozenSet[int], int] = get_frequent_singletons(baskets=baskets, min_support=min_support)
    print(f'Number of singletons: {len(frequent_itemsets)}')

    previous_itemsets = frequent_itemsets.keys()
    set_size = 2
    while len(previous_itemsets) > 1:
        print("------------------------------------")
        print("Computing frequent itemsets of length {}...".format(set_size))

        candidate_sets = create_candidate_itemsets(  # Generate candidate item sets
            previous_itemsets=previous_itemsets,
            set_size=set_size
        )

        print("{} candidates generated.".format(len(candidate_sets)))

        if candidate_sets:  # find whose support >= min_support
            new_frequent_itemsets = filter_frequent_itemsets(
                baskets=baskets,
                candidate_sets=candidate_sets,
                set_size=set_size,
                min_support=min_support
            )

            frequent_itemsets.update(new_frequent_itemsets)
            previous_itemsets = new_frequent_itemsets.keys()
            set_size += 1

            print(f'Finish. {len(new_frequent_itemsets)} frequent itemsets are found.')

    print(f'\nIn total {len(frequent_itemsets)} frequent itemsets are found.')
    print()
    return frequent_itemsets


if __name__ == "__main__":
    result = discover_frequent_itemsets(filename='../data/T10I4D100K.dat', min_support=1000)
    print(result)
