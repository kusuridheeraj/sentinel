#!/bin/bash

# 1. Capture Context
ACTOR=$(whoami)
# Get external IP (simple version) or SSH connection IP
REAL_IP=$(echo $SSH_CONNECTION | awk '{print $1}')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMAND_ARGS="$@"

# 2. Filter: Only care about destructive commands?
# "docker volume rm" -> Action: "volume_delete"
if [[ "$1" == "volume" && "$2" == "rm" ]]; then
    ACTION="DOCKER_VOLUME_DELETE"
    RESOURCE="$3"
    
    # 3. Send to Sentinel API (Silently)
    # curl -X POST http://localhost:8000/audit/log ...
    # We run this in background (&) so it doesn't slow down the admin
    curl -s -X POST "http://localhost:8000/audit/log" 
      -H "Content-Type: application/json" 
      -d "{
        "org_id": "infra_ops",
        "actor_id": "$ACTOR",
        "action": "$ACTION",
        "resource": "$RESOURCE",
        "context": { "ip": "$REAL_IP", "raw_cmd": "docker $COMMAND_ARGS" }
      }" > /dev/null &
fi

# 4. Execute the REAL Docker command
# In a real setup, this would call /usr/bin/docker
echo ">>> [Sentinel] Action Logged. Executing Docker command..."
# /usr/bin/docker "$@" 
# Mocking success for demo:
echo "Volume $3 removed."
