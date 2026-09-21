$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nexPy = Join-Path $scriptDir "tools\nex\nex.py"
if (Test-Path $nexPy) {
    & python $nexPy $args
} else {
    Write-Error "Cannot find NexOS Core CLI script nex.py"
}
