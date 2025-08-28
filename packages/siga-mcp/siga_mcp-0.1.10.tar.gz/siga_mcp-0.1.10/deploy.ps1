# Carrega variáveis do .env se existir
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

function release {
    # Read current version from pyproject.toml
    $content = Get-Content "pyproject.toml"
    $versionLine = $content | Where-Object { $_ -match '^version = "(.+)"$' }
    $currentVersion = $matches[1]
    
    # Parse version parts
    $versionParts = $currentVersion.Split('.')
    $major = [int]$versionParts[0]
    $minor = [int]$versionParts[1]
    $patch = [int]$versionParts[2]
    
    # Increment patch version
    $patch++
    $newVersion = "$major.$minor.$patch"
    
    # Update pyproject.toml
    $newContent = $content -replace '^version = ".+"$', "version = `"$newVersion`""
    $newContent | Set-Content "pyproject.toml"
    
    Write-Host "Version bumped from $currentVersion to $newVersion"
    
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    uv build
    uv publish --token $env:UV_PUBLISH_TOKEN
}

# Executa a função release automaticamente
if ($args.Count -gt 0) {
    & $args[0]
} else {
    release
}