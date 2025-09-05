from typing import List, Tuple
def extract_text_by_page(path: str) -> List[str]:
    """优先用 PyMuPDF (fitz)，否则回退到 pdfplumber。"""
    pages = []
    try:
        import fitz  # PyMuPDF
        with fitz.open(path) as doc:
            for page in doc:
                pages.append(page.get_text("text"))
        return pages
    except Exception:
        pass
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                pages.append(p.extract_text() or "")
        return pages
    except Exception as e:
        raise RuntimeError(f"无法解析 PDF，请安装 PyMuPDF 或 pdfplumber：{e}")
def keyword_hits(pages: List[str], kw: str) -> List[Tuple[int,int]]:
    kw_lower = kw.lower()
    out = []
    for idx, txt in enumerate(pages, start=1):
        c = txt.lower().count(kw_lower) if txt else 0
        if c>0:
            out.append((idx, c))
    return out
