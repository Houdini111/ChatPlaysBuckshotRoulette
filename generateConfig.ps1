Add-Type -AssemblyName System.Windows.Forms

$configFilePath = ".\config.json"

$defaultPath = 'C:\Program Files\Tesseract-OCR'
$tesseractFileName = 'tesseract.exe'
$defaultFile = $defaultPath + "\" + $tesseractFileName

$defaultConfig = [PSCustomObject]@{
  tesseractPath=$defaultFile
  channels=@('')
  defaultName='CHAT'
  actionVotePeriod=15
} 
$config = $defaultConfig.PsObject.Copy()


#Migrate old, adding new fields if they don't exist in the current config file
$existingConfig = $false
if([System.IO.File]::Exists($configFilePath))
{
	$existingConfig = $true
	$fileConfigObj = [PSCustomObject](Get-Content $configFilePath | Out-String | ConvertFrom-Json)
	$defaultConfig.PsObject.Properties | ForEach-Object {
		$attrName = $_.Name
		$attrVal = $_.Value
		$fileConfigHasValue = [bool]($fileConfigObj.PSObject.Properties.name -match $attrName)
		if ($fileConfigHasValue)
		{
			$fileConfigValue = $fileConfigObj | Select-Object -ExpandProperty $attrName
			#Write-Host "Key: $attrName Default: $attrVal In Config: $fileConfigValue"
		}
		else 
		{
			#Write-Host "Key: $attrName Default: $attrVal NO MATCHING KEY IN CONFIG"
			Write-Host "While migrating config file found missing key $attrName and so adding it with default value of $attrVal"
			$fileConfigObj | Add-Member -NotePropertyName $attrName -NotePropertyValue $attrVal
		}
	}
	Write-Host "Finishing ensuring config up to date"
	$config = $fileConfigObj
	Write-Host "Config after migration: "
	Write-Host $config
}

#Ensure tessearact path is valid
if(-not [System.IO.File]::Exists($config.tesseractPath))
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
			$prompt = "ERROR: Expected $tesseractFileName but was given $fileName"
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
if (-not $existingConfig)
{
	$channel = Read-Host -Prompt "Please type the name of the channel to read inputs from"
}
$config | ConvertTo-Json -Depth 4 | Out-File .\config.json  
Write-Host -Prompt "Success! Bot configured successfully."