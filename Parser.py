"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self._file = input_file.read().splitlines()
        i=len(self._file)-1
        while(i>=0):
            #serach for cmd in line
            has_cmd = self._file[i].find("//")
            if(has_cmd != -1):
                #delete cmd from line
                self._file[i] = self._file[i][:has_cmd]
            #delete speace?
            self._file[i] = self._file[i].strip()
            #delete empty lines
            if(self._file[i] == ''):
                del self._file[i]
            i-=1
        #initialise line counter
        self._line = 0
        pass

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if(self._line < len(self._file)):
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self._line += 1
        pass

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if("pop" in self._file[self._line]):
            return "C_POP"
        if("push" in self._file[self._line]):
            return "C_PUSH"
        if("label" in self._file[self._line]):
            return "C_LABEL"
        if("if-goto" in self._file[self._line]):
            return "C_IF"
        if("goto" in self._file[self._line]):
            return "C_GOTO"
        if("function" in self._file[self._line]):
            return "C_FUNCTION"
        if("call" in self._file[self._line]):
            return "C_CALL"
        if("return" in self._file[self._line]):
            return "C_RETURN"
        return "C_ARITHMETIC"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        cmd = self.command_type()
        if(cmd == "C_RETURN"):
            return
        if(cmd == "C_ARITHMETIC"):
            return self._file[self._line]
        speace = self._file[self._line].find(" ")
        var = self._file[self._line][speace+1:]
        if(cmd == "C_LABEL" or cmd == "C_GOTO" or cmd == "C_IF"):
            return var
        speace_2 = var.find(" ")
        return var[:speace_2]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        cmd = self.command_type()
        if(cmd != "C_PUSH" and cmd != "C_POP" and cmd != "C_FUNCTION" and cmd != "C_CALL"):
            return
        speace = self._file[self._line].find(" ")
        var = self._file[self._line][speace+1:]
        speace_2 = var.find(" ")
        return int(var[speace_2+1:])
