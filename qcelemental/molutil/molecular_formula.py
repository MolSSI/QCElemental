import collections
import re
from typing import List


def order_molecular_formula(formula: str, order: str = "alphabetical") -> str:
    """
    Reorders a molecular formula.

    Parameters
    ----------
    formula: str
        A molecular formula
    order: str, optional
        Sorting order of the formula. Valid choices are "alphabetical" and "hill".

    Returns
    -------
    str
        The molecular formula.
    """

    matches = re.findall(r"[A-Z][^A-Z]*", formula)
    if not "".join(matches) == formula:
        raise ValueError(f"{formula} is not a valid molecular formula.")
    count = collections.defaultdict(int)
    for match in matches:
        match_n = re.match(r"(\D+)(\d*)", match)
        assert match_n
        if match_n.group(2) == "":
            n = 1
        else:
            n = int(match_n.group(2))
        count[match_n.group(1)] += n
    symbols = [k for k, v in count.items() for i in range(v)]
    return molecular_formula_from_symbols(symbols=symbols, order=order)


def molecular_formula_from_symbols(symbols: List[str], order: str = "alphabetical") -> str:
    """
    Returns the molecular formula for a list of symbols.

    Parameters
    ----------
    symbols: List[str]
        List of chemical symbols
    order: str, optional
        Sorting order of the formula. Valid choices are "alphabetical" and "hill".

    Returns
    -------
    str
        The molecular formula.
    """

    supported_orders = ["alphabetical", "hill"]
    order = order.lower()
    if order not in supported_orders:
        raise ValueError(f"Unsupported molecular formula order: {order}. Supported orders are f{supported_orders}.")
    count = collections.Counter(x.title() for x in symbols)
    element_order = sorted(count.keys())

    if order == "hill" and "C" in element_order:
        if "H" in element_order:
            element_order.insert(0, element_order.pop(element_order.index("H")))
        element_order.insert(0, element_order.pop(element_order.index("C")))

    ret = []
    for k in element_order:
        c = count[k]
        ret.append(k)
        if c > 1:
            ret.append(str(c))

    return "".join(ret)
