from typing import List
from feyn import Model
from feyn._program import Program
from feyn._query import Parser


def get_identity_model(inputs=["x"], output="y") -> Model:
    # Returns a model that predicts it's input, but scales it down and up internally
    program = Program([output, inputs[0]], qid=1)
    model = program.to_model()
    assert model is not None

    model[0].params.update({"scale": 1, "w": 2.0, "bias": +1})
    model[1].params.update({"scale": 1, "w": 0.5, "bias": -0.5})
    return model


def get_unary_model(inputs=["x"], output="y", fname="exp:1", stypes={}) -> Model:
    program = Program([output, fname, inputs[0]], qid=1)
    model = program.to_model(stypes)
    assert model is not None

    return model


def get_simple_binary_model(inputs, output, stypes={}) -> Model:
    program = Program([output, "add:2", inputs[0], inputs[1]], qid=1)
    model = program.to_model(stypes)
    assert model is not None

    return model


def get_complicated_binary_model(inputs, output, fname, stypes={}) -> Model:
    program = Program([output, "add:2", fname, inputs[0], inputs[1]], qid=1)
    model = program.to_model(stypes)
    assert model is not None

    return model


def get_ternary_model(inputs, output, stypes={}) -> Model:
    program = Program(
        [output, "add:2", "gaussian:2", inputs[0], inputs[1], inputs[2]], qid=1
    )
    model = program.to_model(stypes)
    assert model is not None

    return model


def get_quaternary_model(inputs, output, stypes={}) -> Model:
    program = Program(
        [
            output,
            "add:2",
            "multiply:2",
            "multiply:2",
            inputs[0],
            inputs[1],
            inputs[2],
            inputs[3],
        ],
        qid=1,
    )
    model = program.to_model(stypes)
    assert model is not None

    return model


def get_n_unique_models(n: int) -> List[Model]:
    models: List[Model] = []
    for i in range(n):
        codes = ["y", "add:2", "a", f"f{i}"]

        program = Program(codes, qid=1)
        model = program.to_model()
        assert model is not None

        models.append(model)

    return models


def get_fixed_model() -> Model:
    """
    Used in test_shap and test_importance_table.
    They expect specific states for the registers to be able to test against fixed shap values.
    """
    model = get_simple_binary_model(["x", "y"], "z")

    model[0].params.update(
        {"scale": 1.7049912214279175, "w": 0.6332976222038269, "bias": 0.0}
    )
    model[2].params.update(
        {"scale": 1.0, "w": 0.9261354804039001, "bias": 0.18130099773406982}
    )
    model[3].params.update(
        {"scale": 1.0, "w": 2.7783772945404053, "bias": -0.18129898607730865}
    )
    return model


def get_specific_model(inputs: List[str], output: str, equation: str) -> Model:
    """Auxiliary function for generating a model by an equation using the query language"""

    program = Program(Parser.query_to_codes(output, equation)[1], -1)
    model = program.to_model()
    assert model is not None

    return model
