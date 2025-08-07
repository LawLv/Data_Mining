from collections import defaultdict
from itertools import combinations
from typing import Dict, Set, FrozenSet


def generate_rules(frequent_itemsets: Dict[FrozenSet[int], int], min_conf: float = 0.1) -> Dict[FrozenSet[int], Set[FrozenSet[int]]]:

    rules_dict: Dict[FrozenSet[int], Set[FrozenSet[int]]] = defaultdict(set)

    for itemset in filter(lambda x: len(x) > 1, frequent_itemsets.keys()): # leave those len()=1
        for size in range(1, len(itemset)):
            antecedents = [frozenset(combination) for combination in combinations(itemset, size)]
            for antecedent in antecedents:
                # Calculate the confidence of the rule antecedent -> consequent
                conf = frequent_itemsets[itemset] / frequent_itemsets[antecedent]  

                if conf >= min_conf:
                    consequent = itemset - antecedent
                    rules_dict[antecedent].add(consequent)

    return rules_dict
