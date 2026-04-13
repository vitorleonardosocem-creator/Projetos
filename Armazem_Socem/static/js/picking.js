// Scanner de Códigos de Barras com Câmera
class BarcodeScanner {
    constructor() {
        this.video = document.getElementById('videoScanner');
        this.canvas = document.getElementById('canvasScanner');
        this.ctx = this.canvas.getContext('2d');
        this.scanning = false;
        this.stream = null;
        this.codeReader = null;

        this.initQuagga();
    }

    async initQuagga() {
        // Carrega QuaggaJS para scanner
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/@ericblade/quagga2@1.8.0/dist/quagga.min.js';
        document.head.appendChild(script);

        script.onload = () => {
            this.codeReader = window.Quagga;
            this.startScanner();
        };
    }

    async startScanner() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' } // Câmera traseira
            });
            this.video.srcObject = this.stream;
            this.video.play();

            this.canvas.width = 640;
            this.canvas.height = 480;

            this.scanning = true;
            this.scanLoop();

            document.getElementById('status').textContent = '🔍 Escaneando...';
            document.getElementById('scannerControls').style.display = 'block';
        } catch (err) {
            console.error('Erro câmera:', err);
            document.getElementById('status').textContent = '❌ Câmera não disponível';
        }
    }

    scanLoop() {
        if (!this.scanning) return;

        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Usa QuaggaJS para detetar códigos
        if (this.codeReader) {
            this.codeReader.decodeSingle({
                src: this.canvas.toDataURL(),
                numOfWorkers: 0,
                decoder: {
                    readers: ['code_128_reader', 'ean_reader', 'ean_8_reader', 'code_39_reader']
                }
            }, (result) => {
                if (result && result.codeResult.code) {
                    this.processCode(result.codeResult.code);
                }
            });
        }

        requestAnimationFrame(() => this.scanLoop());
    }

    processCode(codigo) {
        document.getElementById('codigoInput').value = codigo;
        document.getElementById('codigoInput').dispatchEvent(new Event('input'));
        this.playSound();
    }

    playSound() {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVKMbF1fdJivrJBhNjV');
        audio.play();
    }

    stopScanner() {
        this.scanning = false;
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Input manual como fallback
document.addEventListener('DOMContentLoaded', function () {
    const scanner = new BarcodeScanner();

    // Modo manual (teclado)
    document.getElementById('codigoInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            processPicking(this.value.trim());
        }
    });

    // Botão confirmar
    document.getElementById('confirmarBtn').addEventListener('click', function () {
        processPicking(document.getElementById('codigoInput').value.trim());
    });
});

async function processPicking(codigo) {
    if (!codigo) return;

    const btn = document.getElementById('confirmarBtn');
    const resultado = document.getElementById('resultado');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processando...';
    resultado.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';

    try {
        const response = await fetch('/api/picking_scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                localizacao: document.getElementById('localizacaoSelect').value
            })
        });
        const data = await response.json();

        if (data.success) {
            resultado.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show">
                    ✅ <strong>${data.nome}</strong> movido para <strong>${data.localizacao_nome}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            document.getElementById('codigoInput').value = '';
        } else {
            resultado.innerHTML = `
                <div class="alert alert-danger">
                    ❌ ${data.error}
                </div>
            `;
        }
    } catch (e) {
        resultado.innerHTML = '<div class="alert alert-danger">❌ Erro de conexão</div>';
    }

    btn.disabled = false;
    btn.innerHTML = '✅ Confirmar';
}
