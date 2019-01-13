"""
Translate assembly program into Hack machine instruction

nand2tetris project 6
"""
import os
import argparse

PREDEFINED_TABLE = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}
for i in range(16):
    PREDEFINED_TABLE[f"R{i}"] = i


JUMP_TABLE = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


COMMAND_TABLE = {
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "A": "110000",
    "M": "110000",
    "!D": "001101",
    "!A": "110001",
    "!M": "110001",
    "-D": "001111",
    "-A": "110011",
    "-M": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "M+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "M-1": "110010",
    "D+A": "000010",
    "D+M": "000010",
    "D-A": "010011",
    "D-M": "010011",
    "A-D": "000111",
    "M-D": "000111",
    "D&A": "000000",
    "D&M": "000000",
    "D|A": "010101",
    "D|M": "010101",
}


class HackTranslator(object):
    def __init__(self, lines):
        self.original = lines
        self.current = lines
        self.symbol_table = PREDEFINED_TABLE

    def _remove_comments(self):
        self.current = [
            remove_comment(line) for line in self.current if remove_comment(line)
        ]

    def _process_labels(self):
        """
        Process labels such as
        ```
        (LOOP)
        ```
            - Update symbol table
            - Update self.current removing labels
        """
        counter = 0
        result = []
        for line in self.current:
            word = extract_symbol(line)
            if word:
                if word not in self.symbol_table:
                    self.symbol_table[word] = counter
            else:
                result.append(line)
                counter += 1
        self.current = result

    def _process_symbols(self):
        new_address = 16
        res = []
        for line in self.current:
            if is_a_command(line) and (not line[1].isdecimal()):
                word = line[1:]
                if word:
                    if word in self.symbol_table:
                        address = self.symbol_table[word]
                        line = f"@{address}"
                    else:
                        self.symbol_table[word] = new_address
                        line = f"@{new_address}"
                        new_address += 1
            res.append(line)

        self.current = res

    def _codewrite(self):
        return [codewrite(line) for line in self.current]

    def _parse(self, verbose):
        if verbose:
            print("\n------ originally -------")
            self._show()

        self._remove_comments()
        if verbose:
            print("\n------ after removing comments -------")
            self._show()

        self._process_labels()
        if verbose:
            print("\n------ after removing labels -------")
            self._show()

        self._process_symbols()
        if verbose:
            print("\n------ after removing symbols -------")
            self._show()

    def _show(self):
        for line in self.current:
            print(line)

    def run(self, verbose=False):
        self._parse(verbose)
        bin_lines = self._codewrite()
        if verbose:
            print("\n----- Output Hack instructions -----")
            for line in bin_lines:
                print(line)
            print()

        return bin_lines


def _codewrite_c_line(line):
    assert not line.startswith("@")

    try:
        dest, rest = line.split("=")
    except ValueError:
        dest = ""
        rest = line

    try:
        command, jump = rest.split(";")
    except ValueError:
        command = rest
        jump = ""

    d = lookup_dest(dest)
    a, c = lookup_command(command)
    j = lookup_jump(jump)

    assert len(a) == 1
    assert len(c) == 6
    assert len(d) == 3
    assert len(j) == 3
    return f"111{a}{c}{d}{j}"


def _codewrite_a_line(line):
    assert line.startswith("@")
    bin_string = bin(int(line[1:]))[2:].zfill(15)
    return f"0{bin_string}"


def codewrite(line):
    if is_a_command(line):
        res = _codewrite_a_line(line)
    else:
        res = _codewrite_c_line(line)
    return res


def is_a_command(line):
    return line.strip().startswith("@")


def remove_comment(line):
    word, *_ = line.split("//")
    return word.strip()


def lookup_dest(word):
    d1 = int("A" in word)
    d2 = int("D" in word)
    d3 = int("M" in word)
    return f"{d1}{d2}{d3}"


def lookup_jump(word):
    return JUMP_TABLE[word]


def lookup_command(word):
    c = COMMAND_TABLE[word]
    a = str(int("M" in word))
    return a, c


def extract_symbol(line):
    line = line.strip()
    res = ""
    left = line.find("(")
    right = line.find(")")
    if 0 <= left < right:
        res = line[left + 1 : right].strip()
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help=".asm file to translate")
    parser.add_argument("-v", "--verbose", help="verbosity", action="store_true")
    args = parser.parse_args()
    with open(args.input, "r") as f:
        raw_lines = [line.rstrip() for line in f.readlines()]

    translator = HackTranslator(raw_lines)
    result_lines = translator.run(verbose=args.verbose)

    output_path_wo_ext, _ = os.path.splitext(args.input)
    output_path = output_path_wo_ext + ".hack"
    with open(output_path, "w") as f:
        for line in result_lines:
            print(line, file=f)


if __name__ == "__main__":
    main()
