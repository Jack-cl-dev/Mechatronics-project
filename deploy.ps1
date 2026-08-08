# =====================================================================
#  Mechatronics project -- Windows deploy script
# =====================================================================
#
#  WHAT THIS DOES
#    Copies the robot code from the Code folder onto the micro:bit. The
#    micro:bit only ever auto-runs a file called main.py, so whichever program
#    you pick below gets copied to the board renamed to main.py.
#
#  HOW TO RUN IT
#    Easiest:  double-click deploy.bat  (in this same folder)
#    Or:       right-click this file -> "Run with PowerShell"
#
#  YOU DO NOT NEED TO PASS ANY ARGUMENTS. Make your choice in the settings
#  block below, or leave it as 0 and the script will ask you when it runs.
#
# =====================================================================
#  SETTINGS -- this is the only part you should ever need to edit
# =====================================================================

# WHICH PROGRAM TO PUT ON THE ROBOT:
#   0 = ask me when the script runs   (recommended)
#   1 = the normal robot program        -> Code\main.py
#   2 = the obstacle avoidance test     -> Code\test_avoidance.py
$WHICH_PROGRAM = 0

# After copying, stay connected and show the robot's messages on screen?
#   $true  = watch the print() output live (best for testing). Ctrl-C to stop.
#   $false = just copy the files and exit. Press the board's reset button to run.
$WATCH_OUTPUT = $true

# =====================================================================
#  Nothing below here needs editing.
# =====================================================================

$ErrorActionPreference = "Stop"
$exitCode = 0
$script:alreadyExplained = $false

# --- Entry points: exactly one of these is deployed, renamed to main.py. ------
$PROGRAMS = @(
    @{ Choice = 1; File = "main.py";           Label = "Normal robot program (line following + obstacle avoidance)" }
    @{ Choice = 2; File = "test_avoidance.py"; Label = "Obstacle avoidance test only (no line following, no clap switch)" }
)

$MAX_FILESYSTEM_KB = 40   # rough micro:bit V2 budget; warn before mpremote errors

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

# Locate Code\ relative to THIS FILE, not the current directory, so a fresh
# `git clone` works untouched no matter which folder the user launched from.
function Get-RepoRoot {
    if ($PSScriptRoot)                   { return $PSScriptRoot }
    if ($PSCommandPath)                  { return (Split-Path -Parent $PSCommandPath) }
    if ($MyInvocation.MyCommand.Path)    { return (Split-Path -Parent $MyInvocation.MyCommand.Path) }
    return (Get-Location).Path
}

# Run a native command and hand back its exit code and output.
#
# The local $ErrorActionPreference is deliberate and load-bearing: in Windows
# PowerShell 5.1, a native program writing to stderr while the preference is
# "Stop" raises a NativeCommandError and kills the script. mpremote reports "no
# device found" on stderr, and pip prints warnings there, so without this every
# failure path below would explode instead of being handled.
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

