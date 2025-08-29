from collections import Counter

from _qepler import QCell
from .._query import Query

class BaseAlgorithm:
    QLCELL_COUNT = 25

    def __init__(self):
        self.qcells = [QCell() for _ in range(BaseAlgorithm.QLCELL_COUNT)]

    def update(self, models):
        for qcell in self.qcells:
            qcell.decay()

        qid_counter = Counter()

        for m in models:
            qid = m._program.qid

            if qid_counter[qid] >= 6:
                continue

            self.qcells[qid].update(m._program)
            qid_counter[qid] += 1

    def update_priors(self, priors, reset):
        for qcell in self.qcells:
            qcell.update_priors(priors, reset)

    def generate_programs(self, query):
        res = []
        for qid, qcell in enumerate(self.qcells):
            programs = qcell.generate_programs(query)

            for p in programs:
                plen = len(p)
                if not plen:
                    continue
                if plen <= query.max_complexity + 1 and query(p):
                    p.qid = qid
                    res.append(p)

        return res
