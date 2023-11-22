#!/bin/bash

echo "Starting init-postgres-pif.py script at $(date +"%Y-%m-%d %H:%M:%S")"
python /app/init-postgres-pif.py
echo "Finished init-postgres-pif.py script at $(date +"%Y-%m-%d %H:%M:%S")"

#echo "Starting insert-poem-lyrics.py script at $(date +"%Y-%m-%d %H:%M:%S")"
#python /app/insert-poem-lyrics.py
#echo "Finished insert-poem-lyrics.py script at $(date +"%Y-%m-%d %H:%M:%S")"

#echo "Starting insert-poem-web.py script at $(date +"%Y-%m-%d %H:%M:%S")"
#python /app/insert-poem-web.py
#echo "Finished insert-poem-web.py script at $(date +"%Y-%m-%d %H:%M:%S")"

echo "Starting main.py script at $(date +"%Y-%m-%d %H:%M:%S")"
python /app/main.py
echo "Finished main.py script at $(date +"%Y-%m-%d %H:%M:%S")"


