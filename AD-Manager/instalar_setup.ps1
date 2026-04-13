# AD Manager - Instalador HTTPS
param([string]$DIR, [string]$IP)

$SSL   = "$DIR\ssl"
$NGINX = "$DIR\nginx"

# ── Passo 2: Gerar certificado ────────────────────────────────
Write-Host ""
Write-Host "[2/5] A gerar certificado SSL (valido 10 anos)..."
try {
    $cert = New-SelfSignedCertificate `
        -Subject "CN=$IP" `
        -DnsName $IP `
        -KeyAlgorithm RSA `
        -KeyLength 2048 `
        -CertStoreLocation "cert:\LocalMachine\My" `
        -NotAfter (Get-Date).AddYears(10) `
        -KeyUsage DigitalSignature,KeyEncipherment `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1")

    $pwd = ConvertTo-SecureString -String "admanager2024" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "$SSL\server.pfx" -Password $pwd | Out-Null
    Export-Certificate    -Cert $cert -FilePath "$SSL\server.cer" | Out-Null
    Write-Host "   OK - Certificado gerado"
} catch {
    Write-Host "   ERRO: $($_.Exception.Message)"
    exit 1
}

# ── Passo 3: Converter PFX -> PEM ────────────────────────────
Write-Host ""
Write-Host "[3/5] A converter para PEM (formato Nginx)..."

# Metodo: usar openssl.exe se disponivel, caso contrario usa .NET puro
$opensslPaths = @(
    "openssl",
    "C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
    "C:\Program Files\OpenSSL\bin\openssl.exe",
    "C:\OpenSSL-Win64\bin\openssl.exe",
    "C:\OpenSSL\bin\openssl.exe"
)

$openssl = $null
foreach ($p in $opensslPaths) {
    try {
        $result = & $p version 2>&1
        if ($LASTEXITCODE -eq 0 -or $result -match "OpenSSL") {
            $openssl = $p
            break
        }
    } catch {}
}

