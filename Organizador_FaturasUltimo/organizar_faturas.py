import os, re, shutil, threading, subprocess, tempfile
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def tesseract_available():
    if pytesseract is None:
        return False
    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        return True
    try:
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        return True
    except Exception:
        return False

def extract_text_from_pdf(pdf_path):
    text = ""
    if pdfplumber:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:3]:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except Exception:
            pass
    if not text and PdfReader:
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages[:3]:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception:
            pass
    return text

def extract_text_via_ocr(pdf_path):
    if not tesseract_available():
        return ""
    try:
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=3)
        except ImportError:
            with tempfile.TemporaryDirectory() as tmp:
                out_prefix = os.path.join(tmp, "page")
                result = subprocess.run(
                    ['pdftoppm', '-jpeg', '-r', '200', '-f', '1', '-l', '3',
                     str(pdf_path), out_prefix], capture_output=True)
                if result.returncode != 0:
                    return ""
                imgs = sorted(Path(tmp).glob("*.jpg"))
                if not imgs:
                    return ""
                images = [Image.open(str(p)) for p in imgs]
        text = ""
        for img in images:
            t = pytesseract.image_to_string(img, lang='por+eng')
            if t:
                text += t + "\n"
        return text
    except Exception:
        return ""


# ── VAT / NIF extraction ──────────────────────────────────────────────────────

# Matches "VAT: DE 815342996" or "VAT: MX MME000801FN8" — any 2-letter country
VAT_LABEL_RE  = re.compile(r'\bVAT:\s*([A-Z]{2})\s*([\w\-]{4,20})\b')
NIF_LABEL_RE  = re.compile(r'\bNIF:\s*(PT\s*\d{9})\b', re.IGNORECASE)
# "Nº Contribuinte: PT 502260882" — used in non-SOCEM invoices
CONTRIB_RE    = re.compile(r'(?:N[º°]\s*Contribuinte|Contribuinte\s*N[º°]?)[:\s]*(PT\s*\d{9}|\d{9})', re.IGNORECASE)

SOCEM_NIF     = '504032712'
SOCEM_NAME_RE = re.compile(r'SOCEM', re.IGNORECASE)
SOCEM_FULL_RE = re.compile(r'SOCEM\s+ED[\-\u2013]\S.*?(?:Moldes,\s*SA|S\.A\.)', re.IGNORECASE)


