@echo off
REM ============================================================
REM  Creates a taskbar-pinnable "Therapy Notes" shortcut on the
REM  Desktop. Windows won't pin a .bat directly, so this wraps
REM  start.bat in a cmd.exe shortcut (which IS pinnable).
REM  Run this once, then pin the Desktop shortcut.
REM ============================================================

cd /d "%~dp0"
set "APPDIR=%~dp0"

powershell -NoProfile -Command "$d=[Environment]::GetFolderPath('Desktop'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Therapy Notes.lnk')); $s.TargetPath=(Join-Path $env:WINDIR 'System32\cmd.exe'); $s.Arguments='/c start.bat'; $s.WorkingDirectory=$env:APPDIR; $s.IconLocation=(Join-Path $env:APPDIR 'app.ico'); $s.Description='Therapy Note Generator'; $s.Save()"

echo.
echo Created a branded "Therapy Notes" shortcut on the Desktop.
echo.
echo To pin it to the taskbar:
echo   1. Right-click the new Desktop shortcut
echo   2. On Windows 11, click "Show more options"
echo   3. Choose "Pin to taskbar"
echo.
pause
