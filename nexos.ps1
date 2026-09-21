$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nexosPy = Join-Path $scriptDir "tools\nexos\nexos_cli.py"
if (Test-Path $nexosPy) {
    & python $nexosPy $args
} else {
    Write-Error "Cannot find NexOS CLI script nexos_cli.py"
}