def is_socem_invoice(text):
    """True if SOCEM is the ISSUER (our invoice). False if SOCEM is the client (received invoice)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if SOCEM_NAME_RE.search(line):
            # In SOCEM-issued invoices, SOCEM appears in the first few lines as issuer
            # and NIF: PT504032712 appears right below
            block = '\n'.join(lines[i:i+5])
            if SOCEM_NIF in block.replace(' ', ''):
                return True
    return False


def find_client_vat(text, my_nif_bare):
    lines = text.splitlines()

    # Strategy 1: explicit VAT: XX <number> label (any country code)
    for line in lines:
        m = VAT_LABEL_RE.search(line)
        if m and not any(k in line for k in ('Ref.', 'Description', 'Qtd.', 'Referência', 'Amount')):
            country = m.group(1)
            number  = re.sub(r'[\s\-]', '', m.group(2))
            v = country + number
            if my_nif_bare not in v:
                return v

    # Strategy 2: last NIF: PT XXXXXXXXX (domestic PT invoices issued by SOCEM)
    all_nifs = NIF_LABEL_RE.findall(text)
    if all_nifs:
        last = re.sub(r'\s', '', all_nifs[-1]).upper()
        if last[2:] != my_nif_bare:
            return last

    # Strategy 3: Nº Contribuinte (invoices NOT issued by SOCEM — received invoices)
    all_contribs = CONTRIB_RE.findall(text)
    for c in all_contribs:
        bare = re.sub(r'[^0-9]', '', c)
        if bare != my_nif_bare:
            return 'PT' + bare

    return None


def find_client_name(text, my_nif_bare):
    lines = text.splitlines()

    # ── SOCEM-issued invoice ─────────────────────────────────────────────────
    for i, line in enumerate(lines):
        if SOCEM_NAME_RE.search(line):
            # Layout B: SOCEM + client on same line
            m = SOCEM_FULL_RE.search(line)
            if m:
                after = line[m.end():].strip()
                if len(after) > 4:
                    return re.sub(r'[\\/*?:"<>|]', '', after)[:70].strip()
            # Layout A: client on next non-trivial line
            skip = ('NIF:', 'Rua ', 'Av.', 'Payment', 'Cond.', 'Emission',
                    'Data de', 'Due Date', 'BANK:', 'SWIFT', 'Software',
                    'ATCUD', 'Ship.', 'Tax ', 'Total', 'Ref.', 'Utilizador',
                    'Capital:', 'C.R.C.', 'Sociedade', 'T +351', 'socem@',
                    'www.socem', 'Parque', 'Km ', 'Rua do')
            for l in lines[i + 1:]:
                l = l.strip()
                if not l or len(l) < 4 or re.match(r'\d', l):
                    continue
                if any(k in l for k in skip):
                    continue
                return re.sub(r'[\\/*?:"<>|]', '', l)[:70].strip()

    # ── Received invoice (SOCEM is the client, other company is issuer) ──────
    # The issuer is typically in the first lines before "Exmo(s)" or before the address block
    # Look for a company name with legal suffix near the top
    suffixes = (r'Lda\.?|Unipessoal\s+Lda\.?|S\.?\s*A\.?|GmbH|Ltd\.?|'
                r'Inc\.?|S\.?\s*R\.?\s*L\.?|Lda\b')
    company_re = re.compile(
        r'([A-ZÁÉÍÓÚÂÊÔÃÕÀÇ][A-Za-záéíóúâêôãõàçÁÉÍÓÚÂÊÔÃÕÀÇ0-9 ,\.\-&]{2,60}?'
        r'(?:' + suffixes + r')\.?)',
        re.IGNORECASE)
    for line in lines[:15]:
        m = company_re.search(line)
        if m:
            name = re.sub(r'[\\/*?:"<>|]', '', m.group(1))[:70].strip()
            if 'SOCEM' not in name.upper():
                return name

    return ""


# ── Folder helpers ────────────────────────────────────────────────────────────

def make_folder_name(client_vat, client_name):
    parts = [p for p in [client_vat, client_name] if p]
    return ' - '.join(parts) if parts else "Sem_NIF"

def find_existing_folder(base, client_vat):
    if not client_vat:
        return None
    for item in base.iterdir():
        if item.is_dir() and item.name.startswith(client_vat):
            return item
    return None


# ── Core organiser ────────────────────────────────────────────────────────────

def organise_pdfs(folder, my_nif, log_fn, done_fn):
    folder = Path(folder)
    pdfs = list(folder.glob('*.pdf')) + list(folder.glob('*.PDF'))

    if not pdfs:
        log_fn("⚠️  Nenhum PDF encontrado na pasta selecionada.")
        done_fn()
        return

    ocr_ok = tesseract_available()
    log_fn(f"📂  {len(pdfs)} PDF(s) encontrados.")
    log_fn(f"🔎  OCR Tesseract: {'✅ disponível' if ocr_ok else '❌ não encontrado'}\n")

    moved = skipped = 0
    my_nif_bare = re.sub(r'[^0-9]', '', my_nif)

    for pdf_path in pdfs:
        log_fn(f"🔍  {pdf_path.name}")
        text = extract_text_from_pdf(str(pdf_path))

        if not text.strip():
            if ocr_ok:
                log_fn("   📷  Sem texto — a usar OCR...")
                text = extract_text_via_ocr(str(pdf_path))
                if not text.strip():
                    log_fn("   ⚠️  OCR não encontrou texto. A ignorar.\n")
                    skipped += 1
                    continue
                log_fn("   ✔️  OCR concluído.")
            else:
                log_fn("   ⚠️  Sem texto (instala Tesseract para ler este PDF). A ignorar.\n")
                skipped += 1
                continue

        client_vat  = find_client_vat(text, my_nif_bare)
        client_name = find_client_name(text, my_nif_bare)

        if not client_vat and not client_name:
            log_fn("   ⚠️  Cliente não identificado. A ignorar.\n")
            skipped += 1
            continue

        dest_folder = find_existing_folder(folder, client_vat) if client_vat else None
        if dest_folder is None:
            dest_folder = folder / make_folder_name(client_vat, client_name)

        dest_folder.mkdir(exist_ok=True)
        dest_file = dest_folder / pdf_path.name
        if dest_file.exists():
            stem, suffix = pdf_path.stem, pdf_path.suffix
            c = 1
            while dest_file.exists():
                dest_file = dest_folder / f"{stem}_{c}{suffix}"
                c += 1

        shutil.move(str(pdf_path), str(dest_file))
        log_fn(f"   ✅  → {dest_folder.name}/\n")
        moved += 1

    log_fn(f"\n{'─'*50}")
    log_fn(f"✔️   Concluído! {moved} organizados, {skipped} ignorados.")
    if skipped > 0 and not ocr_ok:
        log_fn("ℹ️   Instala o Tesseract OCR para ler os PDFs digitalizados.")
    done_fn()


# ── GUI ───────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Organizador de Faturas PDF")
        self.geometry("660x530")
        self.resizable(False, False)
        self.configure(bg="#f0f4f8")
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg="#1a56db", pady=14)
        header.pack(fill='x')
        tk.Label(header, text="📁 Organizador de Faturas PDF",
                 font=("Segoe UI", 15, "bold"), bg="#1a56db", fg="white").pack()
        tk.Label(header, text="Organiza automaticamente os PDFs por NIF/VAT e nome de empresa",
                 font=("Segoe UI", 9), bg="#1a56db", fg="#c7d9ff").pack()

        body = tk.Frame(self, bg="#f0f4f8", padx=24, pady=16)
        body.pack(fill='both', expand=True)

        tk.Label(body, text="O meu NIF da empresa:",
                 font=("Segoe UI", 10, "bold"), bg="#f0f4f8", anchor='w').pack(fill='x')
        self.nif_var = tk.StringVar()
        tk.Entry(body, textvariable=self.nif_var, font=("Segoe UI", 11),
                 width=22, bd=1, relief='solid').pack(anchor='w', pady=(3, 12))

        tk.Label(body, text="Pasta com os PDFs:",
                 font=("Segoe UI", 10, "bold"), bg="#f0f4f8", anchor='w').pack(fill='x')
        row = tk.Frame(body, bg="#f0f4f8")
        row.pack(fill='x', pady=(3, 12))
        self.folder_var = tk.StringVar()
        tk.Entry(row, textvariable=self.folder_var, font=("Segoe UI", 10),
                 bd=1, relief='solid').pack(side='left', fill='x', expand=True)
        tk.Button(row, text="  Escolher…  ", command=self._pick_folder,
                  font=("Segoe UI", 10), bg="#e2e8f0", relief='flat',
                  cursor='hand2').pack(side='left', padx=(6, 0))

        self.btn = tk.Button(body, text="▶  Organizar Faturas",
                             command=self._start,
                             font=("Segoe UI", 11, "bold"),
                             bg="#1a56db", fg="white", relief='flat',
                             padx=16, pady=8, cursor='hand2',
                             activebackground="#1648c0", activeforeground="white")
        self.btn.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(body, mode='indeterminate', length=600)
        self.progress.pack(fill='x', pady=(0, 8))

        tk.Label(body, text="Registo:", font=("Segoe UI", 9, "bold"),
                 bg="#f0f4f8", anchor='w').pack(fill='x')
        self.log = scrolledtext.ScrolledText(
            body, height=11, font=("Consolas", 9),
            bg="#1e2a3a", fg="#a0cfff",
            insertbackground="white", relief='flat', bd=0, state='disabled')
        self.log.pack(fill='both', expand=True)

    def _pick_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta com PDFs")
        if folder:
            self.folder_var.set(folder)

    def _log(self, msg):
        self.log.configure(state='normal')
        self.log.insert('end', msg + "\n")
        self.log.see('end')
        self.log.configure(state='disabled')

    def _start(self):
        nif    = self.nif_var.get().strip()
        folder = self.folder_var.get().strip()

        if not re.match(r'^(?:PT)?\s*\d{9}$', nif, re.IGNORECASE):
            messagebox.showerror("NIF inválido", "Introduz um NIF válido:\n  504032712  ou  PT504032712")
            return
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Pasta inválida", "Seleciona uma pasta válida.")
            return
        if not pdfplumber and not PdfReader:
            messagebox.showerror("Dependências em falta",
                                 "Corre o INICIAR_ORGANIZADOR.bat para instalar as dependências.")
            return

        self.btn.configure(state='disabled')
        self.progress.start(10)
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')

        threading.Thread(
            target=organise_pdfs,
            args=(folder, nif, self._log, self._done),
            daemon=True).start()

    def _done(self):
        self.progress.stop()
        self.btn.configure(state='normal')


if __name__ == '__main__':
    App().mainloop()
