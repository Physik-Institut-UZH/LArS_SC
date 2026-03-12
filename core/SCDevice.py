import Devs
import pkgutil
import importlib

def load_all_devices():
    print("Loading SC device modules...\n")

    for module_info in pkgutil.iter_modules(Devs.__path__):

        name = module_info.name

        if name.startswith("_"):
            continue

        full_name = f"Devs.{name}"

        importlib.import_module(full_name)

        print(f"  Loaded: {full_name}")

    print("\nRegistered devices:")
    for name in getRegister():
        print(f"  - {name}")
#

def getRegister():
    return SCDevice.register
#

class SCDevice:
    """
    This class provides only the interface and instancing it should fail
    """
    register = dict()
    
    def __init__(self, name:str, varNames:str|list):
        self.name = name
        SCDevice.register[name] = self
        self.varVals = dict(timestamp=None)
        if isinstance(varNames, str):
            self.varVals.update({varNames:None})
        elif isinstance(varNames, list):
            self.varVals.update({var:None for var in varNames})
        #
        self.file_writers = []
    #

    def AddFileWriter(self, writer):
        self.file_writers.append(writer)
    #

    def WriteOnFile(self):
        for writer in self.file_writers:
            writer.write(self.varVals)
        #
    #
    
    def getRegister(self):
        return SCDevice.register
    #
            
    def getVarVals(self):
        return self.varVals
    #
    
    def pollVars(self):
        raise NotImplementedError(f'The class {self.__class__} provides only the interface and shall not be implemented!')
    #
    
    def close(self):
        pass


        
        