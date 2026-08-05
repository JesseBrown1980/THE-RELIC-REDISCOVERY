[CmdletBinding()]
param(
    [ValidateRange(1, 100)]
    [int]$Levels = 5,
    [ValidateRange(0, 100)]
    [int]$CurrentLevel = 4,
    [ValidateRange(0, 100)]
    [int]$FutureLevels = 2,
    [string]$SimulatorRoot = '',
    [string]$MetatagRoot = '',
    [switch]$RelicOnly,
    [switch]$PauseOnExit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:PythonCommand = $null
$script:PythonPrefix = @()
$script:PassedTests = 0

function Resolve-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        $script:PythonCommand = $python.Source
        return
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $py) {
        $script:PythonCommand = $py.Source
        $script:PythonPrefix = @('-3')
        return
    }
    throw 'Python 3 was not found on PATH.'
}

function Invoke-PythonChecked {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [int]$ExpectedTests = -1
    )

    Write-Host ""
    Write-Host "[run] $Label"
    Push-Location $WorkingDirectory
    $previousErrorAction = $ErrorActionPreference
    try {
        # Windows PowerShell 5.1 wraps native stderr as ErrorRecord objects. Unittest writes
        # normal progress to stderr, so preserve it as output and judge only the exit code.
        $ErrorActionPreference = 'Continue'
        $output = @(& $script:PythonCommand @script:PythonPrefix @Arguments 2>&1)
        $nativeExitCode = if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE }
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
        Pop-Location
    }

    foreach ($line in $output) {
        if ($line.ToString() -ne 'System.Management.Automation.RemoteException') {
            Write-Host $line
        }
    }
    if ($nativeExitCode -ne 0) {
        throw "$Label failed with exit code $nativeExitCode."
    }

    if ($ExpectedTests -ge 0) {
        $observed = $null
        foreach ($line in $output) {
            if ($line.ToString() -match '^Ran\s+([0-9]+)\s+tests?') {
                $observed = [int]$Matches[1]
            }
        }
        if ($null -eq $observed) {
            throw "$Label did not report a unittest count."
        }
        if ($observed -ne $ExpectedTests) {
            throw "$Label expected $ExpectedTests tests but observed $observed."
        }
        $script:PassedTests += $observed
    }
    Write-Host "[ok] $Label"
}

function Get-TupleFields {
    param([Parameter(Mandatory = $true)][string]$Row)

    $fields = @{}
    foreach ($part in ($Row -split '\|')) {
        $pair = $part -split '=', 2
        if ($pair.Count -eq 2) {
            $fields[$pair[0]] = $pair[1]
        }
    }
    return $fields
}

function Assert-ExactSidecar {
    param([Parameter(Mandatory = $true)][string]$Path)

    $sidecar = "$Path.sha256"
    if (-not (Test-Path -LiteralPath $sidecar -PathType Leaf)) {
        throw "Missing SHA-256 sidecar: $sidecar"
    }
    $expected = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    $fields = ((Get-Content -Raw -LiteralPath $sidecar).Trim() -split '\s+')
    if ($fields.Count -ne 2 -or $fields[0].ToLowerInvariant() -ne $expected) {
        throw "SHA-256 sidecar differs for $Path"
    }
    Write-Host "[ok] receipt sha256=$expected"
}

