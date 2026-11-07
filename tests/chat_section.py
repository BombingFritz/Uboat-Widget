"""1.3.0: Chat-Modus-Bereich in den Einstellungen eingeklappt, außer der Chat-Modus ist eingeschaltet."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import WIDGET, BEEP, OUT, Checks
from playwright.sync_api import sync_playwright

check = Checks()
def handle(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if "localhost:3000" in u: return route.fulfill(status=503, body="")
    return route.fulfill(status=404, body="")

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(WIDGET); pg.wait_for_timeout(300); pg.evaluate("toggleSettings()")
    check("Standard: Bereich eingeklappt", not pg.is_visible("#chat-section") and pg.inner_text("#chat-section-toggle").startswith("▸"))
    check("Überschrift nennt Streamer und Companion-Server", "STREAMER" in pg.inner_text("#chat-section-toggle").upper() and "COMPANION" in pg.inner_text("#chat-section-toggle").upper())
    pg.click("#chat-section-toggle")
    check("Klick klappt auf", pg.is_visible("#chat-enabled-checkbox") and pg.inner_text("#chat-section-toggle").startswith("▾"))
    pg.click("#chat-section-toggle")
    check("Zweiter Klick klappt zu", not pg.is_visible("#chat-section"))
    # Chat-Modus an -> nach Neuladen offen
    pg.evaluate("localStorage.setItem('bdu_api_key','K'); localStorage.setItem('bdu_chat_enabled','true')")
    pg.reload(); pg.wait_for_timeout(300); pg.evaluate("toggleSettings()")
    check("Chat-Modus an: Bereich offen", pg.is_visible("#chat-enabled-checkbox") and pg.is_checked("#chat-enabled-checkbox"))
    pg.locator("#chat-section-toggle").scroll_into_view_if_needed()
    pg.screenshot(path=os.path.join(OUT, "chat_section_open.png"))
    # RESET -> zu
    pg.click("#reset-btn"); pg.wait_for_timeout(500); pg.click("#reset-btn"); pg.wait_for_timeout(300)
    check("Nach RESET eingeklappt und aus", not pg.is_visible("#chat-section") and pg.evaluate("chatEnabled") is False)
    pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300); pg.evaluate("toggleSettings()")
    pg.locator("#chat-section-toggle").scroll_into_view_if_needed()
    pg.screenshot(path=os.path.join(OUT, "chat_section_closed.png"))
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
