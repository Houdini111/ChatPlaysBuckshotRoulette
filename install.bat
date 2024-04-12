pip install -r requirements.txt
@echo off
echo.
echo.
echo Check if any requirements failed to install
echo Will now check for Tesseract-OCR installation.
echo If a dialog has opened, please select where you installed it.
echo If none has appeared it successfully found it already
Powershell.exe -executionpolicy remotesigned -File chooseTesseractLocation.ps1
echo You're good to go! Go ahead and run the bot now.
pause