function Assert-ReceiptSources {
    param(
        [Parameter(Mandatory = $true)][string]$ReceiptPath,
        [Parameter(Mandatory = $true)][string]$WorkspaceRoot
    )

    Assert-ExactSidecar -Path $ReceiptPath
    $sourceRows = @(Get-Content -LiteralPath $ReceiptPath | Where-Object { $_ -like 'SOURCE|*' })
    if ($sourceRows.Count -ne 5) {
        throw "Expected five SOURCE rows in $ReceiptPath."
    }
    foreach ($row in $sourceRows) {
        $fields = Get-TupleFields -Row $row
        if (-not $fields.ContainsKey('path') -or -not $fields.ContainsKey('sha256')) {
            throw 'Receipt SOURCE row is missing path or sha256.'
        }
        $sourcePath = Join-Path $WorkspaceRoot ($fields['path'] -replace '/', '\')
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            throw "Receipt source is missing: $sourcePath"
        }
        $observed = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourcePath).Hash.ToLowerInvariant()
        if ($observed -ne $fields['sha256'].ToLowerInvariant()) {
            throw "Receipt source hash differs: $sourcePath"
        }
        Write-Host "[ok] source=$($fields['model']) sha256=$observed"
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$workspaceRoot = Split-Path -Parent $repoRoot
if (-not $SimulatorRoot) {
    $SimulatorRoot = Join-Path $workspaceRoot 'asolaria-universe-simulator'
}
if (-not $MetatagRoot) {
    $MetatagRoot = Join-Path $workspaceRoot 'metatagging-quantum-audit-b'
}

$launcherExitCode = 1
try {
    Resolve-PythonCommand
    Write-Host '[launcher] THE RELIC REDISCOVERY'
    Write-Host '[center] C=1 at every Z'
    Write-Host '[sign] HBI -> HBP -> SHA -> SH -> HASH'
    Write-Host '[boundary] transport_chain_inferred=0 bidirectional=0 reverse=0 round_trip=0 exchange=0'
    Write-Host '[safety] E=0 network=0 port_open=0 background_service=0 destructive_wipe=0 auto_recovery=0'

    Invoke-PythonChecked -Label 'Relic reference tests' -WorkingDirectory $repoRoot `
        -Arguments @('-m', 'unittest', '-v') -ExpectedTests 49
    Invoke-PythonChecked -Label 'Relic expanding-wave view' -WorkingDirectory $repoRoot `
        -Arguments @('relic_rediscovery.py', '--levels', $Levels.ToString())
    Invoke-PythonChecked -Label 'SEN_T_I_E_N_C_E microtubule/claustrum hypothesis view' `
        -WorkingDirectory $repoRoot -Arguments @('sentience_microtubule_model.py')
    Invoke-PythonChecked -Label 'TRI_D_O_A_E_SCOPE spherical dradil view' `
        -WorkingDirectory $repoRoot -Arguments @('tridoscope_model.py')
    Invoke-PythonChecked -Label 'Public evidence hypothesis comparison' `
        -WorkingDirectory $repoRoot -Arguments @('public_evidence_comparison.py')

    if ($RelicOnly) {
        Write-Host '[hold] integrated simulator checks skipped by -RelicOnly'
        Write-Host "RESULT|status=PASS|scope=RELIC_ONLY|tests=$script:PassedTests|center=1|order=HBI_HBP_SHA_SH_HASH|E=0|json=0"
        $launcherExitCode = 0
    }
    else {
        $simulator = (Resolve-Path -LiteralPath $SimulatorRoot).Path
        $metatag = (Resolve-Path -LiteralPath $MetatagRoot).Path
        if (-not (Test-Path -LiteralPath (Join-Path $metatag 'quantum_vector_space.py') -PathType Leaf)) {
            throw "Metatag source repository is incomplete: $metatag"
        }

        Invoke-PythonChecked -Label 'Simulator root tests' -WorkingDirectory $simulator `
            -Arguments @('-m', 'unittest', '-v') -ExpectedTests 55
        Invoke-PythonChecked -Label 'Simulator nested tests' -WorkingDirectory $simulator `
            -Arguments @('-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test*.py', '-v') `
            -ExpectedTests 23
        Invoke-PythonChecked -Label 'Relic temporal metatag view' -WorkingDirectory $simulator `
            -Arguments @('relic_temporal_metatags.py', '--current-level', $CurrentLevel.ToString(), `
                '--future-levels', $FutureLevels.ToString())
        Invoke-PythonChecked -Label 'Relic generation comparison' -WorkingDirectory $simulator `
            -Arguments @('compare_relic_metatag_generations.py')

        $receipt = Join-Path $simulator 'receipts\CODEX-RELIC-METATAG-COMPARISON-2026-08-05.hbp'
        Assert-ReceiptSources -ReceiptPath $receipt -WorkspaceRoot $workspaceRoot
        if ($script:PassedTests -ne 127) {
            throw "Integrated launcher expected 127 tests but observed $script:PassedTests."
        }
        Write-Host "RESULT|status=PASS|scope=RELIC_SIMULATED_UNIVERSE|tests=$script:PassedTests|center=1|order=HBI_HBP_SHA_SH_HASH|E=0|json=0"
        $launcherExitCode = 0
    }
}
catch {
    $reason = $_.Exception.Message -replace '[|\r\n]', '_'
    Write-Host "RESULT|status=HOLD|reason=$reason|E=0|json=0"
    $launcherExitCode = 1
}
finally {
    if ($PauseOnExit) {
        [void](Read-Host 'Press Enter to close')
    }
}

exit $launcherExitCode
