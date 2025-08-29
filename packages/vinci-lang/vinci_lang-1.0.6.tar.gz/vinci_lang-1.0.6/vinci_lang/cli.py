import argparse
import random
import os

# VINCI is a general-purpose programming language
# https://seafoodstudios.com
# By SeafoodStudios

class VINCI:
    def __init__(self):
        self.memory = 0
        self.variables = {}
        self.log = []
    def basic_runline(self, line):
        try:
            basic_parser = line.split(" ")
            if basic_parser[0] == "VALUE":
                if len(basic_parser) == 2:
                    try:
                        float(basic_parser[1])
                    except ValueError:
                        raise RuntimeError("ERROR: Must be numerical.")
                    self.memory = float(basic_parser[1])
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "ADD":
                if len(basic_parser) == 3:
                    if basic_parser[1].isalpha() and basic_parser[2].isalpha():
                        if (basic_parser[1] in self.variables) and (basic_parser[2] in self.variables):
                            self.memory = self.variables[basic_parser[1]] + self.variables[basic_parser[2]]
                        else:
                            raise RuntimeError("ERROR: Variable/s don't exist.")
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "MINUS":
                if len(basic_parser) == 3:
                    if basic_parser[1].isalpha() and basic_parser[2].isalpha():
                        if (basic_parser[1] in self.variables) and (basic_parser[2] in self.variables):
                            self.memory = self.variables[basic_parser[1]] - self.variables[basic_parser[2]]
                        else:
                            raise RuntimeError("ERROR: Variable/s don't exist.")
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "MULTIPLY":
                if len(basic_parser) == 3:
                    if basic_parser[1].isalpha() and basic_parser[2].isalpha():
                        if (basic_parser[1] in self.variables) and (basic_parser[2] in self.variables):
                            self.memory = self.variables[basic_parser[1]] * self.variables[basic_parser[2]]
                        else:
                            raise RuntimeError("ERROR: Variable/s don't exist.")
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "DIVIDE":
                if len(basic_parser) == 3:
                    if basic_parser[1].isalpha() and basic_parser[2].isalpha():
                        if (basic_parser[1] in self.variables) and (basic_parser[2] in self.variables):
                            self.memory = self.variables[basic_parser[1]] / self.variables[basic_parser[2]]
                        else:
                            raise RuntimeError("ERROR: Variable/s don't exist.")
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "SET":
                if len(basic_parser) == 2:
                    if basic_parser[1].isalpha():
                        self.variables[basic_parser[1]] = self.memory
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "LOAD":
                if len(basic_parser) == 2:
                    if basic_parser[1].isalpha():
                        if basic_parser[1] in self.variables:
                            self.memory = self.variables[basic_parser[1]]
                        else:
                            raise RuntimeError("ERROR: Variable does not exist.")
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")  
            elif basic_parser[0] == "INPUT":
                if len(basic_parser) == 2:
                    if basic_parser[1].isalpha():
                        userinput = input("INPUT NUMBERS: ")
                        try:
                            float(userinput)
                        except ValueError:
                            raise RuntimeError("USER ERROR: Input must be numerical.")
                        self.variables[basic_parser[1]] = float(userinput)
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "COMMENT":
                return
            elif basic_parser[0] == "LABEL":
                return
            elif basic_parser[0] == "RANDOM":
                if len(basic_parser) == 3:
                    try:
                        lower = float(basic_parser[1])
                        upper = float(basic_parser[2])
                    except Exception as e:
                        raise RuntimeError(f"ERROR: Must be float: {e}")
                    self.memory = random.uniform(lower, upper)
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "OUTPUT":
                if len(basic_parser) == 2:
                    if basic_parser[1].isalpha():
                        print(self.variables[basic_parser[1]])
                    else:
                        raise RuntimeError("ERROR: Must be alphabetical.")
                else:
                    raise RuntimeError("ERROR: Incorrect argument amount.")
            elif basic_parser[0] == "LOG":
                parsed_output = ""
                index = 0
                for char in line:
                    index+=1
                    if index > 4:
                        parsed_output = parsed_output + char
                print(parsed_output)
            elif basic_parser[0] == "OUTPUTCHAR":
                text = ""
                try:
                    for i in range(1, len(basic_parser)):
                        text = text + chr(int(self.variables[basic_parser[i]]))
                except Exception as e:
                    raise RuntimeError(f"ERROR: ASCII Error: {e}")
                    
                print(text)
            elif basic_parser[0] == "INPUTCHAR":
                text = input("INPUT CHARACTERS: ")
                characters = list(text)
                if len(characters) == len(basic_parser)-1:
                    try:
                        for i in range(1, len(basic_parser)):
                            self.variables[basic_parser[i]] = ord(characters[i-1])
                    except Exception as e:
                        raise RuntimeError(f"ERROR: ASCII Error: {e}")
                        
                else:
                    raise RuntimeError(f"USER ERROR: Input must be {len(basic_parser)-1} characters long.")
            else:
                raise RuntimeError("ERROR: Unknown command.")
        except KeyboardInterrupt:
            raise RuntimeError("USER ERROR: User stopped program.")
    def full_execution(self, code):
        line = 0
        try:
            full_parser = code.split("\n")
            labels = {}
            index = 0
            for j in full_parser:
                if not j.strip() or j.strip().startswith("COMMENT"):
                    index += 1
                    continue
                sub_parser = j.split(" ")
                if sub_parser[0] == "LABEL":
                    if len(sub_parser) == 2:
                        if sub_parser[1].isalpha():
                            labels[sub_parser[1]] = index
                        else:
                            raise RuntimeError("ERROR: Must be alphabetical.")
                    else:
                        raise RuntimeError("ERROR: Incorrect argument amount.")
                index += 1
            
            line = 0
            running = 1

            while running == 1:
                if not full_parser[line].strip() or full_parser[line].strip().startswith("COMMENT"):
                    line+=1
                    continue
                else:
                    jump_parser = full_parser[line].strip().split(" ")
                if jump_parser:
                    if jump_parser[0] == "JUMP":
                        if jump_parser[1].isalpha():
                            if jump_parser[1] in labels:
                                if len(jump_parser) == 2:
                                    line = labels[jump_parser[1]]
                                    continue
                                else:
                                    raise RuntimeError("ERROR: Incorrect argument amount.")
                            else:
                                raise RuntimeError("ERROR: Label does not exist.")
                        else:
                            raise RuntimeError("ERROR: Must be alphabetical.")
                    elif jump_parser[0] == "IFZEROJUMP":
                        if self.memory == 0:
                            if jump_parser[1].isalpha():
                                if jump_parser[1] in labels:
                                    if len(jump_parser) == 2:
                                        line = labels[jump_parser[1]]
                                        continue
                                    else:
                                        raise RuntimeError("ERROR: Incorrect argument amount.")
                                else:
                                    raise RuntimeError("ERROR: Label does not exist.")
                            else:
                                raise RuntimeError("ERROR: Must be alphabetical.")
                    elif jump_parser[0] == "EXIT":
                        if len(jump_parser) == 1:
                            running = 0
                        else:
                            raise RuntimeError("ERROR: Incorrect argument amount.")
                    else:
                        self.basic_runline(full_parser[line])
                    line += 1
                    if line >= len(full_parser):
                        running = 0
            return self.log
        except Exception as e:
            if line == 0:
                return [f"Error labeling: {str(e)}"]
            else:
                return [f"Error at line {line}: {str(e)}"]

