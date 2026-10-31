# Optional local Windows Task Scheduler entry. No GitHub Actions.
# Uses the current interactive user's lowest-privilege principal.
# To disable later: Unregister-ScheduledTask -TaskName WERKAtlas_Local_Radar -Confirm:$false
param([switch]$Install)
$ErrorActionPreference="Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = (py -c "import sys; print(sys.executable)").Trim()
$script = Join-Path $root "scripts\daily_local.py"
if (-not (Test-Path $script)) { throw "Missing daily_local.py" }
if (-not $Install) {
  Write-Output "DRY RUN: daily 08:00 local-time read-only GitHub research, user-scoped. Pass -Install to register."
  exit 0
}
$account = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$action = New-ScheduledTaskAction -Execute $python -Argument ('"'+$script+'" --batch-size 10') -WorkingDirectory $root
$principal = New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 25)
Register-ScheduledTask -TaskName "WERKAtlas_Local_Radar" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
$task = Get-ScheduledTask -TaskName "WERKAtlas_Local_Radar"
Write-Output ("TASK_NAME="+$task.TaskName+" STATE="+$task.State+" NEXT_TRIGGER=08:00 LOCAL")
