from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import uuid
import os
import re
import hashlib
from urllib.parse import urlparse
from send_mail import send_mail

def url_to_slug(url: str, max_len: int = 120) -> str:
    parsed = urlparse(url)

    base = f"{parsed.netloc}{parsed.path}"
    if parsed.query:
        base += "-" + parsed.query

    base = base.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")

    if len(base) > max_len:
        h = hashlib.sha1(url.encode()).hexdigest()[:8]
        base = f"{base[:max_len-9]}-{h}"

    return base or "page"

app = FastAPI()

class Req(BaseModel):
    url: str

@app.post("/pdf")
def pdf(req: Req):
    slug = url_to_slug(req.url)
    out = f"/output/{slug}.pdf"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(req.url, wait_until="networkidle", timeout=60000)
            page.pdf(path=out, format="A4", print_background=True)
            browser.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"file": f"{slug}.pdf"}

@app.post('/send_pdf')
def send_pdf(req: Req):
    try:
        target_url = req.url
        payload = Req.model_validate({"url": target_url})
        filename = pdf(payload).get('file')
        full_file_path = os.path.join("output", filename)
        send_mail(
            subject="PDF Generation Complete",
            body=f"Here is the PDF generated from {target_url}",
            attachments=(full_file_path,)
        )

        return {
            "status": "success", 
            "message": "PDF generated and email trigger initiated",
            "path": full_file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
