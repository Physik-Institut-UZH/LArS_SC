###########################################################################
# This script is for producing plots for the group's slow control webpage #
# as it was with the old slow control. However, this pulls data from      #
# InfluxDB and will be discontinued at some point as there is a Grafana   #
# already configured in to plot the data from InfluxDB.                   #
###########################################################################


import sys
from os import path
import time
import signal

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.dates as mdates

from influxdb_client import InfluxDBClient
import pandas as pd

from core import (read_token, load_json_config)



def get_last_measurements(client:InfluxDBClient, bucket:str, meas_name:str,*, minutes:int|None=None, hours:int|None=None) -> pd.DataFrame|None:

    if minutes is None and hours is None:
        raise ValueError(
            'get_last_measurements: either "minutes" or "hours" must be provided.'
        )

    if minutes is not None and hours is not None:
        raise ValueError(
            'get_last_measurements: only one of "minutes" or "hours" can be specified.'
        )
    
    window = f"-{minutes}m" if minutes is not None else f"-{hours}h"

    query = f'''
        from(bucket:"{bucket}")
          |> range(start:{window})
          |> filter(fn:(r) => r["_measurement"] == "{meas_name}")
          |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
          |> sort(columns: ["_time"])
        '''
    

    df = client.query_api().query_data_frame(query)

    # In some cases the function abpve returns a list of dataframes
    if isinstance(df, list):
        df = pd.concat(df, ignore_index=True)
    #

    return df
#

shutdown_request = False
def handle_sigterm(signum, frame):
    global shutdown_request
    print("SIGTERM received: shutting down gracefully...")
    shutdown_request = True
