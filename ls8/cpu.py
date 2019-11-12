"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 7 + [0xF4]
        self.pc = 0
        self.fl = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # Dynamically opens a .ls8 file, depending on the argv
        program = []

        rel_file = sys.argv[1]
        f = open(rel_file)
        f_lines = f.readlines()
        for lines in f_lines:
            if len(lines) == 1:
                continue
            if lines[0] == '#':
                continue
            program.append(int('0b' + lines[:8], 2))

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        for instruction in program:
            self.ram_write(address, instruction)
            address += 1

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # Hard coding instructions
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        MUL = 0b10100010

        halted = False
        while not halted:
            # Instruction Register, and operand declaration
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Check instruction, if we can't hard code instructions
            # binary_IR = format(IR, '08b') # String in binary form

            # num_of_operands = binary_IR[:2] 
            # if num_of_operands == '10': # bit-shift to right by 6, if 1 then
            #     operand_a = self.ram_read(self.pc + 1)
            #     operand_b = self.ram_read(self.pc + 2)
            # elif num_of_operands == '01': # bit-shift to right by 6, if 0 then
            #     operand_a = self.ram_read(self.pc + 1)

            # alu_op = binary_IR[2] # If '1' - there's an ALU operation
            # set_pc = binary_IR[3] # If '1' - we are setting PC
            # instruction_identifier = binary_IR[4:]

            if IR == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 2

            if IR == PRN:
                print(self.reg[operand_a])
                self.pc += 1

            if IR == HLT:
                halted = True

            if IR == MUL:
                self.alu('MUL', operand_a, operand_b)
                self.pc += 2

            self.pc += 1

            # If pc == 256, reset pc
            if self.pc == 256:
                self.pc = 0
