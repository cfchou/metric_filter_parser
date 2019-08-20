from parsimonious import Grammar

#grammar = Grammar(
#    """
#    pattern5 = "{" pattern4 "}"
#    pattern4 = pattern3 (logical pattern3)*
#    pattern3 = pattern2 / pattern1
#    pattern2 = "(" pattern2 / pattern1 ")"
#    pattern1 = compare_eq / compare_ne
#    compare_eq = ~"[a-z A-Z 0-9]+" "=" ~"[a-z A-Z 0-9]+"
#    compare_ne = ~"[a-z A-Z 0-9]+" "!=" ~"[a-z A-Z 0-9]+"
#    logical = "&&" / "||"
#    """
#)


def test():
    grammar = Grammar(
        #pattern = "{" ws text ws "=" ws text ws "}"
        """
        #pattern6 = _ "{" pattern5 "}" _
        #pattern6 = "(" pattern4 (logical pattern4)*
        #pattern5 = pattern4 (logical pattern4)*
        
        #pattern6 = pattern5 / pattern4
        
        
        #pattern7 = _ pattern6 _
        
        # (a || (b || c))
        # ((a || b) || c)
        # ((a || b || c))
        
        pattern7 = "(" pattern7 (logical pattern6)* ")"
        
        pattern6 = pattern5 / pattern4
        # (a || b || c)
        pattern5 = "(" pattern4 ")"
        # a || b || c
        pattern4 = pattern3 (logical pattern3)*
        
        pattern3 = _ (pattern2 / pattern1) _
        pattern2 = "(" _ (pattern2/pattern1) _ ")"
        pattern1 = _ (compare_eq / compare_ne) _
        
        compare_eq = text _ "=" _ text
        compare_ne = text _ "!=" _ text
        logical = "&&" / "||"
        _ = ~"[ \t]"*
        text = ~"[a-zA-Z0-9_-]+"
        
        item = dot identifier ("[" index "]")*
        index = ~"[0-9]|[1-9][0+9]+"
        identifier = ~"[a-zA-Z0-9_-]+"
        
        selector = root item*
        
        root = "$"
        dot = "."
        """
    )
    #data = ' { ( -a_bc= 123 ) || abc = 123 } '
    data = '(((-a_bc=123))||abc=12)'
    print(grammar.parse(data))


def test1():
    grammar = Grammar(
        """
        selector = root item*
        item = dot identifier ("[" index "]")*
        index = ~'([1-9][0-9]+)|[0-9]'
        identifier = ~'[a-zA-Z0-9_-]+'
        root = "$"
        dot = "."
        """
    )
    data = '$.a.b[1][2].c[3]'
    print(grammar.parse(data))
    data = '$.a.b[10][2]'
    print(grammar.parse(data))

def test2():
    grammar = Grammar(
        r"""
        text = text_quoted / text_simple
        text_quoted = ~r'"([^"\\]|\\.)*"'
        text_simple = ~'[a-zA-Z0-9.*_-]+'
        """
    )
    data = '"z,@! \\" ok \\" "'
    print(grammar.parse(data))


# test expr
def grammar3():
    return Grammar(
        """
        expr =  atom_ext / expr_ext
        atom_ext = atom (or expr)*
        expr_ext = '(' expr ')' (or expr)*
        atom = ~'[a-zA-Z0-9._-]+'
        or = '||'
        """
    )


def test3(grammar: Grammar):
    data = '(a||(a))'
    print(grammar.parse(data))
    data = 'a||(a)'
    print(grammar.parse(data))
    data = 'a||a||a'
    print(grammar.parse(data))
    data = '(a)||(a)'
    print(grammar.parse(data))
    data = '(a||(a||(a)))'
    print(grammar.parse(data))
    data = '(a||(a||((a||a)||(a||(a||a)))))||(a)'
    print(grammar.parse(data))
    data = '(a)||a||(a||(a))'
    print(grammar.parse(data))
    data = '(a)||a||(a||a)'
    print(grammar.parse(data))


# allow whitespaces
def grammar4():
    return Grammar(
        """
        expr = (_ atom_ext _) / (_ expr_ext _)
        atom_ext = atom _ (or expr)*
        expr_ext = '(' expr ')' _ (or expr)*
        atom = ~'[a-zA-Z0-9._-]+'
        or = '||'
        _ = ~"[ \t]"*
        """
    )


