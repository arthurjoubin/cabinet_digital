$projectPath = "C:\Users\arthu\OneDrive\Bureau\cabinet_digital"
$parentPath = Split-Path -Parent $projectPath
Set-Location -Path $parentPath
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$destination = "C:\Users\arthu\OneDrive\Bureau\cabinet_digital_$date.zip"

$folderToZip = Split-Path -Leaf $projectPath
$tempFolder = Join-Path $env:TEMP "cabinet_digital"

# Créer une copie temporaire sans node_modules
robocopy $folderToZip $tempFolder /E /XD node_modules

# Créer l'archive à partir du dossier temporaire
Compress-Archive -Path $tempFolder -DestinationPath $destination -Force

# Nettoyer le dossier temporaire
Remove-Item -Path $tempFolder -Recurse -Force