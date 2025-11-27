<#
launcher.ps1
Robust launcher for local development:
- ensures script runs from repo root
- creates or activates a local virtualenv `.venv`
- upgrades pip and installs `requirements.txt` if present
- runs tests and aborts if tests fail
- launches the app using the venv's python (`python -m uvicorn ...`) so the venv is used
#>

Set-StrictMode -Version Latest

# Resolve repository root: start from the script directory and walk up looking for
# a repository marker (requirements.txt, app/, .git, pyproject.toml, setup.py).
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
# Force Resolve-Path to return a string path (Path property) so Join-Path/Test-Path parse cleanly
$cur = (Resolve-Path $scriptDir).Path
$repoRoot = $null
while ($cur) {
	# Evaluate each Test-Path into a boolean variable to avoid parser ambiguity with -or.
	$hasRequirements = Test-Path (Join-Path $cur 'requirements.txt')
	$hasApp = Test-Path (Join-Path $cur 'app')
	$hasGit = Test-Path (Join-Path $cur '.git')
	$hasPyProject = Test-Path (Join-Path $cur 'pyproject.toml')
	$hasSetup = Test-Path (Join-Path $cur 'setup.py')

	if ($hasRequirements -or $hasApp -or $hasGit -or $hasPyProject -or $hasSetup) {
		$repoRoot = $cur
		break
	}

	$parent = Split-Path $cur -Parent
	if ($parent -eq $cur) { break }
	$cur = $parent
}

if (-not $repoRoot) {
	# Fallback to current working directory where the user invoked the script
	$repoRoot = Resolve-Path '.'
}

Set-Location $repoRoot
Write-Host "Repository root:" (Get-Location)

# Require Python (py or python)
if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
	Write-Error "Python is not available on PATH. Install Python 3 and try again."
	exit 1
}

# Prefer the py launcher if available to create venv with the correct Python 3
$pyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { 'py -3' } else { 'python' }

# Create venv if missing
if (-not (Test-Path -Path '.\.venv\Scripts\Activate.ps1')) {
	Write-Host "Creating virtual environment .venv..."
	& $pyCmd -m venv .venv
}

# Activate the venv for this session
Write-Host "Activating .venv..."
& .\.venv\Scripts\Activate.ps1

# Use the venv's python to upgrade pip and install requirements (if present)
Write-Host "Python version:"
python --version

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

if (Test-Path -Path 'requirements.txt') {
	Write-Host "Installing requirements from requirements.txt..."
	python -m pip install -r requirements.txt
}
else {
	Write-Host "No requirements.txt found; skipping pip install step."
}

# Run tests via the venv's python; abort if they fail
Write-Host "Running tests (via venv python)..."
python -m pytest -q
if ($LASTEXITCODE -ne 0) {
	Write-Error "Tests failed (pytest exit code $LASTEXITCODE). Aborting run."
	exit $LASTEXITCODE
}

Write-Host "Tests passed - Running DB Migrations."
python run_migrations.py
if ($LASTEXITCODE -ne 0) {
	Write-Error "DB migration Failed (DB Migration exit code $LASTEXITCODE). Aborting run."
	exit $LASTEXITCODE
}

Write-Host "DB Migrations done. launching app using venv's python."
python -m uvicorn app.main:app --host 0.0.0.0 --port 4200