def test4(grammar: Grammar):
    test3(grammar)
    data = ' ( a || ( a )) '
    print(grammar.parse(data))
    data = ' a || ( a ) '
    print(grammar.parse(data))
    data = ' a || a || a '
    print(grammar.parse(data))
    data = ' ( (a) ) || ( a ) '
    print(grammar.parse(data))
    data = ' ( a || ( a || ( a ) ) ) '
    print(grammar.parse(data))
    data = ' (a || (a || ((a || a) || (a || ( a || a)) ))  ) || (a) '
    print(grammar.parse(data))
    data = ' ( a ) || a || ( a || ( a ) ) '
    print(grammar.parse(data))
    data = ' ( a ) || a || ( a || a) '
    print(grammar.parse(data))


def grammar5():
    return Grammar(
        """
        top_cond = _ '{' cond '}' _
        cond = (_ cond_simple_seq _) / (_ cond_quoted_seq _)
        cond_simple_seq = cond_simple _ (or cond)*
        cond_quoted_seq = '(' cond ')' _ (or cond)*
        cond_simple = ~'[a-zA-Z0-9._-]+'
        or = '||'
        _ = ~"[ \t]"*
        """
    )


def test5(grammar: Grammar):
    data = ' { ( a || ( a )) } '
    print(grammar.parse(data))
    data = ' { a || ( a ) } '
    print(grammar.parse(data))
    data = ' { a || a || a } '
    print(grammar.parse(data))
    data = ' { ( (a) ) || ( a ) } '
    print(grammar.parse(data))
    data = ' { ( a || ( a || ( a ) ) ) } '
    print(grammar.parse(data))
    data = ' { (a || (a || ((a || a) || (a || ( a || a)) ))  ) || (a) } '
    print(grammar.parse(data))
    data = ' { ( a ) || a || ( a || ( a ) ) } '
    print(grammar.parse(data))
    data = ' { ( a ) || a || ( a || a) } '
    print(grammar.parse(data))


def grammar6():
    return Grammar(
        """
        top_cond = _ '{' cond '}' _
        cond = (_ cond_simple_seq _) / (_ cond_quoted_seq _)
        cond_simple_seq = cond_simple _ (boolean_op _ cond)*
        cond_quoted_seq = '(' cond ')' _ (boolean_op _ cond)*
        cond_simple = cmp_basic / cmp_numeric / cmp_is / cmp_not_exists
        
        cmp_basic = (_ cmp_eq _) / (_ cmp_ne _)
        cmp_numeric = (_ cmp_le _) / (_ cmp_ge _) / (_ cmp_lt _) / (_ cmp_gt _)
        cmp_is = (_ cmp_is_true _) / (_ cmp_is_false _) / (_ cmp_is_null _)
        
        cmp_eq = selector _ '=' _ text
        cmp_ne = selector _ '!=' _ text
        
        cmp_le = selector _ '<=' _ text
        cmp_ge = selector _ '>=' _ text
        cmp_lt = selector _ '<' _ text
        cmp_gt = selector _ '>' _ text
        
        cmp_is_true = selector _ 'IS' _ 'TRUE'
        cmp_is_false = selector _ 'IS' _ 'FALSE'
        cmp_is_null = selector _ 'IS' _ 'NULL'
        cmp_not_exists = selector _ 'NOT' _ 'EXISTS'
        
        
        boolean_op = '||' / '&&'
        selector = ~'[a-zA-Z0-9._-]+'
        text = ~'[a-zA-Z0-9._-]+'
        _ = ~'[ \t]*'
        """
    )


def test6(grammar: Grammar):
    data = ' { ( a = 12 || ( b = 34 )) } '
    print(grammar.parse(data))
    data = ' { a = 12 || ( b = 34 ) } '
    print(grammar.parse(data))
    data = ' { a = 12 && b != 34 || c = 56 } '
    print(grammar.parse(data))
    data = ' { ( ( a = 12) ) || ( b != 34 ) } '
    print(grammar.parse(data))
    data = ' { ( a = 12 && ( b = 34 && ( c != 56 ) ) ) } '
    print(grammar.parse(data))
    data = ' { (a = 12 || (b IS TRUE && ((c = 56 && a=78) || (b = 2 && ( a =1  || c = 2)) ))  ) || (b = 4) } '
    print(grammar.parse(data))

    data = ' { ( a = 12 ) || a != 2 || ( a IS NULL|| ( a NOT EXISTS ) ) } '
    print(grammar.parse(data))
    data = ' { ( a NOT EXISTS ) || a IS TRUE || ( a IS FALSE || a NOT EXISTS) } '
    print(grammar.parse(data))


