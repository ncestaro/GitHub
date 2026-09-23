"""Genera il PDF di stampa (con abbondanze) e le anteprime PNG della brochure."""
import pathlib
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
url = (here / "brochure.html").resolve().as_uri()
out = here / "export"
out.mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page(device_scale_factor=3)
    pg.goto(url)
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    pg.emulate_media(media="print")
    pg.pdf(path=str(out / "brochure_stampa_A4_abbondanze3mm.pdf"),
           width="303mm", height="216mm", print_background=True, prefer_css_page_size=True)
    pg.emulate_media(media="print")
    pg.set_viewport_size({"width": 1146, "height": 817})
    for i, name in enumerate(["esterno", "interno"]):
        el = pg.locator(".sheet").nth(i)
        # anteprima al vivo (taglio della sola abbondanza)
        box = el.bounding_box()
        mm = box["width"] / 303
        pg.screenshot(path=str(out / f"anteprima_{name}.png"), full_page=True,
                      clip={"x": box["x"] + 3 * mm, "y": box["y"] + 3 * mm,
                            "width": 297 * mm, "height": 210 * mm})
    b.close()
print("ok")
