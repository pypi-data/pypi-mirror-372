import os
import sys
import feyn

# from feyn import QLattice


def test_update():
    good = 0
    simple = 0
    runs = 30
    max_complexity = 10
    for _ in range(runs):
        lt = feyn.QLattice()

        registers = ["age", "smoker", "insurable", "a", "b", "c", "d"]

        models = lt.sample_models(
            registers, "insurable", max_complexity=max_complexity, kind="classifier"
        )

        the_model = None
        for m in models:
            if len(m) > 5 and m.edge_count > 8:
                the_model = m
                break

        if the_model:
            lt.update(the_model)
            new_models = lt.sample_models(
                registers, "insurable", max_complexity=max_complexity, kind="classifier"
            )

            if the_model in new_models:
                good += 1
                print("+", end="")
            else:
                print("-", end="")
        else:
            print("s", end="")
            simple += 1
        sys.stdout.flush()

    print("\nGood %i, Simple: %i, Bad: %i" % (good, simple, runs - good - simple))


test_update()