def grammar7():
    return Grammar(
        """
        top_cond = _* '{' cond '}' _*
        cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
        cond_simple_seq = cond_simple _* (boolean_op _* cond)*
        cond_quoted_seq = '(' cond ')' _* (boolean_op _* cond)*
        cond_simple = cmp_basic / cmp_numeric / cmp_is / cmp_not_exists
        
        cmp_basic = (_* cmp_eq _*) / (_* cmp_ne _*)
        cmp_numeric = (_* cmp_le _*) / (_* cmp_ge _*) / (_* cmp_lt _*) / (_* cmp_gt _*)
        cmp_is = (_* cmp_is_true _*) / (_* cmp_is_false _*) / (_* cmp_is_null _*)
        
        cmp_eq = selector _* '=' _* text
        cmp_ne = selector _* '!=' _* text
        
        cmp_le = selector _* '<=' _* text
        cmp_ge = selector _* '>=' _* text
        cmp_lt = selector _* '<' _* text
        cmp_gt = selector _* '>' _* text
        
        cmp_is_true = selector _+ 'IS' _+ 'TRUE'
        cmp_is_false = selector _+ 'IS' _+ 'FALSE'
        cmp_is_null = selector _+ 'IS' _+ 'NULL'
        cmp_not_exists = selector _+ 'NOT' _+ 'EXISTS'
        
        boolean_op = '||' / '&&'
        selector = ~'[a-zA-Z0-9._-]+'
        text = ~'[a-zA-Z0-9._-]+'
        _ = ~'[ \t]'
        """
    )


def test7(grammar: Grammar):
    data = ' { ( a = 12 || ( b = 34 )) } '
    print(grammar.parse(data))
    data = ' { a = 12 || ( b = 34 ) } '
    print(grammar.parse(data))
    data = ' { a = 12 && b != 34 || c = 56 } '
    print(grammar.parse(data))
    data = ' { ( ( a = 12) ) || ( b != 34 ) } '
    print(grammar.parse(data))
    data = ' { ( a = 12 && ( b = 34 && ( c != 56 ) ) ) } '
    print(grammar.parse(data))
    data = ' { (a = 12 || (b IS TRUE && ((c = 56 && a=78) || (b = 2 && ( a =1  || c = 2)) ))  ) || (b = 4) } '
    print(grammar.parse(data))

    data = ' { ( a = 12 ) || a != 2 || ( a IS NULL|| ( a NOT EXISTS ) ) } '
    print(grammar.parse(data))
    data = ' { ( a NOT EXISTS ) || a IS TRUE || ( a IS FALSE || a NOT EXISTS) } '
    print(grammar.parse(data))


def grammar8():
    return Grammar(
        """
        top_cond = _* '{' cond '}' _*
        cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
        cond_simple_seq = cond_simple (_+ boolean_op _+ cond)*
        cond_quoted_seq = '(' cond ')' (_+ boolean_op _+ cond)*
        cond_simple = cmp_basic / cmp_numeric / cmp_is / cmp_not_exists

        cmp_basic = cmp_eq / cmp_ne
        cmp_numeric = cmp_le / cmp_ge / cmp_lt / cmp_gt
        cmp_is = cmp_is_true / cmp_is_false / cmp_is_null

        cmp_eq = selector _* '=' _* text
        cmp_ne = selector _* '!=' _* text

        cmp_le = selector _* '<=' _* text
        cmp_ge = selector _* '>=' _* text
        cmp_lt = selector _* '<' _* text
        cmp_gt = selector _* '>' _* text

        cmp_is_true = selector _+ 'IS' _+ 'TRUE'
        cmp_is_false = selector _+ 'IS' _+ 'FALSE'
        cmp_is_null = selector _+ 'IS' _+ 'NULL'
        cmp_not_exists = selector _+ 'NOT' _+ 'EXISTS'

        boolean_op = '||' / '&&'
        selector = ~'[a-zA-Z0-9._-]+'
        text = ~'[a-zA-Z0-9._-]+'
        _ = ~'[ \t]'
        """
    )


