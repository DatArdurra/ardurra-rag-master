param(
  [string]$Repo    = "ParthSharma023/ardurra-rag-master",
  [string]$EnvName = "Human-Resources"
)

# 1) Push the full JSON blob directly from file
Write-Host "Pushing AZD_INITIAL_ENVIRONMENT_CONFIG…"
gh secret set AZD_INITIAL_ENVIRONMENT_CONFIG `
  --repo $Repo `
  --env  $EnvName `
  --body-file .\env-config.json

# 2) Load JSON into an object for the other two
$config = Get-Content .\env-config.json -Raw | ConvertFrom-Json

# 3) Push AZURE_CLIENT_APP_SECRET
if ($config.AZURE_CLIENT_APP_SECRET) {
  Write-Host "Pushing AZURE_CLIENT_APP_SECRET…"
  gh secret set AZURE_CLIENT_APP_SECRET `
    --repo $Repo `
    --env  $EnvName `
    --body "$($config.AZURE_CLIENT_APP_SECRET)"
} else {
  Write-Warning "AZURE_CLIENT_APP_SECRET not found"
}

# 4) Push AZURE_SERVER_APP_SECRET
if ($config.AZURE_SERVER_APP_SECRET) {
  Write-Host "Pushing AZURE_SERVER_APP_SECRET…"
  gh secret set AZURE_SERVER_APP_SECRET `
    --repo $Repo `
    --env  $EnvName `
    --body "$($config.AZURE_SERVER_APP_SECRET)"
} else {
  Write-Warning "AZURE_SERVER_APP_SECRET not found"
}

Write-Host "`n All done."
