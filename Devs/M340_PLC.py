from pymodbus.client import ModbusTcpClient

from struct import pack, unpack
import time
from datetime import datetime, timezone
from pathlib import Path

import traceback

from core.SCDevice import SCDevice
from core import FileWriter

class M340_PLC(SCDevice):
    PLC_TYPES = {
        'REAL':{'size': 2,
                'pack_fmt': '<2H',
                'unpack_fmt': 'f'
                },
        'UINT':{'size': 1,
                'pack_fmt': '<H',
                'unpack_fmt': 'H'
                },
        'WORD':{'size': 1,
                'pack_fmt': '<H',
                'unpack_fmt': 'H'
                }
    }

    PLC_PORT = 502

    PLC_BASE_REG = 0 #Base of the modbus mapping
    
    def __init__(self, name:str, varsdict:dict, plc_ip:str):
        super().__init__(name, list(varsdict))

        self.varDict = varsdict
        self.varVals = {vName:None for vName in self.varDict.keys()}

        self.plc_ip = plc_ip
        
        #Determine the memory chunk to poll each polling
        reg_min = None
        reg_max = None

        for varName, varObj in self.varDict.items():
            reg_start = int(varObj['Register'])
            reg_end = reg_start + int(M340_PLC.PLC_TYPES[varObj['Type']]['size'])

            if reg_min is None:
                reg_min = reg_start
            elif reg_start < reg_min:
                reg_min = reg_start
            #

            if reg_max is None:
                reg_max = reg_end
            elif reg_end > reg_max:
                reg_max = reg_end
            #
        #

        self.regs_num = reg_max-reg_min
        self.regs_range = (reg_min, reg_max)
        
        self.client = ModbusTcpClient(host=self.plc_ip,
                                      port=M340_PLC.PLC_PORT,
                                      name=self.name)
        self._connect()
    #

    def _connect(self):
        self.client.connect()
    #

    def close(self):
        try:
            self.client.close()
        except:
            pass
    #

    def pollVars(self):
        fail = 0 

        # Read the PLC registers
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.varVals['timestamp'] = ts

        rr = self.client.read_holding_registers(address=M340_PLC.PLC_BASE_REG, count=self.regs_num)

        if rr.isError():
            print(f"[ERROR] Modbus: {rr}")
            for var_name in self.varVals:
                fail += 1
                self.varVals[var_name] = None
                return fail
        #

        regs = rr.registers

        for var_name in self.varVals:
            if var_name == 'timestamp':
                continue
            #
            # Get only the variables for which there are no errors
            try:
                self.varVals[var_name] = self.extractVar(regs, var_name)
            except Exception:
                traceback.print_exc()
                fail += 1
                self.varVals[var_name] = None
            #
        #
        return fail
    #

    def extractVar(self, regObj, var_name):
        varreg = self.varDict[var_name]['Register']
        vartype = self.varDict[var_name]['Type']
        varsize = M340_PLC.PLC_TYPES[vartype]['size']
        regs_tpl = tuple(regObj[varreg: varreg+varsize])

        return unpack(M340_PLC.PLC_TYPES[vartype]['unpack_fmt'], pack(M340_PLC.PLC_TYPES[vartype]['pack_fmt'], *regs_tpl))[0]
    #
#

class PressureFileWriter(FileWriter):
    def __init__(self, settings:dict):
        super().__init__(settings=settings)
        self.maxtime = 24*3600 #Fix to 1 file every 24 hours
    #

    def _create_new_file_name(self, timestamp):
        today = datetime.today()
        self.fname = "pressure_" + str(today.year)[2:4] + str(today.month) + str(today.day) + ".txt"

        self.fpath = Path(self.dirpath)/Path(self.fname)
        self.file_ct = int(timestamp)
    #
#

class CryoconFileWriter(FileWriter):
    """
    This class writes files with the same data format as it was from the Cryocon,
    including the heater value (actually the solenoid valve opening). 
    However, the values are actually read from the M340 PLC with the class above.
    """
    def __init__(self, settings:dict):
        super().__init__(settings=settings)
        self.maxtime = 24*3600 #Fix to 1 file every 24 hours
    #

    def _create_new_file_name(self, timestamp):
        today = datetime.today()
        self.fname = str(today.year)[2:4] + str(today.month) + str(today.day) + "_data.txt"

        self.fpath = Path(self.dirpath)/Path(self.fname)
        self.file_ct = int(timestamp)
    #
#



PLC_IP = '192.168.99.2'

PLC_VARS = {
    'PT0':{'Register': 0,
           'Type': 'REAL'
           },
    'PT0_SP':{'Register': 8,
           'Type': 'REAL'
           },
    'TT0':{'Register': 2,
           'Type': 'REAL'
           },
    'TT1':{'Register': 4,
           'Type': 'REAL'
           },
    'TT1_SP':{'Register': 10,
           'Type': 'REAL'
           },
    'V0':{'Register': 6,
           'Type': 'REAL'
           },
    'ControlMode':{'Register': 12,
           'Type': 'UINT'
           }
}

PRESSURE_WRITER_SETTINGS = {
    'dirpath': '/home/lars/data/sc_data/pressure/test',
    'varlst': ['PT0']
}

CRYO_WRITER_SETTINGS = {
    'dirpath': '/home/lars/data/sc_data/cryo/test',
    'varlst': ['TT0','TT1','V0']
}

m340_dev = M340_PLC(name='M340_PLC', varsdict=PLC_VARS, plc_ip=PLC_IP)
m340_dev.AddFileWriter(PressureFileWriter(settings=PRESSURE_WRITER_SETTINGS))
m340_dev.AddFileWriter(CryoconFileWriter(settings=CRYO_WRITER_SETTINGS))
