from collections import defaultdict
from itertools import combinations
from typing import Dict, Set, FrozenSet


def generate_rules(frequent_item_sets: Dict[FrozenSet[int], int], c: float = 0.1) -> Dict[FrozenSet[int], Set[FrozenSet[int]]]:
    """
    This function returns all the association rules having support greater than s and confidence greater than c.

    :param frequent_item_sets: the dictionary of all frequent itemsets with their respective support
    :param c: the threshold confidence
    :return: a dictionary linking each left side itemset of the association rule with all the right side itemsets
    """

    association_rules: Dict[FrozenSet[int], Set[FrozenSet[int]]] = defaultdict(set)

    for item_set in filter(lambda x: len(x) > 1, frequent_item_sets.keys()): # leave those len()=1
        for antecedent_length in range(1, len(item_set)): # all possible length of antecedent
            for antecedent in [frozenset(combination) for combination in combinations(item_set, antecedent_length)]:
                confidence = frequent_item_sets[item_set] / frequent_item_sets[antecedent] # 这个物品集合在所有交易中出现的次数

                if confidence >= c:
                    consequent = item_set - antecedent
                    association_rules[antecedent].add(consequent)

    return association_rules


if __name__ == "__main__":
    print(
        generate_rules(
            {
                frozenset((0,)): 10,
                frozenset((1,)): 10,
                frozenset((0, 1)): 10
            },
            0.1
        )
    )
