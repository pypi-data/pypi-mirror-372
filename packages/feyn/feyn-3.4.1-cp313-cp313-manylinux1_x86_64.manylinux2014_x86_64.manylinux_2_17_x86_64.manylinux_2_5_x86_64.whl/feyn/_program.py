from typing import List, Dict
import numpy as np
import feyn

class Program:
    SIZE = 32

    def __init__(self, codes: List[int], qid: int=0):
        ncodes = len(codes)

        if ncodes < 2:
            raise ValueError("Programs must contain at least an output and an input.")

        self._codes = list(codes)
        self.data = {}
        self.qid = qid

        self.tags = [] # For use by Algo June 2022 algo experiment
        self.quality = np.inf # For use by Algo June 2022 experiment

    def __iter__(self):
        return iter(self._codes[0:len(self)])

    def __getitem__(self, ix: int):
        if type(ix) == int:
            return self._codes[ix]
        
        # Fall back to converting self to a list and use indexer on that
        return list(self)[ix]

    def canonize(self, ix: int):
        """Order the children of a binary at ix after the child opcodes"""
        if self.arity_at(ix) != 2:
            return

        child1 = ix + 1
        child2 = self.find_end(child1)
        if self._codes[child1] <= self._codes[child2]:
            return

        end2 = self.find_end(child2)
        st1 = self._codes[child1:child2]
        st2 = self._codes[child2:end2]
        self._codes = self._codes[:child1] + st2 + st1 + self._codes[end2:]

    def change(self, ix: int, code: str) -> "Program":
        p = Program(self._codes)
        p._codes[ix] = code
        return p

    def insert(self, ix: int, code_seq: List[str]) -> "Program":
        p = Program(self._codes[:ix] + code_seq + self._codes[ix : ])
        return p

    def delete(self, ix: int, replacement: str) -> "Program":
        # The replacement is not used. It is appended to the tail to ensure
        # that the program stays the same length.
        p = Program(self._codes[:ix] + self._codes[ix + 1 :] + [replacement])
        return p

    def concat(self, ar2_code, other):
        codes = self._codes[0:1] + [ar2_code] + self._codes[1:] + other._codes[1:]
        return Program(codes)

    def __len__(self):
        return self.find_end(0)

    def arity_at(self, ix: int) -> int:
        return self.arity_of(ix, self._codes[ix])

    def depth_at(self, ix: int) -> int:
        d = 0
        while True:
            if ix == 0:
                return d
            ix = self.find_parent(ix)
            d += 1

    def find_end(self, ix: int) -> int:
        l = 1
        while True:
            if ix >= Program.SIZE:
                # Invalid program
                return 0

            a = self.arity_at(ix)
            l += a - 1
            ix += 1

            if l == 0:
                return ix

    def find_parent(self, ix: int) -> int:
        """Find the parent of the opcode at ix."""
        depths = self.depths()
        code_depth = depths[ix]
        while ix > 0:
            ix -= 1
            d = depths[ix]
            if d < code_depth:
                break
        return ix

    def depths(self) -> List[int]:
        """Get the depths of each element in the program."""
        res = [-1] * len(self)

        # By convention the root of the program is at depth 1.
        # This leaves space for an output node at depth 0
        res[0] = 0
        for ix, _ in enumerate(self):
            arity = self.arity_at(ix)
            d = res[ix]
            if arity >= 1:
                res[ix+1] = d+1
            if arity == 2:
                c2 = self.find_end(ix+1)
                res[c2] = d+1
        return res

    def copy(self) -> "Program":
        copy = Program(self._codes[:], self.qid)
        copy.data = self.data.copy()

        return copy

    def __hash__(self):
        # Convert the codes anctually in use to a tuple
        t = tuple([self.qid] + self._codes[0 : len(self)])

        # Use buildin hash for tuples
        return hash(t)


    def __repr__(self):
        return "<P " + repr(self._codes) + ">"

    @staticmethod
    def from_json(json):
        # TODO: The stypes {} below was not serialized on save, and is thus wrong. But
        # this should be transient, as I (CW) am working to phase out the program object entirely
        p = Program(json["codes"], qid=json["qid"])
        p.data = json["data"]
        return p

    def to_json(self):
        return {"codes": self._codes, "data": self.data, "qid": self.qid}

    @staticmethod
    def arity_of(ix: int, code: str):
        if ix == 0:
            return 1

        if ":" in code:
            return int(code.split(":")[1])

        return 0

        
    def to_model(self, stypes:Dict[str,str]={}, params:Dict=None):
        l = len(self)
        if l < 2:
            # TODO: Why not raise an exception?
            # Invalid program
            return None

        fnames = []

        output_name = self[0]

        for ix in range(l):
            if ix == 0:
                stype = stypes.get(output_name, "f")
                if stype in ("b"):  # Classifier?
                    fnames.append("out-lr:1")
                else:
                    fnames.append("out-linear:1")
                continue

            code = self[ix]
            arity = self.arity_at(ix)

            if arity == 0:
                stype = stypes.get(code, "f")
                if stype in ["c", "cat", "categorical"]:
                    fnames.append("in-cat:0")
                else:
                    fnames.append("in-linear:0")
            else:
                fnames.append(code)

        return feyn.Model(self, fnames, params)
