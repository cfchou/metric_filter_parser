from json_filter.grammar import _grammar
from json_filter.visitor import JsonFilterVisitor
from json_filter.exception import ParsingException, VisitorException
from parsimonious.exceptions import ParseError, VisitationError


def match(pattern, data):
    """
    Try match pattern and data.
    :param pattern:
    :param data:
    :return: return boolean pattern is legitimate to match, otherwise raises
    ParsingError or VisitorError
    """
    try:
        tree = _grammar.parse(pattern)
        visitor = JsonFilterVisitor(data)
        resolved_expr = visitor.visit(tree)
    except ParseError as e:
        raise ParsingException('Parsing pattern failed') from e
    except VisitationError as e:
        raise VisitorException('Evaluation failed') from e

    if resolved_expr.node.expr_name != 'top_cond':
        raise VisitorException(
            'Not top_cond, possibly an error in the implementation')

    if not isinstance(resolved_expr.value, bool):
        raise VisitorException(
            f'{resolved_expr.value} is not a boolean, possibly an error in '
            f'the implementation')

    return resolved_expr.value
