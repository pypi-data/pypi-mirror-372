
class PMF:
    WDEFAULT = 1.0

    def __init__(self):
        self._pmf = {}

    def get(self, keys):
        return [self._pmf.get(op, PMF.WDEFAULT) for op in keys]

    def set(self, key, val):
        self._pmf[key] = val

    def update(self, key, val):
        newval = self._pmf.get(key, PMF.WDEFAULT) * val
        self._pmf[key] = newval
