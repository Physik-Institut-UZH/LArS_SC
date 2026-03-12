#!/usr/bin/env bash
#set -euo pipefail

PYTHON_EXEC="$HOME/miniconda3/envs/lars/bin/python"

PROJECT_ROOT="$HOME/SlowControl/LArS_SC"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

LARS_WEB_PLOTS_SCRIPT="$HOME/SlowControl/LArS_SC/LArS_Webpage_Plots.py"

LARS_WEB_PLOTS_CONF="$HOME/SlowControl/config/lars_plots_config.json"

# Log file
LARS_WEB_PLOTS_LOGFILE="$HOME/local/var/log/lars_webpage_plots.log"
mkdir -p "$(dirname "$LARS_WEB_PLOTS_LOGFILE")"

# Run with logging
echo "[$(date)] Starting lars_webpage_plots" >> "$LARS_WEB_PLOTS_LOGFILE"
"$PYTHON_EXEC" "$LARS_WEB_PLOTS_SCRIPT" "$LARS_WEB_PLOTS_CONF" >> "$LARS_WEB_PLOTS_LOGFILE" 2>&1
echo "[$(date)] Finished" >> "$LARS_WEB_PLOTS_LOGFILE"

#exec $PYTHON_EXEC $LARS_WEB_PLOTS_SCRIPT $LARS_WEB_PLOTS_CONF
