from parsimonious import Grammar

_grammar = Grammar(
    r"""
    top_cond = '{' cond '}'
    partial = _+ op_boolean _+ cond
    
    cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
    cond_quoted = '(' cond ')'
    cond_simple_seq = cond_simple partial*
    cond_quoted_seq = cond_quoted partial*
    cond_simple = cmp_common / cmp_is_true / cmp_is_false / cmp_is_null / cmp_not_exists

    cmp_common = selector _* op_common _* text
    cmp_is_true = selector _+ 'IS' _+ 'TRUE'
    cmp_is_false = selector _+ 'IS' _+ 'FALSE'
    cmp_is_null = selector _+ 'IS' _+ 'NULL'
    cmp_not_exists = selector _+ 'NOT' _+ 'EXISTS'

    op_common = '=' / '!=' / '<=' / '>=' / '<' / '>'
    op_boolean = '||' / '&&'

    selector = root path+
    path = dot child ('[' index ']')*
    index = ~'([1-9][0-9]+)|[0-9]'
    child = ~'[a-zA-Z0-9_-]+'
    root = "$"
    dot = "."
    
    text = text_quoted / text_simple
    text_quoted = ~r'"([^"\\]|\\.)*"'
    text_simple = ~'[a-zA-Z0-9.*_-]+'
    
    _ = ~'[ \t]'
    """
)

