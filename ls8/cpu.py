"""CPU functionality."""

import sys

LDI  = "0010"
PRN  = "0111"
HLT  = "0001"
ADD  = "0000"
MULT = "0010"
PUSH = "0101"
POP  = "0110"
CALL = "0000"
RET  = "0001"

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 255
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 0xF4
        self.branchtable = {}
        self.branchtable[LDI]  = self.handle_LDI
        self.branchtable[PRN]  = self.handle_PRN
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP

    def handle_LDI(self, register, immediate):
        self.reg[register] = immediate
    
    def handle_PRN(self, register):
        value = self.reg[register]
        print(value)

    def handle_PUSH(self, register):
        value = self.reg[register]
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram_write(value, sp)
    
    def handle_POP(self, Register):
        sp = self.reg[7]
        value = self.ram_read(sp)
        self.reg[Register] = value
        self.reg[7] += 1

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory from a file."""

        if len(sys.argv) < 2:
            print('Please provide file name')
        try:
            with open(sys.argv[1]) as file:
                address = 0
                for line in file:
                    split_line = line.split('#')
                    command = split_line[0]
                    command = command.strip(" \n")
                    if len(command) > 0:
                        if command[0] == '1' or command[0] == '0':
                            self.ram_write(int(command, 2), address)
                            address += 1

        except FileNotFoundError:
            print('Sorry file does not exist')


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # bitwise-AND the result with 0xFF (255) to keep the register values between 0-255.
        if op == ADD:
            result = self.reg[reg_a] + self.reg[reg_b]
        elif op == MULT:
            result = self.reg[reg_a] * self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
        mask = "11111111"
        self.reg[reg_a] = f"{result & int(mask, 2)}"

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
        running = True
        while running:
            # self.trace()            

            IR = f'{self.ram_read(self.pc):08b}'
            IR_int = int(IR, 2)
            # get the number of operands by shifting IR 6 positions
            num_operands = IR_int >> 6
            # get the ALU flag by masking and shifting 5 positions
            alu_mask = "00100000"
            alu = (int(IR, 2) & int(alu_mask, 2)) >> 5
            # get the PC flag by masking and shifting 4 positions
            pc_mask = "00010000"
            pc_set = (int(IR, 2) & int(pc_mask, 2)) >> 4
            # get the Instruction identifier by masking the last 4 bites
            mask = "00001111"
            instruction = f"{int(IR, 2) & int(mask, 2):04b}"
            
            if alu != 1: # not an ALU operation
                if pc_set == 0:
                    if instruction == HLT:
                        running = False
                        return
                    if num_operands == 0:
                        self.branchtable[instruction]()
                    if num_operands == 1:
                        register = self.ram_read(self.pc + 1)
                        self.branchtable[instruction](register)
                    if num_operands == 2:
                        register = self.ram_read(self.pc + 1)
                        immediate = self.ram_read(self.pc + 2)
                        self.branchtable[instruction](register, immediate)
                elif pc_set == 1:
                    if instruction == CALL:
                        # save next instruction to the stack
                        self.reg[7] -= 1
                        sp = self.reg[7]
                        return_location = self.pc + 2
                        self.ram_write(return_location, sp)

                        # set pc to the address in register
                        register = self.ram_read(self.pc + 1)
                        self.pc = self.reg[register]
                        continue

                    elif instruction == RET:
                        # pop return location from stack
                        sp = self.reg[7]
                        return_location = self.ram_read(sp)
                        self.pc = return_location
                        continue

            elif alu == 1: # ALU operation
                register1 = self.ram_read(self.pc + 1)
                register2 = self.ram_read(self.pc + 2)
                self.alu(instruction, register1, register2)
            self.pc += num_operands + 1
