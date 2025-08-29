import random

from typing import Dict, List

from .._program import Program
from .._query import Query
from ._pmf import PMF

def choose_code_from_state(ix, prev, opcodes, opcode_weights, reg_codes, reg_weights):
    # Given the local state (ix, prev) we should choose a new opcode.
    if prev == 0:
        mut = "i"
    else:
        ar = Program.arity_of(ix, prev)
        if ar == 0:
            mut = random.choices(["i", "c", "d"], weights=(4.0, 3.0, 1.0))[0]
        elif ar == 1:
            mut = random.choices(["i", "c", "d"], weights=(1.0, 1.0, 1.5))[0]
        else:  # ar == 2
            mut = random.choices(["i", "c", "d"], weights=(4.0, 3.0, 1.0))[0]

    if reg_codes:
        w = opcode_weights + [1.0] if ix == 1 else opcode_weights + [16.0]
        available_opcodes = opcodes + ["<input>"]
    else:
        w = opcode_weights
        available_opcodes = opcodes

    code = random.choices(available_opcodes, w)[0]

    if code == "<input>":
        # Choose a random register
        code = random.choices(reg_codes, reg_weights)[0]

    return mut, code



class ProgramCollection:
    def __init__(self):
        self.programs = []

        self.register_pmf = PMF()
        self.op_pmf = PMF()
        self.op_pmf._pmf = {
            "exp:1":        1.0,
            "gaussian:1":   1.0,
            "inverse:1":    1.0,
            "linear:1":     1.0,
            "log:1":        1.0,
            "sqrt:1":       1.0,
            "squared:1":    1.0,
            "tanh:1":       1.0,
            "add:2":        5.3,
            "gaussian:2":   5.3,
            "multiply:2":   5.3,
        }

    def decay(self):
        self.programs = []

    def update(self, program) -> None:
        self.programs.append(program)

    def update_priors(self, priors, reset):
        if reset:
            self.register_pmf._pmf.update(priors)
        else:
            for key, val in priors:
                self.register_pmf.update(key, val)


    def generate_programs(
        self,
        query: Query,
    ) -> List[Dict]:

        if query.max_complexity == 1:
            # This complexity only allows registers
            functions = []
        elif query.max_complexity < 2:
            # This complexity only allows unary operators and registers
            functions = [fname for fname in query.function_names if ":1" in fname]
        else:
            # This complexity can make use of all operators
            functions = query.function_names

        number_of_programs_to_generate = 60
        permcount = number_of_programs_to_generate // (len(self.programs) + 1)

        reg_weights = self.register_pmf.get(query.inputs)
        opcode_weights = self.op_pmf.get(functions)

        res = []
        for p in self.programs:
            for _ in range(permcount):

                # Determine local state
                ix = random.randint(1, len(p) - 1)
                prev = p[ix]

                # Choose mutation type and code from local state
                mut, code = choose_code_from_state(ix, prev, functions, opcode_weights, query.inputs, reg_weights)

                # Mutate the program
                if mut == "c":
                    newp = p.change(ix, code)
                elif mut == "i":
                    newp = p.insert(ix, [code])
                else:
                    newp = p.delete(ix, code)

                res.append(newp)

        partial_codes = query.partial_codes()
        for _ in range(permcount):
            codes = [
                choose_code_from_state(
                    ix, 0, ixcodes, self.op_pmf.get(ixcodes), ixregs, self.register_pmf.get(ixregs)
                )[1]
                if ixcodes or ixregs
                else choose_code_from_state(ix, 0, functions, opcode_weights, query.inputs, reg_weights)[1]
                for ix, (ixcodes, ixregs) in enumerate(partial_codes)
            ]

            p = Program(codes)
            res.append(p)

        return res
