Add-Type -AssemblyName System.Windows.Forms

$defaultPath = 'C:\Program Files\Tesseract-OCR'
$tesseractFileName = 'tesseract.exe'
$defaultFile = $defaultPath + "\" + $tesseractFileName

if([System.IO.File]::Exists($defaultFile))
{
	exit
}

$configJson = Get-Content .\config.json -Raw | ConvertFrom-Json 

$FileBrowser = New-Object System.Windows.Forms.OpenFileDialog
$FileBrowser.Title = "Please select the installed tesseract.exe file"
$FileBrowser.InitialDirectory = 'C:\Program Files\Tesseract-OCR'
$FileBrowser.Filter = 'Executable files (*.exe)|'
$FileBrowser.CheckFileExists = $true
if($FileBrowser.ShowDialog() -eq "OK")
{
    $filePath = $FileBrowser.FileName
	$fileName = [System.IO.Path]::GetFileName($filePath)
	if ($fileName -ne $tesseractFileName) 
	{
		$prompt = "ERROR:. Expected $tesseractFileName but was given $fileName"
		Read-Host -Prompt $prompt
		exit
	}
	$configJson.tesseractPath = $filePath
	$configJson | ConvertTo-Json -Depth 4 | Out-File .\config.json  
	Read-Host -Prompt "Success! Tessearct found and configured successfully. Press any key to exit"
}
else 
{
	Read-Host -Prompt "ERROR: You must choose have installed Tessearct OCR and configured this program to point to it"
}