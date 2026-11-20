"""Open the deployed Streamlit app in a real (headless) browser so it counts as a visit.
Wakes the app if it is asleep, then checks the dashboard actually rendered.
Streamlit Cloud serves the app inside an iframe, so every frame is searched."""
import sys
import time
from playwright.sync_api import sync_playwright

URL = "https://sumitmeena3112-sudo-ola-ride-insights-app-necfnq.streamlit.app/"
MARKER = "Total bookings"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, timeout=120_000)
    page.wait_for_timeout(8_000)
    wake = page.get_by_role("button", name="Yes, get this app back up!")
    if wake.count():
        print("App was asleep - clicking wake-up button")
        wake.first.click()
    ok = False
    deadline = time.time() + 240
    while time.time() < deadline and not ok:
        for fr in page.frames:
            try:
                if fr.get_by_text(MARKER).count():
                    ok = True
                    break
            except Exception:  # noqa: BLE001  (frame may navigate while we poll)
                pass
        if not ok:
            page.wait_for_timeout(3_000)
    if ok:
        print("OK: dashboard rendered")
    else:
        print("FAILED: dashboard did not render. Title:", page.title(), "| frames:", len(page.frames))
        print("Page text:", page.inner_text("body")[:500].replace("\n", " | "))
    browser.close()
sys.exit(0 if ok else 1)
