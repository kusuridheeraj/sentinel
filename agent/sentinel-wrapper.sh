#!/bin/bash

# Configuration
# In production, these should be in /etc/sentinel/config.env
SENTINEL_URL="http://localhost:8000"
ORG_ID="infra_ops"
REAL_DOCKER_BIN="/usr/bin/docker"

# 1. Capture Identity
# Who is the human?
ACTOR=$(whoami)
# Where are they coming from? (SSH Source IP)
# If running locally, this might be empty, so we default to 'local'.
SOURCE_IP=$(echo $SSH_CONNECTION | awk '{print $1}')
if [ -z "$SOURCE_IP" ]; then
    SOURCE_IP="local_console"
fi

# 2. Capture Command
# What are they trying to do?
COMMAND_ARGS="$@"
FULL_CMD="docker $COMMAND_ARGS"

# 3. Classify Action
# We only want to log 'destructive' or 'important' actions to save noise.
# This simple logic checks if the command contains 'rm', 'stop', 'kill', 'prune'.
IS_DESTRUCTIVE=0
if [[ " $@ " =~ " rm " ]] || [[ " $@ " =~ " stop " ]] || [[ " $@ " =~ " kill " ]] || [[ " $@ " =~ " prune " ]]; then
    IS_DESTRUCTIVE=1
fi

# 4. Log to Sentinel (If destructive or forced)
if [ $IS_DESTRUCTIVE -eq 1 ]; then
    # We define the resource as the last argument (heuristic)
    # e.g. "docker volume rm my_vol" -> resource="my_vol"
    RESOURCE="${@: -1}"
    
    # Send to API silently in background (timeout 1s to not lag terminal)
    curl -s -X POST "$SENTINEL_URL/audit/log" 
      -H "Content-Type: application/json" 
      -d "{
        "org_id": "$ORG_ID",
        "actor_id": "$ACTOR",
        "action": "docker_command",
        "resource": "$RESOURCE",
        "context": {
            "ip": "$SOURCE_IP",
            "command": "$FULL_CMD",
            "risk": "high"
        }
      }" --max-time 1 > /dev/null 2>&1 &
fi

# 5. Execute Original Command
# Pass all arguments exactly as received to the real docker binary
"$REAL_DOCKER_BIN" "$@"
