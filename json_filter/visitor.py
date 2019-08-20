import re
from collections import namedtuple
from enum import Enum
from numbers import Number

import jmespath
from parsimonious import NodeVisitor

from json_filter.exception import SelectorException, VisitorException
from json_filter.grammar import _grammar

# RSEC stands for ReSolvedExpr's category
RSEC = Enum('RSEC',
            ['OP_COMMON', 'OP_BOOLEAN', 'SELECTOR', 'TEXT_SIMPLE',
             'TEXT_QUOTED',
             'CMP', 'COND', 'PARTIAL'])

# When visiting a node that we care about(excluding spaces, brackets, ...),
# we will return a ResolvedExpr that
ResolvedExpr = namedtuple('ResolvedExpr', ['category', 'value', 'node'])


def op_ne(x, y): return x != y


def op_eq(x, y): return x == y


def op_lt(x, y): return x < y


def op_le(x, y): return x <= y


def op_gt(x, y): return x > y


def op_ge(x, y): return x >= y


def op_or_bind2(y):
    # An 'or' op with a bound right oprand
    def op_or(x):
        return x or y

    return op_or


def op_and_bind2(y):
    # An 'and' op with a bound right oprand
    def op_and(x):
        return x and y

    return op_and


def _is_number_like_str(s):
    # Test if the give str is number-like, e.g. "123", "1e2", "34.78"
    try:
        float(s)
        return True
    except ValueError:
        return False


def _str_to_number(s):
    # Convert a number-like str to a number
    # assert _is_number_like(s)
    try:
        return int(s)
    except ValueError:
        return float(s)


def _match_strings(pattern, target):
    # Match strings pattern and target. '*' at the beginning or the end of
    # the pattern is wildcard.
    wildcard_begin = pattern.find('*')
    wildcard_end = pattern.rfind('*')
    if 0 == wildcard_begin < wildcard_end == len(pattern) - 1:
        return target.find(pattern[1:wildcard_end - 1]) != -1
    elif wildcard_begin == 0:
        fixed = pattern[1:]
        return len(fixed) == 0 or target[-len(fixed):] == fixed
    elif wildcard_end == len(pattern) - 1:
        fixed = pattern[:wildcard_end]
        return target[:len(fixed)] == fixed
    else:
        return pattern == target