def test8(grammar: Grammar):
    data = ' { ( a = 12 || ( b = 34 )) } '
    print(grammar.parse(data))
    data = ' { a = 12 || ( b = 34 ) } '
    print(grammar.parse(data))
    data = ' { a = 12 && b != 34 || c = 56 } '
    print(grammar.parse(data))
    data = ' { ( ( a = 12) ) || ( b != 34 ) } '
    print(grammar.parse(data))
    data = ' { ( a = 12 && ( b = 34 && ( c != 56 ) ) ) } '
    print(grammar.parse(data))
    data = ' { (a = 12 || (b IS TRUE && ((c = 56 && a=78) || (b = 2 && ( a =1 ' \
           ' || c = 2)) ))  ) || (b = 4) } '
    print(grammar.parse(data))

    data = ' { ( a = 12 ) || a != 2 || ( a IS NULL || ( a NOT EXISTS ) ) } '
    print(grammar.parse(data))
    data = ' { ( a NOT EXISTS ) || a IS TRUE || ( a IS FALSE || a NOT EXISTS) ' \
           '} '
    print(grammar.parse(data))


def grammar9():
    return Grammar(
        """
        top_cond = _* '{' cond '}' _*
        cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
        cond_simple_seq = cond_simple (_+ op_boolean _+ cond)*
        cond_quoted_seq = '(' cond ')' (_+ op_boolean _+ cond)*
        cond_simple = cmp_common / cmp_is / cmp_not_exists

        cmp_common = selector _* op_common _* text
        cmp_is = selector _+ 'IS' _+ ('TRUE' / 'FALSE' / 'NULL')
        cmp_not_exists = selector _+ 'NOT' _+ 'EXISTS'

        op_common = '=' / '!=' / '<=' / '>=' / '<' / '>'
        op_boolean = '||' / '&&'
        selector = ~'[a-zA-Z0-9._-]+'
        text = ~'[a-zA-Z0-9._-]+'
        _ = ~'[ \t]'
        """
    )


def grammar10():
    return Grammar(
        """
        top_cond = _* '{' cond '}' _*
        cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
        cond_simple_seq = cond_simple (_+ op_boolean _+ cond)*
        cond_quoted_seq = '(' cond ')' (_+ op_boolean _+ cond)*
        cond_simple = cmp_common / cmp_is / cmp_not_exists

        cmp_common = selector _* op_common _* text
        cmp_is = selector _+ 'IS' _+ ('TRUE' / 'FALSE' / 'NULL')
        cmp_not_exists = selector _+ 'NOT' _+ 'EXISTS'

        op_common = '=' / '!=' / '<=' / '>=' / '<' / '>'
        op_boolean = '||' / '&&'
        
        selector = root path*
        path = dot child ('[' index ']')*
        
        index = ~'([1-9][0-9]+)|[0-9]'
        child = ~'[a-zA-Z0-9_-]+'
        text = ~'[a-zA-Z0-9._-]+'
        root = "$"
        dot = "."
        _ = ~'[ \t]'
        """
    )


def test10(grammar: Grammar):
    data = ' { ( $.a = 12 || ( $.b = 34 )) } '
    print(grammar.parse(data))
    data = ' { ( $.a.bc IS NULL || ( $.b.xy = ab )) } '
    print(grammar.parse(data))
    data = ' { ( $.a[0] NOT EXISTS || ( $.b[2][1] = 34 )) } '
    print(grammar.parse(data))
    data = ' { ( $.a[0]<=12 || ( $.b[2][1].c = 34 )) } '
    print(grammar.parse(data))
    data = ' { ($.a[0] <= 12 || ( $.b[10][1] =34 )) } '
    print(grammar.parse(data))
    data = ' { $.a.b = 12 && $.b != 34 || $.c = 56 } '
    print(grammar.parse(data))
    #data = ' { ( ( a = 12) ) || ( b != 34 ) } '
    #print(grammar.parse(data))
    #data = ' { ( a = 12 && ( b = 34 && ( c != 56 ) ) ) } '
    #print(grammar.parse(data))
    #data = ' { (a = 12 || (b IS TRUE && ((c = 56 && a=78) || (b = 2 && ( a =1 ' \
    #       ' || c = 2)) ))  ) || (b = 4) } '
    #print(grammar.parse(data))

    #data = ' { ( a = 12 ) || a != 2 || ( a IS NULL || ( a NOT EXISTS ) ) } '
    #print(grammar.parse(data))
    #data = ' { ( a NOT EXISTS ) || a IS TRUE || ( a IS FALSE || a NOT EXISTS) ' \
    #       '} '
    #print(grammar.parse(data))


