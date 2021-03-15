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
    def find_instruction(hexcode: str):
        for i in Instructions:
            if i.value == hexcode:
                return i


@unique
class BitWidth(Enum):
    TWO_BIT = 2
    FOUR_BIT = 4
    EIGHT_BIT = 8
    SIXTEEN_BIT = 16
    THIRTY_TWO_BIT = 32
    SIXTY_FOUR_BIT = 64

    def max_value(self):
        return 2 ** self.value - 1


class Register:
    def __init__(self, bit_width: BitWidth):
        self.bitWidth = bit_width
        self.maxValue = self.bitWidth.max_value()
        self.value = 0

    def set_value(self, value: int):
        if value > self.maxValue:
            value = value - self.maxValue
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self):
        return format(self.value, '02X')


class Counter:
    def __init__(self, bit_width: BitWidth):
        self.bitWidth = bit_width
        self.maxValue = self.bitWidth.max_value()
        self.value = 0

    def set_counter(self, address: int):
        assert 0 <= address <= self.maxValue
        self.value = address

    def get_counter(self):
        return self.value

    def inc_counter(self):
        self.value += 1
        if self.value > self.maxValue:
            self.value = 0

    def __str__(self):
        return format(self.value, '02X')


class RAM:
    def __init__(self, address_width: BitWidth, data_width: BitWidth):
        self.addressWidth = address_width
        self.dataWidth = data_width
        self.addressMaxValue = self.addressWidth.max_value()
        self.dataMaxValue = self.dataWidth.max_value()
        self.memory = dict()

    def read(self, address: int):
        if not (0 <= address <= self.addressMaxValue):
            raise RuntimeError("Invalid Address: " + hex(address))
        return self.memory.get(address, 0)

    def write(self, address: int, value: int):
        if value > self.dataMaxValue:
            value = value - self.dataMaxValue
        self.memory[address] = value

    def get_mem_list(self):
        mem_list = []
        for row in range(16):
            for col in range(16):
                mem_list.append(self.read(row * 16 + col))
        return mem_list