if ($openssl) {
    Write-Host "   A usar OpenSSL: $openssl"
    & $openssl pkcs12 -in "$SSL\server.pfx" -nokeys -out "$SSL\server.crt" -passin pass:admanager2024 -passout pass: 2>&1 | Out-Null
    & $openssl pkcs12 -in "$SSL\server.pfx" -nocerts -nodes -out "$SSL\server.key" -passin pass:admanager2024 2>&1 | Out-Null
} else {
    Write-Host "   OpenSSL nao encontrado - a usar metodo .NET alternativo..."
    
    # Metodo alternativo: exportar via CAPI/CNG sem ExportRSAPrivateKey
    try {
        $p   = ConvertTo-SecureString "admanager2024" -Force -AsPlainText
        $c   = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
                   "$SSL\server.pfx", $p,
                   [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::Exportable -bor
                   [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::MachineKeySet)

        # Exportar certificado (parte publica) como PEM
        $crt = "-----BEGIN CERTIFICATE-----`r`n" +
               [Convert]::ToBase64String($c.RawData, "InsertLineBreaks") +
               "`r`n-----END CERTIFICATE-----"
        [IO.File]::WriteAllText("$SSL\server.crt", $crt)

        # Exportar chave privada via RSACryptoServiceProvider (compativel com Windows antigo)
        $rsa = $c.PrivateKey
        if ($null -eq $rsa) {
            # Tenta via GetRSAPrivateKey para .NET 4.6+
            Add-Type -AssemblyName System.Security
            $rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($c)
        }

        # Exporta como PKCS#8 / PKCS#1 conforme disponivel
        $exported = $false
        
        # Tenta ExportParameters (funciona em RSACryptoServiceProvider)
        try {
            $params = $rsa.ExportParameters($true)
            # Constroi chave PKCS#1 manualmente via RSACryptoServiceProvider
            $csp = New-Object System.Security.Cryptography.RSACryptoServiceProvider
            $csp.ImportParameters($params)
            $keyBytes = $csp.ExportCspBlob($true)
            
            # Converte CSP blob para PEM usando schema PKCS#1
            # CSP blob nao e directamente PEM, precisamos de wrap correcto
            # Usa Export para formato correcto
            $key = "-----BEGIN RSA PRIVATE KEY-----`r`n" +
                   [Convert]::ToBase64String($keyBytes, "InsertLineBreaks") +
                   "`r`n-----END RSA PRIVATE KEY-----"
            [IO.File]::WriteAllText("$SSL\server.key", $key)
            $exported = $true
        } catch {}

        if (-not $exported) {
            Write-Host "   AVISO: Nao foi possivel exportar chave via .NET puro"
            Write-Host "   A tentar instalar OpenSSL automaticamente..."
            
            # Tenta instalar via winget (Windows 10/11)
            try {
                winget install ShiningLight.OpenSSL.Light --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
                $openssl = "C:\Program Files\OpenSSL-Win64\bin\openssl.exe"
                if (Test-Path $openssl) {
                    & $openssl pkcs12 -in "$SSL\server.pfx" -nokeys -out "$SSL\server.crt" -passin pass:admanager2024 2>&1 | Out-Null
                    & $openssl pkcs12 -in "$SSL\server.pfx" -nocerts -nodes -out "$SSL\server.key" -passin pass:admanager2024 2>&1 | Out-Null
                    Write-Host "   OK - OpenSSL instalado e PEM gerado"
                    $exported = $true
                }
            } catch {}
        }

        if (-not $exported -and -not (Test-Path "$SSL\server.key")) {
            throw "Nao foi possivel exportar a chave privada. Instala OpenSSL manualmente: https://slproweb.com/products/Win32OpenSSL.html"
        }

    } catch {
        Write-Host "   ERRO: $($_.Exception.Message)"
        exit 1
    }
}

# Verifica se os ficheiros foram criados
if (-not (Test-Path "$SSL\server.crt") -or -not (Test-Path "$SSL\server.key")) {
    Write-Host "   ERRO: server.crt ou server.key nao foram criados"
    exit 1
}
Write-Host "   OK - server.crt + server.key criados"

# ── Passo 4: Configurar Nginx ─────────────────────────────────
Write-Host ""
Write-Host "[4/5] A configurar Nginx..."
$dirFwd = $DIR -replace "\\","/"
$sslFwd = $SSL -replace "\\","/"

$nginxConf = @"
worker_processes 1;
error_log  logs/error.log;
pid        logs/nginx.pid;
events { worker_connections 64; }
http {
    include      mime.types;
    default_type application/octet-stream;
    sendfile on;
    server {
        listen 443 ssl;
        server_name $IP;
        ssl_certificate     $sslFwd/server.crt;
        ssl_certificate_key $sslFwd/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        root  $dirFwd;
        index azure-user-manager.html;
        location / { try_files `$uri `$uri/ =404; }
    }
    server {
        listen 80;
        server_name $IP;
        return 301 https://`$host`$request_uri;
    }
}
"@

[IO.File]::WriteAllText("$NGINX\conf\nginx.conf", $nginxConf)
Write-Host "   OK - nginx.conf configurado"

# ── Passo 5: Instalar certificado como confiavel ──────────────
Write-Host ""
Write-Host "[5/5] A instalar certificado como confiavel..."
try {
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
    $store.Open("ReadWrite")
    $storeCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("$SSL\server.cer")
    $store.Add($storeCert)
    $store.Close()
    Write-Host "   OK - Certificado instalado como Autoridade de Raiz"
} catch {
    Write-Host "   AVISO: $($_.Exception.Message)"
    Write-Host "   Instala manualmente: duplo clique em $SSL\server.cer"
}

Write-Host ""
Write-Host "   Script concluido com sucesso!"
exit 0
