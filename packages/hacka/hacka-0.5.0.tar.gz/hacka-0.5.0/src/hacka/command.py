import sys

class Option :
    def __init__(self, name, letter="", default=False, help="" ):
        self._name= name
        self._letter= letter
        self._default= default
        self._value= self._default
        self._help= help

    # set:
    def setOn(self, aThing):
        if type( self._default ) is int :
            self._value= int(aThing)
        elif type( self._default ) is float :
            self._value= float(aThing)
        else :
            self._value= aThing

    # test:
    def needArgument(self) :
        return not type( self._default ) is bool
    
    # String:
    def help(self):
        s= "\t"
        if self._letter != "" :
            s+= f"-{self._letter}, "
        s+= f"--{self._name}\n"
        return s + f"\t\t{self._help} (default: {self._default})"
    
    def __str__(self) :
        s= f"-{self._letter}"
        if s == "-" :
            s= f"--{self._name}"
        if self.needArgument() :
            s+= f" {self._value}"
        return s

class Command :
    # Constructor:
    def __init__(self, name, options=[], help=""):
        self._cmd= name
        self._options= { o._name:o for o in options }
        self._arguments= []
        self._help= help
        self._ready= False
        self._log= ""
    
    # Accessor:
    def name(self):
        return self._name
    
    def options(self):
        return [ self._options[m] for m in self._options ]
    
    def option(self, name):
        return self._options[name]._value
    
    def arguments(self):
        return self._arguments
    
    def argument(self, i=0):
        if self._arguments == [] :
            return ""
        return self._arguments[i]

    def ready(self):
        return self._ready
    
    def log(self):
        return self._log

    def optionShort(self):
        dico= {}
        for opName in self._options :
            if self._options[opName]._letter != "" :
                dico[ self._options[opName]._letter ]= opName
        return dico

    # interpret a command line (typically sys.argv):
    def process(self, commandLine=sys.argv ):
        self._ready= False
        self._log= ""
        self._arguments= []
        dico= self.optionShort()
        # Pop command.
        commandLine.pop(0)
        
        while len(commandLine) != 0 :
            isOption= False
            option= -1
            element= commandLine.pop(0)
            if element[:2] == '--' :
                if not element[2:] in self._options :
                    self._log= f"> {element[2:]} is not an option !!!"
                    return self._ready
                isOption= True
                option= self._options[element[2:]]
            elif element[:1] == '-' :
                for op in element[1:] :
                    if not op in dico :
                        self._log= f"> -{op} is not an option !!!"
                        return self._ready
                for op in element[1:len(element)-1] :
                    if self._options[ dico[op] ].needArgument() :
                        self._log= f"> {dico[op]} option require an argument !!!"
                        return self._ready
                    self._options[ dico[op] ]._value= True
                isOption= True
                option= self._options[ dico[ element[-1] ] ]

            if isOption :
                if option.needArgument() :
                    if len(commandLine) == 0 or commandLine[0][0] == "-" :
                        self._log= f"> {option._name} option require an argument !!!"
                        return self._ready
                    option.setOn( commandLine.pop(0) )
                else :
                    option._value= True
            else :
                self._arguments.append( element )
        self._ready= True
        return self._ready

    # String:
    def help(self) :
        h= f"COMMAND: {self._cmd} [OPTIONS] [ARGUMENTS]\n\n\t{self._help}\n\nOPTIONS:\n"
        for op in self.options() :
            h+= op.help()
            h+= "\n\n"
        return h

    def __str__(self) :
        cmdLine= [self._cmd]
        for op in self.options() :
            if op.needArgument() or op._value :
                cmdLine.append( str(op) )
        cmdLine+= self._arguments
        return " ".join( cmdLine )
