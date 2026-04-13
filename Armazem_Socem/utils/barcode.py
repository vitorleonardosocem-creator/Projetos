from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.graphics.barcode import code128
from reportlab.lib.units import inch
import os

def gerar_barcode_pdf(codigo, nome_arquivo):
    """Gera PDF com barcode que lê EXATAMENTE o 'codigo' no scanner"""
    pasta = 'static/barcodes'
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    pdf_path = os.path.join(pasta, nome_arquivo)
    c = canvas.Canvas(pdf_path, pagesize=A6)
    width, height = A6
    
    # Barcode GRANDE
    barcode = code128.Code128(codigo, barHeight=2*inch, barWidth=2)
    barcode.drawOn(c, (width - barcode.width)/2, height*0.6)
    
    # Texto centrado MANUAL
    c.setFont("Helvetica-Bold", 28)
    text_width = c.stringWidth(codigo, "Helvetica-Bold", 28)
    c.drawString((width - text_width)/2, height*0.35, codigo)
    
    c.save()
    return f"/static/barcodes/{nome_arquivo}"

# NOVA FUNÇÃO PARA AÇÓS
def gerar_barcode_aco_pdf(codigo_aco, nome_aco):
    """Barcode AÇO - scanner lê APENAS 'A001'"""
    codigo_exato = f"A{codigo_aco}"  # Scanner lê "A001"
    nome_arquivo = f"ACO_{codigo_aco}.pdf"
    return gerar_barcode_pdf(codigo_exato, nome_arquivo)

