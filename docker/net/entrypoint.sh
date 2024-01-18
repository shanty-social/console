#!/bin/sh

# NOTE: Perform the following actions in a loop:
# 1. Get network interfaces from API
# 2. Set up network interfaces
# 3. Update network interface status via API.
# 4. Sleep, but allow sleep to be interrupted by...
# 4. Open a websocket connection and wait for network event.