class JsonFilterVisitor(NodeVisitor):
    # Regex used for stripping off the root and the immediate dot($.) in the
    # selector.
    # ```
    #   m = _selector_re.match('$.a.b[1].c')
    #   assert m.groups() == ('a.b[1].c',)
    # ```
    _selector_re = re.compile(r'\$\.(.+)')

    # Regex, for an array selector, return the tuple of the upper parts in the
    # selector and the index of the rightmost array element.
    # ```
    #   m = _selector_re_array_upper.match('a[1].b[2][1010]')
    #   assert m.groups() == ('a[1].b[2]', '1010')
    # ```
    _selector_re_array_upper = re.compile(r'(.+)(?:\[([1-9][0-9]+|[0-9])\])+$')
    op_map = {
        '!=': op_ne,
        '=': op_eq,
        '<': op_lt,
        '<=': op_le,
        '>': op_gt,
        '>=': op_ge,
        '||': op_or_bind2,
        '&&': op_and_bind2
    }

    def __init__(self, target) -> None:
        super().__init__()
        self.target = target

    @staticmethod
    def _flatten(it):
        # A generator that flatten a nested list.
        for i in it:
            if isinstance(i, list):
                yield from JsonFilterVisitor._flatten(i)
            else:
                yield i

    @staticmethod
    def _get_resolved_expr(visited_children, resolved_expr_category,
                           flatten=True):
        if flatten:
            visited_children = JsonFilterVisitor._flatten(visited_children)
        f = filter(
            lambda x: isinstance(x,
                                 ResolvedExpr) and x.category ==
                      resolved_expr_category,
            visited_children)
        while (yield from f) is not None:
            pass

    @staticmethod
    def _get_resolved_expr_first(visited_children, resolved_expr_category,
                                 flatten=True):
        try:
            if flatten:
                visited_children = JsonFilterVisitor._flatten(visited_children)
            g = JsonFilterVisitor._get_resolved_expr(visited_children,
                                                     resolved_expr_category)
            return next(g)
        except StopIteration:
            return None

    def visit_op_common(self, node, visited_children):
        return ResolvedExpr(RSEC.OP_COMMON, self.op_map[node.text], node)

    def visit_op_boolean(self, node, visited_children):
        return ResolvedExpr(RSEC.OP_BOOLEAN, self.op_map[node.text], node)

    def visit_selector(self, node, visited_children):
        path = self._selector_re.match(node.text)
        if path is None or len(path.groups()) != 1:
            raise SelectorException(f'can not extract path from {node.text}')
        return ResolvedExpr(RSEC.SELECTOR, path[1], node)

    def visit_text(self, node, visited_children):
        assert len(visited_children) == 1
        assert visited_children[0].category in [RSEC.TEXT_SIMPLE,
                                                RSEC.TEXT_QUOTED]

        child = visited_children[0]
        return ResolvedExpr(child.category, child.value, node)

    def visit_text_quoted(self, node, visited_children):
        # Strip off initial and ending double quotes
        return ResolvedExpr(RSEC.TEXT_QUOTED, node.text[1:-1], node)

    def visit_text_simple(self, node, visited_children):
        return ResolvedExpr(RSEC.TEXT_SIMPLE, node.text, node)

    def visit_cmp_is_true(self, node, visited_children):
        selector = self._get_resolved_expr_first(visited_children,
                                                 RSEC.SELECTOR).value
        target_value = jmespath.search(selector, self.target)
        # False if target_value is None
        return ResolvedExpr(RSEC.CMP, target_value is True, node)

    def visit_cmp_is_false(self, node, visited_children):
        selector = self._get_resolved_expr_first(visited_children,
                                                 RSEC.SELECTOR).value
        target_value = jmespath.search(selector, self.target)
        # False if target_value is None
        return ResolvedExpr(RSEC.CMP, target_value is False, node)

    def visit_cmp_not_exists(self, node, visited_children):
        selector = self._get_resolved_expr_first(visited_children,
                                                 RSEC.SELECTOR).value
        target_value = jmespath.search(selector, self.target)
        if target_value is not None:
            return ResolvedExpr(RSEC.CMP, False, node)

        # jmespath returns None if selected field not existed or it is set
        # to null. cmp_not_exists should only return True for the former.

        m = self._selector_re_array_upper.match(selector)
        if m is not None:
            # selector ends in 'whatever[N]'
            # assert len(m.groups()) != 2
            parent = jmespath.search(m[1], self.target)
            if parent is None:
                return ResolvedExpr(RSEC.CMP, True, node)

            # assert isinstance(parent, list):
            if len(parent) <= int(m[2]):
                return ResolvedExpr(RSEC.CMP, True, node)

            # assert parent[int(m[2])] is None
            return ResolvedExpr(RSEC.CMP, False, node)

        # selector ends in 'whatever.abc' or 'abc'
        i = selector.rfind('.')
        if i == -1:
            # use self.target is the default sentinel
            target_value = self.target.get(selector, self.target)
            if target_value == self.target:
                return ResolvedExpr(RSEC.CMP, True, node)
            # assert target_value exists and is None
            return ResolvedExpr(RSEC.CMP, False, node)

        parent = jmespath.search(selector[:i], self.target)
        if parent is None:
            return ResolvedExpr(RSEC.CMP, True, node)

        # use parent is the default sentinel
        target_value = parent.get(selector[i + 1:], parent)
        if target_value == parent:
            return ResolvedExpr(RSEC.CMP, True, node)

        # assert target_value exists and is None
        return ResolvedExpr(RSEC.CMP, False, node)

    def visit_cmp_is_null(self, node, visited_children):
        selector = self._get_resolved_expr_first(visited_children,
                                                 RSEC.SELECTOR).value
        target_value = jmespath.search(selector, self.target)
        if target_value is not None:
            return ResolvedExpr(RSEC.CMP, False, node)

        # jmespath returns None if selected field not existed or it is set
        # to null. cmp_is_null should only return True for the later.

        m = self._selector_re_array_upper.match(selector)
        if m is not None:
            # selector ends in 'whatever[N]'
            # assert len(m.groups()) != 2
            parent = jmespath.search(m[1], self.target)
            if parent is None:
                return ResolvedExpr(RSEC.CMP, False, node)
            # assert isinstance(parent, list):
            if len(parent) <= int(m[2]):
                return ResolvedExpr(RSEC.CMP, False, node)
            # assert parent[int(m[2])] is None
            return ResolvedExpr(RSEC.CMP, True, node)

        # selector ends in 'whatever.abc' or 'abc'
        i = selector.rfind('.')
        if i == -1:
            # use self.target is the default sentinel
            target_value = self.target.get(selector, self.target)
            if target_value == self.target:
                return ResolvedExpr(RSEC.CMP, False, node)
            # assert target_value exists and is None
            return ResolvedExpr(RSEC.CMP, True, node)

        parent = jmespath.search(selector[:i], self.target)
        if parent is None:
            return ResolvedExpr(RSEC.CMP, False, node)

        # use parent is the default sentinel
        target_value = parent.get(selector[i + 1:], parent)
        if target_value == parent:
            return ResolvedExpr(RSEC.CMP, False, node)

        # assert target_value exists and is None
        return ResolvedExpr(RSEC.CMP, True, node)

    def _cmp_common_text_quoted(self, op_common, text_quoted, target_value):
        if op_common.node.text in ['<', '<=', '>', '>=']:
            # strings can't do numeric op like '>'
            raise VisitorException(
                f'{op_common.node.text} does not apply to string')

        # assert op_common.node.text in ['!=', '=']
        if isinstance(target_value, int):
            try:
                v = int(text_quoted.value)
                return op_common.value(target_value, v)
            except ValueError:
                pass
        elif isinstance(target_value, float):
            try:
                v = float(text_quoted.value)
                return op_common.value(target_value, v)
            except ValueError:
                pass
        # text_quoted is not number-like,
        # ===========
        # FIXME

        if type(target_value) in [str, int, float]:
            if _is_number_like_str(text_quoted.value) and isinstance(target_value, Number):
                return op_common.value(target_value,
                                       _str_to_number(text_quoted.value))

            # TODO: scientific notation changes representation, i.e. str(1e2) == '100.0'
            target_value_str = str(target_value)
            ret = _match_strings(text_quoted.value, target_value_str)
            return (op_common.node.text == '=' and ret) or (
                op_common.node.text == '!=' and not ret)
        else:
            # target_value is not a str or number, i.e. null, array, object
            return False

    def _cmp_common_text_simple(self, op_common, text_simple, target_value):
        # text_simple, may or may not look like a number
        if op_common.node.text in ['<', '<=', '>', '>=']:
            if not _is_number_like_str(text_simple.value):
                # non number-like strings can't do numeric op, e.g.
                # {$.foo > abc}
                raise VisitorException(
                    f'{op_common.node.text} does not apply to string')

            # text_simple looks like a number, e.g.
            # {$.foo > 12.34}
            # then they can compare if target_value is a number
            if isinstance(target_value, Number):
                return op_common.value(target_value,
                                       _str_to_number(text_simple.value))
            # target_value is not a number, i.e. str, null, array, object
            return False

        # assert op_common.node.text in ['!=', '=']
        if type(target_value) in [str, int, float]:
            if _is_number_like_str(text_simple.value) and isinstance(target_value, Number):
                return op_common.value(target_value,
                                       _str_to_number(text_simple.value))

            # TODO: scientific notation changes representation, i.e. str(1e2) == '100.0'
            target_value_str = str(target_value)
            ret = _match_strings(text_simple.value, target_value_str)
            return (op_common.node.text == '=' and ret) or (
                op_common.node.text == '!=' and not ret)
        else:
            # target_value is not a str or number, i.e. null, array, object
            return False

    def visit_cmp_common(self, node, visited_children):
        selector = self._get_resolved_expr_first(visited_children,
                                                 RSEC.SELECTOR).value
        target_value = jmespath.search(selector, self.target)
        if target_value is None:
            # Consider it false when the field not existed in target
            return ResolvedExpr(RSEC.CMP, False, node)
        op = self._get_resolved_expr_first(visited_children, RSEC.OP_COMMON)
        text = self._get_resolved_expr_first(visited_children, RSEC.TEXT_QUOTED)
        if text is not None:
            ret = self._cmp_common_text_quoted(op, text, target_value)
            return ResolvedExpr(RSEC.CMP, ret, node)

        text = self._get_resolved_expr_first(visited_children,
                                             RSEC.TEXT_SIMPLE)
        ret = self._cmp_common_text_simple(op, text, target_value)
        return ResolvedExpr(RSEC.CMP, ret, node)

    def visit_cond_simple(self, node, visited_children):
        assert len(visited_children) == 1
        assert visited_children[0].category == RSEC.CMP
        return ResolvedExpr(RSEC.COND, visited_children[0].value, node)

    def visit_cond_quoted(self, node, visited_children):
        cond = self._get_resolved_expr_first(visited_children, RSEC.COND)
        return ResolvedExpr(RSEC.COND, cond.value, node)

    def visit_partial(self, node, visited_children):
        op = self._get_resolved_expr_first(visited_children,
                                           RSEC.OP_BOOLEAN).value
        cond_value = self._get_resolved_expr_first(visited_children,
                                                   RSEC.COND).value
        return ResolvedExpr(RSEC.PARTIAL, op(cond_value), node)

    def visit_cond_simple_seq(self, node, visited_children):
        cond_value = self._get_resolved_expr_first(
            visited_children, RSEC.COND).value
        for partial in self._get_resolved_expr(visited_children, RSEC.PARTIAL):
            cond_value = partial.value(cond_value)
        return ResolvedExpr(RSEC.COND, cond_value, node)

    def visit_cond_quoted_seq(self, node, visited_children):
        cond_value = self._get_resolved_expr_first(
            visited_children, RSEC.COND).value
        for partial in self._get_resolved_expr(visited_children, RSEC.PARTIAL):
            cond_value = partial.value(cond_value)
        return ResolvedExpr(RSEC.COND, cond_value, node)

    def visit_cond(self, node, visited_children):
        cond = self._get_resolved_expr_first(visited_children, RSEC.COND)
        return ResolvedExpr(RSEC.COND, cond.value, node)

    def visit_top_cond(self, node, visited_children):
        cond = self._get_resolved_expr_first(visited_children, RSEC.COND)
        return ResolvedExpr(RSEC.COND, cond.value, node)

    def generic_visit(self, node, visited_children):
        return visited_children or node


def test3():
    data = {
        'ab': {
            'cd': [
                [
                    {},
                    {
                        'g': [
                            None,
                            '123.22'
                        ]
                    }
                ]
            ]
        },
        'cd': None,
        'ef': [None]
    }
    pattern = '{$.cd IS NULL && $.ab NOT EXISTS}'
    tree = _grammar.parse(pattern)
    visitor = JsonFilterVisitor(data)
    output = visitor.visit(tree)
    print(output)


def test4():
    src = r"""
    {
        "eventType": "UpdateTrail",
        "sourceIPAddress": "111.111.111.111",
        "arrayKey": [
            "value",
            "another value"
        ],
        "objectList": [
           {
             "name": "a",
             "id": 1
           },
           {
             "name": "b",
             "id": 2
           }
        ],
        "SomeObject": null,
        "ThisFlag": true
    }
    """
    import json
    data = json.loads(src)
    pattern = '{ $.sourceIPAddress != 123.123.* }'
    tree = _grammar.parse(pattern)
    visitor = JsonFilterVisitor(data)
    output = visitor.visit(tree)
    print(output)


if __name__ == '__main__':
    test4()
