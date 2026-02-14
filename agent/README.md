# Sentinel Infrastructure Agent

This agent transparently wraps the `docker` command to log high-risk actions to the Sentinel Audit Log.

## How it Works
It uses a **Shell Alias** to intercept commands.
1. User types `docker volume rm data_db`.
2. The alias redirects this to `/usr/local/bin/sentinel-docker`.
3. The script:
   - Captures `SSH_CONNECTION` (Real IP).
   - Captures `whoami` (Real User).
   - POSTs the audit log to Sentinel API.
4. The script passes the command to the *real* `/usr/bin/docker`.

## Installation

Run this on your bastion host or production servers:

```bash
cd agent
sudo ./install.sh
```

## Configuration
Edit `/usr/local/bin/sentinel-docker` to point to your Sentinel Server URL.

## Security Note
This is a **User-Space Hook**. A sophisticated attacker with root access can bypass aliases (`/usr/bin/docker volume rm`). 
For kernel-level enforcement, you would need an **eBPF Probe** (Roadmap Item).
But for tracking "Accidental Deletions" or "20 Admins," this is 99% effective.
