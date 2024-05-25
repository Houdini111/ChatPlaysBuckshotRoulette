Add-Type -AssemblyName System.Windows.Forms

$configFilePath = ".\config.json"

$defaultConfig = [PSCustomObject]@{
  channels=@('')
  defaultName='CHAT'
  actionVotePeriod=15
  instructionsCooldown=15
  runChatbot=$true
  runGamebot=$true
  runOverlay=$true
  useSidebarActionOverlay=$false
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

Write-Host ""
Write-Host ""
Write-Host ""
if (-not $existingConfig)
{
	$channel = Read-Host -Prompt "Please type the name of the channel to read inputs from"
}
$config | ConvertTo-Json -Depth 4 | Out-File .\config.json  
Write-Host -Prompt "Success! Bot configured successfully."