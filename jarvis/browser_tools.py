"""
Browser automation using Playwright (sync API).
Keeps browser instance alive between calls.
"""
from __future__ import annotations
import base64

_playwright_instance = None
_browser = None
_page = None


def _get_page():
    """Gets or creates a Playwright browser page. Returns (page, error_str)."""
    global _playwright_instance, _browser, _page
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright não instalado. Corre: pip install playwright && playwright install chromium"

    try:
        # Reutiliza instância se já estiver aberta
        if _page is not None and not _page.is_closed():
            return _page, None

        # Fecha instâncias antigas se necessário
        if _browser is not None:
            try:
                _browser.close()
            except Exception:
                pass
        if _playwright_instance is not None:
            try:
                _playwright_instance.stop()
            except Exception:
                pass

        _playwright_instance = sync_playwright().start()
        _browser = _playwright_instance.chromium.launch(
            headless=False,  # Visível para o utilizador ver o que está a acontecer
            args=["--start-maximized"]
        )
        context = _browser.new_context(no_viewport=True)
        _page = context.new_page()
        return _page, None
    except Exception as e:
        return None, f"Erro ao iniciar browser: {e}"


def browser_navigate(url: str) -> str:
    """Navega para um URL."""
    page, err = _get_page()
    if err:
        return err
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        return f"Navegou para: {page.url}\nTítulo: {page.title()}"
    except Exception as e:
        return f"Erro ao navegar para '{url}': {e}"


def browser_click(selector_or_text: str) -> str:
    """Clica num elemento por texto visível ou seletor CSS/XPath."""
    page, err = _get_page()
    if err:
        return err
    try:
        # Tenta por texto primeiro
        try:
            page.get_by_text(selector_or_text, exact=False).first.click(timeout=5000)
            return f"Clicou em elemento com texto '{selector_or_text}'."
        except Exception:
            pass
        # Tenta por seletor CSS
        try:
            page.click(selector_or_text, timeout=5000)
            return f"Clicou em seletor '{selector_or_text}'."
        except Exception:
            pass
        # Tenta por role/label
        try:
            page.get_by_label(selector_or_text).first.click(timeout=3000)
            return f"Clicou em elemento com label '{selector_or_text}'."
        except Exception:
            pass
        return f"Não foi possível encontrar e clicar em '{selector_or_text}'."
    except Exception as e:
        return f"Erro ao clicar: {e}"


def browser_fill(selector_or_label: str, value: str) -> str:
    """Preenche um campo de formulário."""
    page, err = _get_page()
    if err:
        return err
    try:
        # Tenta por label
        try:
            page.get_by_label(selector_or_label, exact=False).first.fill(value, timeout=5000)
            return f"Campo '{selector_or_label}' preenchido com '{value}'."
        except Exception:
            pass
        # Tenta por placeholder
        try:
            page.get_by_placeholder(selector_or_label, exact=False).first.fill(value, timeout=5000)
            return f"Campo com placeholder '{selector_or_label}' preenchido."
        except Exception:
            pass
        # Tenta por seletor CSS
        try:
            page.fill(selector_or_label, value, timeout=5000)
            return f"Campo '{selector_or_label}' preenchido."
        except Exception:
            pass
        return f"Não foi possível preencher o campo '{selector_or_label}'."
    except Exception as e:
        return f"Erro ao preencher campo: {e}"


def browser_screenshot() -> str:
    """Tira screenshot da página atual do browser e devolve base64."""
    page, err = _get_page()
    if err:
        return err
    try:
        png_bytes = page.screenshot(full_page=False)
        b64 = base64.b64encode(png_bytes).decode()
        return f'{{"type": "screenshot", "base64": "{b64}", "media_type": "image/png", "source": "browser", "url": "{page.url}"}}'
    except Exception as e:
        return f"Erro ao tirar screenshot do browser: {e}"


def browser_get_text() -> str:
    """Obtém o texto visível da página atual."""
    page, err = _get_page()
    if err:
        return err
    try:
        text = page.inner_text("body")
        # Limpa espaços excessivos
        import re
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = text.strip()
        if len(text) > 4000:
            text = text[:4000] + "\n\n[... texto truncado a 4000 caracteres]"
        return f"URL: {page.url}\nTítulo: {page.title()}\n\n{text}"
    except Exception as e:
        return f"Erro ao obter texto da página: {e}"


def browser_close() -> str:
    """Fecha o browser."""
    global _playwright_instance, _browser, _page
    try:
        if _page is not None:
            try:
                _page.close()
            except Exception:
                pass
            _page = None
        if _browser is not None:
            try:
                _browser.close()
            except Exception:
                pass
            _browser = None
        if _playwright_instance is not None:
            try:
                _playwright_instance.stop()
            except Exception:
                pass
            _playwright_instance = None
        return "Browser fechado com sucesso."
    except Exception as e:
        return f"Erro ao fechar browser: {e}"
