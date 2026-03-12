import sys
import time
import signal

from core import (getRegister, load_all_devices, read_token, load_json_config)
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

import traceback

shutdown_request = False
def handle_sigterm(signum, frame):
    global shutdown_request
    print("SIGTERM received: shutting down gracefully...")
    shutdown_request = True
#
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__=="__main__":

    if len(sys.argv) != 2:
        raise RuntimeError("Usage: python DataIngestor.py <config.json>")

    try:
        cfg = load_json_config(sys.argv[1])
    except Exception as err:
        print('ERROR --> DataIngestor.py: failed to read the json configuration file: {err}', file=sys.stderr)
        sys.exit(1)
    #

    INFLUXDB_URL = cfg["influxdb"]["url"]
    INFLUXDB_ORG = cfg["influxdb"]["org"]
    INFLUXDB_BUCKET = cfg["influxdb"]["bucket"]
    INFLUXDB_TOKEN = read_token(cfg["influxdb"]["token_file"])

    MEAS_NAME = cfg["measurement"]

    POLL_INTERVAL = cfg["poll_interval"]
    
    load_all_devices()
    
    devs_dict = getRegister()

    if not devs_dict:
        print("[ERROR]: No devices registered.")
        sys.exit(1)
    
    try:
        with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as influxdb_client:
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

            while not shutdown_request:
                t0 = time.time()

                points_lst = []
                for devname, dev in devs_dict.items():

                    try:
                        dev.pollVars()
                        data_dict = dev.getVarVals()
                        dev.WriteOnFile()
                    except KeyboardInterrupt:
                        raise #This is needed to let the application exit
                    #
                    except Exception as err:
                        print(f"[ERROR] Device {devname} failed:")
                        traceback.print_exc()
                        continue   # don't kill SC
                    
                    print(f'Data from device "{devname}":')
                    print(data_dict)
                    
                    for varName, varVal in data_dict.items():
                        if varName == 'timestamp':
                            continue
                        if varVal is None:
                            continue
                        points_lst.append(Point(MEAS_NAME).field(varName, varVal).time(data_dict['timestamp']))
                    #
                #
                print('---------------\n')

                if points_lst:
                    try:
                        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points_lst)
                    except Exception:
                        print("[ERROR] InfluxDb write failed")
                        traceback.print_exc()

                dt = time.time() - t0
                time.sleep(max(0, POLL_INTERVAL - dt))
            #
        #
    except KeyboardInterrupt:
        print('Exit from the application as per user request: KeyboardInterrupt received.')
        shutdown_request = True
    #
    finally:
        print("Cleaning up resources...")
        for devname, dev in devs_dict.items():
            dev.close()
        #
        print("Shutdown complete.")
        sys.exit(0)
    #  
#
