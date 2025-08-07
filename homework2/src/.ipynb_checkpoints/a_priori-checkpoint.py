from collections import defaultdict, Counter
from typing import Dict, List, Set, KeysView, FrozenSet
from itertools import combinations
import numpy as np


def read_dataset(file: str) -> List[Set[int]]:
    """
    Read .dat file. Every row is a basket of items.
    Returns the list of the baskets.[{set},{set},{set}...,{set}]
    """
    with open(file, "r") as f:
        baskets: List[Set[int]] = list(
            map(
                lambda basket: {int(item_id) for item_id in basket.split()},
                f.read().splitlines() # make the file into a list splited by rows
            )
        )
    f.close()

    return baskets


def find_frequent_singletons(baskets: List[Set[int]], s: int = 1,) -> Dict[FrozenSet[int], int]:
    """
    Find all the singletons having a support greater than s.
    baskets: the list of all baskets
    s: the threshold
    Return the set of all frequent singletons
    """

    item_to_support = defaultdict(int)

    for basket in baskets:
        for item in basket:
            item_to_support[frozenset([item])] += 1

    print(f'Different items: {len(item_to_support)}')
    print(f'Average support: {np.mean(list(item_to_support.values())):.2f}')

    return dict(filter(
            lambda element: element[1] > s,
            item_to_support.items()
        )
               )


def generate_candidate_item_sets(precedent_item_sets: KeysView[FrozenSet[int]],item_set_length: int) -> Set[FrozenSet[int]]:
    """
    Step k+1: Find the set of candidate (new frequent itemsets), by combining the itemsets found at step k.
    precedent_item_sets: the frequent itemsets found at time k
    item_set_length: the length of the next candidates to be returned
    Return a set of candidate frequent itemsets of length k+1
    """
    return {
        item_set_left | item_set_right
        for item_set_left, item_set_right in combinations(precedent_item_sets, 2)
        if len(item_set_left | item_set_right) == item_set_length
    }


def pick_frequent_item_sets(baskets: List[Set[int]],candidate_item_sets: Set[FrozenSet[int]],item_set_length: int,s: int = 1) -> Dict[FrozenSet[int], int]:
    """
    Find all the itemsets with a support greater than s.
    candidate_item_sets: the set of itemsets candidate
    item_set_length: the length of the itemsets
    s: the threshold
    Return the set of all frequent itemsets
    """
    item_set_to_support = Counter([
            frozenset(item_set)
            for basket in baskets
            for item_set in combinations(basket, item_set_length)
            if frozenset(item_set) in candidate_item_sets
    ])  # 统计候选项集中每个项集的支持度（出现次数）

    return dict(
        filter(
            lambda element: element[1] > s,
            item_set_to_support.items()
        )
    )  # 从支持度字典中挑选出支持度大于阈值的项集


def find_frequent_item_sets(file: str,s: int = 1,) -> Dict[FrozenSet[int], int]:
    """
    Generates the set of frequent itemsets with (support >= s) and (maximum size = maximum_item_set_size).
    s: the minimum support required to consider an itemset frequent
    Return the set of all frequent itemsets, represented as frozensets, mapped to their support
    """

    baskets = read_dataset(file=file)

    # The first frequent itemsets are the frequent singletons
    frequent_item_sets: Dict[FrozenSet[int], int] = find_frequent_singletons(baskets=baskets, s=s,)
    print(f'Number of singletons: {len(frequent_item_sets)}')

    precedent_frequent_item_sets = frequent_item_sets.keys()
    item_set_length = 2
    while len(precedent_frequent_item_sets) > 1:
        print("------------------------------------")
        print("Computing frequent itemsets of length {}...".format(item_set_length))

        candidate_item_sets = generate_candidate_item_sets( # Generate candidate item sets
            precedent_item_sets=precedent_frequent_item_sets,
            item_set_length=item_set_length
        )

        print("{} candidates generated.".format(len(candidate_item_sets)))

        if len(candidate_item_sets) > 0: # find whose support >= s
            new_frequent_item_sets = pick_frequent_item_sets(
                baskets=baskets,
                candidate_item_sets=candidate_item_sets,
                item_set_length=item_set_length,
                s=s
            )

            frequent_item_sets.update(new_frequent_item_sets)
            precedent_frequent_item_sets = new_frequent_item_sets.keys()
            item_set_length += 1

            print(f'Finish. {len(new_frequent_item_sets)} frequent items was/were found.')

    print(f'\nTotally {len(frequent_item_sets)} frequent items were found.')
    print()
    return frequent_item_sets


if __name__ == "__main__":
    print(
        find_frequent_item_sets(
            file='../data/T10I4D100K.dat',
            s=1000
        )
    )
