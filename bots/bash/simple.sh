#!/bin/bash
set -e

debug() { 
  echo "$@" >&2; 
}

read_block() {
  while IFS=$'\n' read -r LINE; do
    test -z "$LINE" && break
    echo "$LINE"
  done
}

INIT=$1
debug "init YAML: $INIT"

echo "- set-speed 100 set-rotation-speed -50"
TIME=$(date +%s)
while true; do
  YAML=$(read_block)
  ID=$(echo "$YAML" | grep "^[[:space:]]*id: " | cut -d":" -f2- | xargs)
  NEW_TIME=$(date +%s)
  if test $((NEW_TIME - TIME)) -ge 1; then 
    echo "$ID fire"
    TIME=$NEW_TIME
  else
    echo "$ID"    
  fi 
done
