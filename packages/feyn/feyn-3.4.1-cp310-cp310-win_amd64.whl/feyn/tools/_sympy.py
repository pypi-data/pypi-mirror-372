import math
from typing import Any, Union, Dict
from feyn import Model
from pandas import Series, DataFrame


def sympify_element(elm, symbolic_lr=False, symbolic_cat=True, include_weights=True):
    import sympy

    fmt = lambda s: f"{s:.{15}e}"

    if elm.fname == "in-linear:0":
        name = sympy.Symbol(get_sanitized_name(elm.name))
        w, b, scale_offset = 1, 0, 0
        if include_weights:
            scale_offset = sympy.sympify(f"{fmt(elm.params['scale_offset'])}")
            w = sympy.sympify(f"{fmt(elm.params['scale'])} * {fmt(elm.params['w'])}")
            b = sympy.sympify(f"{fmt(elm.params['bias'])}")
        return (name - scale_offset) * w + b
    elif elm.fname == "in-cat:0":
        b = 0
        if include_weights:
            b = sympy.sympify(f"{fmt(elm.params['bias'])}")

        if not symbolic_cat:
            cats = elm.params["categories"]
            input_name = get_sanitized_name(elm.name)
            sym_tuples = [
                (sympy.Symbol(f"{input_name}_{cat_name}"), weight)
                for cat_name, weight in cats
            ]
            expr = b
            for sym, w in sym_tuples:
                expr = expr + sym * w

            return expr

        name = sympy.Symbol(_get_symbolic_category(elm))
        return name + b
    elif elm.fname == "multiply:2":
        s = "__x0__ * __x1__"
    elif elm.fname == "add:2":
        s = "__x0__ + __x1__"
    elif elm.fname == "tanh:1":
        s = "tanh(__x0__)"
    elif elm.fname == "inverse:1":
        s = "1/__x0__"
    elif elm.fname == "log:1":
        s = "log(__x0__)"
    elif elm.fname == "exp:1":
        s = "exp(__x0__)"
    elif elm.fname == "sqrt:1":
        s = "sqrt(__x0__)"
    elif elm.fname == "squared:1":
        s = "__x0__**2"
    elif elm.fname == "gaussian:2":
        if include_weights:
            s = "exp(-(__x0__**2 / .5 +__x1__**2 / .5))"
        else:
            s = "exp(-(__x0__**2 +__x1__**2))"
    elif elm.fname == "gaussian:1":
        if include_weights:
            s = "exp(-(__x0__**2 / .5))"
        else:
            s = "exp(-(__x0__**2))"
    elif elm.fname == "linear:1" and elm.name == "":
        s = "__x0__"
        if include_weights:
            s = f"{fmt(elm.params['w'])} * {s} + {fmt(elm.params['bias'])}"
    elif elm.fname == "out-linear:1":
        s = "__x0__"
        if include_weights:
            s = f"{fmt(elm.params['scale'])} * ({fmt(elm.params['w'])} * {s} + {fmt(elm.params['bias'])})"
    elif elm.fname == "out-lr:1":
        output = "__x0__"
        if include_weights:
            output = f"{fmt(elm.params['w'])} * {output} + {fmt(elm.params['bias'])}"
        if symbolic_lr:
            s = f"1/(1+exp(-({output})))"
        else:
            s = f"logreg({output})"
    else:
        raise ValueError("Unsupported %s" % elm.fname)

    return sympy.sympify(s)


def get_sanitized_name(name):
    illegal_characters = ["_"]
    sanitized = name
    for char in illegal_characters:
        sanitized = sanitized.replace(char, "")

    return sanitized


def _get_symbolic_category(elm):
    cnt = 0
    name = get_sanitized_name(elm.name)
    for i_name in elm._model.names[1:]:
        if get_sanitized_name(i_name) == name:
            cnt = cnt + 1

    if cnt > 1:
        return f"{name}_{elm._ix}cat"
    else:
        return f"{name}_cat"


def _signif(x, digits):
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)


def _round_expression(expr, digits):
    import sympy

    for a in sympy.preorder_traversal(expr):
        if isinstance(a, sympy.Float):
            expr = expr.subs(a, _signif(a, digits))

    return expr


def sympify_model(
    m: Model, signif: int = 6, symbolic_lr: bool = False, symbolic_cat: bool = True, include_weights: bool = True
) -> Any:
    """Convert a feyn Model to a sympy expression.

    Arguments:
        m {feyn.Model} -- the Model to convert

    Keyword Arguments:
        signif {int} -- The number of significant digits to use for weights and biases in the converted expression (default: {6})
        symbolic_lr {bool} -- Whether to replace the logistic function with a symbol (logreg) (default: {False})
        symbolic_cat {bool} -- Whether to use symbols to represent categorical inputs, or expand their values into the expression (default: {True})
        include_weights {bool} -- Whether to include weights and biases in the expression, or return just the symbolic form (default: {True})

    Returns:
        Any -- A sympy expression for the Model.
    """
    exprs = [
        sympify_element(
            elm,
            symbolic_lr=symbolic_lr,
            symbolic_cat=symbolic_cat,
            include_weights=include_weights,
        )
        for elm in m
    ]

    for elm in reversed(list(m)):
        if elm.arity > 0:
            exprs[elm._ix] = exprs[elm._ix].subs({"__x0__": exprs[elm.children[0]]})
        if elm.arity > 1:
            exprs[elm._ix] = exprs[elm._ix].subs({"__x1__": exprs[elm.children[1]]})

    return _round_expression(exprs[0], signif)


def get_sympy_substitutions(model: Model, sample: Union[Series, DataFrame], symbolic_cat: bool = True) -> Dict[str, Any]:
    """Generates a value substitution dictionary that can be used to evaluate a sympy expression based on a feyn.Model.
    Takes as arguments the model to generate for, and a single sample from a pd.DataFrame that contains the values to substitute.

    Especially useful for models with categorical inputs that are otherwise cumbersome to evaluate since information is lost if using a symbolic categorical representation, or tedious to populate if using an expanded representation.

    Example: Evaluation of the sympy expression using the `subs` or `evalf` functions with the dictionary as input.
    >>> expr = model.sympify()
    >>> subs_dict = get_sympy_substitutions(model, data.iloc[0])
    >>> expr.evalf(subs=subs_dict)

    Arguments:
        model {Model} -- The feyn Model the sympy expression was created from
        sample {Union[Series, DataFrame]} -- The sample to use in evaluation.

    Keyword Arguments:
        symbolic_cat {bool} -- Whether the sympy expression uses a symbolic categorical input, or the categories as expanded values (default: {True})

    Returns:
        Dict[str, Any] -- A dictionary containing the symbol names and values to substitute
    """
    subs = {}
    for elem in model:
        if elem.name != "":
            if elem.fname == "in-cat:0":
                value = sample[elem.name]
                if symbolic_cat:
                    val = dict(elem.params["categories"]).get(value, 0)
                    symbol_name = _get_symbolic_category(elem)
                    subs[symbol_name] = val
                else:
                    categories = dict(elem.params["categories"]).keys()
                    for cat_name in categories:
                        subs[f"{elem.name}_{cat_name}"] = 0
                    subs[f"{elem.name}_{value}"] = 1
            elif elem.fname == "in-linear:0":
                subs[elem.name] = sample[elem.name]
    return subs