#
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise RuntimeError("Usage: LArS_Webpage_Plots.py <config.json>")

    cfg = load_json_config(sys.argv[1])

    INFLUXDB_URL = cfg["influxdb"]["url"]
    INFLUXDB_ORG = cfg["influxdb"]["org"]
    INFLUXDB_BUCKET = cfg["influxdb"]["bucket"]
    INFLUXDB_TOKEN = read_token(cfg["influxdb"]["token_file"])

    MEAS_NAME = cfg["measurement"]

    PLOTS_DIR = cfg["plots_dir"]
    LOOP_SLEEP_SECS = cfg["loop_sleep_secs"]

    plt.rcParams['figure.figsize'] = (18.0, 8.)  
    plt.rcParams.update({'font.size': 22})
    plt.ioff()
    
    try:
        while not shutdown_request:
            with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
                #Pull the 72 hours data
                print('Pulling the last 72 hrs data')
                df_72h = get_last_measurements(client=client, 
                                               bucket=INFLUXDB_BUCKET,
                                               meas_name=MEAS_NAME,
                                               hours=72
                                               )
                
                print('Pulling the last 8 hrs data')
                df_8h = get_last_measurements(client=client,
                                              bucket=INFLUXDB_BUCKET,
                                              meas_name=MEAS_NAME,
                                              hours=8
                                              )
                
                print('Pulling the last 8 hrs data')
                df_4h = get_last_measurements(client=client,
                                              bucket=INFLUXDB_BUCKET,
                                              meas_name=MEAS_NAME,
                                              hours=4
                                              )
            #
            
            
            print('Building the webpage plots')


            ####################################
            # Pressure - Temperature plots 72h #
            ####################################
            fig, ax1 = plt.subplots()

            #Formatting graph
            ax1.ticklabel_format(useOffset=False)
            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')
            ax1.xaxis.set_major_formatter(xfmt)

            #Temperature plot
            mask_tt0 = df_72h["TT0"].notna() #Gas temp
            mask_tt1 = df_72h["TT1"].notna() #Liquid temp
            ax1.set_ylabel('Temperature [K]', color='r')
            ax1.plot(df_72h.loc[mask_tt0, '_time'],
                     df_72h.loc[mask_tt0, 'TT0'],
                     linewidth=4,
                     color='r',
                     label='TT0 in the gas phase'
                     )
            ax1.plot(df_72h.loc[mask_tt1, '_time'],
                     df_72h.loc[mask_tt1, 'TT1'],
                     linewidth=4,
                     color='g',
                     label='TT1 in liquid phase'
                     )
            ax1.tick_params(axis='y', labelcolor='r')

            #Pressure plot
            ax2 = ax1.twinx() # instantiate a second axes that shares the same x-axis
            ax2.set_ylabel('Pressure[mBar]', color='orange')  # we already handled the x-label with ax1
            mask_pt0 = df_72h["PT0"].notna()
            ax2.plot(df_72h.loc[mask_pt0, '_time'],
                     df_72h.loc[mask_pt0, 'PT0'],
                     color='orange',
                     linewidth=4,
                     label='PT0'
                     )
            #Plot and save
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            ax1.legend(loc='best')
            ax2.legend(loc='best')
            plt.title('Pressure variation in 72 hours')
            
            plt.savefig( path.join(PLOTS_DIR,'pressure_72hrs.png'),format='png')

            plt.close(fig)


            ##########################
            # Temperatures plots 4hr #
            ##########################

            fig = plt.figure()
            ax = plt.gca()
            ax.ticklabel_format(useOffset=False)
            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')
            ax.xaxis.set_major_formatter(xfmt)

            mask_tt0 = df_4h["TT0"].notna() #Gas temp
            mask_tt1 = df_4h["TT1"].notna() #Liquid temp
            ax.set_ylabel('Temperature [K]', color='r')
            ax.plot(df_4h.loc[mask_tt0, '_time'],
                     df_4h.loc[mask_tt0, 'TT0'],
                     linewidth=4,
                     color='r',
                     label='TT0 in the gas phase'
                     )
            ax.plot(df_4h.loc[mask_tt1, '_time'],
                     df_4h.loc[mask_tt1, 'TT1'],
                     linewidth=4,
                     color='g',
                     label='TT1 in liquid phase'
                     )
            ax.tick_params(axis='y', labelcolor='r')

            ax.legend(loc='best')
            #ax.xlabel('time')
            ax.set_ylabel('Temperature [K]')
            plt.title('Temperature variation in 4 hours')
            plt.savefig(path.join(PLOTS_DIR,'today_Temperature.png'),format='png')

            plt.close(fig)

            
            ##############################
            # Heater (valve) plot - 4 hr #
            ##############################
            fig = plt.figure()
            ax = plt.gca()
            ax.ticklabel_format(useOffset=False)

            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')
            ax.xaxis.set_major_formatter(xfmt)

            v0_mask = df_4h['V0'].notna()
            ax.plot(df_4h.loc[v0_mask, '_time'],
                    df_4h.loc[v0_mask, 'V0'],
                    linewidth=4,
                    color='orchid',
                    )
            
            ax.set_ylabel('N2 valve position [%]')
            plt.title('Control variation in 4 hours')
            plt.savefig(path.join(PLOTS_DIR,'today_Heater.png'),format='png')
            
            plt.close(fig)


            ###########################
            # Temperatures plots 72hr #
            ###########################
            fig = plt.figure()
            ax = plt.gca()
            ax.ticklabel_format(useOffset=False)

            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')
            ax.xaxis.set_major_formatter(xfmt)

            mask_tt0 = df_72h["TT0"].notna() #Gas temp
            mask_tt1 = df_72h["TT1"].notna() #Liquid temp
            ax.set_ylabel('Temperature [K]', color='r')
            ax.plot(df_72h.loc[mask_tt0, '_time'],
                     df_72h.loc[mask_tt0, 'TT0'],
                     linewidth=4,
                     color='r',
                     label='TT0 in the gas phase'
                     )
            ax.plot(df_72h.loc[mask_tt1, '_time'],
                     df_72h.loc[mask_tt1, 'TT1'],
                     linewidth=4,
                     color='g',
                     label='TT1 in liquid phase'
                     )
            ax.tick_params(axis='y', labelcolor='r')
            ax.legend(loc='best')
            ax.set_ylabel('Temperature [K]')
            plt.title('Temperature variation in 72 hours')
            plt.savefig(path.join(PLOTS_DIR,'72h_Temperature.png'),format='png')

            plt.close(fig)


            ###############################
            # Heater (valve) plot - 72 hr #
            ###############################

            fig = plt.figure()
            ax = plt.gca()
            ax.ticklabel_format(useOffset=False)

            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')
            ax.xaxis.set_major_formatter(xfmt)

            v0_mask = df_72h['V0'].notna()
            ax.plot(df_72h.loc[v0_mask, '_time'],
                    df_72h.loc[v0_mask, 'V0'],
                    linewidth=4,
                    color='orchid',
                    )
            
            ax.set_ylabel('N2 valve position [%]')
            plt.title('Control variation in 72 hours')
            plt.savefig(path.join(PLOTS_DIR,'72h_Heater.png'),format='png')
            
            plt.close(fig)

            
            #####################################
            # Levelmeter - Temperature plot 4hr #
            #####################################

            fig, ax1 = plt.subplots()
            ax1.ticklabel_format(useOffset=False)
            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')

            ax1.xaxis.set_major_formatter(xfmt)
            ax1.set_ylabel('Temperature [K]', color='r')

            tt1_mask = df_4h['TT1'].notna()
            ax1.plot(df_4h.loc[tt1_mask,'_time'],
                     df_4h.loc[tt1_mask,'TT1'],
                     linewidth=4,
                     color='green',
                     label='TT1 in liquid phase'
                     )
            ax1.tick_params(axis='y', labelcolor='g')

            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

            ax2.set_ylabel('Level[mm]', color='b')  # we already handled the x-label with ax1
            lm_mask = df_4h['LLM_cal'].notna()
            ax2.plot(df_4h.loc[lm_mask,'_time'],
                     df_4h.loc[lm_mask,'LLM_cal'],
                     linewidth=2, # This is because it would cover the previous trace of TT1
                     color='b',
                     label='Level from the bottom'
                     )
            ax2.tick_params(axis='y', labelcolor='b')
            #ax2.set_ylim(0, 4000)
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.title('Level variation in 4 hours')
            plt.savefig(path.join(PLOTS_DIR,'LevelMeterShort.png'),format='png')
            
            plt.close(fig)


            #####################################
            # Levelmeter - Temperature plot 8hr #
            #####################################

            fig, ax1 = plt.subplots()

            ax1.ticklabel_format(useOffset=False)
            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')

            ax1.xaxis.set_major_formatter(xfmt)
            ax1.set_ylabel('Temperature [K]', color='r')

            tt1_mask = df_8h['TT1'].notna()
            ax1.plot(df_8h.loc[tt1_mask,'_time'],
                     df_8h.loc[tt1_mask,'TT1'],
                     linewidth=4,
                     color='green',
                     label='TT1 in liquid phase'
                     )
            ax1.tick_params(axis='y', labelcolor='g')

            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

            ax2.set_ylabel('Level[mm]', color='b')  # we already handled the x-label with ax1
            lm_mask = df_8h['LLM_cal'].notna()
            ax2.plot(df_8h.loc[lm_mask,'_time'],
                     df_8h.loc[lm_mask,'LLM_cal'],
                     linewidth=2, # This is because it would cover the previous trace of TT1
                     color='b',
                     label='Level from the bottom'
                     )
            
            ax2.tick_params(axis='y', labelcolor='b')
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.title('Level variation in 8 hours')
            plt.savefig(path.join(PLOTS_DIR,'LevelMeter_8h.png'),format='png')
            
            plt.close(fig)


            ######################################
            # Levelmeter - Temperature plot 72hr #
            ######################################

            fig, ax1 = plt.subplots()

            ax1.ticklabel_format(useOffset=False)
            # rotate and align the tick labels so they look better
            fig.autofmt_xdate()
            xfmt = mdates.DateFormatter('%m-%d %H:%M')
            
            ax1.xaxis.set_major_formatter(xfmt)
            ax1.set_ylabel('Temperature [K]', color='r')

            tt1_mask = df_72h['TT1'].notna()
            ax1.plot(df_72h.loc[tt1_mask,'_time'],
                     df_72h.loc[tt1_mask,'TT1'],
                     linewidth=4,
                     color='green',
                     label='TT1 in liquid phase'
                     )
            ax1.tick_params(axis='y', labelcolor='g')

            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

            ax2.set_ylabel('Level[mm]', color='b')  # we already handled the x-label with ax1
            lm_mask = df_72h['LLM_cal'].notna()
            ax2.plot(df_72h.loc[lm_mask,'_time'],
                     df_72h.loc[lm_mask,'LLM_cal'],
                     linewidth=2, # This is because it would cover the previous trace of TT1
                     color='b',
                     label='Level from the bottom'
                     )
            
            ax2.tick_params(axis='y', labelcolor='b')
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.title('Level variation in 72 hours')
            plt.savefig(path.join(PLOTS_DIR,'LevelMeterLong.png'),format='png')
            
            plt.close(fig)

            print('All plots built and saved successfully.')

            time.sleep(LOOP_SLEEP_SECS)
    #
    except KeyboardInterrupt:
        print('Exit from the application as per user request: KeyboardInterrupt received.')
        shutdown_request = True
    #

    print('Shutdown complete.')