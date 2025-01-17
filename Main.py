"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO,
        bootstrap: bool) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
        bootstrap (bool): if this is True, the current file is the 
            first file we are translating.
    """
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)
    output_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    code_writer.set_file_name(output_filename)
    if(bootstrap):
        code_writer.bootstrap()
    while(parser.has_more_commands()):
        cmd = parser.command_type()
        if(cmd == "C_ARITHMETIC"):
            arg1 = parser.arg1()
            code_writer.write_arithmetic(arg1)
        elif(cmd == "C_PUSH" or cmd == "C_POP"):
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            code_writer.write_push_pop(cmd, arg1, arg2)
        elif(cmd == "C_LABEL" or cmd == "C_GOTO" or cmd == "C_IF"):
            arg1 = parser.arg1()
            if(cmd == "C_LABEL"):
                code_writer.write_label(arg1)
            elif(cmd == "C_GOTO"):
                code_writer.write_goto(arg1)
            else:
                code_writer.write_if(arg1)
        elif(cmd == "C_FUNCTION"):
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            code_writer.write_function(arg1, arg2)
        elif(cmd == "C_CALL"):
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            code_writer.write_call(arg1 , arg2)
        else: #cmd == "C_RETURN"
            code_writer.write_return()
        parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
    
    """input_path = "BasicLoop.vm"
    output_path = "BasicLoop.asm"
    output_file = open(output_path, 'w')
    bootstrap = False
    with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)"""
