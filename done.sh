#!/bin/bash

while true; do
    if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
        conda deactivate
    else
        break
    fi
done