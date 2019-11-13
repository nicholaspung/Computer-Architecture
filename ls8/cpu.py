"""CPU functionality."""

import sys

SP = 7
STACK_START = 0xF4

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = STACK_START # SP
        self.pc = 0
        self.fl = 0
        self.alu_dispatch = {
            0b0000: self.handle_add,
            0b0010: self.handle_mul
        }
        self.pc_dispatch = {}
        self.op_dispatch = {
            0b0010: self.handle_ldi,
            0b0111: self.handle_prn,
            0b0101: self.handle_push,
            0b0110: self.handle_pop
        }

    def handle_push(self, reg_value):
        if self.reg[SP] == 0:
            print("Stack Overflow, stopping CPU.")
            return

        # Decrement SP
        self.reg[SP] -= 1

        # Get address pointed by SP, copy given reg value into address
        self.ram[self.reg[SP]] = self.reg[reg_value]

    def handle_pop(self, reg_value):
        # Get value from SP, save to given reg value
        self.reg[reg_value] = self.ram[self.reg[SP]]

        # Increment SP
        self.reg[SP] += 1

        # If at bottom of stack, resets stack back to start
        if self.reg[SP] > STACK_START:
            print("Stack underflow, resetting stack.")
            self.reg[SP] = STACK_START

    def handle_ldi(self, op1, op2):
        self.reg[op1] = op2

    def handle_prn(self, op1):
        print(self.reg[op1])

    def handle_add(self, reg_a, reg_b):
        self.reg[reg_a] += self.reg[reg_b]

    def handle_mul(self, reg_a, reg_b):
        self.reg[reg_a] *= self.reg[reg_b]

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

        num_of_operands = op >> 6
        op_ii = op & 0b00001111

        if self.alu_dispatch[op_ii]:
            if num_of_operands == 0b01:
                self.alu_dispatch[op_ii](reg_a)
            else:
                self.alu_dispatch[op_ii](reg_a, reg_b)
        # if op == 0b0000: # "ADD"
        #     self.reg[reg_a] += self.reg[reg_b]
        # elif op == 0b0010: # "MUL"
        #     self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
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

            # Can create a dispatch table with all the codes
            # Then depending
            if alu_op == 0b1:
                self.alu(IR, operand_a, operand_b)
            elif set_pc == 0b1:
                pass
            else:
                if instruction_identifier == 0b1 and alu_op == 0b0 and set_pc == 0b0:
                    halted = True
                else:
                    if num_of_operands == 0b01:
                        self.op_dispatch[instruction_identifier](operand_a)
                    elif num_of_operands == 0b10:
                        self.op_dispatch[instruction_identifier](operand_a, operand_b)
                    else:
                        self.op_dispatch[instruction_identifier]()
                # if IR == LDI:
                #     self.reg[operand_a] = operand_b

                # if IR == PRN:
                #     print(self.reg[operand_a])

            self.pc += num_of_operands + 1

            # If pc == 256, reset pc
            if self.pc >= 256:
                self.pc = 0
