' ==============================================================
' Sejati Corp 3D Virtual Workspace & Multi-Agent Telemetry Hub
' Silent Auto-Start Script (Zero Console Flash / 24-7 Background)
' ==============================================================
Option Explicit
Dim WshShell, fso, http, isRunning, pyExe

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

pyExe = "C:\Users\user\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

isRunning = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.open "GET", "http://127.0.0.1:8800/office", False
http.setTimeouts 500, 500, 500, 500
http.send
If Err.Number = 0 Then
    If http.status = 200 Then
        isRunning = True
    End If
End If
Err.Clear
On Error GoTo 0

If Not isRunning Then
    If fso.FolderExists("D:\agent\multi_agent_dashboard") Then
        WshShell.CurrentDirectory = "D:\agent\multi_agent_dashboard"
        WshShell.Run """" & pyExe & """ server.py", 0, False
    End If
End If
