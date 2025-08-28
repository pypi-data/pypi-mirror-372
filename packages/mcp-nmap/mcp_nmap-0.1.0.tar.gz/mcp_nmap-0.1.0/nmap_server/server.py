#!/usr/bin/env python3
import subprocess
import re
import asyncio
import sys
from mcp.server.fastmcp import FastMCP

# --- Create the FastMCP instance ---
mcp = FastMCP("Easy Nmap MCP Server")

# --- Helper Functions ---
def is_valid_network(network_address: str) -> bool:
    """Checks if a string is a valid IP or a CIDR network range."""
    if '/' in network_address:
        ip_part, cidr_part = network_address.split('/')
        try:
            return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip_part) and 0 <= int(cidr_part) <= 32
        except ValueError:
            return False
    return bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', network_address))

async def run_nmap_scan(command_list: list) -> dict:
    """Executes an Nmap command in a non-blocking way."""
    def blocking_scan():
        try:
            print(f"[SERVER] Running command: {' '.join(command_list)}", file=sys.stderr, flush=True)
            result = subprocess.run(command_list, capture_output=True, text=True, timeout=3600)
            return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Scan timed out after 1 hour."}
        except Exception as e:
            return {"success": False, "output": "", "error": f"A Python error occurred: {e}"}
            
    return await asyncio.to_thread(blocking_scan)

# --- Scan Presets ---
LIGHT_SCANS = {
    "top100": {"name": "Top 100 Ports", "cmd": ["nmap", "-T4", "--top-ports", "100", "-Pn"]},
    "ping_check": {"name": "Host Discovery (Ping Scan)", "cmd": ["nmap", "-sn"]},
    "light_banner": {"name": "Light Service Banners", "cmd": ["nmap", "-sV", "--version-light", "-T4", "--top-ports", "100"]},
}
MEDIUM_SCANS = {
    "top1000": {"name": "Top 1000 Ports + Services", "cmd": ["nmap", "-sV", "-T3", "--top-ports", "1000"]},
    "os_detection": {"name": "OS Detection", "cmd": ["nmap", "-O"]},
    "default_scripts": {"name": "Default Scripts", "cmd": ["nmap", "-sC"]},
}
DEEP_SCANS = {
    "full_ports": {"name": "All 65,535 Ports", "cmd": ["nmap", "-p-", "-T3"]},
    "aggressive_full": {"name": "Aggressive Full Scan", "cmd": ["nmap", "-A", "-p-", "-T3"]},
    "vuln_scan": {"name": "Vulnerability Scan (Top 1000 ports)", "cmd": ["nmap", "-sV", "--script", "vuln", "--top-ports", "1000"]},
}

async def _execute_scan(scan_category_name: str, scan_dict: dict, target: str, scan_type: str):
    """Helper to validate and run any type of scan."""
    if not is_valid_network(target):
        return f"Error: Invalid target IP or network '{target}'"
    
    selected_scan = scan_dict.get(scan_type)
    if not selected_scan:
        return f"Error: Invalid scan type '{scan_type}'. Available: {', '.join(scan_dict.keys())}"

    command_to_run = selected_scan["cmd"] + [target]
    scan_result = await run_nmap_scan(command_to_run)

    if scan_result["success"]:
        return (f"✅ {scan_category_name} SCAN COMPLETED for {target} ({selected_scan['name']})\n\n"
                f"📊 RESULTS:\n--------------------------------------------------\n"
                f"{scan_result['output'] or 'Nmap produced no output.'}")
    else:
        return (f"❌ {scan_category_name} SCAN FAILED for {target} ({selected_scan['name']})\n\n"
                f"🚫 Error: {scan_result['error']}")

# --- MCP Tools ---
@mcp.tool()
async def scan_menu():
    """Shows all available scan options."""
    menu_text = "🎯 NMAP SCANNER MENU\n====================\n"
    menu_text += "\n🟢 LIGHT SCANS\n"
    for key, scan in LIGHT_SCANS.items(): menu_text += f" • {key}: {scan['name']}\n"
    menu_text += "\n🟡 MEDIUM SCANS\n"
    for key, scan in MEDIUM_SCANS.items(): menu_text += f" • {key}: {scan['name']}\n"
    menu_text += "\n🔴 DEEP SCANS\n"
    for key, scan in DEEP_SCANS.items(): menu_text += f" • {key}: {scan['name']}\n"
    return menu_text

@mcp.tool()
async def light_scan(target: str, scan_type: str):
    """Performs a light, fast scan."""
    return await _execute_scan("LIGHT", LIGHT_SCANS, target, scan_type)

@mcp.tool()
async def medium_scan(target: str, scan_type: str):
    """Performs a medium-detail scan."""
    return await _execute_scan("MEDIUM", MEDIUM_SCANS, target, scan_type)

@mcp.tool()
async def deep_scan(target: str, scan_type: str):
    """Performs a deep, slow, and comprehensive scan."""
    return await _execute_scan("DEEP", DEEP_SCANS, target, scan_type)

# --- Run MCP Server (stdin/stdout) ---
def main():
    """Entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
