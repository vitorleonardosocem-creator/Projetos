# Abre a porta 8005 no Windows Firewall para acesso interno à rede
# Correr como Administrador

$regra = "JogoScore porta 8005"

if (Get-NetFirewallRule -DisplayName $regra -ErrorAction SilentlyContinue) {
    Write-Host "  Regra ja existe — a actualizar..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName $regra
}

New-NetFirewallRule `
    -DisplayName $regra `
    -Direction   Inbound `
    -Protocol    TCP `
    -LocalPort   8005 `
    -Action      Allow `
    -Profile     Private,Domain `
    -Description "Permite acesso ao JogoScore (FastAPI) na porta 8005 pela rede interna." | Out-Null

Write-Host "  [OK] Porta 8005 aberta no Firewall." -ForegroundColor Green
Write-Host "  Acesso: http://192.168.10.156:8005" -ForegroundColor Cyan
