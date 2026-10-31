# WERKAtlas Research Hub on the local Windows Task Scheduler. No GitHub Actions.
# Daily 08:00 GitHub + news; additionally news-only at 12:00, 16:00 and 20:00.
param([switch]$Install)
$ErrorActionPreference="Stop"
$root=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python=(py -c "import sys; print(sys.executable)").Trim()
$script=Join-Path $root "scripts\run_research_hub.py"
if(-not (Test-Path $script)){throw "Missing scripts/run_research_hub.py"}
if(-not $Install){
  Write-Output "DRY RUN: daily GitHub/news 08:00; news-only 12:00, 16:00, 20:00"
  exit 0
}
$account=[Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal=New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 25)

$dailyTrigger=New-ScheduledTaskTrigger -Daily -At "08:00"
$dailyAction=New-ScheduledTaskAction -Execute $python -Argument ('"'+$script+'"') -WorkingDirectory $root
Register-ScheduledTask -TaskName "WERKAtlas_Local_Radar" -Action $dailyAction -Trigger $dailyTrigger -Principal $principal -Settings $settings -Force|Out-Null

$newsTriggers=@("12:00","16:00","20:00")|ForEach-Object {New-ScheduledTaskTrigger -Daily -At $_}
$newsAction=New-ScheduledTaskAction -Execute $python -Argument ('"'+$script+'" --news-only') -WorkingDirectory $root
Register-ScheduledTask -TaskName "WERKAtlas_News_Refresh" -Action $newsAction -Trigger $newsTriggers -Principal $principal -Settings $settings -Force|Out-Null

Get-ScheduledTask -TaskName "WERKAtlas_Local_Radar","WERKAtlas_News_Refresh" |
  ForEach-Object {Write-Output ("TASK="+$_.TaskName+" STATUS="+$_.State+" TRIGGERS="+$_.Triggers.Count)}
