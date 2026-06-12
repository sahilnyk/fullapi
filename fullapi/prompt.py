"""Interactive prompts with modern arrow key navigation."""

import re
import sys
import tty
import termios
import time
import os
from fullapi.colors import (
    error, info, muted, bold, color, Style
)
from fullapi.config import ProjectConfig

# Regex to strip ANSI escape codes for width calculations
ANSI_ESCAPE = re.compile(r'\033\[[0-9;]*m')


def _visible_len(text: str) -> int:
    """Calculate visible length excluding ANSI escape codes."""
    return len(ANSI_ESCAPE.sub('', text))


def prompt_config(project_name: str) -> ProjectConfig:
    """Prompt user for configuration with modern UI."""
    print()
    print(f"  {bold('Creating project:')} {info(project_name)}")
    print()
    
    mode = _prompt_choice(
        "Mode",
        ["Minimal structure", 
         "Production-ready"]
    )
    mode = "basic" if mode == 0 else "full"
    print()
    
    database = _prompt_choice(
        "Database",
        ["No database",
         "SQLite",
         "PostgreSQL",
         "MySQL"]
    )
    db_map = {0: "none", 1: "sqlite", 2: "postgresql", 3: "mysql"}
    database = db_map[database]
    print()
    
    auth = _prompt_choice(
        "Authentication",
        ["No auth",
         "JWT authentication"]
    )
    auth = auth == 1
    print()
    
    redis = _prompt_choice(
        "Redis Caching",
        ["Skip Redis",
         "Add Redis caching"]
    )
    redis = redis == 1
    print()
    
    middleware = _prompt_choice(
        "Middleware",
        ["Skip Middleware",
         "Add Middleware"]
    )
    middleware = middleware == 1
    print()
    
    logging = _prompt_choice(
        "Logging",
        ["Skip Logging",
         "Add Logging"]
    )
    logging = logging == 1
    print()
    
    docker = _prompt_choice(
        "Docker",
        ["Skip Docker",
         "Add Docker files"]
    )
    docker = docker == 1
    print()

    terraform = _prompt_choice(
        "Terraform",
        ["Skip Terraform",
         "Add Terraform infrastructure"]
    )
    terraform = terraform == 1

    # Terraform prompts
    cloud_provider = None
    region = None
    instance_size = "small"

    if terraform:
        print()
        cloud_provider_idx = _prompt_choice(
            "Cloud Provider",
            ["AWS",
             "Google Cloud (GCP)",
             "Azure"]
        )
        provider_map = {0: "aws", 1: "gcp", 2: "azure"}
        cloud_provider = provider_map[cloud_provider_idx]

        print()
        # Region selection based on provider
        if cloud_provider == "aws":
            region_idx = _prompt_choice(
                "AWS Region",
                ["us-east-1",
                 "us-west-2",
                 "eu-west-1"]
            )
            regions = ["us-east-1", "us-west-2", "eu-west-1"]
            region = regions[region_idx]
        elif cloud_provider == "gcp":
            region_idx = _prompt_choice(
                "GCP Region",
                ["us-central1",
                 "us-west1",
                 "europe-west1"]
            )
            regions = ["us-central1", "us-west1", "europe-west1"]
            region = regions[region_idx]
        elif cloud_provider == "azure":
            region_idx = _prompt_choice(
                "Azure Region",
                ["eastus",
                 "westus2",
                 "westeurope"]
            )
            regions = ["eastus", "westus2", "westeurope"]
            region = regions[region_idx]

        print()
        size_idx = _prompt_choice(
            "Instance Size",
            ["Small (1 vCPU, 2GB RAM) - $10-15/month",
             "Medium (2 vCPU, 4GB RAM) - $25-35/month",
             "Large (4 vCPU, 8GB RAM) - $60-80/month"]
        )
        sizes = ["small", "medium", "large"]
        instance_size = sizes[size_idx]

    return ProjectConfig(
        name=project_name,
        mode=mode,
        database=database,
        auth=auth,
        docker=docker,
        redis=redis,
        middleware=middleware,
        logging=logging,
        terraform=terraform,
        cloud_provider=cloud_provider,
        region=region,
        instance_size=instance_size
    )


def _prompt_choice(title: str, options: list) -> int:
    """Modern arrow key navigation menu with in-place redraw."""
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        tty.setraw(sys.stdin.fileno())
        
        selected = 0
        first_draw = True
        # Total lines: title(1) + blank(1) + options(N) + hint(1) = N + 3
        total_lines = len(options) + 3
        
        while True:
            # Move cursor up to redraw in place (except first draw)
            if not first_draw:
                sys.stdout.write(f"\033[{total_lines}A")
            
            # Draw title
            sys.stdout.write('\r\033[2K')
            sys.stdout.write(f"  {bold(title)}\r\n")
            
            # Draw blank line
            sys.stdout.write('\r\033[2K')
            sys.stdout.write("\r\n")
            
            # Draw options with perfect alignment
            for i, desc in enumerate(options):
                sys.stdout.write('\r\033[2K')
                if i == selected:
                    # Selected: colored "> " + colored desc
                    prefix = color("> ", Style.GREEN, Style.BOLD)
                    sys.stdout.write(f"  {prefix}{color(desc, Style.BOLD)}\r\n")
                else:
                    # Unselected: "  " + plain desc (4 spaces total indent)
                    sys.stdout.write(f"    {desc}\r\n")
            
            # Draw hint line
            sys.stdout.write('\r\033[2K')
            sys.stdout.write(f"  {muted('↑↓ navigate • Enter select • Ctrl+C exit')}\r\n")
            
            sys.stdout.flush()
            first_draw = False
            
            # Handle keyboard input
            char = sys.stdin.read(1)
            
            if char == '\x1b':  # Arrow key sequence
                sys.stdin.read(1)  # Consume '['
                arrow = sys.stdin.read(1)
                if arrow == 'A' and selected > 0:  # Up arrow
                    selected -= 1
                elif arrow == 'B' and selected < len(options) - 1:  # Down arrow
                    selected += 1
            elif char in ['\r', '\n']:  # Enter key
                return selected
            elif char == '\x03':  # Ctrl+C
                print("\n  Cancelled")
                sys.exit(0)
                
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def _clear_lines(num_lines: int):
    """Clear specified number of lines from terminal."""
    sys.stdout.write("\r")  # Return to column 0 first
    sys.stdout.write("\033[" + str(num_lines) + "A")  # Move up N lines
    sys.stdout.write("\033[J")  # Clear from cursor to end
    sys.stdout.flush()


def show_loading_animation(message: str, duration: float = 2.0):
    """Show loading animation with spinner."""
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    
    print(f"  {color(message, Style.CYAN)}", end="", flush=True)
    
    while time.time() - start_time < duration:
        for spinner in spinners:
            print(f"\r  {color(message, Style.CYAN)} {color(spinner, Style.CYAN)}", end="", flush=True)
            time.sleep(0.1)
    
    print(f"\r  {color(message, Style.CYAN)} {color('✓', Style.GREEN, Style.BOLD)}", flush=True)
    print()
