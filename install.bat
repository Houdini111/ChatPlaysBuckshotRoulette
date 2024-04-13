pip install -r requirements.txt
@echo off
Powershell.exe -executionpolicy remotesigned -File generateConfig.ps1
echo You're good to go! Go ahead and run the bot now.
pause