"""Constants used across engine and studio commands."""

from rich.console import Console

console = Console()

# Cost information
HOURLY_COSTS = {
    "cpu": 0.50,  # r6i.2xlarge
    "cpumax": 2.02,  # r7i.8xlarge
    "t4": 0.75,  # g4dn.2xlarge
    "a10g": 1.50,  # g5.2xlarge
    "a100": 21.96,  # p4d.24xlarge
    "4_t4": 3.91,  # g4dn.12xlarge
    "8_t4": 7.83,  # g4dn.metal
    "4_a10g": 6.24,  # g5.12xlarge
    "8_a10g": 16.29,  # g5.48xlarge
}

# SSH config management
SSH_MANAGED_COMMENT = "# Managed by dh engine"
