import ast
import operator
import math


# Predefined relations

def generate_less_equal(elements):
    return {(a, b) for a in elements for b in elements if a <= b}


def generate_greater_equal(elements):
    return {(a, b) for a in elements for b in elements if a >= b}


def generate_divisibility(elements):
    return {
        (a, b) for a in elements
        for b in elements
        if a != 0 and b % a == 0
    }


def generate_identity(elements):
    return {(a, a) for a in elements}


# Allowed operators

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

COMPARE = {
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}

FUNCTIONS = {
    "abs": abs,
    "sqrt": math.sqrt,
    "floor": math.floor,
    "ceil": math.ceil,
}


def evaluate(node, values):

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.Name):
        if node.id in values:
            return values[node.id]
        raise ValueError("Use only a and b.")

    if isinstance(node, ast.BinOp):
        op = OPS.get(type(node.op))
        if not op:
            raise ValueError("Unsupported operator.")
        return op(
            evaluate(node.left, values),
            evaluate(node.right, values)
        )

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return +evaluate(node.operand, values)
        if isinstance(node.op, ast.USub):
            return -evaluate(node.operand, values)
        if isinstance(node.op, ast.Not):
            return not evaluate(node.operand, values)
        raise ValueError("Unsupported operator.")

    if isinstance(node, ast.Compare):
        left = evaluate(node.left, values)

        for op_node, right_node in zip(
            node.ops, node.comparators
        ):
            op = COMPARE.get(type(op_node))
            if not op:
                raise ValueError("Unsupported comparison.")

            right = evaluate(right_node, values)

            if not op(left, right):
                return False

            left = right

        return True

    if isinstance(node, ast.BoolOp):
        values_list = [
            evaluate(x, values)
            for x in node.values
        ]

        if isinstance(node.op, ast.And):
            return all(values_list)

        if isinstance(node.op, ast.Or):
            return any(values_list)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function.")

        name = node.func.id

        if name not in FUNCTIONS:
            raise ValueError("Unsupported function.")

        return FUNCTIONS[name](
            *[
                evaluate(x, values)
                for x in node.args
            ]
        )

    raise ValueError("Unsupported expression.")


def validate_condition(condition):
    if not condition.strip():
        raise ValueError("Please enter a condition.")

    try:
        tree = ast.parse(condition, mode="eval")
        evaluate(tree.body, {"a": 1, "b": 2})
    except ZeroDivisionError:
        pass
    except Exception as e:
        raise ValueError(f"Invalid condition: {e}")


def evaluate_condition(condition, a, b):
    tree = ast.parse(condition, mode="eval")

    result = evaluate(
        tree.body,
        {"a": a, "b": b}
    )

    if not isinstance(result, bool):
        raise ValueError(
            "Condition must contain a comparison."
        )

    return result


def generate_from_condition(elements, condition):
    validate_condition(condition)
    relation = set()

    for a in elements:
        for b in elements:
            try:
                if evaluate_condition(condition, a, b):
                    relation.add((a, b))
            except ZeroDivisionError:
                pass

    return relation