class CPU:
    def __init__(self):
        self.pc = Counter(BitWidth.EIGHT_BIT)
        self.reg_a = Register(BitWidth.EIGHT_BIT)
        self.reg_b = Register(BitWidth.EIGHT_BIT)
        self.reg_out = Register(BitWidth.EIGHT_BIT)
        self.ram_mem = RAM(BitWidth.EIGHT_BIT, BitWidth.EIGHT_BIT)
        self.reg_cz = Register(BitWidth.TWO_BIT)

        self.enable = False

        self.carry = False
        self.zero = False

        self.current_instruction = 0
        self.current_instruction_decoded = 0

    def is_enabled(self):
        return self.enable

    def set_enabled(self, status: bool):
        self.enable = status

    def set_instructions(self, commands: list):

        for i in range(self.ram_mem.addressMaxValue + 1):
            self.ram_mem.write(i,
                               commands[i]
                               if i < len(commands)
                               else 0)

    def reset(self):
        self.pc.set_counter(0)
        self.reg_a.set_value(0)
        self.reg_b.set_value(0)
        self.reg_out.set_value(0)

    def cz(self, num: int):
        c = ''
        z = ''
        if num == 0:
            z = '1'
            self.zero = True
        else:
            z = '0'
            self.zero = False
        if num > 255:
            c = '1'
            self.carry = True
        else:
            c = '0'
            self.carry = False
        return int(c+z, 2)

    def fetch(self):
        self.current_instruction = self.ram_mem.read(
            self.pc.get_counter())

    def decode(self):
        self.current_instruction_decoded = Instructions.find_instruction(
            format(self.current_instruction, '02X'))
        self.pc.inc_counter()

    def execute(self):
        i = self.current_instruction_decoded

        if i == Instructions.HALT:
            self.set_enabled(False)

        elif i == Instructions.OUTL:
            arg = self.ram_mem.read(self.pc.get_counter())
            self.reg_out.set_value(arg)
            self.pc.inc_counter()

        elif i == Instructions.OUTR:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_mem = self.ram_mem.read(arg)
            self.reg_out.set_value(arg_mem)
            self.pc.inc_counter()

        elif i == Instructions.OUTA:
            arg_a = self.reg_a.get_value()
            self.reg_out.set_value(arg_a)

        elif i == Instructions.OUTB:
            arg_b = self.reg_b.get_value()
            self.reg_out.set_value(arg_b)

        elif i == Instructions.MOVLA:
            arg = self.ram_mem.read(self.pc.get_counter())
            self.reg_a.set_value(arg)
            self.pc.inc_counter()

        elif i == Instructions.MOVLB:
            arg = self.ram_mem.read(self.pc.get_counter())
            self.reg_b.set_value(arg)
            self.pc.inc_counter()

        elif i == Instructions.MOVRA:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_mem = self.ram_mem.read(arg)
            self.reg_a.set_value(arg_mem)
            self.pc.inc_counter()

        elif i == Instructions.MOVRB:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_mem = self.ram_mem.read(arg)
            self.reg_b.set_value(arg_mem)
            self.pc.inc_counter()

        elif i == Instructions.MOVAR:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_a = self.reg_a.get_value()
            self.ram_mem.write(arg, arg_a)
            self.pc.inc_counter()

        elif i == Instructions.MOVBR:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_b = self.reg_b.get_value()
            self.ram_mem.write(arg, arg_b)
            self.pc.inc_counter()

        elif i == Instructions.ADDA:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_a.set_value(arg_a+arg_b)
            self.reg_cz.set_value(self.cz(arg_a+arg_b))

        elif i == Instructions.ADDB:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_b.set_value(arg_a+arg_b)
            self.reg_cz.set_value(self.cz(arg_a+arg_b))

        elif i == Instructions.SUBBA:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_a.set_value(arg_a-arg_b)
            self.reg_cz.set_value(self.cz(arg_a-arg_b))

        elif i == Instructions.SUBAB:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_b.set_value(arg_b-arg_a)
            self.reg_cz.set_value(self.cz(arg_b-arg_a))

        elif i == Instructions.ANDA:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_a.set_value(arg_a & arg_b)
            self.reg_cz.set_value(self.cz(arg_b & arg_a))

        elif i == Instructions.ANDB:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_b.set_value(arg_a & arg_b)
            self.reg_cz.set_value(self.cz(arg_b & arg_a))

        elif i == Instructions.ORA:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_b.set_value(arg_a | arg_b)
            self.reg_cz.set_value(self.cz(arg_b | arg_a))

        elif i == Instructions.ORB:
            arg_a = self.reg_a.get_value()
            arg_b = self.reg_b.get_value()
            self.reg_b.set_value(arg_a | arg_b)
            self.reg_cz.set_value(self.cz(arg_b | arg_a))

        elif i == Instructions.JMPL:
            arg = self.ram_mem.read(self.pc.get_counter())
            self.pc.set_counter(arg)

        elif i == Instructions.JMPR:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_mem = self.ram_mem.read(arg)
            self.pc.set_counter(arg_mem)

        elif i == Instructions.JMPA:
            arg_a = self.reg_a.get_value()
            self.pc.set_counter(arg_a)

        elif i == Instructions.JMPB:
            arg_b = self.reg_b.get_value()
            self.pc.set_counter(arg_b)

        elif i == Instructions.JZFL:
            arg = self.ram_mem.read(self.pc.get_counter())
            if self.zero:
                self.pc.set_counter(arg)
            else:
                self.pc.inc_counter()

        elif i == Instructions.JZFR:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_mem = self.ram_mem.read(arg)
            if self.zero:
                self.pc.set_counter(arg_mem)
            else:
                self.pc.inc_counter()

        elif i == Instructions.JZFA:
            arg_a = self.reg_a.get_value()
            if self.zero:
                self.pc.set_counter(arg_a)

        elif i == Instructions.JZFB:
            arg_b = self.reg_b.get_value()
            if self.zero:
                self.pc.set_counter(arg_b)

        elif i == Instructions.JCFL:
            arg = self.ram_mem.read(self.pc.get_counter())
            if self.carry:
                self.pc.set_counter(arg)
            else:
                self.pc.inc_counter()

        elif i == Instructions.JCFR:
            arg = self.ram_mem.read(self.pc.get_counter())
            arg_mem = self.ram_mem.read(arg)
            if self.carry:
                self.pc.set_counter(arg_mem)
            else:
                self.pc.inc_counter()

        elif i == Instructions.JCFA:
            arg_a = self.reg_a.get_value()
            if self.carry:
                self.pc.set_counter(arg_a)

        elif i == Instructions.JCFB:
            arg_b = self.reg_b.get_value()
            if self.carry:
                self.pc.set_counter(arg_b)

    def __str__(self):
        output_str = ""

        output_str += "RegA:\t"+self.reg_a.__str__()+"\n"
        output_str += "RegB:\t"+self.reg_b.__str__()+"\n"
        output_str += "  PC:\t"+self.pc.__str__()+"\n"
        output_str += "  CZ:\t"+self.reg_cz.__str__()+"\n"
        output_str += " RAM:\n\n"+self.ram_mem.__str__()+"\n"
        return output_str


if __name__ == '__main__':
    cpu = CPU()
    mem_list = [17, 255, 18, 25, 33, 0]
    cpu.set_instructions(mem_list)
    cpu.set_enabled(True)
    while cpu.is_enabled():
        cpu.fetch()
        cpu.decode()
        cpu.execute()
    print(cpu)
    print(cpu.carry)
