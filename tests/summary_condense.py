"""1.4.0: Zusammenfassung verdichten, Spaßmeldungen weglassen, kein explizites Caching (ADR 0006),
Anzeige des automatisch zwischengespeicherten Anteils, fester Anfang des Systemtexts."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import WIDGET, BEEP, OUT, Checks
from playwright.sync_api import sync_playwright

check = Checks()
calls = []
mode = {"summary": "Neue Lage: Geleitzug versenkt.", "finish": "STOP",
        "usage": {"promptTokenCount": 3410, "cachedContentTokenCount": 2950, "candidatesTokenCount": 20, "totalTokenCount": 3430}}


def handle(route):
    u = route.request.url
    body = route.request.post_data or ""
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    calls.append((u.split("?")[0], body))
    if ":generateContent" in u:
        summary = "Fasse folgende Funksprüche" in body or "Gesamtzusammenfassung" in body
        text = mode["summary"] if summary else "Verstanden."
        fin = mode["finish"] if summary else "STOP"
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": fin}], "usageMetadata": mode["usage"]}))
    if "/v1/chat/completions" in u:
        summary = "Gesamtzusammenfassung" in body or "Fasse folgende Funksprüche" in body
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "choices": [{"message": {"content": mode["summary"] if summary else "Universal."}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1234, "prompt_tokens_details": {"cached_tokens": 1024}}}))
    return route.fulfill(status=404, body="")


def hist(n):
    return [{"role": "user" if i % 2 == 0 else "assistant", "text": f"Eintrag {i}: Lage gemeldet.",
             "timestamp": "2026-11-01T10:00:00.000Z"} for i in range(n)]


def prepare(pg, summary, n=12, idx=0):
    pg.evaluate("""([h, s, i]) => { conversationHistory = h; historySummary = s; lastSummaryIndex = i;
                   summaryPauseEntries = 0; summaryFailureShown = false; }""", [hist(n), summary, idx])
    calls.clear()


def last_gen():
    gen = [c for c in calls if ":generateContent" in c[0]]
    return json.loads(gen[-1][1]) if gen else {}


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('bdu_api_key','K'); localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite');")
    pg.goto(WIDGET); pg.wait_for_timeout(300)

    # 1) Kurze Zusammenfassung: anhängen, Spaß-Regel im Prompt
    prepare(pg, "Alte Lage.")
    pg.evaluate("summarizeHistory()")
    req = last_gen(); prompt = req["contents"][0]["parts"][0]["text"]
    check("Normal: eine Anfrage, Budget 300", len(calls) == 1 and req["generationConfig"]["maxOutputTokens"] == 300, req.get("generationConfig"))
    check("Normal: Spaß-Regel mit Beispielen des Nutzers", "Spargelvorräte sind leer" in prompt and "Bier ist alle" in prompt and "Enthebung seines Kommandos" in prompt)
    check("Normal: Antwort „KEINE MELDUNG“ vorgesehen", "KEINE MELDUNG" in prompt)
    check("Normal: angehängt", pg.evaluate("historySummary") == "Alte Lage.\n\nNeue Lage: Geleitzug versenkt.")
    check("Normal: Index = Länge - 4, gespeichert", pg.evaluate("lastSummaryIndex") == 8 and pg.evaluate("localStorage.getItem('bdu_last_summary_index')") == "8")

    # 2) Nur Spaßmeldungen: nichts anhängen, Index trotzdem weiter
    mode["summary"] = "KEINE MELDUNG."
    prepare(pg, "Alte Lage.")
    pg.evaluate("summarizeHistory()")
    check("Nur Spaß: Zusammenfassung unverändert, Index weiter", pg.evaluate("historySummary") == "Alte Lage." and pg.evaluate("lastSummaryIndex") == 8)
    check("Nur Spaß: keine Fehlermeldung", "FEHLGESCHLAGEN" not in pg.inner_text("#chat-log"))

    # 3) Lange Zusammenfassung: verdichten, ersetzen
    mode["summary"] = "Verdichtet: U-68 vor Freetown, zwei Frachter versenkt."
    long_summary = "U-4: Fahrt in der Nordsee. " * 64   # 1.728 Zeichen + 400 > 2.000
    prepare(pg, long_summary)
    pg.evaluate("summarizeHistory()")
    req = last_gen(); prompt = req["contents"][0]["parts"][0]["text"]
    boot = pg.evaluate("bootContext")
    check("Verdichten: eine Anfrage, Budget 1500", len(calls) == 1 and req["generationConfig"]["maxOutputTokens"] == 1500, req.get("generationConfig"))
    check("Verdichten: bisherige Zusammenfassung und neue Funksprüche im Prompt", long_summary.strip() in prompt and "Eintrag 0" in prompt and "Eintrag 7" in prompt and "Eintrag 8" not in prompt)
    check("Verdichten: Boot-Kontext zur Einordnung, nicht wiederholen", boot in prompt and "nicht wiederholen" in prompt)
    check("Verdichten: Ziel 1200 Zeichen, deutlich kürzer, Spaß-Regel", "1200 Zeichen" in prompt and "deutlich kürzer" in prompt and "Spargelvorräte" in prompt)
    check("Verdichten: Ergebnis ersetzt die Zusammenfassung", pg.evaluate("historySummary") == mode["summary"])
    check("Verdichten: gespeichert, Index weiter", pg.evaluate("localStorage.getItem('bdu_history_summary')") == mode["summary"] and pg.evaluate("lastSummaryIndex") == 8)

    # 4) Unter der Grenze (1.500 + 400 <= 2.000) wird noch angehängt
    mode["summary"] = "Teil."
    prepare(pg, "x" * 1500)
    pg.evaluate("summarizeHistory()")
    check("Knapp unter der Grenze: angehängt", pg.evaluate("historySummary") == "x" * 1500 + "\n\nTeil.")

    # 5) Verdichten abgeschnitten: alte Zusammenfassung bleibt, Meldung einmal
    mode["summary"] = "Verdichtet, aber abgesch"; mode["finish"] = "MAX_TOKENS"
    prepare(pg, long_summary)
    pg.evaluate("summarizeHistory()")
    check("Abgeschnitten: alte Zusammenfassung und Index bleiben", pg.evaluate("historySummary") == long_summary and pg.evaluate("lastSummaryIndex") == 0)
    check("Abgeschnitten: Meldung im Display", "ZUSAMMENFASSUNG FEHLGESCHLAGEN" in pg.inner_text("#chat-log"))
    mode["finish"] = "STOP"; mode["summary"] = "KEINE MELDUNG"
    prepare(pg, long_summary)
    pg.evaluate("summarizeHistory()")
    check("Verdichten mit „KEINE MELDUNG“ gilt als Fehlschlag", pg.evaluate("historySummary") == long_summary and pg.evaluate("lastSummaryIndex") == 0)
    mode["summary"] = "y" * (len(long_summary) + 10)
    prepare(pg, long_summary)
    pg.evaluate("summarizeHistory()")
    check("Verdichtung nicht kürzer als vorher: Fehlschlag, alte bleibt", pg.evaluate("historySummary") == long_summary and pg.evaluate("lastSummaryIndex") == 0)
    mode["summary"] = "z" * 2500   # länger als die Obergrenze, aber kürzer als vorher: übernehmen
    prepare(pg, "w" * 5786)
    pg.evaluate("summarizeHistory()")
    check("Verdichtung über 2.000, aber kürzer als vorher (5.786): übernommen", pg.evaluate("historySummary") == "z" * 2500)

    # 6) Anzeige: Token der letzten Anfrage, davon automatisch zwischengespeichert (D1)
    check("Anzeige vor der ersten Anfrage", "noch keine" in pg.inner_text("#token-last-usage"))
    mode["summary"] = "Teil."
    pg.evaluate("callApi('Meldung')")
    check("Anzeige Gemini: 3.410 Tokens, davon 2.950", "3.410 Tokens, davon 2.950 automatisch zwischengespeichert" in pg.inner_text("#token-last-usage"), pg.inner_text("#token-last-usage"))

    # 7) Fester Anfang des Systemtexts bei wechselndem Status und Zusammenfassung
    calls.clear()
    pg.evaluate("currentStatus = 'Status A'; historySummary = 'Zusammenfassung A';")
    pg.evaluate("callApi('Eins')")
    pg.evaluate("currentStatus = 'Status B'; historySummary = 'Zusammenfassung B';")
    pg.evaluate("callApi('Zwei', {chat: true})")
    gen = [json.loads(c[1]) for c in calls if ":generateContent" in c[0]]
    prefix = pg.evaluate("SAFETY_RULES + '\\n' + systemPrompt + '\\n\\n=== BOOT-INFORMATIONEN ===\\n' + bootContext")
    texts = [g["systemInstruction"]["parts"][0]["text"] for g in gen]
    check("Beide Anfragen beginnen gleich bis einschließlich Boot-Kontext", len(texts) == 2 and all(t.startswith(prefix) for t in texts))
    check("Status und Zusammenfassung stehen dahinter", "Status B" in texts[1] and texts[1].index("Status B") > len(prefix) and "Zusammenfassung B" in texts[1])
    check("Kein cachedContent, kein Aufruf von cachedContents", all("cachedContent" not in g for g in gen) and not [c for c in calls if "cachedContents" in c[0]])

    # 8) Universal: Verdichten und Anzeige
    pg.evaluate("apiType = 'universal'; customBaseUrl = 'http://localhost:11434'; currentModel = 'llama3';")
    mode["summary"] = "Universal verdichtet."
    prepare(pg, long_summary)
    pg.evaluate("summarizeHistory()")
    uc = [json.loads(c[1]) for c in calls if "chat/completions" in c[0]]
    check("Universal: Verdichten mit max_tokens 1500", len(uc) == 1 and uc[0]["max_tokens"] == 1500 and "Gesamtzusammenfassung" in uc[0]["messages"][0]["content"])
    check("Universal: Ergebnis ersetzt", pg.evaluate("historySummary") == "Universal verdichtet.")
    pg.evaluate("callApi('Meldung')")
    check("Anzeige Universal: 1.234 Tokens, davon 1.024", "1.234 Tokens, davon 1.024" in pg.inner_text("#token-last-usage"), pg.inner_text("#token-last-usage"))
    pg.evaluate("toggleSettings(); document.getElementById('api-type-universal').checked = true; toggleApiTypeUI();")
    check("Token-Schätzung auch im Universal-Modus sichtbar", pg.is_visible("#token-estimate"))
    check("Kein Caching-Schalter, kein Hinweis auf Caching-Minimum", pg.locator("#caching-group").count() == 0 and "Minimum für Caching" not in pg.inner_text("#token-estimate"))
    pg.locator("#token-estimate").scroll_into_view_if_needed()
    pg.screenshot(path=os.path.join(OUT, "summary_condense_settings.png"))

    # 9) Export ohne cachingEnabled
    st = pg.evaluate("buildExportData().settings")
    check("Export enthält kein cachingEnabled", "cachingEnabled" not in st)
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
