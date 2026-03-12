#!/usr/bin/env bash
set -euo pipefail

PYTHON_EXEC="$HOME/miniconda3/envs/lars/bin/python"

LARS_WEB_PLOTS_SCRIPT="$HOME/SlowControl/LArS_SC/LArS_Webpage_Plots.py"

LARS_WEB_PLOTS_CONF="$HOME/SlowControl/config/lars_plots_config.json"

exec $PYTHON_EXEC $LARS_WEB_PLOTS_SCRIPT $LARS_WEB_PLOTS_CONF
