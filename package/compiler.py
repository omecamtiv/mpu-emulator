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


def compile(code: str):
    instructions = [e.name for e in Instructions]
    arg_instructions = ['OUTL', 'OUTR', 'MOVLA', 'MOVLB',
                        'MOVRA', 'MOVRB', 'MOVAR', 'MOVBR',
                        'JMPL', 'JMPR', 'JZFL', 'JZFR',
                        'JCFL', 'JCFR']
    mem_list = []
    error_code = 'Success'
    instructions_list = code.strip().split('\n')
    length = len(code.strip().split())
    if length > 256:
        error_code = 'OverflowError'
    elif length == 0:
        pass
    else:
        for i in instructions_list:
            cmd = i.split()
            if cmd[0] in instructions:
                if cmd[0] in arg_instructions:
                    arg = cmd[1]
                    try:
                        d = int(arg, 16)
                        opcode = int(Instructions.find_opcode(
                            cmd[0]),
                            16)
                        mem_list.append(opcode)
                        mem_list.append(d)
                    except:
                        error_code = 'ArgumentError'
                else:
                    opcode = int(Instructions.find_opcode(
                        cmd[0]),
                        16)
                    mem_list.append(opcode)
            else:
                error_code = 'InstructionError'

    return mem_list, error_code


if __name__ == '__main__':
    txt = "MOVLA AB\nOUTA\nHALT"
    l, e = compile(txt)
    print(l)
    print(e)
