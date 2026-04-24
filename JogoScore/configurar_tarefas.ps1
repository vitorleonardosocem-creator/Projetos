# ============================================================
#  configurar_tarefas.ps1
#  Cria as 3 tarefas do JogoScore no Task Scheduler do servidor
#  Correr como Administrador no servidor 192.168.10.156
# ============================================================

$pasta = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host ""
Write-Host "  Pasta do JogoScore: $pasta" -ForegroundColor Cyan
Write-Host ""

# ── Tarefa 1: WebApp — arranca com o sistema ─────────────────
$nomeApp = "JogoScore_WebApp"

$acaoApp = New-ScheduledTaskAction `
    -Execute  "wscript.exe" `
    -Argument "`"$pasta\iniciar_webapp.vbs`"" `
    -WorkingDirectory $pasta

$gatilhoApp = New-ScheduledTaskTrigger -AtStartup

$defApp = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit    (New-TimeSpan -Hours 0) `
    -RestartCount          3 `
    -RestartInterval       (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable

$principalApp = New-ScheduledTaskPrincipal `
    -UserId    "SYSTEM" `
    -RunLevel  Highest `
    -LogonType ServiceAccount

if (Get-ScheduledTask -TaskName $nomeApp -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $nomeApp -Confirm:$false
    Write-Host "  [REMOVED] Tarefa antiga $nomeApp removida." -ForegroundColor Yellow
}

Register-ScheduledTask `
    -TaskName   $nomeApp `
    -TaskPath   "\JogoScore\" `
    -Action     $acaoApp `
    -Trigger    $gatilhoApp `
    -Settings   $defApp `
    -Principal  $principalApp `
    -Description "Arranca o servidor web JogoScore (FastAPI/uvicorn) na porta 8005." | Out-Null

Write-Host "  [OK] $nomeApp criada (arranca com o sistema)" -ForegroundColor Green


# ── Tarefa 2: Job SINEX — todos os dias às 06:30 ─────────────
$nomeSinex = "JogoScore_SINEX_Job"

$acaoSinex = New-ScheduledTaskAction `
    -Execute         "cmd.exe" `
    -Argument        "/c `"$pasta\run_sinex_job.bat`"" `
    -WorkingDirectory $pasta

# Segunda a Sexta às 06:30
$gatilhosSinex = @()
foreach ($dia in @("Monday","Tuesday","Wednesday","Thursday","Friday")) {
    $gatilhosSinex += New-ScheduledTaskTrigger `
        -Weekly -DaysOfWeek $dia -At "06:30"
}

$defSinex = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -StartWhenAvailable

$principalSinex = New-ScheduledTaskPrincipal `
    -UserId    "SYSTEM" `
    -RunLevel  Highest `
    -LogonType ServiceAccount

if (Get-ScheduledTask -TaskName $nomeSinex -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $nomeSinex -Confirm:$false
    Write-Host "  [REMOVED] Tarefa antiga $nomeSinex removida." -ForegroundColor Yellow
}

Register-ScheduledTask `
    -TaskName   $nomeSinex `
    -TaskPath   "\JogoScore\" `
    -Action     $acaoSinex `
    -Trigger    $gatilhosSinex `
    -Settings   $defSinex `
    -Principal  $principalSinex `
    -Description "Processa pontos SINEX do dia anterior. Corre seg-sex às 06:30." | Out-Null

Write-Host "  [OK] $nomeSinex criada (seg-sex 06:30)" -ForegroundColor Green


# ── Tarefa 3: Job IDOntime — todos os dias às 06:45 ──────────
$nomeIdon = "JogoScore_IDOntime_Job"

$acaoIdon = New-ScheduledTaskAction `
    -Execute          "cmd.exe" `
    -Argument         "/c `"$pasta\run_idontime_job.bat`"" `
    -WorkingDirectory $pasta

$gatilhosIdon = @()
foreach ($dia in @("Monday","Tuesday","Wednesday","Thursday","Friday")) {
    $gatilhosIdon += New-ScheduledTaskTrigger `
        -Weekly -DaysOfWeek $dia -At "06:45"
}

$defIdon = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -StartWhenAvailable

$principalIdon = New-ScheduledTaskPrincipal `
    -UserId    "SYSTEM" `
    -RunLevel  Highest `
    -LogonType ServiceAccount

if (Get-ScheduledTask -TaskName $nomeIdon -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $nomeIdon -Confirm:$false
    Write-Host "  [REMOVED] Tarefa antiga $nomeIdon removida." -ForegroundColor Yellow
}

Register-ScheduledTask `
    -TaskName   $nomeIdon `
    -TaskPath   "\JogoScore\" `
    -Action     $acaoIdon `
    -Trigger    $gatilhosIdon `
    -Settings   $defIdon `
    -Principal  $principalIdon `
    -Description "Processa pontos IDOntime do dia anterior. Corre seg-sex às 06:45." | Out-Null

Write-Host "  [OK] $nomeIdon criada (seg-sex 06:45)" -ForegroundColor Green


# ── Resumo ────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "   3 tarefas criadas em \JogoScore\" -ForegroundColor Cyan
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "   JogoScore_WebApp       -> Arranque do sistema" -ForegroundColor White
Write-Host "   JogoScore_SINEX_Job    -> Seg-Sex 06:30" -ForegroundColor White
Write-Host "   JogoScore_IDOntime_Job -> Seg-Sex 06:45" -ForegroundColor White
Write-Host ""
Write-Host "  Podes ver e editar em: Agendador de Tarefas > JogoScore" -ForegroundColor Gray
Write-Host ""
