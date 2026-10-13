#!/usr/bin/env python3
"""
Agent Client SDK & CLI for Hermes Multi-Agent Dashboard & Bus.
Enables agents and automated scripts to communicate with the dashboard,
post messages, dispatch tasks, and update telemetry.
"""
import sys
import os
import json
import argparse
import urllib.request
import urllib.error

DEFAULT_HUB_URL = os.environ.get("HERMES_HUB_URL", "http://localhost:8800")

def api_post(endpoint: str, data: dict, hub_url: str = DEFAULT_HUB_URL):
    url = f"{hub_url.rstrip('/')}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": str(e), "status": "failed"}

def api_get(endpoint: str, hub_url: str = DEFAULT_HUB_URL):
    url = f"{hub_url.rstrip('/')}{endpoint}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": str(e), "status": "failed"}

def main():
    parser = argparse.ArgumentParser(description="Hermes Agent Client CLI for Dashboard Bus")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Send message
    send_p = subparsers.add_parser("send", help="Send a message or contract to the dashboard bus")
    send_p.add_argument("--from", dest="sender", required=True, help="Sending agent name (e.g. backend, security)")
    send_p.add_argument("--to", dest="target", default="all", help="Target agent or 'all'")
    send_p.add_argument("--msg", required=True, help="Message content")
    send_p.add_argument("--type", default="chat", choices=["chat", "task", "result", "alert"], help="Message category")
    send_p.add_argument("--sync-blackboard", action="store_true", help="Also sync to Obsidian Blackboard")
    send_p.add_argument("--hub", default=DEFAULT_HUB_URL, help="Hub URL")

    # Dispatch task
    dispatch_p = subparsers.add_parser("dispatch", help="Dispatch a task to an agent via the Hub")
    dispatch_p.add_argument("--agent", required=True, help="Target specialist profile")
    dispatch_p.add_argument("--prompt", required=True, help="Task instruction")
    dispatch_p.add_argument("--sender", default="Orchestrator", help="Initiator name")
    dispatch_p.add_argument("--hub", default=DEFAULT_HUB_URL, help="Hub URL")

    # Status
    status_p = subparsers.add_parser("status", help="Get status of all agents from the hub")
    status_p.add_argument("--hub", default=DEFAULT_HUB_URL, help="Hub URL")

    # Sync
    sync_p = subparsers.add_parser("sync", help="Trigger Obsidian blackboard sync")
    sync_p.add_argument("--hub", default=DEFAULT_HUB_URL, help="Hub URL")

    args = parser.parse_args()

    if args.subcommand == "send":
        res = api_post("/api/messages", {
            "sender": args.sender,
            "target": args.target,
            "content": args.msg,
            "type": args.type,
            "sync_blackboard": args.sync_blackboard
        }, hub_url=args.hub)
        print(json.dumps(res, indent=2))

    elif args.subcommand == "dispatch":
        res = api_post("/api/dispatch", {
            "profile": args.agent,
            "prompt": args.prompt,
            "sender": args.sender,
            "sync_blackboard": True
        }, hub_url=args.hub)
        print(json.dumps(res, indent=2))

    elif args.subcommand == "status":
        res = api_get("/api/status", hub_url=args.hub)
        if "error" in res:
            print(f"[ERROR]: Hub server at {args.hub} is not responding. Make sure server.py is running.")
        else:
            print(f"Hub Status: {res.get('status')} | Agents: {res.get('total_agents')} | Uptime: {res.get('uptime_formatted')}")
            agents = api_get("/api/agents", hub_url=args.hub).get("agents", {})
            for name, data in agents.items():
                print(f"  [{data['status'].upper():<6}] {name:<14} | Tasks: {data['total_tasks']} | Avg: {data['avg_latency_ms']}ms")

    elif args.subcommand == "sync":
        res = api_post("/api/blackboard/sync", {}, hub_url=args.hub)
        print(json.dumps(res, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