def grammar11():
    return Grammar(
        r"""
        top_cond = _* '{' cond '}' _*
        cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
        cond_simple_seq = cond_simple (_+ op_boolean _+ cond)*
        cond_quoted_seq = '(' cond ')' (_+ op_boolean _+ cond)*
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


def test11(grammar: Grammar):
    test10(grammar)
    data = ' { ( $.a = "12" || ( $.b = 34 )) } '
    print(grammar.parse(data))
    data = ' { ( $.a.bc IS NULL || ( $.b.xy = "ab" )) } '
    print(grammar.parse(data))
    data = ' { ( $.a[0] NOT EXISTS || ( $.b[2][1] = "34" )) } '
    print(grammar.parse(data))
    data = ' { ( $.a[0]<=12 || ( $.b[2][1].c = "34" )) } '
    print(grammar.parse(data))
    data = ' { ($.a[0] <="12" || ( $.b[10][1] =34 )) } '
    print(grammar.parse(data))
    data = ' { $.a.b ="12" && $.b != 3.4.5 || $.c = 56 } '
    print(grammar.parse(data))
    data = ' { $.a="12" && $.b != 3.4.5 || $.c = 56 } '
    print(grammar.parse(data))


def test12(grammar: Grammar):
    data = [' { $.eventType = "UpdateTrail" } ',
            '{ $.sourceIPAddress != 123.123.* }',
            '{ $.arrayKey[0] = "value" }',
            '{ $.objectList[1].id = 2 }',
            '{ $.SomeObject IS NULL }',
            '{ $.SomeOtherObject NOT EXISTS }',
            '{ $.ThisFlag IS TRUE } ']

    for datum in data:
        print(grammar.parse(datum))


def test13(grammar: Grammar):
    data = '{($.user.id = 2 && $.users[0].email = "nonmatch") || $.actions[2] = "GET"}'
    print(grammar.parse(data))

    data = [' { ($.user.id = 1) && ($.users[0].email = "John.Doe@example.com") } ',
        '{($.user.id = 2 && $.users[0].email = "nonmatch") || $.actions[2] = "GET"}',
        '{ $.user.email = "John.Stiles@example.com" || $.coordinates[0][1] = nonmatch && $.actions[2] = nomatch }',
        '{ ($.user.email = "John.Stiles@example.com" || $.coordinates[0][1] = nonmatch) && $.actions[2] = nomatch }']

    for datum in data:
        print(grammar.parse(datum))


def test14(grammar: Grammar):
    data = '{ ($.user.id = 2 && $.user.id = "a \\" b") || $.a="1"}'
    print(grammar.parse(data))


def grammar12():
    return Grammar(
        r"""
        top_cond = _* '{' cond '}' _*
        cond = (_* cond_simple_seq _*) / (_* cond_quoted_seq _*)
        cond_simple_seq = cond_simple cond_tail*
        cond_quoted_seq = cond_quoted cond_tail*
        cond_quoted = '(' cond ')'
        cond_tail = _ + op_boolean _+ cond
        cond_simple = cmp_common / cmp_is_true / cmp_is_false / cmp_is_null / 
        cmp_not_exists

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


if __name__ == '__main__':
    test1()
    test2()
    test3(grammar3())
    test4(grammar4())
    test5(grammar5())
    test6(grammar6())
    test7(grammar7())
    test8(grammar8())
    test8(grammar9())
    test10(grammar10())
    test11(grammar11())
    test12(grammar11())
    test13(grammar11())
    test14(grammar11())
    test11(grammar12())
    test12(grammar12())
    test13(grammar12())
    test14(grammar12())


