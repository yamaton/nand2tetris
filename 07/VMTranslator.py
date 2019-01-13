"""
nand2tetris project 7

Arithmetic and logical commands
applied to stack machine
```
add
sub
neg
eq
gt
lt
and
or
not
```

Memory access: push to and pop from
```
argument
local
static
this
that
pointer
temp
```

"""
import argparse
import os
import logging
import enum
import uuid
import itertools as it

ARITHMETIC_BINARY = {"add": "+", "sub": "-", "and": "&", "or": "|"}
ARITHMETIC_CMP = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
ARITHMETIC_UNARY = {"neg": "-", "not": "!"}

SET_ARITHMETIC_STR = (
    ARITHMETIC_BINARY.keys() | ARITHMETIC_CMP.keys() | ARITHMETIC_UNARY.keys()
)

SEGMENTS = set(
    """
    argument
    local
    static
    this
    that
    pointer
    temp
""".strip().split()
)

IN_MEMORY_MAP = dict(SP="SP", LCL="LCL", ARG="ARG", THIS="THIS", THAT="THAT")


class C(enum.Enum):
    ARITHMETIC = "arithmetic"
    PUSH = "push"
    POP = "pop"
    LABEL = "label"
    GOTO = "goto"
    IF = "if"
    FUNCTION = "function"
    RETURN = "return"
    CALL = "call"


class Parser(object):
    def __init__(self, iterable):
        self.iterable = iterable

    def _gen(self):
        for entry in self.iterable:
            cleaned = self._remove_comment(entry)
            if cleaned:
                yield self.parse_line(cleaned)

    def __iter__(self):
        return iter(self._gen())

    def parse_line(self, line):
        args = line.split()
        cmd = _str_to_cmd(args[0])
        return cmd, args

    def _remove_comment(self, line):
        line = line.strip()
        idx = line.find("//")
        if idx >= 0:
            line = line[:idx].strip()
        return line


class CodeWriter(object):
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return iter(self._gen())

    def _gen(self):
        g = it.chain.from_iterable(map(self._f, self.iterable))
        return g

    def _f(self, item):
        cmd, args = item
        # print("[debug] _f args:", args)
        if cmd is C.PUSH:
            yield from self._f_push(args)
        elif cmd is C.ARITHMETIC:
            yield from self._f_arithmetic(args)
        elif cmd is C.POP:
            yield from self._f_pop(args, show=True)
        else:
            yield "Unimpremented"

    def _f_push(self, args):
        # print("[debug] args:", args)
        _, seg, index = args
        addr = self._addr(seg, index)
        yield f"// {' '.join(args)}"
        yield f"@{addr}"
        if seg == "constant":
            yield "D=A"
        else:
            yield "D=M"
        sp_addr = IN_MEMORY_MAP["SP"]
        yield f"@{sp_addr}"
        yield "A=M"
        yield "M=D"
        yield f"@{sp_addr}"
        yield "M=M+1"
        yield ""

    def _f_pop(self, args=(), show=False):
        if show:
            yield "// pop"
        sp_addr = IN_MEMORY_MAP["SP"]
        yield f"@{sp_addr}"
        yield "AM=M-1"
        yield "D=M"
        if args:
            _, segment, index = args
            addr = self._addr(segment, index)
            yield f"@{addr}"
            yield "M=D"
        if show:
            yield ""

    def _f_arithmetic(self, args):
        op_name = args[0]
        if op_name in ARITHMETIC_BINARY:
            res = self._arithmetic_binary(op_name)
        elif op_name in ARITHMETIC_CMP:
            res = self._arithmetic_cmp(op_name)
        elif op_name in ARITHMETIC_UNARY:
            res = self._arithmetic_unary(op_name)
        else:
            raise ValueError("Undefined arithmetic")
        yield from res

    def _arithmetic_binary(self, op_name):
        op = ARITHMETIC_BINARY[op_name]
        yield f"// {op_name}"
        yield from self._f_pop()

        sp_addr = IN_MEMORY_MAP["SP"]
        yield f"@{sp_addr}"
        yield "A=M-1"
        yield f"M=D{op}M"
        yield ""

    def _arithmetic_cmp(self, op_name):
        op = ARITHMETIC_CMP[op_name]
        rnd = random_str()
        true_label = "true_" + rnd
        end_label = "end_" + rnd

        yield f"// {op_name}"
        yield from self._f_pop()

        sp_addr = IN_MEMORY_MAP["SP"]
        yield f"@{sp_addr}"
        yield "A=M-1"
        yield "D=D-M"

        yield f"@{true_label}"
        yield f"D;{op}"
        yield f"@{sp_addr}"
        yield "A=M-1"
        yield "M=0"
        yield f"@{end_label}"
        yield "0;JMP"
        yield f"({true_label})"
        yield f"@{sp_addr}"
        yield "A=M-1"
        yield "M=-1"
        yield f"({end_label})"
        yield ""

    def _arithmetic_unary(self, op_name):
        op = ARITHMETIC_UNARY[op_name]
        sp_addr = IN_MEMORY_MAP["SP"]
        yield f"// {op_name}"
        yield f"@{sp_addr}"
        yield "A=M-1"
        yield f"M={op}M"
        yield ""

    def _addr(self, segment, index):
        if segment == "constant":
            res = index
        elif segment == "local":
            res = IN_MEMORY_MAP["LCL"] + index
        elif segment == "argument":
            res = IN_MEMORY_MAP["ARG"] + index
        elif segment == "this" or segment == "pointer":
            res = IN_MEMORY_MAP["THIS"] + index
        elif segment == "that":
            res = IN_MEMORY_MAP["THAT"] + index
        elif segment == "temp":
            res = IN_MEMORY_MAP["THIS"] + index
        elif segment == "static":
            res = __name__ + "." + str(index)
        else:
            raise ValueError(f"Unimplemented: segment = {segment}")
        return res


def _str_to_cmd(s):
    if s in SET_ARITHMETIC_STR:
        res = C.ARITHMETIC
    else:
        res = C(s)
    return res


def random_str():
    return str(uuid.uuid4())[:8]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help=".vm file to translate")
    args = parser.parse_args()

    file_vm = args.input
    file_wo_ext, _ = os.path.splitext(file_vm)
    file_asm = file_wo_ext + ".asm"
    with open(file_vm, "r") as fin:
        with open(file_asm, "w") as fout:
            parser = Parser(fin)
            code_writer = CodeWriter(parser)
            for line in code_writer:
                print(line, file=fout)

    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"Loading: {file_vm}")
    logging.info(f"Saving : {file_asm}")

if __name__ == "__main__":
    main()