function Find-Mpremote {
    if (Get-Command mpremote -ErrorAction SilentlyContinue) { return @("mpremote") }
    # Very common on Windows: the package is installed but Python's Scripts
    # folder isn't on PATH, so the bare `mpremote` command doesn't resolve.
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
            Write-Warn "mpremote is missing. Installing it with '$py' (this needs internet)..."
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

    # --- 1. Locate the repo and the Code folder --------------------------
    $root = Get-RepoRoot
    Set-Location -LiteralPath $root
    # Set-Location only moves PowerShell's own location. Child processes read
    # the real process working directory, so pin that too -- otherwise the
    # relative "Code/x.py" paths handed to mpremote could resolve elsewhere.
    [Environment]::CurrentDirectory = $root

    $codeDir = Join-Path $root "Code"
    if (-not (Test-Path -LiteralPath $codeDir)) {
        Stop-With "Can't find the 'Code' folder next to this script." @(
            "This script has to stay in the top level of the cloned repo,"
            "next to the Code folder. Right now it is in:"
            "  $root"
            "If you copied deploy.ps1 somewhere else on its own, move it back."
        )
    }
    Write-Good "Repo folder: $root"

    # --- 2. Which program? ----------------------------------------------
    $available = @()
    foreach ($p in $PROGRAMS) {
        if (Test-Path -LiteralPath (Join-Path $codeDir $p.File)) { $available += $p }
    }
    if ($available.Count -eq 0) {
        Stop-With "None of the deployable programs exist in $codeDir." @(
            "Expected to find main.py or test_avoidance.py in there."
            "Try re-cloning the repo, or check you are on the right git branch."
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
            "Set WHICH_PROGRAM to 0 near the top of this script to be shown"
            "the list of programs that actually exist."
        )
    }
    $entry = $selected.File
    Write-Good "Deploying: $entry"
    Write-Good "  ($($selected.Label))"

    # --- 3. Work out the file list ---------------------------------------
    # Everything the chosen program imports. robot_*.py are the vendor demo
    # scripts -- they have top-level while loops and nothing imports them, so
    # they stay off the board to save its very limited filesystem space.
    $entryNames = @($PROGRAMS | ForEach-Object { $_.File })
    # -Filter on Windows can over-match via legacy 8.3 short names (the classic
    # "*.doc also matches .docx"), so re-check the extension properly.
    $modules = @(Get-ChildItem -LiteralPath $codeDir -Filter "*.py" -File |
                 Where-Object { $_.Extension -eq ".py" } |
                 Where-Object { $entryNames -notcontains $_.Name } |
                 Where-Object { $_.Name -notlike "robot_*.py" } |
                 Sort-Object Name)
    if ($modules.Count -eq 0) {
        Stop-With "Found no modules to copy in $codeDir." @(
            "Code\ should contain maqueen.py, compass.py, sound_detect.py,"
            "obstacle_detect.py and object_avoidance.py. Try re-cloning."
        )
    }

    $entryFile = Get-Item -LiteralPath (Join-Path $codeDir $entry)
    $moduleBytes = ($modules | Measure-Object -Property Length -Sum).Sum
    $totalKb = [math]::Round((([double]$moduleBytes + $entryFile.Length) / 1KB), 1)
    Write-Good "$($modules.Count) module(s) + $entry = $totalKb KB"
    if ($totalKb -gt $MAX_FILESYSTEM_KB) {
        Write-Warn "That is a lot for a micro:bit. If you get a 'No space' error"
        Write-Warn "below, wipe the board's files first with:"
        Write-Warn "  mpremote connect auto fs rm :main.py"
    }

    # --- 4. Find (or install) mpremote -----------------------------------
    Write-Step "Looking for mpremote (the tool that talks to the board)..."
    $mpremote = Find-Mpremote
    if (-not $mpremote) {
        $havePython = (Get-Command python -ErrorAction SilentlyContinue) -or
                      (Get-Command py -ErrorAction SilentlyContinue) -or
                      (Get-Command python3 -ErrorAction SilentlyContinue)
        if (-not $havePython) {
            Stop-With "Python is not installed, so mpremote cannot be installed either." @(
                "1. Install Python from https://www.python.org/downloads/"
                "2. IMPORTANT: tick 'Add python.exe to PATH' in the installer."
                "3. Close this window, then run deploy.bat again."
            )
        }
        if (-not (Install-Mpremote)) {
            Stop-With "Could not install mpremote automatically." @(
                "Open Command Prompt and run:"
                "   python -m pip install --user mpremote"
                "then run deploy.bat again."
            )
        }
        $mpremote = Find-Mpremote
        if (-not $mpremote) {
            Stop-With "mpremote was installed, but Python still cannot import it." @(
                "Close this window, open a new one, and run deploy.bat again."
                "(PATH changes only apply to newly opened windows.)"
            )
        }
    }
    $mpExe = $mpremote[0]
    $mpPre = @()
    if ($mpremote.Count -gt 1) { $mpPre = $mpremote[1..($mpremote.Count - 1)] }
    Write-Good "Using: $($mpremote -join ' ')"

    function Invoke-Mpremote {
        param([string[]]$MpArgs, [switch]$Capture)
        return Invoke-Native -Exe $mpExe -Arguments ($mpPre + $MpArgs) -Capture:$Capture
    }

    # --- 5. Is a board actually plugged in? ------------------------------
    Write-Step "Looking for the micro:bit..."
    $attempt = 0
    while ($true) {
        $probe = Invoke-Mpremote -MpArgs @("connect", "auto", "exec", "pass") -Capture
        if ($probe.Code -eq 0) { Write-Good "Found it."; break }

        $attempt++
        Write-Problem "Cannot talk to the micro:bit."
        if ($probe.Output.Trim()) {
            Write-Host "   (mpremote said: $($probe.Output.Trim()))" -ForegroundColor DarkGray
        }
        Write-Host ""
        Write-Host "CHECK ALL OF THESE:" -ForegroundColor Yellow
        Write-Host "   * The micro:bit is plugged in with a USB DATA cable" -ForegroundColor Yellow
        Write-Host "     (charge-only cables look identical but will not work)" -ForegroundColor Yellow
        Write-Host "   * Nothing else is holding the port -- close Mu, Thonny," -ForegroundColor Yellow
        Write-Host "     any Python/MakeCode editor tab, and any serial monitor" -ForegroundColor Yellow
        Write-Host "   * The board has MicroPython flashed on it, not MakeCode" -ForegroundColor Yellow
        Write-Host "   * Try a different USB port or cable" -ForegroundColor Yellow
        Write-Host ""
        if ($attempt -ge 3) {
            Stop-With "Gave up after $attempt attempts to reach the board." @(
                "Once the board appears in Device Manager as a USB Serial Device,"
                "run deploy.bat again."
            )
        }
        Read-Host "   Fix it and press Enter to retry (or close this window to give up)" | Out-Null
    }

    # --- 6. Copy ----------------------------------------------------------
    Write-Step "Copying modules to the board..."
    foreach ($m in $modules) {
        Write-Host "   $($m.Name)"
        # Relative paths on purpose: mpremote treats a leading ':' as "on the
        # board", and Windows absolute paths carry their own colon.
        $r = Invoke-Mpremote -MpArgs @("connect", "auto", "fs", "cp",
                                       "Code/$($m.Name)", ":$($m.Name)") -Capture
        if ($r.Code -ne 0) {
            Stop-With "Failed to copy $($m.Name) to the board." @(
                "mpremote said: $($r.Output.Trim())"
                "If that mentions space, wipe the board's files and try again."
            )
        }
    }
    Write-Good "$($modules.Count) module(s) copied."

    Write-Step "Copying Code\$entry to the board as main.py..."
    Write-Host "   (main.py is the only filename the micro:bit runs on its own)" -ForegroundColor DarkGray
    $r = Invoke-Mpremote -MpArgs @("connect", "auto", "fs", "cp",
                                   "Code/$entry", ":main.py") -Capture
    if ($r.Code -ne 0) {
        Stop-With "Failed to copy $entry to the board as main.py." @(
            "mpremote said: $($r.Output.Trim())"
        )
    }
    Write-Good "Done -- the board runs $entry whenever it is reset or powered on."

    # --- 7. Run -----------------------------------------------------------
    if ($WATCH_OUTPUT) {
        Write-Step "Starting the program. Press Ctrl-C to stop it."
        if ($entry -eq "test_avoidance.py") {
            Write-Host "   Reminder: put the robot on the floor, then press button A" -ForegroundColor DarkGray
            Write-Host "   on the micro:bit to start driving. Button B stops it." -ForegroundColor DarkGray
            Write-Host "   If the compass needs calibrating, the board will show TILT --" -ForegroundColor DarkGray
            Write-Host "   tilt it to fill the screen, holding it away from the motors." -ForegroundColor DarkGray
        }
        Write-Host ""
        Invoke-Mpremote -MpArgs @("connect", "auto", "run", "Code/$entry") | Out-Null
        Write-Host ""
        Write-Good "Program ended. It is still on the board -- press reset to run it again."
    }
    else {
        Write-Step "Files are on the board."
        Write-Good "Press the reset button on the back of the micro:bit to run it."
    }
}
catch {
    # Stop-With already printed a friendly explanation. Anything reaching here
    # without that flag is unexpected, so show it rather than a bare stack trace.
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
