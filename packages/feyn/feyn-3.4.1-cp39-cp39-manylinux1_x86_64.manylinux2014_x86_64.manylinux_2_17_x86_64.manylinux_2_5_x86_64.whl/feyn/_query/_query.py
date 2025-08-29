import random
from typing import List, Tuple
from .._program import Program
import os

from lark import Lark, Tree, Token

DIR, _ = os.path.split(__file__)
QUERY_GRAMMAR = os.path.join(DIR, "query_grammar.lark")

PARSER = Lark.open(QUERY_GRAMMAR, start="expr", parser="lalr")

SPECIAL_OPCODES = {
    "register_any": '?',
    "interact1": "func:1",
    "interact2": "func:2",
    "wildcard": '_',
    "exclude": '!',
    # 50-80 are also reserved
}
class Parser:
    @staticmethod
    def _translate_ast(ast) -> str:
        """Translate a node in a lark AST to an opcode."""
        if isinstance(ast, Token):
            term_name = ast.value.strip("\"'")
            return term_name

        dat = ast.data
        special_code = SPECIAL_OPCODES.get(dat)
        if special_code is not None:
            return special_code
        if dat == "expr":
            return "add:2"
        if dat == "term":
            return "multiply:2"

        else:
            dat += ":" + str(len(ast.children))

        return dat

    @staticmethod
    def query_to_codes(output_name: str, user_query: str) -> Tuple[int, List[int]]:
        """Convert a user-written query into the program representation."""
        res_codes = [output_name]
        min_complexity = 0

        ast = PARSER.parse(user_query)

        def _recurse(node):
            nonlocal res_codes, min_complexity
            if isinstance(node, Tree) and node.data == "wildcard":
                wc_codes = [SPECIAL_OPCODES["wildcard"]]
                max_wc_complexity = 30
                wc_terms = set()
                wc_banned = set()

                for child in node.children:
                    if isinstance(child, Tree):
                        wc_codes.append(SPECIAL_OPCODES["exclude"])
                        term_code = Parser._translate_ast(child.children[0])
                        wc_banned.add(term_code)
                        wc_codes.append(term_code)
                    elif child.type in ["SINGLE_ESCAPED_STRING", "DOUBLE_ESCAPED_STRING"]:
                        term_name = child.value.strip("\"'")
                        wc_terms.add(term_name)
                        wc_codes.append(term_name)
                    else:
                        max_wc_complexity = min(int(child.value), max_wc_complexity)

                wc_codes.append(max_wc_complexity)
                res_codes += wc_codes

                min_wc_complexity = max(1, 2 * (len(wc_terms) - 1))
                complexity_diff = min_wc_complexity - max_wc_complexity
                if complexity_diff > 0:
                    raise ValueError(
                        f"\n\nToo much complexity requested in wildcard subtree. Either increase the allowed complexity (currently {max_wc_complexity-50}) or remove {complexity_diff} input(s) from the wildcard."
                    )
                inconsistent = [c for c in wc_terms.intersection(wc_banned)]
                if inconsistent:
                    msg = "Inconsistent required inclusion and exclusion of terminal"
                    if len(inconsistent) >= 2:
                        msg += "s"
                    msg += " " + ", ".join([f"'{t}'" for t in inconsistent]) + "."
                    raise ValueError(msg)
                min_complexity += min_wc_complexity
                return

            min_complexity += 1
            res_codes.append(Parser._translate_ast(node))
            if isinstance(node, Tree):
                nchildren = len(node.children)
                if nchildren:
                    _recurse(node.children[0])
                if nchildren == 2:
                    _recurse(node.children[1])
                if nchildren > 2:
                    _recurse(Tree(node.data, node.children[1:]))

        _recurse(ast)
        return min_complexity, res_codes

