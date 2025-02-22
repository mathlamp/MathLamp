grammar = r"""
?start: sum
          | NAME "=" sum    -> assign_var

    ?func: "out" "(" sum ")" -> out
         | "sqrt" "(" sum ")" -> sqrt
         | "pow" "(" sum "," sum ")" -> pow

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "%" atom  -> mod

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"
         | func

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
    %ignore /\/\/[^\n]*/
"""
