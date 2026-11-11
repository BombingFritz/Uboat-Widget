"""1.2.1: Alles muss ohne Browser-Dialoge gehen (OBS zeigt keine; confirm() liefert false)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BENCH, EXAMPLE, BEEP, OUT, EXPORT_NOKEY, EXPORT_TEST
import json, sys
from playwright.sync_api import sync_playwright
W = WIDGET
res = []
def check(n, c, info=""):
    res.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n + ("" if c else "  " + str(info)))
def routes(pg):
    def h(route):
        u = route.request.url
        if u.startswith("file://"): return route.continue_()
        if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
        return route.fulfill(status=404, body="")
    pg.route("**/*", h)
with sync_playwright() as p:
    b = p.chromium.launch(); c = b.new_context(); pg = c.new_page(); routes(pg)
    dialogs, errs = [], []
    pg.on("dialog", lambda d: (dialogs.append(d.message[:50]), d.dismiss()))
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(W); pg.wait_for_timeout(300)
    pg.evaluate("toggleSettings()")
    label = pg.inner_text("#import-btn")
    # Datei laden wie in OBS
    pg.set_input_files("#import-file-input", EXPORT_NOKEY); pg.wait_for_timeout(300)
    check("Datei laden: Inhalt im Textfeld", pg.input_value("#transfer-text").startswith("{"))
    check("Datei laden: Rückfrage im Statusfeld", "100 Verlaufseinträge" in pg.inner_text("#transfer-status") and "BESTÄTIGEN" in pg.inner_text("#transfer-status"), pg.inner_text("#transfer-status"))
    check("Datei laden: Button zeigt IMPORT BESTÄTIGEN", "IMPORT BESTÄTIGEN" in pg.inner_text("#import-btn"))
    check("Noch nichts importiert", pg.evaluate("conversationHistory.length") == 0)
    pg.wait_for_timeout(500)
    with pg.expect_navigation():
        pg.click("#import-btn")
    pg.wait_for_timeout(500)
    check("Klick auf IMPORT BESTÄTIGEN importiert (100 Einträge)", pg.evaluate("conversationHistory.length") == 100)
    check("Boot-Kontext übernommen", "U-68" in pg.evaluate("bootContext"))
    # Text einfügen + zweimal klicken, Zeitablauf
    pg.evaluate("toggleSettings()")
    pg.fill("#transfer-text", open(EXPORT_NOKEY, encoding="utf-8").read())
    pg.click("#import-btn")
    check("Erster Klick fragt nur", "BESTÄTIGEN" in pg.inner_text("#import-btn"))
    pg.fill("#transfer-text", "kein json")
    pg.click("#import-btn")
    check("Geänderter Text: Fehler statt Import, Rückfrage aufgehoben", "❌" in pg.inner_text("#transfer-status") and "BESTÄTIGEN" not in pg.inner_text("#import-btn"))
    # Verlauf löschen
    pg.click("#clear-last-exchange-btn")
    check("LETZTEN FUNKSPRUCH: erster Klick fragt", "SICHER" in pg.inner_text("#clear-last-exchange-btn") and pg.evaluate("conversationHistory.length") == 100)
    pg.wait_for_timeout(500); pg.click("#clear-last-exchange-btn")
    check("LETZTEN FUNKSPRUCH: zweiter Klick löscht ein Paar", pg.evaluate("conversationHistory.length") == 98)
    check("LETZTEN FUNKSPRUCH: Beschriftung zurück", "LETZTEN FUNKSPRUCH" in pg.inner_text("#clear-last-exchange-btn"))
    pg.click("#clear-history-btn")
    pg.wait_for_timeout(10500)
    check("HISTORY: Rückfrage verfällt nach 10 s", "HISTORY LÖSCHEN" in pg.inner_text("#clear-history-btn") and pg.evaluate("conversationHistory.length") == 98)
    pg.dblclick("#clear-history-btn")
    check("HISTORY: versehentlicher Doppelklick löscht nicht", pg.evaluate("conversationHistory.length") == 98)
    pg.wait_for_timeout(500); pg.click("#clear-history-btn")
    check("HISTORY: zweiter Klick löscht", pg.evaluate("conversationHistory.length") == 0)
    # Speichern ohne Schlüssel, Modelle ohne Schlüssel
    pg.fill("#api-key-input", "")
    pg.click("#save-settings-btn")
    check("SPEICHERN ohne Schlüssel: Hinweis auf dem Button", "API-SCHLÜSSEL FEHLT" in pg.inner_text("#save-settings-btn"))
    pg.wait_for_timeout(3200)
    check("SPEICHERN: Beschriftung zurück", pg.inner_text("#save-settings-btn").strip() == "SPEICHERN", pg.inner_text("#save-settings-btn"))
    pg.evaluate("fetchModels()")
    check("MODELLE SUCHEN ohne Schlüssel: Hinweis in der Liste", "API-Schlüssel" in pg.inner_text("#model-list-display"))
    # RESET
    pg.evaluate("localStorage.setItem('bdu_api_key','X'); localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite')")
    pg.click("#reset-btn")
    check("RESET: erster Klick fragt", "NOCHMAL" in pg.inner_text("#reset-btn") and pg.evaluate("localStorage.getItem('bdu_api_key')") == "X")
    pg.wait_for_timeout(500); pg.click("#reset-btn")
    check("RESET: zweiter Klick setzt zurück", pg.evaluate("localStorage.getItem('bdu_api_key')") is None)
    # Senden ohne Schlüssel
    pg.evaluate("toggleSettings()")
    pg.fill("#user-input", "Test"); pg.evaluate("sendMessage()")
    check("Senden ohne Schlüssel: Hinweis im Display", pg.locator("#chat-log .msg-sys", has_text="Schlüsselmaschine nicht eingestellt").count() == 1)
    check("Kein einziger Browser-Dialog", not dialogs, dialogs)
    check("Keine JS-Fehler", not errs, errs)
    # Screenshot der Einstellungen mit aktiver Rückfrage
    pg.evaluate("toggleSettings()")
    pg.set_input_files("#import-file-input", EXPORT_NOKEY); pg.wait_for_timeout(300)
    pg.locator("#import-btn").scroll_into_view_if_needed()
    pg.screenshot(path=os.path.join(OUT, "obs_import.png"))
    b.close()
print(f"\n{sum(1 for _, ok in res if ok)}/{len(res)} bestanden")
sys.exit(0 if all(ok for _, ok in res) else 1)
