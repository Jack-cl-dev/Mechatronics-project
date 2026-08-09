# =====================================================================
#  Mechatronics project -- Windows deploy script
# =====================================================================
#
#  DEPLOYMENT FLOW
#    Code\*.py -> minify.py -> .minified\*.py -> micro:bit
#
#  mpremote is always given one concrete filename at a time. No wildcard
#  is passed to mpremote.
#
#  HOW TO RUN IT
#    Easiest: double-click deploy.bat
#    Or: right-click this file -> "Run with PowerShell"
#
# =====================================================================

# WHICH PROGRAM TO PUT ON THE ROBOT:
#   0 = ask me when the script runs
#   1 = the normal robot program        -> Code\main.py
#   2 = the obstacle avoidance test     -> Code\test_avoidance.py
$WHICH_PROGRAM = 0

# After copying, stay connected and show the robot's messages on screen?
$WATCH_OUTPUT = $true

# =====================================================================
# Nothing below here needs editing.
# =====================================================================

$ErrorActionPreference = "Stop"
$exitCode = 0
$script:alreadyExplained = $false

$PROGRAMS = @(
    @{ Choice = 1; File = "main.py";           Label = "Normal robot program (line following + obstacle avoidance)" }
    @{ Choice = 2; File = "test_avoidance.py"; Label = "Obstacle avoidance test only (no line following, no clap switch)" }
)

$MINIFIED_DIR_NAME = ".minified"
$MAX_FILESYSTEM_KB = 40

function Write-Step    ($m) { Write-Host ""; Write-Host ">> $m" -ForegroundColor Cyan }
function Write-Good    ($m) { Write-Host "   $m" -ForegroundColor Green }
function Write-Warn    ($m) { Write-Host "   $m" -ForegroundColor Yellow }
function Write-Problem ($m) { Write-Host ""; Write-Host "PROBLEM: $m" -ForegroundColor Red }

function Stop-With ($message, $fixLines) {
    Write-Problem $message
    if ($fixLines) {
        Write-Host ""
        Write-Host "HOW TO FIX IT:" -ForegroundColor Yellow
        foreach ($line in $fixLines) { Write-Host "   $line" -ForegroundColor Yellow }
    }
    $script:alreadyExplained = $true
    throw $message
}

function Get-RepoRoot {
    if ($PSScriptRoot)                { return $PSScriptRoot }
    if ($PSCommandPath)               { return (Split-Path -Parent $PSCommandPath) }
    if ($MyInvocation.MyCommand.Path) { return (Split-Path -Parent $MyInvocation.MyCommand.Path) }
    return (Get-Location).Path
}

function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments, [switch]$Capture)
    $ErrorActionPreference = "Continue"
    $global:LASTEXITCODE = 0
    if ($Capture) {
        $output = & $Exe @Arguments 2>&1 | Out-String
        return @{ Code = $LASTEXITCODE; Output = $output }
    }
    & $Exe @Arguments
    return @{ Code = $LASTEXITCODE; Output = "" }
}

function Find-Python {
    foreach ($py in @("python", "py", "python3")) {
        if (Get-Command $py -ErrorAction SilentlyContinue) {
            return $py
        }
    }
    return $null
}

function Find-Mpremote {
    if (Get-Command mpremote -ErrorAction SilentlyContinue) { return @("mpremote") }

    foreach ($py in @("python", "py", "python3")) {
        if (Get-Command $py -ErrorAction SilentlyContinue) {
            $probe = Invoke-Native -Exe $py -Arguments @("-c", "import mpremote") -Capture
            if ($probe.Code -eq 0) { return @($py, "-m", "mpremote") }
        }
    }
    return $null
}

function Install-Mpremote {
    foreach ($py in @("python", "py", "python3")) {
        if (Get-Command $py -ErrorAction SilentlyContinue) {
            Write-Warn "mpremote is missing. Installing it with '$py'..."
            $r = Invoke-Native -Exe $py -Arguments @("-m", "pip", "install", "--user", "--upgrade", "mpremote")
            if ($r.Code -eq 0) { return $true }
        }
    }
    return $false
}

