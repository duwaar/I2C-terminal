#!/usr/bin/env python3
'''
A terminal interface for the i2c bus.
Elaine Jeffery
20 June 2018
'''

import smbus
from os import system

class I2CTerminal():
    '''
    Starts an I2C terminal.
    Note: Globally, "input" refers to input into the terminal/slave device,
    while "output" refers to output returned from the slave.
    '''

    def __init__(self, port=1):
        self.run = True
        self.out_form = "h"
        self.device = "0x0"

        self.port = port
        self.bus = smbus.SMBus(self.port) # Connect to the specified i2c port (i2c-1 by default).

        self.show_help()


    def show_help(self):
        '''
        Display the help menu.
        '''
        print("---------------------------------------------------------------------------------")
        print("Welcome to Russell's I2C bus terminal!                                           ")
        print("")
        print("After setting the device address, commands should be sent separated by spaces, in")
        print("the following order:                                                             ")
        print("read/write, register, data                                                       ")
        print("")
        print("Remember to include the base indicator at the beginning of the number, i.e. if   ")
        print("the number is hex, it should start with 0x...; if it is binary, it should        ")
        print("start with 0b...; or if it is octal, 0o... Decimal numbers are already decimal.  ")
        print("")
        print("---------------------------------------------------------------------------------")
        print(" Functon                  Example command                                        ")
        print("---------------------------------------------------------------------------------")
        print("-Set device address:      to 0x4e                                                ")
        print("-Send a read command:     r 0x10                                                 ")
        print("-Send a write command:    w 0x12 0b10011011                                      ")
        print("-Show this help:          help                                                   ")
        print("-Leave the terminal:      exit                                                   ")
        print("-Scan the bus:            scan                                                   ")
        print("-Set the output format:   out h                                                  ")
        print(" -Options: he(x), (b)in,                                                         ")
        print("  (d)ec, (t)wo's comp,                                                           ")
        print("  or (o)ctal.                                                                    ")
        print()


    def set_out(self, form):
        '''
        Set the format in which the output from the i2c device is shown.
        '''
        if form is "b" or "o" or "d" or "h" or "t":
            self.out_form = form
            print("out_form set to", self.out_form)
        else:
            print("Error: {} is not a valid output form.".format(form))


    def set_device(self, dev):
        '''
        Set the address of the i2c device on the bus.
        '''
        self.device = dev
        print("device set to", self.device)


    def convert_out(self, num):
        '''
        Convert an int message into the appropriate numerical format.
        '''
        if self.out_form == "h":
            print(hex(num))
        elif self.out_form == "b":
            print(bin(num))
        elif self.out_form == "d":
            print(num)
        elif self.out_form == "t":
            if num >= 128:
                print(num - 256)
            else:
                print(num)
        else:
            print("Problem with out_form.")


    def convert_in(self, num):
        '''
        Recognize hex (0x...), binary (0b...), octal (0o...), and decimal, and convert to decimal.
        '''
        if num[0:2] == "0x":
            new_num = int(num, 16)
        elif num[0:2] == "0b":
            new_num = int(num, 2)
        elif num[0:2] == "0o":
            new_num = int(num, 8)
        elif num.isnumeric():
            pass # Assume that the entered value is base-10.
        else:
            print("Error: {} is not a number.".format(num))
            raise ValueError

        return new_num


    def send_to_device(self, command):
        '''
        Send a read or write command to the given device address.
        '''
        # Must start with "r" AND have exactly two arguments to initiate a read.
        if command.split()[0] == "r" and len(command.split()) == 2:
            dev = self.convert_in(self.device)
            cmd = self.convert_in(command.split()[1])

            msg = self.bus.read_byte_data(dev, cmd)
            self.convert_out(msg)

        # Must start with "w" AND have exactly three arguments to initiate a write.
        elif command.split()[0] == "w" and len(command.split()) == 3:
            dev = self.convert_in(self.device)
            cmd = self.convert_in(command.split()[1])
            dat = self.convert_in(command.split()[2])

            self.bus.write_byte_data(dev, cmd, dat)


    def bus_scan(self):
        '''
        Display all devices on the bus.
        '''
        system("i2cdetect -y " + str(self.port))


    def prompt(self):
        '''
        Get a command from the user, and execute it.
        '''
        prompt_line = "i2c-" + str(self.port) + " " + str(self.device) + ": " # The prompt's status line.
        command = input(prompt_line) # Get the command.
        
        # Exit the terminal.
        if command == "exit":
            self.run = False
        # Display help.
        elif command == "help":
            self.show_help()
        # No command.
        elif command.strip() == '':
            pass
        # Set output format.
        elif command.split()[0] == "out":
            self.set_out(command.split()[1])
        # Set device address.
        elif command[0:2] == "to":
            self.set_device(command.split()[1])
        # Send a read or write command.
        elif command[0] == "r" or command[0] == "w":
            self.send_to_device(command)
        # Display devices on the bus.
        elif command == "scan":
            self.bus_scan()

        else:
            print("Command not supported.")


def main():
    term = I2CTerminal()

    while term.run == True:
        term.prompt()


main()
