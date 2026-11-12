Client for communicating with a custom TCP server on Quader for BM31

QUADERA TcpControl add-in
=========================

Makes QUADERA listen on a TCP port (default 15000) so another program can
start, stop and export measurements. Based on the calls used by the
Triggered Run add-in.

Install
-------
1. Copy this "TcpControl" folder next to the "TriggeredRun" source folder
   (normally My Documents\My Quadera\Scripting\Code).
2. In QUADERA open any measurement project, then
   Tools > Programming > Add-in Manager...
3. Browse to TcpControl.vbproj (or pick TcpControl in the list) and click Edit.
4. In the VSTA editor choose Build > Build TcpControl. The build copies
   TcpControl.dll into the add-ins folder (..\..\QuaderaAddIns), the same
   place the Triggered Run build uses.
5. Back in the Add-in Manager, tick TcpControl and click OK.
   A small "QUADERA TCP Control" window appears showing the port and a log.
   Allow it through Windows Firewall when asked.

To load it automatically:  Quadera.exe /addin:TcpControl

Settings (top of TcpControlForm.vb, rebuild after changing)
-----------------------------------------------------------
ListenPort      TCP port, default 15000
LocalOnly       True = only programs on the QUADERA PC can connect
AllowedClients  comma-separated client IP addresses; empty = any

Protocol
--------
Plain text, one command per line (LF or CRLF), UTF-8.
Each command returns one line: "OK ..." or "ERR <reason>".

PING                         check the link
STATUS                       device, connected state, running state, project
DEVICES                      list instruments (index=name)
DEVICE <index>               choose the instrument (default: index 0)
CONNECT / DISCONNECT         connect QUADERA to the instrument
OPEN <template.qmt>|<name.qmp>
                             new measurement project from a template
                             (full path of the template on the QUADERA PC)
FILAMENT ON|OFF              switch the filament
SEM ON|OFF                   switch the SEM
START                        start the measurement
STOP                         stop the measurement
EXPORT [name.asc]            ASCII export; default is the project name + .asc
CLOSE                        close the project (stop first)
QUIT                         end this connection

Typical sequence
----------------
OPEN C:\...\MyTemplate.qmt|run_001.qmp
FILAMENT ON
START
STOP
EXPORT
CLOSE

Notes
-----
- EXPORT needs a project opened with OPEN. START and STOP also work on a
  project you opened by hand in QUADERA.
- Switch the filament (and SEM if used) on before START; otherwise QUADERA
  may show a question box on the PC and wait for a click.
- Use a new name for every OPEN, as with the Triggered Run add-in.
- Closing the TCP Control window stops remote control but not a measurement.
- There is no password. Use AllowedClients or the firewall to limit access.
