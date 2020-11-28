#!/bin/bash

echo -e "\nVirtual Envrionment:"

# path to self
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

start_venv() {
    source $SCRIPTPATH/venv/bin/activate

    export FLASK_ENV=$1

    PYTHON_VERS=`python --version`
    echo -e " * interpreter $PYTHON_VERS"
    echo -e " * FLASK_ENV   $FLASK_ENV"
    echo -e "\nPIP:"
    pip freeze $1 | while read x; do echo -e " * $x"; done
    echo -e
    echo -e "Flask server:"

}

start_venv development
python kdm-manager.py
