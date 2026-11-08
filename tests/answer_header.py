"""1.4.0: Eigene Kopfzeile des Modells am Antwortanfang wird entfernt (BUGS B23)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import WIDGET, BEEP, OUT, Checks
from playwright.sync_api import sync_playwright

check = Checks()
answer = {"text": "**BdU an U-68:**\n\nVerstanden. Torpedos und Treibstoff sind kritisch.\nMeldung über Brennstoffstand."}


def handle(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if ":generateContent" in u:
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": answer["text"]}]}, "finishReason": "STOP"}]}))
    return route.fulfill(status=404, body="")


cases = [
    ("**BdU an U-68:**\n\nVerstanden.", "Verstanden."),
    ("FT von BdU an U-68: Weitermachen.", "Weitermachen."),
    ("BdU an U-68:\nKurs halten.\nZweite Zeile.", "Kurs halten.\nZweite Zeile."),
    ("__BdU:__ Gut gemacht.", "Gut gemacht."),
    ("Verstanden. BdU an U-68: bleibt.", "Verstanden. BdU an U-68: bleibt."),
    ("BdU ist zufrieden: weiter so.", "BdU ist zufrieden: weiter so."),
    ("**BdU an U-68:**", "**BdU an U-68:**"),
]

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('bdu_api_key','K');")
    pg.goto(WIDGET); pg.wait_for_timeout(300); pg.evaluate("typewriterSpeedPatch = true")
    for raw, want in cases:
        got = pg.evaluate("t => stripAnswerHeader(t)", raw)
        check(f"stripAnswerHeader({raw[:30]!r})", got == want, repr(got))
    pg.fill("#user-input", "Status Treibstoff?"); pg.evaluate("sendMessage()")
    pg.wait_for_function("!document.getElementById('status-light').classList.contains('transmitting')", timeout=60000)
    last = pg.locator("#chat-log .msg-bdu").last.inner_text()
    check("Display: nur eine Kopfzeile", last.count("BdU an") == 1 and "U-68" not in last and "**" not in last and last.startswith("FT von BdU an"), last)
    check("Display: Zeilenumbruch im Text bleibt", pg.locator("#chat-log .msg-bdu").last.locator("br").count() == 1)
    stored = pg.evaluate("conversationHistory[conversationHistory.length - 1].text")
    check("Verlauf speichert die Antwort ohne eigene Kopfzeile", stored.startswith("Verstanden.") and "**" not in stored, stored)
    # Alter Verlauf mit Kopfzeile: Anzeige nach Neuladen ohne doppelte Kopfzeile, gespeicherter Text unverändert
    pg.evaluate("""conversationHistory.push({role:'user', text:'Alt', timestamp:new Date().toISOString()},
                   {role:'assistant', text:'**BdU an U-68:**\\n\\nAlte Antwort.', timestamp:new Date().toISOString()});
                   localStorage.setItem('bdu_conversation_history', JSON.stringify(conversationHistory));""")
    pg.reload(); pg.wait_for_timeout(400)
    last = pg.locator("#chat-log .msg-bdu").last.inner_text()
    check("Wiederherstellung: alte Antwort ohne doppelte Kopfzeile", last.count("BdU an") == 1 and "Alte Antwort." in last and "**" not in last, last)
    check("Gespeicherter alter Eintrag unverändert", pg.evaluate("conversationHistory[conversationHistory.length - 1].text").startswith("**BdU an U-68:**"))
    pg.screenshot(path=os.path.join(OUT, "answer_header.png"))
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
