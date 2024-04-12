@echo off

for /f "delims=" %%# in  ('"wmic path Win32_VideoController  get CurrentHorizontalResolution,CurrentVerticalResolution /format:value"') do (
  set "%%#">nul
)

set /a halfWidth=%CurrentHorizontalResolution%/2
set charWidth=8 ::Found manually
set /a windowWidth=%halfWidth%/%charWidth%
echo "####"
echo %windowWidth%


MODE %windowWidth%, 10 
python bot.py