"""CPU functionality."""

import sys

class BranchTable:
    def __init__(self):
        self.branchtable = {}
        self.branchtable['LDI'] = self.handle_ldi
        self.branchtable['PRN'] = self.handle_prn
        self.branchtable['HLT'] = self.handle_hlt
        self.branchtable['MUL'] = self.handle_mul

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

        if len(sys.argv) != 2:
            print("Usage: comp.py filename")
            sys.exit(1)

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

        if op == 0b0000: # "ADD"
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b0010: # "MUL"
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

            # --- Bitwise operators ---
            num_of_operands = IR >> 6 
            alu_op = (IR & 0b00100000) >> 5 # If '1' - there's an ALU operation
            set_pc = (IR & 0b00010000) >> 4 # If '1' - we are setting PC
            instruction_identifier = IR & 0b00001111

            if alu_op == 0b1:
                self.alu(instruction_identifier, operand_a, operand_b)
            elif set_pc == 0b1:
                pass
            else:
                if IR == LDI:
                    self.reg[operand_a] = operand_b

                if IR == PRN:
                    print(self.reg[operand_a])

                if IR == HLT:
                    halted = True

            self.pc += num_of_operands + 1

            # If pc == 256, reset pc
            if self.pc >= 256:
                self.pc = 0