def main():
    try:
        vinci = VINCI()
        
        parser = argparse.ArgumentParser(description="VINCI Programming Language")
        subparsers = parser.add_subparsers(dest="command")

        parser_init = subparsers.add_parser("init", help="Create/initialize a new .vinci file.")
        parser_init.add_argument("fileforinit", help="VINCI source file (.vinci).")
        
        parser_run = subparsers.add_parser("run", help="Run a VINCI program")
        parser_run.add_argument("fileforrun", help="VINCI source file (.vinci).")

        parser_info = subparsers.add_parser("info", help="Learn about VINCI")
        
        args = parser.parse_args()
        
        if args.command is None:
            print("VINCI Programming Language")
            print("'Study without desire spoils the memory, and it retains nothing that it takes in'")
            print("― Leonardo da Vinci")
            exit()
        if args.command == "init":
            if os.path.exists(args.fileforinit):
                print("File already exists, could not create file.")
            else:
                with open(args.fileforinit, 'w') as file:
                    file.write("COMMENT New VINCI file, generated by language file initializer.")
                print(f"File created at {args.fileforinit}")
        elif args.command == "run":
            with open(args.fileforrun, "r") as file:
                content = file.read()
            result = vinci.full_execution(content)
            for line in result:
                print(line)
        elif args.command == "info":
            print("VINCI Programming Language")
            print("By SeafoodStudios, find them at https://seafoodstudios.com/")
            print("VINCI is a general-purpose, number oriented programming language designed to be beginner friendly.")
            print("VINCI has a very unique syntax, and it requires a small learning curve. It has variables, which are the storage method. There is also memory, which is where calculations are performed. There are no loops or conditionals, because there is a JUMP method, allowing you to jump to LABELs in the program.")
            yesno = input("Would you like to learn about the commands? (y/n): ")
            if isinstance(yesno, str) and yesno == "y":
                print("Commands:")
                print("VALUE <number>: Assigns a numerical value to memory.")
                print("ADD <var1> <var2>: Adds two variables and stores the result in memory.")
                print("MINUS <var1> <var2>: Subtracts two variables and stores the result in memory.")
                print("MULTIPLY <var1> <var2>: Multiplies two variables and stores the result in memory.")
                print("DIVIDE <var1> <var2>: Divides two variables and stores the result in memory.")
                print("SET <var>: Saves the current memory value to a variable.")
                print("LOAD <var>: Loads the value of a variable into memory.")
                print("INPUT <var>: Prompts the user for input and stores the numerical input in a variable.")
                print("COMMENT <text>: Ignores the line, useful for comments in the code.")
                print("LABEL <label>: Defines a label to be used for jumps in the code.")
                print("RANDOM <min> <max>: Generates a random floating-point number between min and max and stores it in memory.")
                print("OUTPUT <var>: Outputs the value of a variable.")
                print("LOG <string>: Logs a string.")
                print("OUTPUTCHAR <var1> <var2> ...: Outputs characters corresponding to the ASCII values stored in the variables.")
                print("INPUTCHAR <var1> <var2> ...: Prompts the user for a string of characters and stores their ASCII values in the specified variables.")
                print("JUMP <label>: Jumps to the specified label.")
                print("IFZEROJUMP <label>: Jumps to the specified label if the memory value is zero.")
                print("EXIT: Exits the program.")
                print("""Some more 'odd' features of this language are that variable values and memory values can only be floats and labels and variable names can only be alphabetical.""")
                print("Thanks, and enjoy VINCI!")
            else:
                print("You have chosen not to learn about the commands. Exiting...")
                exit()
    except Exception as e:
        print("Fatal Error: " + str(e))
if __name__ == "__main__":
    main()