try {
    Write-Host "=====================================================" -ForegroundColor White
    Write-Host " Mechatronics project -- micro:bit deploy" -ForegroundColor White
    Write-Host "=====================================================" -ForegroundColor White

    # --- 1. Locate the repo ----------------------------------------------
    $root = Get-RepoRoot
    Set-Location -LiteralPath $root
    [Environment]::CurrentDirectory = $root

    $codeDir = Join-Path $root "Code"
    $minifiedDir = Join-Path $root $MINIFIED_DIR_NAME
    $minifyScript = Join-Path $root "minify.py"

    if (-not (Test-Path -LiteralPath $codeDir)) {
        Stop-With "Can't find the 'Code' folder next to this script." @(
            "This script has to stay in the top level of the cloned repo."
            "Right now it is in: $root"
        )
    }

    if (-not (Test-Path -LiteralPath $minifyScript)) {
        Stop-With "Can't find minify.py next to deploy.ps1." @(
            "Keep deploy.ps1, minify.py and the Code folder together at the repo root."
        )
    }

    Write-Good "Repo folder: $root"

    # --- 2. Which program? -----------------------------------------------
    $available = @()
    foreach ($p in $PROGRAMS) {
        if (Test-Path -LiteralPath (Join-Path $codeDir $p.File)) { $available += $p }
    }

    if ($available.Count -eq 0) {
        Stop-With "None of the deployable programs exist in $codeDir." @(
            "Expected to find main.py or test_avoidance.py in there."
        )
    }

    $choice = $WHICH_PROGRAM
    if ($choice -ne 1 -and $choice -ne 2) {
        if ($choice -ne 0) {
            Write-Warn "WHICH_PROGRAM is set to '$choice', which is not 0, 1 or 2. Asking instead."
        }

        Write-Step "What do you want to put on the robot?"
        foreach ($p in $available) {
            Write-Host "   [$($p.Choice)] $($p.Label)"
            Write-Host "       -> Code\$($p.File)" -ForegroundColor DarkGray
        }

        Write-Host ""
        while ($true) {
            $answer = "$(Read-Host '   Type 1 or 2 and press Enter')".Trim()
            if ($answer -eq "1" -or $answer -eq "main") { $choice = 1; break }
            if ($answer -eq "2" -or $answer -eq "test") { $choice = 2; break }
            Write-Warn "Did not understand '$answer'. Please type just 1 or 2."
        }
    }

    $selected = @($available | Where-Object { $_.Choice -eq $choice })[0]
    if (-not $selected) {
        Stop-With "Program $choice was chosen, but its file is missing from $codeDir." @(
            "Set WHICH_PROGRAM to 0 near the top of this script to choose from available programs."
        )
    }

    $entry = $selected.File
    Write-Good "Deploying: $entry"
    Write-Good "  ($($selected.Label))"

    # --- 3. Find Python and minify everything in Code -------------------
    Write-Step "Minifying Code\ into $MINIFIED_DIR_NAME\..."

    $python = Find-Python
    if (-not $python) {
        Stop-With "Python is required to run minify.py." @(
            "Install Python from https://www.python.org/downloads/"
            "Make sure 'Add python.exe to PATH' is enabled."
        )
    }

    if (Test-Path -LiteralPath $minifiedDir) {
        Remove-Item -LiteralPath $minifiedDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $minifiedDir -Force | Out-Null

    $minifyResult = Invoke-Native -Exe $python -Arguments @(
        $minifyScript,
        $codeDir,
        $minifiedDir
    ) -Capture

    if ($minifyResult.Code -ne 0) {
        Stop-With "minify.py failed." @(
            $minifyResult.Output.Trim()
        )
    }

    $entryMinified = Join-Path $minifiedDir $entry
    if (-not (Test-Path -LiteralPath $entryMinified)) {
        Stop-With "Minification did not produce $MINIFIED_DIR_NAME\$entry." @(
            "Check the minify.py output above for a parse error."
        )
    }

    # --- 4. Work out the minified file list ------------------------------
    # Get-ChildItem gives us concrete files. Each one is handed separately
    # to mpremote; no wildcard is ever passed to mpremote.
    $entryNames = @($PROGRAMS | ForEach-Object { $_.File })
    $modules = @(Get-ChildItem -LiteralPath $minifiedDir -File |
                 Where-Object { $_.Extension -eq ".py" } |
                 Where-Object { $entryNames -notcontains $_.Name } |
                 Sort-Object Name)

    $allMinified = @(Get-ChildItem -LiteralPath $minifiedDir -File |
                     Where-Object { $_.Extension -eq ".py" } |
                     Sort-Object Name)

    if ($allMinified.Count -eq 0) {
        Stop-With "minify.py produced no Python files." @(
            "Check that Code\ contains .py files."
        )
    }

    $totalBytes = ($allMinified | Measure-Object -Property Length -Sum).Sum
    $totalKb = [math]::Round(([double]$totalBytes / 1KB), 1)
    Write-Good "$($allMinified.Count) minified Python file(s): $totalKb KB"

    if ($totalKb -gt $MAX_FILESYSTEM_KB) {
        Write-Warn "That is a lot for a micro:bit. If you get a 'No space' error,"
        Write-Warn "wipe the board's files first and run this script again."
    }

    # --- 5. Find (or install) mpremote ----------------------------------
    Write-Step "Looking for mpremote..."
    $mpremote = Find-Mpremote

    if (-not $mpremote) {
        if (-not (Install-Mpremote)) {
            Stop-With "Could not install mpremote automatically." @(
                "Run: python -m pip install --user mpremote"
                "Then run deploy.ps1 again."
            )
        }

        $mpremote = Find-Mpremote
        if (-not $mpremote) {
            Stop-With "mpremote was installed, but Python still cannot import it." @(
                "Close this window, open a new PowerShell window, and run deploy.ps1 again."
            )
        }
    }

    $mpExe = $mpremote[0]
    $mpPre = @()
    if ($mpremote.Count -gt 1) {
        $mpPre = $mpremote[1..($mpremote.Count - 1)]
    }
    Write-Good "Using: $($mpremote -join ' ')"

    function Invoke-Mpremote {
        param([string[]]$MpArgs, [switch]$Capture)
        return Invoke-Native -Exe $mpExe -Arguments ($mpPre + $MpArgs) -Capture:$Capture
    }

    # --- 6. Check the board ----------------------------------------------
    Write-Step "Looking for the micro:bit..."
    $attempt = 0

    while ($true) {
        $probe = Invoke-Mpremote -MpArgs @("connect", "auto", "exec", "pass") -Capture
        if ($probe.Code -eq 0) {
            Write-Good "Found it."
            break
        }

        $attempt++
        Write-Problem "Cannot talk to the micro:bit."

        if ($probe.Output.Trim()) {
            Write-Host "   (mpremote said: $($probe.Output.Trim()))" -ForegroundColor DarkGray
        }

        Write-Host ""
        Write-Host "CHECK ALL OF THESE:" -ForegroundColor Yellow
        Write-Host "   * The micro:bit is plugged in with a USB DATA cable" -ForegroundColor Yellow
        Write-Host "   * Nothing else is holding the port" -ForegroundColor Yellow
        Write-Host "   * The board has MicroPython flashed on it, not MakeCode" -ForegroundColor Yellow
        Write-Host "   * Try a different USB port or cable" -ForegroundColor Yellow
        Write-Host ""

        if ($attempt -ge 3) {
            Stop-With "Gave up after $attempt attempts to reach the board." @(
                "Once the board appears in Device Manager as a USB Serial Device,"
                "run deploy.ps1 again."
            )
        }

        Read-Host "   Fix it and press Enter to retry (or close this window to give up)" | Out-Null
    }

    # --- 7. Copy minified modules, one concrete file at a time -----------
    Write-Step "Copying minified modules to the board..."

    foreach ($m in $modules) {
        Write-Host "   $($m.Name)"

        $r = Invoke-Mpremote -MpArgs @(
            "connect", "auto", "fs", "cp",
            $m.FullName,
            ":$($m.Name)"
        ) -Capture

        if ($r.Code -ne 0) {
            Stop-With "Failed to copy $($m.Name) to the board." @(
                "mpremote said: $($r.Output.Trim())"
                "If that mentions space, wipe the board's files and try again."
            )
        }
    }

    Write-Good "$($modules.Count) module(s) copied."

    # The selected entry point is copied separately as main.py.
    Write-Step "Copying minified $entry to the board as main.py..."

    $r = Invoke-Mpremote -MpArgs @(
        "connect", "auto", "fs", "cp",
        $entryMinified,
        ":main.py"
    ) -Capture

    if ($r.Code -ne 0) {
        Stop-With "Failed to copy $entry to the board as main.py." @(
            "mpremote said: $($r.Output.Trim())"
        )
    }

    Write-Good "Done -- the board will run $entry whenever it is reset or powered on."

    # --- 8. Run the minified entry script -------------------------------
    if ($WATCH_OUTPUT) {
        Write-Step "Starting the minified program. Press Ctrl-C to stop it."

        if ($entry -eq "test_avoidance.py") {
            Write-Host "   Reminder: put the robot on the floor, then press button A" -ForegroundColor DarkGray
            Write-Host "   on the micro:bit to start driving. Button B stops it." -ForegroundColor DarkGray
            Write-Host "   If the compass needs calibrating, the board will show TILT --" -ForegroundColor DarkGray
            Write-Host "   tilt it to fill the screen, holding it away from the motors." -ForegroundColor DarkGray
        }

        Write-Host ""
        Invoke-Mpremote -MpArgs @("connect", "auto", "run", $entryMinified) | Out-Null
        Write-Host ""
        Write-Good "Program ended. It is still on the board -- press reset to run it again."
    }
    else {
        Write-Step "Files are on the board."
        Write-Good "Press the reset button on the back of the micro:bit to run it."
    }
}
catch {
    if (-not $script:alreadyExplained) {
        Write-Problem $_.Exception.Message
        Write-Host "   (unexpected error at line $($_.InvocationInfo.ScriptLineNumber))" -ForegroundColor DarkGray
    }
    $exitCode = 1
}
finally {
    Write-Host ""
    Read-Host "Press Enter to close this window" | Out-Null
}

exit $exitCode
