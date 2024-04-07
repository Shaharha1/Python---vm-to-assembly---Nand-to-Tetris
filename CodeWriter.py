"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self._file = output_stream
        self._name = ""
        self._counter = 0
        self._call_counter = 0
        pass

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self._name = filename
        pass

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self._file.write("//"+command+"\n")
        self._sp_sub() #SP--
        if(command == "add" or command == "sub" or command == "eq" or command == "gt" or command == "lt" or command == "and" or command == "or"):
            self._d_eq_sp_ptr() #D=y
            self._sp_sub() #SP--
            self._file.write("A=M\n") #M=X
            if(command == "add"):
                self._file.write("M=D+M\n") #X+Y
            elif(command == "sub"):
                self._file.write("M=M-D\n") #X-Y
            elif(command == "eq"):
                self._file.write("D=D-M\n") #if D-M==0 -> true
                self._a_cmd("zero"+str(self._counter)) #@zero counter
                self._file.write("D;JEQ\n")
                self._insert_false() #*SP=0
                self._a_cmd("final"+str(self._counter)) #@final counter
                self._file.write("D;JMP\n")
                self._l_cmd("zero"+str(self._counter)) #(zero counter)
                self._insert_true() #*SP=-1
                self._l_cmd("final"+str(self._counter)) #(final counter)
                self._counter+=1
            elif(command == "gt"):
                self._file.write("D=M-D\n") #if D-M > 0 -> true
                self._a_cmd("zero"+str(self._counter)) #@zero counter
                self._file.write("D;JGT\n")
                self._insert_false() #*SP=0
                self._a_cmd("final"+str(self._counter)) #@final counter
                self._file.write("D;JMP\n")
                self._l_cmd("zero"+str(self._counter)) #(zero counter)
                self._insert_true() #*SP=-1
                self._l_cmd("final"+str(self._counter)) #(final counter)
                self._counter+=1
            elif(command == "lt"):
                self._file.write("D=M-D\n") #if D-M < 0 -> true
                self._a_cmd("zero"+str(self._counter)) #@zero counter
                self._file.write("D;JLT\n")
                self._insert_false() #*SP=0
                self._a_cmd("final"+str(self._counter)) #@final counter
                self._file.write("D;JMP\n")
                self._l_cmd("zero"+str(self._counter)) #(zero counter)
                self._insert_true() #*SP=-1
                self._l_cmd("final"+str(self._counter)) #(final counter)
                self._counter+=1
            elif(command == "and"):
                self._file.write("M=D&M\n") #M = D&M
            elif(command == "or"):
                self._file.write("M=D|M\n") #M = D|M
        else:
            self._file.write("@SP\n") #M=*SP
            self._file.write("A=M\n")
            if(command == "neg"):
                self._file.write("M=-M\n") #-Y
            elif(command == "not"):
                self._file.write("M=!M\n") #*SP = !(*SP)
        self._sp_plus() #SP++

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        self._file.write("//"+command+" "+segment+" "+str(index)+"\n")
        if(command == "C_PUSH"):
            if(segment == "local" or segment == "argument" or segment == "this" or segment == "that"):
                if(segment == "local"):
                    cmd = "LCL"
                elif(segment == "argument"):
                    cmd = "ARG"
                elif(segment == "this"):
                    cmd = "THIS"
                else:
                    cmd = "THAT"
                self._a_cmd(cmd) #@cmd
                self._file.write("D=M\n") #D=*(cmd)
                self._a_cmd(str(index)) #A=index (@index)
                self._file.write("A=A+D\n") #A=*(cmd) + index
                self._file.write("D=M\n") #D=*addr
                self._sp_ptr_eq_d() #*SP=*addr(D)
                self._sp_plus() #SP++ 
            elif(segment == "constant"):
                self._a_cmd(str(index)) #@index
                self._file.write("D=A\n") #D=index
                self._sp_ptr_eq_d() #*SP=index
                self._sp_plus() #SP++
            elif(segment == "static"):
                self._file.write("@"+self._name+"."+str(index)+"\n") #@FOO.index (in symbolTable translate to 16+index)
                self._file.write("D=M\n") #D=*(Static i)
                self._sp_ptr_eq_d() #*SP = @FOO.index
                self._sp_plus() #SP++ 
            elif(segment == "temp"):
                num = 5 + int(index)
                self._a_cmd(str(num)) #@temp i 
                self._file.write("D=M\n") #D=*(temp i)
                self._sp_ptr_eq_d() #*SP = *addr(D)
                self._sp_plus() #SP++ 
            elif(segment == "pointer"):
                if(int(index) == 1):
                    self._a_cmd("THAT") #@THAT
                    self._file.write("D=M\n")
                    """self._a_cmd(str(index)) #@index
                    self._file.write("A=A+D\n") #A=pointer index
                    self._file.write("D=M\n") #D=*(pointer index)"""
                else:
                    self._a_cmd("THIS") #@THIS
                    self._file.write("D=M\n")
                    """self._a_cmd(str(index)) #@index
                    self._file.write("A=A+D\n") #A=pointer index
                    self._file.write("D=M\n") #D=*(pointer index)"""
                self._sp_ptr_eq_d() #*SP = D
                self._sp_plus() #SP++
        elif(command == "C_POP"):
            if(segment == "local" or segment == "argument" or segment == "this" or segment == "that"):
                if(segment == "local"):
                    cmd = "LCL"
                elif(segment == "argument"):
                    cmd = "ARG"
                elif(segment == "this"):
                    cmd = "THIS"
                else:
                    cmd = "THAT"
                self._sp_sub() #SP--
                self._d_eq_sp_ptr() #D=*SP
                self._a_cmd(cmd) #@cmd
                self._file.write("A=M\n")
                i=0
                int_index = int(index)
                while(i<int_index): #@*(cmd+i)
                    self._file.write("A=A+1\n")
                    i+=1                
                self._file.write("M=D\n")#M = D
            elif(segment == "static"):
                self._sp_sub() #SP--
                self._d_eq_sp_ptr() #D=*SP
                self._file.write("@"+self._name+"."+str(index)+"\n") #@FOO.index
                self._file.write("M=D\n") #@*(FOO.index) = D
            elif(segment == "temp"):
                num = 5 + int(index)
                self._sp_sub() #SP--
                self._d_eq_sp_ptr() #D=*SP
                self._a_cmd(str(num)) #@temp i
                self._file.write("M=D\n") #*addr = *SP
            elif(segment == "pointer"):
                self._sp_sub() #SP--
                self._d_eq_sp_ptr() #D=*SP
                if(int(index) == 1):
                    self._file.write("@THAT\n")
                else:
                    self._file.write("@THIS\n")
                self._file.write("M=D\n")
        pass

    "extra functions"
    def _a_cmd(self, address) -> None:
        self._file.write("@"+address+"\n")      
    def _l_cmd(self, word):
        self._file.write("("+word+")"+"\n")
    def _sp_plus(self):
        self._file.write("@SP\n") #SP++
        self._file.write("M=M+1\n")
    def _sp_sub(self):
        self._file.write("@SP\n") #SP--
        self._file.write("M=M-1\n")
    def _d_eq_sp_ptr(self):
        self._file.write("@SP\n") #D=*SP
        self._file.write("A=M\n")
        self._file.write("D=M\n")
    def _sp_ptr_eq_d(self):
        self._file.write("@SP\n") #*SP=D
        self._file.write("A=M\n")
        self._file.write("M=D\n")
    def _insert_true(self):
        self._file.write("@SP\n") #*SP=true
        self._file.write("A=M\n")
        self._file.write("M=-1\n")
    def _insert_false(self):
        self._file.write("@SP\n") #*SP=false
        self._file.write("A=M\n")
        self._file.write("M=0\n")
    def bootstrap(self):
        self._a_cmd("256")
        self._file.write("D=A\n") #D=256
        self._a_cmd("SP")
        self._file.write("M=D\n") #SP=256
        self.write_call("Sys.init", 0)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self._file.write("//Label "+label+"\n")
        self._l_cmd(self._name+"."+label+"$bar")
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self._file.write("//go-to "+label+"\n")
        self._a_cmd(self._name+"."+label+"$bar")
        self._file.write("0;JMP\n")
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        self._file.write("//if "+label+"\n")
        self._sp_sub() #*SP--
        self._file.write("A=M\n")
        self._file.write("D=M\n") #D=*SP
        self._a_cmd(self._name+"."+label+"$bar") #@Xxx.Foo$bar
        self._file.write("D;JNE\n") #if D!=0 -> jump  if true -> call go-to, else nothing
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self._file.write("//"+function_name+" "+str(n_vars)+"\n")
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        self._l_cmd(function_name)
        #self._l_cmd(function_name+"$bar")
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self._a_cmd("SP")
        i=0
        while(i<n_vars):
            self._file.write("A=M\n") #A=SP
            self._file.write("M=0\n") #create new local
            self._sp_plus() #SP++
            i+=1
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        self._file.write("//call cmd "+function_name+" "+str(n_args)+"\n")
        # push return_address   // generates a label and pushes it to the stack
        self._a_cmd(self._name+"."+function_name+"$ret."+str(self._call_counter)) #ret address
        self._file.write("D=A\n") #D=ret address
        self._sp_ptr_eq_d() #*SP=ret address
        self._sp_plus() #SP++
        # push LCL              // saves LCL of the caller
        self._a_cmd("LCL")
        self._file.write("D=M\n") #D=LCL
        self._sp_ptr_eq_d() #*SP=D
        self._sp_plus() #SP++
        # push ARG              // saves ARG of the caller
        self._a_cmd("ARG")
        self._file.write("D=M\n") #D=ARG
        self._sp_ptr_eq_d() #*SP=D
        self._sp_plus() #SP++
        # push THIS             // saves THIS of the caller
        self._a_cmd("THIS")
        self._file.write("D=M\n") #D=THIS
        self._sp_ptr_eq_d() #*SP=D
        self._sp_plus() #SP++
        # push THAT             // saves THAT of the caller
        self._a_cmd("THAT")
        self._file.write("D=M\n") #D=THAT
        self._sp_ptr_eq_d() #*SP=D
        self._sp_plus() #SP++
        # ARG = SP-5-n_args     // repositions ARG
        num = 5+n_args
        self._a_cmd(str(num)) #A=num
        self._file.write("D=A\n") #D=num
        self._a_cmd("SP")
        self._file.write("A=M\n") #A=SP
        self._file.write("D=A-D\n") #D=SP-5-n_args
        self._a_cmd("ARG")
        self._file.write("M=D\n") #ARG=SP-5-n_args
        # LCL = SP              // repositions LCL
        self._a_cmd("SP") #M=SP
        self._file.write("D=M\n") #D=SP
        self._a_cmd("LCL")
        self._file.write("M=D\n") #LCL=SP
        # goto function_name    // transfers control to the callee
        self._a_cmd(function_name)
        #self._a_cmd(function_name+"$bar")
        self._file.write("0;JMP\n")
        # (return_address)      // injects the return address label into the code
        self._l_cmd(self._name+"."+function_name+"$ret."+str(self._call_counter))
        self._call_counter+=1
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        self._file.write("//return cmd\n")
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        self._a_cmd("LCL")
        self._file.write("D=M\n") #D=*LCL
        self._a_cmd("R13")
        self._file.write("M=D\n") #@R13 = *LCL = frame
        # return_address = *(frame-5)   // puts the return address in a temp var #??
        self._a_cmd("5")
        self._file.write("D=A\n") #D=5
        self._a_cmd("R13") #M=*LCL=frame
        self._file.write("A=M-D\n") #A=frame-5
        self._file.write("D=M\n") #D=*(frame-5)
        self._a_cmd("R14")
        self._file.write("M=D\n") #return address in R14
        # *ARG = pop()                  // repositions the return value for the caller
        self._sp_sub() #SP--
        self._d_eq_sp_ptr() #D=*SP
        self._a_cmd("ARG") #A=ARG
        self._file.write("A=M\n")
        self._file.write("M=D\n") #*ARG = POP()
        # SP = ARG + 1                  // repositions SP for the caller
        self._a_cmd("ARG")
        self._file.write("D=M\n") #D=ARG
        self._a_cmd("SP")
        self._file.write("M=D+1\n") #M=ARG+1
        # THAT = *(frame-1)             // restores THAT for the caller
        self._a_cmd("R13")
        self._file.write("A=M-1\n") #A=frame-1
        self._file.write("D=M\n") #D=*(frame-1)
        self._a_cmd("THAT")
        self._file.write("M=D\n") #THAT = D = *(frame-1)
        # THIS = *(frame-2)             // restores THIS for the caller
        self._a_cmd("R13")
        self._file.write("A=M-1\n") #A=frame-1
        self._file.write("A=A-1\n") #A=frame-2
        self._file.write("D=M\n") #D=*(frame-2)
        self._a_cmd("THIS")
        self._file.write("M=D\n") #THIS = D = *(frame-2)
        # ARG = *(frame-3)              // restores ARG for the caller
        self._a_cmd("R13")
        self._file.write("A=M-1\n") #A=frame-1
        self._file.write("A=A-1\n") #A=frame-2
        self._file.write("A=A-1\n") #A=frame-3
        self._file.write("D=M\n") #D=*(frame-3)
        self._a_cmd("ARG")
        self._file.write("M=D\n") #ARG = D = *(frame-3)
        # LCL = *(frame-4)              // restores LCL for the caller
        self._a_cmd("R13")
        self._file.write("A=M-1\n") #A=frame-1
        self._file.write("A=A-1\n") #A=frame-2
        self._file.write("A=A-1\n") #A=frame-3
        self._file.write("A=A-1\n") #A=frame-4
        self._file.write("D=M\n") #D=*(frame-4)
        self._a_cmd("LCL")
        self._file.write("M=D\n") #LCL = D = *(frame-4)
        # goto return_address           // go to the return address
        self._a_cmd("R14")
        self._file.write("A=M\n")
        self._file.write("0;JMP\n")
        pass
