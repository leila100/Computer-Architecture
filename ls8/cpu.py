"""CPU functionality."""

import sys

LDI  = 0b10000010
PRN  = 0b01000111
HLT  = 0b00000001 
ADD  = 0b10100000
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
AND  = 0b10101000
OR   = 0b10101010
XOR  = 0b10101011
NOT  = 0b01101001
SHL  = 0b10101100
SHR  = 0b10101101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 0xF4
        self.fl = 0b00000000 # 0b00000LGE
        self.branchtable = {
            HLT: self.handle_HLT,
            LDI: self.handle_LDI,
            PRN: self.handle_PRN,
            ADD: self.handle_ADD,
            MUL: self.handle_MUL,
            PUSH: self.handle_PUSH,
            POP: self.handle_POP,
            CALL: self.handle_CALL,
            RET: self.handle_RET,
            CMP: self.handle_CMP,
            JMP: self.handle_JMP,
            JEQ: self.handle_JEQ,
            JNE: self.handle_JNE,
            AND: self.handle_AND,
            OR: self.handle_OR,
            XOR: self.handle_XOR,
            NOT: self.handle_NOT,
            SHL: self.handle_SHL,
            SHR: self.handle_SHR
        }
    def handle_HLT(self, registera, registerb):
        self.running = False

    def handle_LDI(self, register, immediate):
        self.reg[register] = immediate
    
    def handle_PRN(self, register_a, register_b):
        value = self.reg[register_a]
        print(value)
    
    def handle_ADD(self, register_a, register_b):
        self.alu(ADD, register_a, register_b)
    
    def handle_MUL(self, register_a, register_b):
        self.alu(MUL, register_a, register_b)

    def handle_PUSH(self, register_a, register_b):
        value = self.reg[register_a]
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram_write(value, sp)
    
    def handle_POP(self, register_a, register_b):
        sp = self.reg[7]
        value = self.ram_read(sp)
        self.reg[register_a] = value
        self.reg[7] += 1
    
    def handle_CALL(self, register_a, register_b):
        # save next instruction to the stack
        self.reg[7] -= 1
        sp = self.reg[7]
        return_location = self.pc + 2
        self.ram_write(return_location, sp)

        # set pc to the address in register
        register = self.ram_read(self.pc + 1)
        self.pc = self.reg[register]
    
    def handle_RET(self, register_a, register_b):
        # pop return location from stack
        sp = self.reg[7]
        return_location = self.ram_read(sp)
        self.pc = return_location

    def handle_CMP(self, register_a, register_b):
        '''
        Compare the values in two registers.
        If they are equal, set the Equal E flag to 1, otherwise set it to 0.
        If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
        If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
        '''
        value1 = self.reg[register_a]
        value2 = self.reg[register_b]
        if value1 == value2:
            mask = 0b00000001
            self.fl = self.fl | mask # set the E flag to 1
        else:
            mask = 0b11111110
            self.fl = self.fl & mask # set the E flag to 0
        
        if value1 < value2:
            mask = 0b00000100
            self.fl = self.fl | mask # set the L flag to 1
        else:
            mask = 0b11111011
            self.fl = self.fl & mask # set the L flag to 0

        if value1 > value2:
            mask = 0b00000010
            self.fl = self.fl | mask # set the G flag to 1
        else:
            mask = 0b11111101
            self.fl = self.fl & mask # set the G flag to 0
    
    def handle_JMP(self, register_a, register_b):
        '''
        Jump to the address stored in the given register.
        Set the PC to the address stored in the given register.
        '''
        jump_to_address = self.reg[register_a]
        self.pc = jump_to_address

    def handle_JEQ(self, register_a, register_b):
        '''
        If equal flag is set (true), jump to the address stored in the given register.
        '''
        mask = 0b00000001
        E_flag = mask & self.fl
        if E_flag == 1:
            self.handle_JMP(register_a, register_b)
        else:
            self.pc += 2

    def handle_JNE(self, register_a, register_b):
        '''
        If E flag is clear (false, 0), jump to the address stored in the given register.
        '''
        mask = 0b00000001
        E_flag = mask & self.fl
        if E_flag == 0:
            self.handle_JMP(register_a, register_b)
        else:
            self.pc += 2

    def handle_AND(self, register_a, register_b):
        '''
        Bitwise-AND the values in registerA and registerB, then store the result in registerA.
        '''
        self.alu(AND, register_a, register_b)
    
    def handle_OR(self, register_a, register_b):
        '''
        Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
        '''
        self.alu(OR, register_a, register_b)
    
    def handle_XOR(self, register_a, register_b):
        '''
        Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
        '''
        self.alu(XOR, register_a, register_b)

    def handle_NOT(self, register_a, register_b):
        '''
        Perform a bitwise-NOT on the value in a register.
        '''
        self.alu(NOT, register_a, register_b)
    
    def handle_SHL(self, register_a, register_b):
        '''
        Shift the value in registerA left by the number of bits specified in registerB, filling the low bits with 0.
        '''
        self.alu(SHL, register_a, register_b)

    def handle_SHR(self, register_a, register_b):
        '''
        Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.
        '''
        self.alu(SHR, register_a, register_b)

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
        if op == ADD:
            # result = self.reg[reg_a] + self.reg[reg_b]
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == AND:
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == XOR:
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == SHL:
            shift_value = self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] << shift_value
        elif op == SHR:
            print(f"before {self.reg[reg_a]:08b}")
            shift_value = self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] >> shift_value
            print(f"after {self.reg[reg_a]:08b}")
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
        while self.running:
            IR = self.ram_read(self.pc)
            num_operands = IR >> 6
            pc_mask = 0b00010000
            pc_set = (IR & pc_mask) >> 4

            if IR in self.branchtable:
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                self.branchtable[IR](operand_a, operand_b)
                if pc_set != 1:
                    self.pc += num_operands + 1
            else:
                print("Instruction not valid")