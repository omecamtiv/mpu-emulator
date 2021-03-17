from enum import Enum, unique


@unique
class Instructions(Enum):
    HALT = "00"
    OUTL = "01"
    OUTR = "02"
    OUTA = "03"
    OUTB = "04"
    MOVLA = "11"
    MOVLB = "12"
    MOVRA = "13"
    MOVRB = "14"
    MOVAR = "15"
    MOVBR = "16"
    ADDA = "21"
    ADDB = "22"
    SUBBA = "23"
    SUBAB = "24"
    ANDA = "31"
    ANDB = "32"
    ORA = "33"
    ORB = "34"
    JMPL = "41"
    JMPR = "42"
    JMPA = "43"
    JMPB = "44"
    JZFL = "51"
    JZFR = "52"
    JZFA = "53"
    JZFB = "54"
    JCFL = "61"
    JCFR = "62"
    JCFA = "63"
    JCFB = "64"

    @staticmethod
    def find_opcode(instruction: str):
        val = ''
        for i in Instructions:
            if i.name == instruction:
                val = i.value
                break
            else:
                val = Instructions.HALT.value
        return val


@unique
class CompilerError(Enum):
    NoError = 0
    InstructionError = 1
    ArgumentError = 2
    LabelError = 3
    MaxInstructionsError = 4


class Compiler:
    def __init__(self, list: list):
        self.list = list
        self.instructions = [e.name for e in Instructions]
        self.arg_instructions = ['OUTL', 'OUTR', 'MOVLA',
                                 'MOVLB', 'MOVRA', 'MOVRB',
                                 'MOVAR', 'MOVBR', 'JMPL',
                                 'JMPR', 'JZFL', 'JZFR',
                                 'JCFL', 'JCFR']
        self.label = "#"
        self.counter = 0
        self.mem_dict = dict()
        self.error_code = CompilerError.NoError

    @staticmethod
    def checkHex(hexstring: str):
        try:
            int(hexstring, 16)
            return True
        except ValueError:
            return False

    def checkInstruction(self, instruction: str):
        if instruction in self.instructions:
            return True
        else:
            return False

    def checkArg(self, instruction: str):
        b = False
        if instruction in self.arg_instructions:
            b = True
        return b

    def checkLabel(self, instruction: str):
        b = False
        if instruction[:1] == self.label:
            b = True
        return b

    def getCount(self):
        return self.counter

    def compile(self):
        n = 0
        while n < len(self.list):
            i = self.list[n]
            if self.checkInstruction(i):
                pos = self.counter
                opcode = Instructions.find_opcode(i)
                self.mem_dict[pos] = opcode
                self.counter += 1
                if self.checkArg(i):
                    pos = self.counter
                    n += 1
                    arg = self.list[n]
                    if self.checkHex(arg):
                        self.mem_dict[pos] = arg
                        self.counter += 1
                    else:
                        self.error_code = CompilerError.ArgumentError
                        break
            else:
                if self.checkLabel(i):
                    label = i[1:]
                    if self.checkHex(label):
                        c = int(label, 16)
                        if c not in self.mem_dict:
                            self.counter = c
                        else:
                            self.error_code = CompilerError.LabelError
                            break
                    else:
                        self.error_code = CompilerError.LabelError
                        break
                else:
                    self.error_code = CompilerError.InstructionError
                    break
            n += 1

        if self.getCount() >= 256:
            self.error_code = CompilerError.MaxInstructionsError
        if self.error_code == CompilerError.NoError:
            mem_list = []
            for i in range(256):
                mem_list.append(self.mem_dict.get(i, "00"))
            return [int(e, 16) for e in mem_list], self.error_code
        else:
            return [], self.error_code


if __name__ == '__main__':
    txt = "#0A\nMOVLA AB\nOUTA\nHALT\n#0E\nMOVLA BA\nOUTA\nHALT"
    compiler = Compiler(txt.split())
    l, e = compiler.compile()
    print(l)
    print(e.name)
