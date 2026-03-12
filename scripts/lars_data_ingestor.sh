#!/usr/bin/env bash
set -euo pipefail

PYTHON_EXEC="$HOME/miniconda3/envs/lars/bin/python"

LARS_DATA_ING_SCRIPT="$HOME/SlowControl/LArS_SC/DataIngestor.py"

LARS_DATA_ING_CONF="$HOME/SlowControl/config/lars_dataingestor_config.json"

exec $PYTHON_EXEC $LARS_DATA_ING_SCRIPT $LARS_DATA_ING_CONF