class Query:
    def __init__(self, query_string: str, max_complexity, input_names, function_names, output_name):
        self.inputs = input_names
        self.function_names = function_names
        self.output = output_name

        self.max_complexity = max_complexity
        query_complexity, query_codes = Parser.query_to_codes(output_name, query_string)

        if query_complexity > max_complexity:
            raise ValueError(
                f"The complexity of the query, {query_complexity}, is greater than the max_complexity {max_complexity} of this sample_models."
            )

        self.query_codes = query_codes
        self.query_size = len(query_codes)

        self.output_code = query_codes[0]

    def __call__(self, p: Program) -> bool:
        """Match programs p to this query sequence."""

        plen = len(p)
        ixP = 0
        ixQP = 0
        while 1:
            if ixQP >= self.query_size and ixP >= plen:
                return True

            qcode = self.query_codes[ixQP]

            if qcode == "?":
                if not p.arity_at(ixP) == 0:
                    return False
            elif qcode == "func:1":
                if not p.arity_at(ixP) == 1:
                    return False
            elif qcode == "func:2":
                if not p.arity_at(ixP) == 2:
                    return False

            elif qcode == "_":
                offset = self._consume_wildcard(self.query_codes[ixQP:])
                ixQP += offset

                st_end = p.find_end(ixP)
                program_subtree = p._codes[ixP:st_end]
                ixP = st_end - 1
                if len(program_subtree) - 1 > self.n_edges:
                    return False

                subtree_terminals = set(filter(lambda code: Program.arity_of(1, code) == 0, program_subtree))
                if self.must_contain.difference(subtree_terminals):
                    return False
                if self.cant_contain.intersection(subtree_terminals):
                    return False

            elif qcode == "!":
                ixQP += 1
                banned_terminal = self.query_codes[ixQP]
                if not p.arity_at(ixP) == 0:
                    return False
                if p[ixP] == banned_terminal:
                    return False

            else:
                if not qcode == p[ixP]:
                    return False

            ixP += 1
            ixQP += 1

        return True

    def partial_codes(self) -> List:
        """Return a partially filled out code sequence for the QCell to complete.
        The complete program is always expected to match the user query.

        The partially filled out code sequence either has elements (op_codes, reg_codes) or (None, None)."""
        res = []
        ix = 0

        ar1 = [fname for fname in self.function_names if ":1" in fname]
        ar2 = [fname for fname in self.function_names if ":2" in fname]

        while ix < len(self.query_codes):
            code = self.query_codes[ix]

            if code == "?":
                res.append(([], self.inputs))
            elif code == "func:1":
                res.append((ar1, []))
            elif code == "func:2":
                res.append((ar2, []))

            elif code == "_":
                ix += self._consume_wildcard(self.query_codes[ix:])
                if self.must_contain:
                    available_terms = set(random.choices(self.inputs, k=max(len(self.must_contain), 30)))
                    available_terms = list(available_terms.union(self.must_contain).difference(self.cant_contain))
                    available_codes = self.function_names
                else:
                    available_codes, available_terms = None, None

                min_size = 2 * (len(self.must_contain) - 1)
                max_size = min(10, self.n_edges)
                subtree_size = random.randint(min_size, max_size)
                res.extend([(available_codes, available_terms)] * subtree_size)

            elif code == "!":
                ix += 1
                available = self.inputs[:]
                available.remove(self.query_codes[ix])
                res.append(([], available))

            else:
                if ":" not in code:
                    res.append(([code], []))
                else:
                    res.append(([], [code]))

            ix += 1

        return res + [(None, None)] * (Program.SIZE - len(res))

    def _consume_wildcard(self, codes):
        self.must_contain = set()
        self.cant_contain = set()
        ix = 1
        while 1:
            code = codes[ix]
            if isinstance(code, int):
                self.n_edges = code
                break

            if code == "!":
                self.cant_contain.add(codes[ix + 1])
                ix += 2
                continue

            self.must_contain.add(codes[ix])
            ix += 1

        return ix
