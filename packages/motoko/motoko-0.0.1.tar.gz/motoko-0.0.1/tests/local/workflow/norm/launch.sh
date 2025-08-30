#!/bin/bash

echo 'here is the job'
echo __BLACKDYNAMITE__id__

# # NOTE: need to export environment variables so that jobs and runs can be found by doIt.py
# sbatch --export=ALL sub.sh
python doIt.py
