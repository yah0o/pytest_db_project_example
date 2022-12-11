#!/bin/bash

counter=0

while true; do
  status=$(docker-compose -f docker-compose.yaml ps | grep "Exit\|starting\|unhealthy\|Restarting")
  if [ "$status" = "" ]; then
    echo "All services are up!"
    exit 0
  elif [ "$counter" -gt 300 ]; then
    echo "Counter: $counter times reached; Exiting loop!"
    echo "Status: $status"
    exit 1
  else
    counter=$((counter+1))
  fi
  sleep 1
done