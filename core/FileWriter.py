import time
from datetime import datetime, timezone
from pathlib import Path


class FileWriter:
    def __init__(self, settings:dict):
        self.dirpath = settings['dirpath']
        Path(self.dirpath).mkdir(parents=True, exist_ok=True)
        self.maxtime = 24*3600 #Defaults to 1 file every 24 hours
        if 'maxtime' in settings:
            self.maxtime = int(settings['maxtime'])
        #
        
        self.var_lst = list(settings['varlst'])
        
        self.fname = None #Filename of the current output file
        self.fpath = None #Current full path of the output file
        self.file_ct = None #Creation timestamp of the last/current file
    #

    def _create_new_file_name(self, timestamp):
        raise NotImplementedError(f'The class {self.__class__} provides only the interface and only derived concrete classes shall be instanced!')
    #

    def write(self, varVals:dict):
        ts = int(time.time())
        if (self.file_ct is None) or (ts>=(self.file_ct+self.maxtime)):
            self._create_new_file_name(ts)
        #
        with open(self.fpath, 'a+') as outfile:
            unixtime = datetime.fromisoformat(varVals["timestamp"]).astimezone().timestamp()
            line = f'{int(unixtime)}'
            for var in self.var_lst:
                line += f'\t{varVals[var]}'
            line += '\n'
            outfile.write(line)
        #
    #
#
