Add-Type -AssemblyName System.Windows.Forms

$defaultPath = 'C:\Program Files\Tesseract-OCR'
$tesseractFileName = 'tesseract.exe'
$defaultFile = $defaultPath + "\" + $tesseractFileName



$tesseractPath = $defaultFile
if(-not [System.IO.File]::Exists($defaultFile))
{
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
		$tesseractPath = $filePath
		Write-Host "Success! Tessearct found and configured successfully."
	}
	else 
	{
		Read-Host -Prompt "ERROR: You must choose have installed Tessearct OCR and configured this program to point to it"
		exit
	}
}

Write-Host ""
Write-Host ""
Write-Host ""
$channel = Read-Host -Prompt "Please type the name of the channel to read inputs from"
#$config = @{
#	'tesseractPath' = $tesseractPath
#	'channels' = @{$channel}
#}
$config = [PSCustomObject]@{
  tesseractPath=$tesseractPath
  channels=@($channel)
} 
$config | ConvertTo-Json -Depth 4 | Out-File .\config.json  
Read-Host -Prompt "Success! Bot configured successfully."