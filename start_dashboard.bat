@echo off
title Hermes Multi-Agent Command & Telemetry Hub
cd /d "D:\agent\multi_agent_dashboard"
echo ============================================================
echo   STARTING HERMES MULTI-AGENT COMMAND & TELEMETRY HUB
echo ============================================================
echo   Dashboard URL : http://localhost:8800
echo   Profiles      : 12 Active (1 Orchestrator + 11 Specialists)
echo   Vault Sync    : D:\agent\agent brain
echo ============================================================
echo.
python server.py
pause
