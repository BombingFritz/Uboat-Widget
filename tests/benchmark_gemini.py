"""Prüft bench/bench.html:
1. Request-Body identisch zum Widget (index.html) für alle Standardfragen (Kaleu, Status:, Chat).
2. Ablauf: Durchlauf, 429-Wiederholung, Tageslimit, Fortsetzen, Blindbewertung, Auflösen, Export ohne Schlüssel.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BENCH, EXAMPLE, BEEP, OUT, EXPORT_NOKEY, EXPORT_TEST
import json, os, sys
from playwright.sync_api import sync_playwright


checks = []
def check(name, cond, info=""):
    checks.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (("  " + info) if info and not cond else ""))

def common_routes(page, bodies, responder=None):
    def handle(route):
        url, req = route.request.url, route.request
        if url.startswith("file://"): return route.continue_()
        if url.endswith(".wav") or "/raw/" in url:
            return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
        if "fonts.g" in url or "unsplash" in url: return route.fulfill(status=200, body="")
        if "localhost:3000" in url: return route.fulfill(status=200, content_type="application/json", body="{}")
        if ":generateContent" in url:
            body = json.loads(req.post_data)
            bodies.append((url, body))
            if responder: return responder(route, url, body)
            return route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "candidates": [{"content": {"parts": [{"text": "**BdU an U-68:**\n\nAntwort."}]}, "finishReason": "STOP"}],
                "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 10, "totalTokenCount": 110}}))
        if "/v1beta/models?" in url:
            return route.fulfill(status=200, content_type="application/json", body=json.dumps({"models": [
                {"name": "models/gemini-3.5-flash-lite", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-2.5-flash-lite", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/gemini-3.5-flash", "supportedGenerationMethods": ["generateContent"]},
                {"name": "models/text-embedding-004", "supportedGenerationMethods": ["embedContent"]}]}))
        return route.fulfill(status=404, body="")
    page.route("**/*", handle)

with sync_playwright() as p:
    b = p.chromium.launch()

    # Fragen aus der Bench-Seite holen
    ctx0 = b.new_context(); pg = ctx0.new_page(); common_routes(pg, [])
    pg.goto(BENCH)
    questions = pg.evaluate("DEFAULT_QUESTIONS")
    ctx0.close()

    # ---- 1. Widget-Requests sammeln (je Frage frischer Browser-Kontext mit importiertem Export) ----
    widget_bodies = {}
    for q in questions:
        c = b.new_context(); pg = c.new_page(); bodies = []
        common_routes(pg, bodies)
        pg.on("dialog", lambda d: d.accept())
        pg.goto(WIDGET)
        pg.evaluate("t => { document.getElementById('transfer-text').value = t; importData(); return new Promise(r => setTimeout(() => { importData(); r(); }, 450)); }", open(EXPORT_TEST).read())
        pg.wait_for_timeout(1500)  # Reload nach Import
        assert pg.evaluate("conversationHistory.length") == 100, "Import im Widget fehlgeschlagen"
        if q["mode"] == "kaleu":
            pg.fill("#user-input", q["text"])
            pg.evaluate("sendMessage()")
        else:
            pg.evaluate("t => { lastOwnSendAt = 0; chatQueue.push({id: 'x', text: t}); processChatQueue(); }", q["text"])
        for _ in range(100):
            if bodies: break
            pg.wait_for_timeout(100)
        widget_bodies[q["id"]] = bodies[0][1] if bodies else None
        check(f"Widget-Request erfasst {q['id']}", bodies, "")
        c.close()

    # ---- 2. Bench-Requests ----
    c = b.new_context(); pg = c.new_page(); bench_bodies = []
    common_routes(pg, bench_bodies)
    pg.on("dialog", lambda d: d.accept())
    pg.goto(BENCH)
    pg.evaluate("window.sleep = () => Promise.resolve()")
    pg.fill("#key-gemini", "TESTKEY")
    pg.click("#btn-models")
    pg.wait_for_timeout(300)
    labels = pg.locator("#model-list label").all_inner_texts(); labels = [l for l in labels if l.strip()]
    check("Modellliste gefiltert auf flash-lite", len(labels) == 2 and all("flash-lite" in l for l in labels), str(labels))
    pg.set_input_files("#ctx-file", EXPORT_TEST)
    pg.wait_for_timeout(300)
    check("Hinweis: Schlüssel im Export verworfen", "verworfen" in pg.inner_text("#ctx-status"))
    check("Kontext geladen, Volltext 4 Einträge", pg.evaluate("state.contexts.length === 1 && getContextHistory(state.contexts[0].history, state.contexts[0].lastSummaryIndex).length === 4"))
    pg.evaluate("state.models = ['gemini-3.5-flash-lite']")
    pg.fill("#repeats", "1"); pg.fill("#pause", "0")
    pg.evaluate("run()")
    pg.wait_for_function("!running && state.results.length === %d" % len(questions), timeout=20000)
    by_text = {}
    for url, body in bench_bodies:
        by_text[body["contents"][-1]["parts"][0]["text"]] = body
    for q in questions:
        wb = widget_bodies.get(q["id"])
        ut = wb["contents"][-1]["parts"][0]["text"] if wb else None
        bb = by_text.get(ut)
        same = wb is not None and bb == wb
        info = ""
        if not same and wb and bb:
            for k in wb:
                if wb[k] != bb.get(k): info += f" Feld {k} unterschiedlich;"
        check(f"Request identisch Widget = Bench: {q['id']} ({q['mode']})", same, info)
    k5 = by_text.get(next(q["text"] for q in questions if q["id"] == "k5"))
    check("Status-Meldung ersetzt Status im Systemtext", k5 and "Seit vier Tagen keine Feindberührung." in k5["systemInstruction"]["parts"][0]["text"].split("=== AKTUELLER STATUS ===")[1].split("===")[0])
    c1 = by_text.get("Funkspruch aus dem Chat (nicht vom Kaleu):\n" + next(q["text"] for q in questions if q["id"] == "c1"))
    check("Chat: Chat-Regeln + Standard-Chat-Persönlichkeit (alter Export ohne Feld)", c1 and "TON GEGENÜBER DEM CHAT" in c1["systemInstruction"]["parts"][0]["text"] and c1["generationConfig"]["maxOutputTokens"] == 200)
    check("Chat-Antwort bereinigt", pg.evaluate("state.results.filter(r => r.mode === 'chat').every(r => r.text === 'Antwort.')"))
    check("Kaleu-Antwort unverändert", pg.evaluate("state.results.filter(r => r.mode === 'kaleu').every(r => r.text.startsWith('**BdU an U-68:**'))"))
    ls = pg.evaluate("localStorage.getItem('bdu_bench_state_v1')")
    check("Kein Schlüssel im localStorage", "TESTKEY" not in ls)
    flags = pg.evaluate("autoFlags(state.results.find(r => r.mode === 'chat'))")
    check("Automatische Befunde Chat (Kopfzeile, Formatierung, Zeilenumbruch, Floskel)",
          {"Kopfzeile (bereinigt)", "Formatierung (bereinigt)", "Zeilenumbruch (bereinigt)", "Floskel (≤ 3 Wörter)"} <= set(flags), str(flags))
    c.close()

    # ---- 3. Ablauf mit zwei Modellen, 429, Tageslimit, Fortsetzen ----
    state = {"calls": {}}
    def responder(route, url, body):
        model = url.split("/models/")[1].split(":")[0]
        n = state["calls"][model] = state["calls"].get(model, 0) + 1
        if model == "gemini-2.5-flash-lite" and n == 1:
            return route.fulfill(status=429, content_type="application/json", body=json.dumps({"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "Quota exceeded per minute"}}))
        if model == "gemini-3.5-flash" and n >= 2 and not state.get("day_ok"):
            return route.fulfill(status=429, content_type="application/json", body=json.dumps({"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "Quota exceeded for metric generate_content_free_tier_requests, limit: 20 per day"}}))
        txt = f"{model} Antwort auf: " + body["contents"][-1]["parts"][0]["text"][:20]
        fin = "MAX_TOKENS" if model == "gemini-3.5-flash" else "STOP"
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": txt}]}, "finishReason": fin}],
            "usageMetadata": {"promptTokenCount": 5000, "candidatesTokenCount": 40, "thoughtsTokenCount": 12, "totalTokenCount": 5052}}))

    c = b.new_context(accept_downloads=True); pg = c.new_page(); bodies = []
    common_routes(pg, bodies, responder)
    pg.on("dialog", lambda d: d.accept())
    pg.goto(BENCH)
    pg.evaluate("window.sleep = () => Promise.resolve()")
    pg.fill("#key-gemini", "TESTKEY")
    pg.set_input_files("#ctx-file", EXPORT_NOKEY)
    pg.wait_for_timeout(200)
    check("Ohne Schlüssel im Export kein Hinweis", "verworfen" not in pg.inner_text("#ctx-status"))
    pg.evaluate("state.models = ['gemini-3.5-flash-lite', 'gemini-2.5-flash-lite', 'gemini-3.5-flash']; state.questions = state.questions.slice(0, 3)")
    pg.fill("#repeats", "2"); pg.fill("#pause", "0")
    pg.evaluate("run()")
    pg.wait_for_function("!running", timeout=20000)
    res = pg.evaluate("state.results")
    ok = [r for r in res if r["ok"]]
    check("429 (Minute) wird wiederholt", any(r["model"] == "gemini-2.5-flash-lite" for r in ok) and state["calls"]["gemini-2.5-flash-lite"] == 7, str(state["calls"]))
    check("Tageslimit: Modell übersprungen, nur 1 Ergebnis", sum(1 for r in ok if r["model"] == "gemini-3.5-flash") == 1 and state["calls"]["gemini-3.5-flash"] == 2, str(state["calls"]))
    check("Andere Modelle vollständig (je 6)", sum(1 for r in ok if r["model"] == "gemini-3.5-flash-lite") == 6 and sum(1 for r in ok if r["model"] == "gemini-2.5-flash-lite") == 6)
    check("Abgeschnitten erkannt", any("abgeschnitten" in pg.evaluate("r => autoFlags(r)", r) for r in ok if r["model"] == "gemini-3.5-flash"))
    check("Log nennt Tageskontingent", "Tageskontingent" in pg.inner_text("#log"))
    before = dict(state["calls"])
    state["day_ok"] = True
    pg.evaluate("run()")
    pg.wait_for_function("!running", timeout=20000)
    new_calls = {k: state["calls"][k] - before.get(k, 0) for k in state["calls"]}
    check("Fortsetzen holt nur Fehlendes nach (5 Aufrufe 3.5-flash)", new_calls == {"gemini-3.5-flash-lite": 0, "gemini-2.5-flash-lite": 0, "gemini-3.5-flash": 5}, str(new_calls))
    check("Jetzt 18 Ergebnisse", pg.evaluate("state.results.filter(r => r.ok).length") == 18)

    # Blindbewertung
    pg.select_option("#rate-q", "k1")
    pg.wait_for_timeout(100)
    txt = pg.inner_text("#rate-view")
    answers = pg.locator("#rate-view .answer")
    check("Bewertung: 6 Antworten je Frage", answers.count() == 6)
    check("Bewertung: keine Modellnamen-Tags vor Auflösen", pg.locator("#rate-view .answer .tag").count() == 0)
    order1 = [answers.nth(i).get_attribute("data-key") for i in range(answers.count())]
    pg.reload(); pg.wait_for_timeout(200)
    pg.select_option("#rate-q", "k1"); pg.wait_for_timeout(100)
    order2 = [pg.locator("#rate-view .answer").nth(i).get_attribute("data-key") for i in range(6)]
    check("Reihenfolge nach Neuladen gleich", order1 == order2)
    check("Reihenfolge gemischt (nicht nach Modell sortiert)", order1 != sorted(order1))
    for qid in ["k1", "k2", "k3"]:
        pg.select_option("#rate-q", qid); pg.wait_for_timeout(50)
        for i in range(6):
            a = pg.locator("#rate-view .answer").nth(i)
            a.locator(f"button[data-points='{(i % 5) + 1}']").click()
            pg.locator("#rate-view .answer").nth(i).locator("button[data-stream='1']" if i % 2 else "button[data-stream='0']").click()
            if i == 0: pg.locator("#rate-view .answer").nth(0).locator("input[data-flaw='kurz']").check()
    pg.wait_for_timeout(100)
    check("Fortschritt 3/3", "3/3" in pg.inner_text("#rate-progress"), pg.inner_text("#rate-progress"))
    check("Auswertung vor Auflösen verborgen", "gemini" not in pg.inner_text("#eval-view"))
    pg.click("#btn-reveal"); pg.wait_for_timeout(100)
    ev = pg.inner_text("#eval-view")
    check("Auswertung nach Auflösen mit Modellen", all(m in ev for m in ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-3.5-flash"]))
    check("Auswertung: Mängelzählung", pg.evaluate("Object.values(state.ratings).filter(r => r.flaws.includes('kurz')).length") == 3)
    check("Bewertung zeigt Modell nach Auflösen", pg.locator("#rate-view .answer .tag").count() == 6)
    with pg.expect_download() as dl:
        pg.click("#btn-export")
    path = dl.value.path()
    exp = open(path).read()
    check("Export ohne Schlüssel", "TESTKEY" not in exp)
    d = json.loads(exp)
    check("Export enthält Ergebnisse und Bewertungen", len(d["results"]) == 18 and len(d["ratings"]) == 18)
    # Import in frische Seite
    c2 = b.new_context(); pg2 = c2.new_page(); common_routes(pg2, [])
    pg2.on("dialog", lambda d: d.accept())
    pg2.goto(BENCH)
    pg2.set_input_files("#import-file", path); pg2.wait_for_timeout(300)
    check("Import stellt Stand wieder her", pg2.evaluate("state.results.length === 18 && state.revealed === true"))
    pg.set_viewport_size({"width": 390, "height": 800})
    pg.select_option("#rate-q", "k1"); pg.wait_for_timeout(100)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    check("Handybreite: kein waagerechtes Scrollen der Seite", sw <= 392, str(sw))
    pg.set_viewport_size({"width": 1100, "height": 1600})
    pg.wait_for_timeout(200); pg.locator("#s-rate").screenshot(path=os.path.join(OUT, "bench_rate.png")); pg.locator("#s-eval").screenshot(path=os.path.join(OUT, "bench_eval.png"))
    b.close()

failed = [n for n, ok in checks if not ok]
print(f"\n{len(checks) - len(failed)}/{len(checks)} bestanden")
sys.exit(1 if failed else 0)
