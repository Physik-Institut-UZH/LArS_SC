#!/usr/bin/env bash

CONDA_ENV="lars"
PYTHON_EXEC="$HOME/miniconda3/envs/$CONDA_ENV/bin/python"

CRON_LOG="$HOME/local/var/log/cron/EnsureLarsWebplots.log"
mkdir -p "$(dirname "$CRON_LOG")"

LARS_WEB_PLOTS_SCRIPT="$HOME/SlowControl/LArS_SC/LArS_Webpage_Plots.py"
LARS_WEB_PLOTS_CONF="$HOME/SlowControl/config/lars_plots_config.json"

# Log file
LARS_WEB_PLOTS_LOGFILE="$HOME/local/var/log/lars_webpage_plots.log"

# Check if process is running
if pgrep -f "$PYTHON_EXEC $LARS_WEB_PLOTS_SCRIPT" > /dev/null ; then
  echo "$(date) : Script running" >> "$CRON_LOG" 2>&1
  exit 0
else
  echo "$(date) : Restarting Script" >> "$CRON_LOG" 2>&1

  PROJECT_ROOT="$HOME/SlowControl/LArS_SC"
  export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

  "$PYTHON_EXEC" "$LARS_WEB_PLOTS_SCRIPT" "$LARS_WEB_PLOTS_CONF" >> "$LARS_WEB_PLOTS_LOGFILE" 2>&1 &

  exit 0
fi
