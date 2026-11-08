"""1.3.2: „LETZTEN FUNKSPRUCH LÖSCHEN“ entfernt Meldung und Antwort als Paar (BUGS B19)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import WIDGET, BEEP, OUT, Checks
from playwright.sync_api import sync_playwright

check = Checks()
requests = []


def handle(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if ":generateContent" in u:
        requests.append(json.loads(route.request.post_data or "{}"))
        return route.fulfill(status=200, content_type="application/json",
                             body=json.dumps({"candidates": [{"content": {"parts": [{"text": "Verstanden."}]}, "finishReason": "STOP"}]}))
    return route.fulfill(status=404, body="")


def history(roles):
    return [{"role": r, "text": f"{r} {i}", "timestamp": "2026-11-01T10:00:00.000Z"} for i, r in enumerate(roles)]


def load(pg, roles, idx):
    pg.evaluate("""([h, i]) => { localStorage.setItem('bdu_api_key', 'K');
                   localStorage.setItem('bdu_caching_enabled', 'false');
                   localStorage.setItem('bdu_conversation_history', JSON.stringify(h));
                   localStorage.setItem('bdu_history_summary', 'Frühere Lage.');
                   localStorage.setItem('bdu_last_summary_index', String(i)); }""", [history(roles), idx])
    pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("toggleSettings()")


def delete(pg):
    pg.click("#clear-last-exchange-btn"); pg.wait_for_timeout(450); pg.click("#clear-last-exchange-btn"); pg.wait_for_timeout(100)


def roles(pg):
    return pg.evaluate("conversationHistory.map(e => e.role)")


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(WIDGET); pg.wait_for_timeout(300)

    # Normalfall: 5 Paare, letzter Index hinter dem Ende
    load(pg, ["user", "assistant"] * 5, 9)
    check("Beschriftung nennt den letzten Funkspruch", "LETZTEN FUNKSPRUCH LÖSCHEN" in pg.inner_text("#clear-last-exchange-btn"))
    pg.click("#clear-last-exchange-btn")
    check("Erster Klick fragt nur", "SICHER" in pg.inner_text("#clear-last-exchange-btn") and len(roles(pg)) == 10)
    pg.wait_for_timeout(450); pg.click("#clear-last-exchange-btn"); pg.wait_for_timeout(100)
    check("Zweiter Klick löscht genau ein Paar", roles(pg) == ["user", "assistant"] * 4, roles(pg))
    check("Beschriftung zurück", "LETZTEN FUNKSPRUCH LÖSCHEN" in pg.inner_text("#clear-last-exchange-btn"))
    check("Zusammenfassungsstand auf Verlaufslänge begrenzt und gespeichert",
          pg.evaluate("lastSummaryIndex") == 8 and pg.evaluate("localStorage.getItem('bdu_last_summary_index')") == "8")
    check("Gekürzter Verlauf gespeichert", len(json.loads(pg.evaluate("localStorage.getItem('bdu_conversation_history')"))) == 8)
    check("Meldung im Display", "Letzter Funkspruch aus der History gelöscht (2 Einträge)" in pg.inner_text("#chat-log"))
    check("Zähler aktualisiert", pg.inner_text("#history-count").strip() == "8")

    # Nächste Anfrage: keine zwei Kaleu-Meldungen hintereinander
    requests.clear()
    pg.evaluate("callApi('Neue Meldung')")
    contents = requests[-1].get("contents", []) if requests else []
    r = [c.get("role") for c in contents]
    check("Nächste Anfrage wechselt sauber zwischen Kaleu und BdU",
          bool(r) and r[-1] == "user" and all(a != b2 for a, b2 in zip(r, r[1:])), r)

    # Index vor dem Ende bleibt unverändert
    load(pg, ["user", "assistant"] * 5, 4)
    delete(pg)
    check("Index vor dem Ende bleibt", pg.evaluate("lastSummaryIndex") == 4)

    # Alter Verlauf mit unbeantworteter Meldung am Ende (aus „LETZTE 5 LÖSCHEN“ bis 1.3.1)
    load(pg, ["user", "assistant", "user", "assistant", "user"], 0)
    delete(pg)
    check("Unbeantwortete Meldung am Ende wird entfernt, Verlauf endet mit Antwort", roles(pg) == ["user", "assistant"] * 2, roles(pg))

    # Zwei unbeantwortete Meldungen am Ende
    load(pg, ["user", "assistant", "user", "user"], 0)
    delete(pg)
    check("Mehrere unbeantwortete Meldungen am Ende werden entfernt", roles(pg) == ["user", "assistant"], roles(pg))

    # Nur ein Paar, dann leer
    load(pg, ["user", "assistant"], 2)
    delete(pg)
    check("Letztes Paar: Verlauf leer, Index 0", roles(pg) == [] and pg.evaluate("lastSummaryIndex") == 0)
    delete(pg)
    check("Leerer Verlauf: Hinweis statt Fehler", "Keine History zum Kürzen vorhanden" in pg.inner_text("#chat-log"))

    pg.evaluate("document.getElementById('clear-last-exchange-btn').scrollIntoView()")
    pg.screenshot(path=os.path.join(OUT, "history_pairs.png"))
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
