$logFile = Join-Path $PSScriptRoot "check_weather_task.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$info = Get-ScheduledTaskInfo -TaskName "KakaoWeatherNotify"
$result = $info.LastTaskResult
$lastRun = $info.LastRunTime

$lines = @()
$lines += "[$timestamp] LastRunTime=$lastRun LastTaskResult=$result"

if ($result -eq 0) {
    $lines += "[$timestamp] KakaoWeatherNotify succeeded."
} else {
    $lines += "[$timestamp] KakaoWeatherNotify failed (result=$result). Re-running notify_weather.py to capture error..."
    Push-Location $PSScriptRoot
    $output = & python notify_weather.py 2>&1
    Pop-Location
    $lines += $output
}

$lines | Out-File -FilePath $logFile -Append -Encoding utf8
