import time
import serial
from datetime import datetime, timezone
from pathlib import Path

from core import SCDevice
from core import FileWriter


class Levelmeter_UTI(SCDevice):
    def __init__(self, name, port, baudrate, working_mode, settings, timeout=1.0):
        super().__init__(name=name, varNames=[name+'_raw', name+'_cal'])

        self.varVals = {var_name: None for var_name in self.varVals.keys()}

        self.port = port
        self.baudrate = baudrate
        self.working_mode = working_mode
        self.settings = settings
        self.timeout = timeout

        #Try to start the communication here
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=timeout)
        self.connect()
    #

    def connect(self):
        
        if not self.ser.isOpen():
            self.ser.open()
        #

        self.ser.write('@'.encode()) #Command to start the communication with the chipset managing the UTI chipset
        time.sleep(0.01)

        self.ser.write(str(self.working_mode).encode())
        time.sleep(0.01)
    #

    def pollVars(self):
        fail = 0
        
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self.varVals['timestamp'] = ts

        try:
            res_tpl = self.uti_read()
            self.varVals[self.name+'_raw'] = float(res_tpl[0])
            self.varVals[self.name+'_cal'] = float(res_tpl[1])
        except Exception as err:
            fail += 1
            self.varVals[self.name] = None

        return fail
    #

    def uti_read(self):
        self.ser.write("m".encode()) #To send a single measurement request
        time.sleep(0.1) #Time to let all the byte be written into the input buffer

        #numchar = 0

        #while numchar == 0:
        #    numchar = self.ser.inWaiting()
        #    twait = time.time()
        #

        buffer = self.ser.read(self.ser.inWaiting())
        words = buffer.split()
        
        #Debug logging here
        
        tref = float(int('0x'+words[1].decode(),16))
        tx = float(int('0x'+words[2].decode(),16))
        toff = float(int('0x'+words[0].decode(),16))

        val = self.settings['ref_cap']*(tx-toff)/(tref-toff)
        
        lev = val*self.settings['m_cal'] + self.settings['q_cal']
        #Debug logging here

        return (val, lev)

    #
        
    def close(self):
        self.ser.close()
    #

class LM_UTI_Writer(FileWriter):
    def __init__(self, settings:dict):
        super().__init__(settings=settings)
    #

    def _create_new_file_name(self, timestamp):
        self.fname = str(int(timestamp))+'.txt'
        self.fpath = Path(self.dirpath)/Path(self.fname)
        self.file_ct = int(timestamp)
    #
#


PORT = '/dev/ttyUSB0'

BAUDRATE = 9600 #Baudrate

REF_CAP = 33.0 #In pF units

UTI_WORKING_MODE = 4

SETTINGS_DICT = {
    'ref_cap': 33.0, #In pF units
    'cD0': 6.0, #In mm units
    'cDi': 1.2, #In mm units
    'er1': 1.5, #Permittivity of LAr
    'er2': 1.0, #Permittivity of GAr
    'EmptyCapacity': 15.4, #In pF units
    'offset': 25.0, #Offset from the bottom of crystat to bottom of levelmeter
    'corr': 1.04159, #Correction factor from calibration GAr
    'm_cal': 16.021, #Slope (from Gloria's fit)
    'q_cal': -938.520, #Constant/intercept (from Gloria's fit)
    }

WRITER_SETTINGS = {
    'dirpath': '/home/lars/data/sc_data/levelmeter/test',
    'varlst': ['LLM_raw', 'LLM_cal'],
    'filetime': 20
}

lm_dev = Levelmeter_UTI(name='LLM', port=PORT, baudrate=BAUDRATE, working_mode=UTI_WORKING_MODE, settings=SETTINGS_DICT, timeout=1.0)
lm_dev.AddFileWriter( LM_UTI_Writer(settings=WRITER_SETTINGS) )
