"""1.4.0: Zweites Modell für Chat-Antworten und Zusammenfassungen (Nutzerentscheidung 08.11.2026)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import WIDGET, BEEP, OUT, Checks, reload_keeping_storage
from playwright.sync_api import sync_playwright

check = Checks()
calls = []


def handle(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if ":generateContent" in u:
        body = route.request.post_data or ""
        model = u.split("/models/")[1].split(":")[0]
        kind = "summary" if ("Fasse folgende" in body or "Gesamtzusammenfassung" in body) else ("chat" if "Funkspruch aus dem Chat" in body else "main")
        calls.append((kind, model))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": "Teil." if kind == "summary" else "Verstanden."}]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 1200, "cachedContentTokenCount": 0}}))
    if "/v1/chat/completions" in u:
        body = json.loads(route.request.post_data)
        text = body["messages"][-1]["content"]
        kind = "summary" if ("Fasse folgende" in text or "Gesamtzusammenfassung" in text) else ("chat" if "Funkspruch aus dem Chat" in text else "main")
        calls.append((kind, "U:" + body["model"]))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"choices": [{"message": {"content": "Teil."}, "finish_reason": "stop"}]}))
    return route.fulfill(status=404, body="")


def hist(n):
    return [{"role": "user" if i % 2 == 0 else "assistant", "text": f"E{i}", "timestamp": "2026-11-08T20:00:00.000Z"} for i in range(n)]


def run_all(pg):
    calls.clear()
    pg.evaluate("callApi('Meldung')")
    pg.evaluate("callApi('Hallo BdU', {chat: true})")
    pg.evaluate("h => { conversationHistory = h; historySummary = 'Alt.'; lastSummaryIndex = 0; summaryPauseEntries = 0; return summarizeHistory(); }", hist(10))
    return dict(calls)


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('bdu_api_key','K'); localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite');")
    pg.goto(WIDGET); pg.wait_for_timeout(300)

    # Ohne zweites Modell: alles über das aktive Modell
    pg.evaluate("toggleSettings()")
    check("Feld vorhanden und leer", pg.input_value("#secondary-model-input") == "")
    got = run_all(pg)
    check("Leer: alles über das aktive Modell", got == {"main": "gemini-2.5-flash-lite", "chat": "gemini-2.5-flash-lite", "summary": "gemini-2.5-flash-lite"}, got)

    # Zweites Modell eintragen und speichern
    pg.fill("#secondary-model-input", "  gemini-3.5-flash-lite ")
    pg.evaluate("saveSettings()")
    check("Gespeichert (getrimmt), Feld zeigt bereinigten Wert", pg.evaluate("localStorage.getItem('bdu_secondary_model')") == "gemini-3.5-flash-lite" and pg.input_value("#secondary-model-input") == "gemini-3.5-flash-lite")
    got = run_all(pg)
    check("Eigene Funksprüche: aktives Modell", got.get("main") == "gemini-2.5-flash-lite", got)
    check("Chat-Antworten: zweites Modell", got.get("chat") == "gemini-3.5-flash-lite", got)
    check("Zusammenfassungen: zweites Modell", got.get("summary") == "gemini-3.5-flash-lite", got)
    check("Anzeige „Letzte Zusammenfassung“ nennt das zweite Modell (1.4.1)", "· gemini-3.5-flash-lite)" in pg.inner_text("#last-summary-info"), pg.inner_text("#last-summary-info"))
    pg.evaluate("callApi('Hallo BdU', {chat: true})")
    pg.evaluate("toggleSettings()")
    check("Anzeige „Letzte Anfrage“ nennt das Modell", "(gemini-3.5-flash-lite)" in pg.inner_text("#token-last-usage"), pg.inner_text("#token-last-usage"))
    pg.evaluate("callApi('Meldung')")
    check("… und nach eigener Meldung das aktive", "(gemini-2.5-flash-lite)" in pg.inner_text("#token-last-usage"))
    pg.locator("#secondary-model-input").scroll_into_view_if_needed()
    pg.screenshot(path=os.path.join(OUT, "secondary_model.png"))

    # Neuladen
    reload_keeping_storage(pg)
    check("Nach Neuladen: Feld und Wert erhalten", pg.input_value("#secondary-model-input") == "gemini-3.5-flash-lite" and pg.evaluate("secondaryModel") == "gemini-3.5-flash-lite")

    # Export / Import
    exp = pg.evaluate("buildExportData()")
    check("Export enthält secondaryModel", exp["settings"].get("secondaryModel") == "gemini-3.5-flash-lite")
    d = pg.evaluate("raw => parseImportData(raw)", json.dumps(exp))
    check("Import liest secondaryModel", d["secondaryModel"] == "gemini-3.5-flash-lite")
    del exp["settings"]["secondaryModel"]
    d = pg.evaluate("raw => parseImportData(raw)", json.dumps(exp))
    check("Älterer Export ohne Feld: null (bisheriger Wert bleibt)", d["secondaryModel"] is None)

    # Universal-Modus
    pg.evaluate("apiType = 'universal'; customBaseUrl = 'http://localhost:11434'; currentModel = 'llama3'; secondaryModel = 'llama3.2:1b';")
    got = run_all(pg)
    check("Universal: aktives Modell für eigene, zweites für Chat und Zusammenfassung",
          got == {"main": "U:llama3", "chat": "U:llama3.2:1b", "summary": "U:llama3.2:1b"}, got)

    # RESET
    pg.evaluate("toggleSettings()")
    pg.evaluate("() => { clearSettings(); return new Promise(r => setTimeout(() => { clearSettings(); r(); }, 450)) }")
    check("RESET: Wert und Feld leer", pg.evaluate("secondaryModel") == "" and pg.evaluate("localStorage.getItem('bdu_secondary_model')") is None and pg.input_value("#secondary-model-input") == "")
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
