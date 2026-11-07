"""Benchmark mit Groq/Mistral: Request identisch zu callUniversal(), Modelllisten, Schlüssel je Anbieter,
nicht verfügbares Modell, mehrteilige Gemini-Antwort, Beispielkontext (auch im Widget importierbar)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BENCH, EXAMPLE, BEEP, OUT, EXPORT_NOKEY, EXPORT_TEST
import json, os, sys
from playwright.sync_api import sync_playwright

res = []
def check(n, c, info=""):
    res.append(bool(c)); print(("PASS " if c else "FAIL ") + n + ("" if c else "  " + str(info)[:300]))

calls = []
def handler(route):
    req = route.request; url = req.url
    if url.startswith("file://"): return route.continue_()
    if url.endswith(".wav") or "/raw/" in url: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if "fonts.g" in url or "unsplash" in url: return route.fulfill(status=200, body="")
    if "localhost:3000" in url: return route.fulfill(status=200, content_type="application/json", body="{}")
    auth = req.headers.get("authorization", "")
    if url == "https://api.groq.com/openai/v1/models":
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"data": [
            {"id": "llama-3.3-70b-versatile"}, {"id": "openai/gpt-oss-120b"}, {"id": "whisper-large-v3"}, {"id": "meta-llama/llama-guard-4-12b"}]}))
    if url == "https://openrouter.ai/api/v1/models":
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"data": [
            {"id": "meta-llama/llama-3.3-70b-instruct:free"}, {"id": "google/gemma-3-27b-it:free"}, {"id": "openai/gpt-5"}]}))
    if url == "http://eigene.example/v1/models":
        calls.append(("custom-models", url, auth, None))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"data": [{"id": "mein-modell"}]}))
    if url == "https://api.mistral.ai/v1/models":
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"data": [
            {"id": "mistral-small-latest", "capabilities": {"completion_chat": True}},
            {"id": "mistral-embed", "capabilities": {"completion_chat": False}},
            {"id": "mistral-ocr-latest", "capabilities": {"completion_chat": False}}]}))
    if "/v1beta/models?" in url:
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"models": [
            {"name": "models/gemini-3.5-flash-lite", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/gemini-2.5-flash-lite", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/gemini-3.5-flash", "supportedGenerationMethods": ["generateContent"]}]}))
    if url.endswith("/v1/chat/completions"):
        body = json.loads(req.post_data); calls.append(("universal", url, auth, body))
        if body["model"] == "gibts-nicht":
            return route.fulfill(status=404, content_type="application/json", body=json.dumps({"error": {"message": "The model `gibts-nicht` does not exist", "code": "model_not_found"}}))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "**BdU an U-68:**\n\nVerstanden. Weitermachen, Kaleu."}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5000, "completion_tokens": 20, "total_tokens": 5020}}))
    if ":generateContent" in url:
        body = json.loads(req.post_data); calls.append(("gemini", url, auth, body))
        if "gemini-2.0" in url:
            return route.fulfill(status=404, content_type="application/json", body=json.dumps({"error": {"code": 404, "status": "NOT_FOUND", "message": "This model models/gemini-2.0-flash-lite is no longer available."}}))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": "Denke nach", "thought": True}, {"text": "Rückmarsch wird"}, {"text": " genehmigt."}]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 5000, "candidatesTokenCount": 10}}))
    return route.fulfill(status=404, body="")

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---- Widget im Universal-Modus (Groq-Adresse) mit Beispielkontext: Requests mitschneiden ----
    questions = None
    widget = {}
    for provider, base, model in [("groq", "https://api.groq.com/openai", "llama-3.3-70b-versatile"), ("mistral", "https://api.mistral.ai", "mistral-small-latest")]:
        c = b.new_context(); pg = c.new_page(); pg.route("**/*", handler)
        pg.on("dialog", lambda d: d.dismiss())
        pg.goto(WIDGET)
        if questions is None:
            pass
        pg.evaluate("t => { document.getElementById('transfer-text').value = t; importData(); return new Promise(r => setTimeout(() => { importData(); r(); }, 450)); }", open(EXAMPLE, encoding="utf-8").read())
        pg.wait_for_timeout(1500)
        check(f"Beispielkontext im Widget importierbar ({provider})", pg.evaluate("conversationHistory.length") == 10 and "U-68" in pg.evaluate("bootContext"))
        pg.evaluate(f"""() => {{ localStorage.setItem('bdu_api_type','universal'); localStorage.setItem('bdu_custom_base_url','{base}');
                     localStorage.setItem('bdu_current_model','{model}'); localStorage.setItem('bdu_api_key','WKEY'); }}""")
        pg.reload(); pg.wait_for_timeout(400)
        bp = b.new_page(); bp.route("**/*", handler); bp.goto(BENCH)
        questions = bp.evaluate("DEFAULT_QUESTIONS"); bp.close()
        for q in questions:
            n0 = len(calls)
            if q["mode"] == "kaleu":
                pg.evaluate("t => callApi(t)", q["text"])
            else:
                pg.evaluate("t => callApi(t, {chat: true})", q["text"])
            widget[(provider, q["id"])] = calls[n0][3] if len(calls) > n0 else None
        # Status:-Meldung über sendMessage (setzt Status vorher)
        k5 = next(q for q in questions if q["id"] == "k5")
        n0 = len(calls)
        pg.fill("#user-input", k5["text"]); pg.evaluate("sendMessage()")
        for _ in range(100):
            if len(calls) > n0: break
            pg.wait_for_timeout(100)
        widget[(provider, "k5")] = calls[n0][3]
        c.close()

    # ---- Benchmark ----
    c = b.new_context(accept_downloads=True); pg = c.new_page(); pg.route("**/*", handler)
    pg.on("dialog", lambda d: d.accept())
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BENCH)
    pg.evaluate("window.sleep = () => Promise.resolve()")
    pg.fill("#key-gemini", "GKEY"); pg.fill("#key-groq", "QKEY"); pg.fill("#key-mistral", "MKEY")
    pg.click("#btn-models"); pg.wait_for_timeout(500)
    ml = pg.inner_text("#model-list")
    check("Modellliste: Groq-Chatmodelle, ohne Whisper/Guard", "llama-3.3-70b-versatile" in ml and "openai/gpt-oss-120b" in ml and "whisper" not in ml and "guard" not in ml, ml)
    check("Modellliste: Mistral ohne Embed/OCR", "mistral-small-latest" in ml and "embed" not in ml and "ocr" not in ml, ml)
    check("Modellliste: Gemini nur Flash-Lite", "gemini-2.5-flash-lite" in ml and "gemini-3.5-flash\n" not in ml + "\n" and "gemini-3.5-flash " not in ml, ml)
    check("Statuszeile je Anbieter", pg.inner_text("#key-status").count("Verbindung funktioniert") == 3, pg.inner_text("#key-status"))
    pg.check("#models-all"); pg.wait_for_timeout(100)
    check("Alle Gemini-Modelle auf Wunsch", "gemini-3.5-flash" in pg.inner_text("#model-list").replace("gemini-3.5-flash-lite", ""))
    # Modelle ankreuzen über die Checkboxen
    pg.evaluate("state.models = []; renderModels()")
    for mid in ["groq:llama-3.3-70b-versatile", "mistral:mistral-small-latest", "gemini-3.5-flash-lite"]:
        pg.check(f"#model-list input[data-model='{mid}']")
    check("Auswahl per Checkbox gespeichert", sorted(pg.evaluate("state.models")) == sorted(["groq:llama-3.3-70b-versatile", "mistral:mistral-small-latest", "gemini-3.5-flash-lite"]))
    pg.select_option("#model-manual-provider", "groq"); pg.fill("#model-manual", "gibts-nicht"); pg.click("#btn-model-add")
    pg.select_option("#model-manual-provider", "gemini"); pg.fill("#model-manual", "gemini-2.0-flash-lite"); pg.click("#btn-model-add")
    check("Von Hand mit Anbieter", "groq:gibts-nicht" in pg.evaluate("state.models") and "gemini-2.0-flash-lite" in pg.evaluate("state.models"))
    pg.set_input_files("#ctx-file", EXAMPLE); pg.wait_for_timeout(300)
    check("Beispielkontext lädt im Benchmark", pg.evaluate("state.contexts.length === 1 && state.contexts[0].history.length === 10"), pg.inner_text("#ctx-status"))
    pg.fill("#repeats", "1"); pg.fill("#pause", "0")
    n0 = len(calls)
    pg.evaluate("run()")
    pg.wait_for_function("!running", timeout=30000)
    bench_calls = calls[n0:]
    R = pg.evaluate("state.results")
    # Vergleich mit Widget
    for provider, model in [("groq", "llama-3.3-70b-versatile"), ("mistral", "mistral-small-latest")]:
        for q in questions:
            utext = ("Funkspruch aus dem Chat (nicht vom Kaleu):\n" + q["text"]) if q["mode"] == "chat" else q["text"]
            bb = next((c4 for kind, url, auth, c4 in bench_calls if kind == "universal" and c4["model"] == model and c4["messages"][-1]["content"] == utext), None)
            check(f"{provider} {q['id']}: Request identisch zum Widget (callUniversal)", bb is not None and bb == widget[(provider, q["id"])],
                  "" if bb is None else [k for k in bb if bb[k] != widget[(provider, q['id'])].get(k)])
    urls = {(kind, url.split('?')[0], auth) for kind, url, auth, _ in bench_calls}
    check("Groq: richtige Adresse und eigener Schlüssel", ("universal", "https://api.groq.com/openai/v1/chat/completions", "Bearer QKEY") in urls)
    check("Mistral: richtige Adresse und eigener Schlüssel", ("universal", "https://api.mistral.ai/v1/chat/completions", "Bearer MKEY") in urls)
    check("Gemini: Schlüssel GKEY in der URL", any(kind == "gemini" and "key=GKEY" in url for kind, url, _, _ in bench_calls))
    check("Nicht vorhandenes Groq-Modell: nur 1 Versuch, dann übersprungen", sum(1 for k, u, a, c4 in bench_calls if k == "universal" and c4["model"] == "gibts-nicht") == 1)
    check("Gemini 2.0 (nicht mehr verfügbar): nur 1 Versuch", sum(1 for k, u, a, c4 in bench_calls if "gemini-2.0" in u) == 1)
    check("Log nennt übersprungene Modelle", pg.inner_text("#log").count("nicht verfügbar") == 2, pg.inner_text("#log")[-500:])
    gem = [r for r in R if r["model"] == "gemini-3.5-flash-lite" and r["ok"]]
    check("Gemini: alle Text-Teile ohne Denk-Teil", gem and all(r["raw"] == "Rückmarsch wird genehmigt." for r in gem), gem[:1])
    check("Gemini: Teile-Anzahl erfasst und als Befund", gem and gem[0]["parts"] == 2 and "2 Text-Teile" in pg.evaluate("r => autoFlags(r)", gem[0]))
    gq = [r for r in R if r["model"] == "groq:llama-3.3-70b-versatile" and r["ok"]]
    check("Groq: 10 Antworten, Tokens erfasst", len(gq) == 10 and gq[0]["usage"]["prompt"] == 5000)
    check("Chat-Antwort Groq bereinigt", all(r["text"] == "Verstanden. Weitermachen, Kaleu." for r in gq if r["mode"] == "chat"))
    ls = pg.evaluate("localStorage.getItem('bdu_bench_state_v1')")
    check("Keine Schlüssel im localStorage", not any(k in ls for k in ["GKEY", "QKEY", "MKEY"]))
    # ohne Groq-Schlüssel starten
    pg.fill("#key-groq", "")
    pg.evaluate("state.results = []")
    msgs = []
    pg.once("dialog", lambda d: msgs.append(d.message))
    pg.evaluate("run()"); pg.wait_for_timeout(200)
    check("Fehlender Schlüssel wird vor dem Start gemeldet", msgs and "Groq" in msgs[0], msgs)
    # Auswertung zeigt Anbieter
    pg.fill("#key-groq", "QKEY")
    # alter Stand ohne Präfix bleibt Gemini
    check("Alte Modell-IDs ohne Präfix = Gemini", pg.evaluate("parseModelId('gemini-2.5-flash-lite').provider") == "gemini")
    # OpenRouter (nur :free) und eigene Adresse (ohne Schlüssel, Adresse mit /v1/ am Ende)
    pg.fill("#key-gemini", ""); pg.fill("#key-groq", ""); pg.fill("#key-mistral", "")
    pg.fill("#key-openrouter", "OKEY"); pg.fill("#custom-base-url", "http://eigene.example/v1/"); pg.fill("#key-custom", "")
    pg.click("#btn-models"); pg.wait_for_timeout(500)
    ml = pg.inner_text("#model-list")
    check("OpenRouter: nur kostenlose Modelle", "llama-3.3-70b-instruct:free" in ml and "gemma-3-27b-it:free" in ml and "gpt-5" not in ml, ml)
    check("Eigene Adresse: Modellliste über normalisierte Adresse, ohne Schlüssel-Header",
          any(k == "custom-models" and a == "" for k, u, a, _ in calls), [c[:3] for c in calls if c[0] == "custom-models"])
    check("Eigene Adresse: Modell in der Liste", "mein-modell" in ml, ml)
    pg.evaluate("state.models = ['openrouter:google/gemma-3-27b-it:free', 'custom:mein-modell']; state.results = []; state.questions = state.questions.slice(0, 2)")
    n0 = len(calls)
    pg.evaluate("run()"); pg.wait_for_function("!running", timeout=30000)
    nc = calls[n0:]
    check("OpenRouter: Adresse, Schlüssel, Modellname mit :free", any(u == "https://openrouter.ai/api/v1/chat/completions" and a == "Bearer OKEY" and c4["model"] == "google/gemma-3-27b-it:free" for k, u, a, c4 in nc))
    check("Eigene Adresse: /v1 nicht doppelt, ohne Schlüssel kein Authorization-Header", any(u == "http://eigene.example/v1/chat/completions" and a == "" for k, u, a, c4 in nc), [(u, a) for k, u, a, c4 in nc])
    R2 = pg.evaluate("state.results")
    check("Ergebnisse beider Anbieter, Adresse bei eigener Adresse gespeichert",
          sum(1 for r in R2 if r["ok"]) == 4 and all(r.get("baseUrl") == "http://eigene.example" for r in R2 if r["model"].startswith("custom:")), R2[:1])
    pg.fill("#custom-base-url", "")
    msgs2 = []; pg.once("dialog", lambda d: msgs2.append(d.message))
    pg.evaluate("state.results = []; run()"); pg.wait_for_timeout(200)
    check("Fehlende Adresse wird vor dem Start gemeldet", msgs2 and "Eigene Adresse" in msgs2[0], msgs2)
    # CORS-Fehler wird verständlich
    pg.route("https://api.mistral.ai/v1/chat/completions", lambda r: r.abort())
    e = pg.evaluate("callUniversalModel('mistral','x',{}).then(()=> 'ok', e => e.message)")
    check("Blockierte Anfrage: Hinweis auf CORS", "CORS" in e, e)
    check("Keine JS-Fehler", not errs, errs)
    pg.set_viewport_size({"width": 1100, "height": 900})
    pg.locator("#s-key").screenshot(path=os.path.join(OUT, "bench_keys.png"))
    pg.locator("#s-models").screenshot(path=os.path.join(OUT, "bench_models.png"))
    b.close()
print(f"\n{sum(res)}/{len(res)} bestanden")
sys.exit(0 if all(res) else 1)
