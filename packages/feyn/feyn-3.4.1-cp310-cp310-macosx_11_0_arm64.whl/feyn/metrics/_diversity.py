from typing import Dict, List, Tuple
import numpy as np
from feyn._model import Model


def levenshtein_distance(m1: Model, m2: Model) -> int:
    """Simple levenshtein distance implementation. Not taking into account commutativity of binary operators.
    Source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    """

    p1 = m1._program[:len(m1._program)]
    p2 = m2._program[:len(m2._program)]

    if len(p1) < len(p2):
        return levenshtein_distance(m2, m1)
    if len(p2) == 0:
        return len(p1)

    previous_row = range(len(p2) + 1)
    for i, c1 in enumerate(p1):
        current_row = [i + 1]
        for j, c2 in enumerate(p2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def tree_edit_distance(m1: Model, m2: Model) -> int:
    """Tree edit distance algorithm [Zhang and Shasha 1989].
    The cost of insertions, deletions and substitution edit operations are set to 1."""

    def _model_to_tree_dict(m: Model) -> Dict[int, List[int]]:
        l = len(m)

        tree_dict = {}
        for elem in reversed(m):
            ix = l - elem._ix
            children = [l - cix for cix in elem.children]
            tree_dict[ix] = children

        return tree_dict

    def _post_order(
        tree_dict: Dict[int, List[int]],
        node: int,
        result_dict: Dict[int, int],
        counter: int,
    ) -> Tuple[Dict[int, int], int]:
        for child_node in tree_dict[node]:
            result_dict, counter = _post_order(
                tree_dict, child_node, result_dict, counter
            )
        result_dict[node] = counter
        counter += 1
        return result_dict, counter

    def _get_left_most_leaf(node: int, tree_dict: Dict[int, List[int]]) -> int:
        subtrees = tree_dict.get(node, [])
        if len(subtrees) == 0:
            return node
        left_child = subtrees[0]
        return _get_left_most_leaf(left_child, tree_dict)

    def _compute_left_most_leaf_dict(tree_dict: Dict[int, List[int]]) -> Dict[int, int]:
        """Compute dictionary mapping nodes to the left most leaf descendant"""
        return {node: _get_left_most_leaf(node, tree_dict) for node in tree_dict.keys()}

    def _keyroot_predicate(node: int, tree_dict: Dict[int, List[int]], l: Dict[int, int]) -> bool:
        """Predicate for a node being a key root in a given tree"""
        left_most_leaf = l[node]
        all_nodes_with_left_most_leaf = [
            n for n in tree_dict.keys() if left_most_leaf == l[n]
        ]
        return all(node >= n for n in all_nodes_with_left_most_leaf)

    def _compute_keyroots(tree_dict: Dict[int, List[int]], l: Dict[int, int]) -> List[int]:
        nodes = tree_dict.keys()
        keyroots = [node for node in nodes if _keyroot_predicate(node, tree_dict, l)]
        return keyroots

    def _dist_function(i: int, j: int, node_to_opcode1: Dict[int, int], node_to_opcode2: Dict[int, int]) -> int:
        if node_to_opcode1[i] == node_to_opcode2[j]:
            return 0
        else:
            return 1

    def _compute_treedist(
        t1: Dict[int, List[int]],
        t2: Dict[int, List[int]],
        i: int, j: int,
        l1: Dict[int, int],
        l2: Dict[int, int],
        node_to_opcode1: Dict[int, int],
        node_to_opcode2: Dict[int, int]
    ) -> None:
        """Updates a global tree distance table during execution"""

        t1_mapping_dict, c1 = _post_order(t1, i, {}, 1)
        t2_mapping_dict, c2 = _post_order(t2, j, {}, 1)
        t1_mapping_dict = {v: k for k, v in t1_mapping_dict.items()}
        t2_mapping_dict = {v: k for k, v in t2_mapping_dict.items()}

        forestdist = np.zeros((c1, c2), dtype=int)

        for x in range(1, forestdist.shape[0]):
            forestdist[x, 0] = forestdist[x - 1, 0] + 1
        for y in range(1, forestdist.shape[1]):
            forestdist[0, y] = forestdist[0, y - 1] + 1

        for x in range(1, forestdist.shape[0]):
            for y in range(1, forestdist.shape[1]):
                if (
                    l1.get(t1_mapping_dict[x], -1) == l1[i]
                    and l2.get(t2_mapping_dict[y], -1) == l2[j]
                ):
                    # Comparison between two trees
                    forestdist[x, y] = min(
                        forestdist[x - 1, y] + 1,
                        forestdist[x, y - 1] + 1,
                        forestdist[x - 1, y - 1]
                        + _dist_function(
                            t1_mapping_dict[x],
                            t2_mapping_dict[y],
                            node_to_opcode1,
                            node_to_opcode2,
                        ),
                    )
                    treedist[
                        t1_mapping_dict[x] - 1, t2_mapping_dict[y] - 1
                    ] = forestdist[x, y]
                else:
                    forestdist[x, y] = min(
                        forestdist[x - 1, y] + 1,
                        forestdist[x, y - 1] + 1,
                        forestdist[x - 1, y - 1]
                        + treedist[t1_mapping_dict[x] - 1, t2_mapping_dict[y] - 1],
                    )

    def _convert_models_to_right_graph_format(m1: Model, m2: Model):
        """The algorithm expects a post order ordering of the nodes and that the ordering is 1-indexed (i.e. the first node is number 1 and not 0)"""

        m1_program_length = len(m1._program)
        m2_program_length = len(m2._program)

        ### Build tree dictionary
        # Convert models to graph dictionary format
        t1 = _model_to_tree_dict(m1)
        t2 = _model_to_tree_dict(m2)
        # Compute post ordering
        t1_mapping_dict_outer, _ = _post_order(t1, m1_program_length, {}, 1)
        t2_mapping_dict_outer, _ = _post_order(t2, m2_program_length, {}, 1)
        # Change tree dictionary to use post ordering of nodes as labels
        t1 = {
            t1_mapping_dict_outer[key]: [t1_mapping_dict_outer[child_node] for child_node in subtrees]
            for key, subtrees in t1.items()
        }
        t2 = {
            t2_mapping_dict_outer[key]: [t2_mapping_dict_outer[child_node] for child_node in subtrees]
            for key, subtrees in t2.items()
        }

        ### Build map of node label to program opcode
        m1_relevant_program_part_reversed_order = list(reversed(m1._program[:m1_program_length]))
        m2_relevant_program_part_reversed_order = list(reversed(m2._program[:m2_program_length]))
        node_to_opcode1 = {t1_mapping_dict_outer[idx + 1]: opcode for idx, opcode in enumerate(m1_relevant_program_part_reversed_order)}
        node_to_opcode2 = {t2_mapping_dict_outer[idx + 1]: opcode for idx, opcode in enumerate(m2_relevant_program_part_reversed_order)}
        node_to_opcode1[m1_program_length] = 0 # Assign opcode for output node
        node_to_opcode2[m2_program_length] = 0

        return t1, t2, node_to_opcode1, node_to_opcode2


    # Compute auxiliary look-up tables and lists
    t1, t2, node_to_opcode1, node_to_opcode2 = _convert_models_to_right_graph_format(m1, m2)
    l1 = _compute_left_most_leaf_dict(t1)
    l2 = _compute_left_most_leaf_dict(t2)
    t1_keyroots = _compute_keyroots(t1, l1)
    t2_keyroots = _compute_keyroots(t2, l2)

    # Compute tree distance table
    treedist = np.zeros((len(t1.keys()), len(t2.keys())), dtype=int)
    for i in t1_keyroots:
        for j in t2_keyroots:
            _compute_treedist(t1, t2, i, j, l1, l2, node_to_opcode1, node_to_opcode2)

    # The tree distance between the full trees are at the lower right corner of the matrix
    return treedist[-1, -1]
