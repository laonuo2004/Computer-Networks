1120231863 CGI-Support Multi-Threaded Web Server
================================================

Environment: Windows 10 or later. No separate Python installation is required.

Quick start
-----------
1. Keep this executable, _internal, webroot and README.txt in the same folder.
2. Open PowerShell in this folder.
3. Run:

   .\1120231863CGIMultiThreadedWebServer.exe

4. Open http://127.0.0.1:8888/ in a browser.
5. Press Ctrl+C in the server window to stop it.

Optional arguments
------------------
  --host 0.0.0.0          Listen on all IPv4 interfaces.
  --port 8888             Listening port.
  --workers 8             Fixed worker thread count.
  --max-connections 32    Maximum open connections.

The server creates webroot\data\students.db when first started and writes one
access log per run under webroot\log. Do not delete or move the webroot folder.
