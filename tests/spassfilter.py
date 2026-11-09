"""1.4.0: benchmark/spassfilter.html – Kopie der Prompt-Funktionen wortgleich zum Widget, Anfrage identisch
zu summarizeHistory(), Ablauf und Auswertung mit simulierter Gemini-API, Export ohne Schlüssel."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BEEP, OUT, Checks
from playwright.sync_api import sync_playwright

check = Checks()
TOOL_PATH = os.path.join(ROOT, "benchmark", "spassfilter.html")
TOOL = "file://" + TOOL_PATH
widget_src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
tool_src = open(TOOL_PATH, encoding="utf-8").read()

# 1) Wortgleiche Kopie
def const_line(src, name):
    m = re.search(r"^        const " + name + r" = .*$", src, re.M)
    return m.group(0) if m else None
def func(src, name):
    i = src.find("        function " + name + "(")
    if i < 0: return None
    j = src.index("\n        }\n", i)
    return src[i:j]
for n in ["SUMMARY_MAX_TOKENS", "SUMMARY_TEMPERATURE", "SUMMARY_CONDENSE_TARGET_CHARS", "SUMMARY_CONDENSE_MAX_TOKENS", "SUMMARY_NOTHING", "SUMMARY_FUN_RULE"]:
    check(f"Konstante {n} wortgleich", const_line(widget_src, n) is not None and const_line(widget_src, n) == const_line(tool_src, n))
for n in ["formatSummaryHistory", "buildSummaryPrompt"]:
    check(f"Funktion {n} wortgleich", func(widget_src, n) is not None and func(widget_src, n) == func(tool_src, n))

widget_bodies, tool_bodies = [], []
state = {"set": [], "fail_first": False}

def widget_route(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if ":generateContent" in u:
        widget_bodies.append(json.loads(route.request.post_data))
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"candidates": [{"content": {"parts": [{"text": "Teil."}]}, "finishReason": "STOP"}]}))
    return route.fulfill(status=404, body="")

def tool_route(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if ":generateContent" not in u: return route.fulfill(status=404, body="")
    body = json.loads(route.request.post_data)
    tool_bodies.append((u, body))
    if state["fail_first"]:
        state["fail_first"] = False
        return route.fulfill(status=429, content_type="application/json", body=json.dumps({"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "Rate limit per minute"}}))
    if state.get("overload", 0) > 0:
        state["overload"] -= 1
        return route.fulfill(status=503, content_type="application/json", body=json.dumps({"error": {"code": 503, "status": "UNAVAILABLE", "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later."}}))
    prompt = body["contents"][0]["parts"][0]["text"]
    items = [it for it in state["set"] if it["kaleu"] in prompt]
    if "Gesamtzusammenfassung" in prompt:
        # simulierte Verdichtung: alle ernsten Fakten, aber versehentlich der Spargel
        text = "ET 42, Kingston Star 7.500 BRT versenkt, Diesel ausgefallen, Kramer verwundet, Versorger Python GF 71, Geleitzug SL 89, Alarmtauchen wegen Wal, Feier. Spargel leer."
    elif items and all(it["kind"] == "spass" for it in items):
        text = "KEINE MELDUNG."
    else:
        text = " ".join(it["kaleu"] + " " + it["bdu"] for it in items if it["kind"] != "spass")
    return route.fulfill(status=200, content_type="application/json", body=json.dumps({
        "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}],
        "usageMetadata": {"promptTokenCount": 500, "candidatesTokenCount": 60}}))

with sync_playwright() as p:
    b = p.chromium.launch()
    tool = b.new_page(); tool.route("**/*", tool_route)
    errs = []; tool.on("pageerror", lambda e: errs.append(str(e)))
    tool.goto(TOOL); tool.wait_for_timeout(300)
    state["set"] = tool.evaluate("TEST_SET")
    check("Testsatz: 5 ernst, 5 Spaß, 2 Grenzfälle, Block 3 nur Spaß, Blöcke zu 3",
          [it["kind"] for it in state["set"]].count("ernst") == 5 and [it["kind"] for it in state["set"]].count("spass") == 5
          and [it["kind"] for it in state["set"]].count("grenzfall") == 2 and tool.evaluate("blocks()[ONLY_FUN_BLOCK].every(it => it.kind === 'spass') && blocks().length === 4 && blocks().every(b => b.length === 3)"))
    check("Testsatz in der Seite angezeigt", tool.locator("#set-table tr").count() == 13)

    # 2) Anfrage identisch zum Widget (normal und verdichtet)
    w = b.new_page(); w.route("**/*", widget_route)
    w.add_init_script("localStorage.setItem('bdu_api_key','K'); localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite');")
    w.goto(WIDGET); w.wait_for_timeout(300)
    entries = tool.evaluate("entriesFor(blocks()[0], 0)")
    boot = tool.evaluate("TEST_BOOT")
    filler = [{"role": "user", "text": "x", "timestamp": "2026-11-08T21:00:00.000Z"}, {"role": "assistant", "text": "y", "timestamp": "2026-11-08T21:00:00.000Z"}] * 2
    w.evaluate("([h, boot]) => { conversationHistory = h; historySummary = ''; lastSummaryIndex = 0; bootContext = boot; summaryPauseEntries = 0; }", [entries + filler, boot])
    w.evaluate("summarizeHistory()")
    expected = tool.evaluate("buildRequestBody(buildSummaryPrompt(formatSummaryHistory(entriesFor(blocks()[0], 0)), false, '', TEST_BOOT), SUMMARY_MAX_TOKENS)")
    check("Normale Zusammenfassung: Anfrage identisch zum Widget", widget_bodies and widget_bodies[-1] == expected)
    prev = "Vorherige Lage. " * 120
    w.evaluate("([h, boot, prev]) => { conversationHistory = h; historySummary = prev; lastSummaryIndex = 0; bootContext = boot; summaryPauseEntries = 0; }", [entries + filler, boot, prev])
    w.evaluate("summarizeHistory()")
    expected = tool.evaluate("prev => buildRequestBody(buildSummaryPrompt(formatSummaryHistory(entriesFor(blocks()[0], 0)), true, prev, TEST_BOOT), SUMMARY_CONDENSE_MAX_TOKENS)", prev)
    check("Verdichtung: Anfrage identisch zum Widget", widget_bodies[-1] == expected)
    w.close()

    check("Standard: 2 Läufe", tool.input_value("#runs") == "2")
    # 3) Ablauf mit simulierter API: 2 Läufe, ein Minutenlimit mit Wiederholung
    tool.evaluate("sleep = () => Promise.resolve()")
    tool.fill("#key", "GEHEIM-TESTKEY"); tool.fill("#runs", "2"); tool.fill("#pause", "0")
    state["fail_first"] = True; tool_bodies.clear()
    tool.click("#btn-run")
    tool.wait_for_function("document.getElementById('run-status').textContent === 'Fertig.'", timeout=60000)
    check("2 Läufe × 5 Aufrufe + 1 Wiederholung", len(tool_bodies) == 11, len(tool_bodies))
    check("Modell und Schlüssel in der Adresse", "models/gemini-3.5-flash-lite:generateContent" in tool_bodies[0][0] and "key=GEHEIM-TESTKEY" in tool_bodies[0][0])
    check("Budgets: 4 × 300, 1 × 1500 je Lauf", [bd["generationConfig"]["maxOutputTokens"] for _, bd in tool_bodies[1:6]] == [300] * 4 + [1500])
    res = tool.evaluate("results")
    check("Angehängt: Fakten 5/5, Spaß 5/5, Grenzfälle 2/2",
          all(r["scoreAppended"]["ernst"] == {"ok": 5, "of": 5} and r["scoreAppended"]["spass"] == {"ok": 5, "of": 5} and r["scoreAppended"]["grenzfall"] == {"ok": 2, "of": 2} for r in res), res[0].get("scoreAppended"))
    check("Verdichtet: Spargel erkannt (Spaß 4/5), Fakten 5/5",
          all(r["scoreCondensed"]["spass"] == {"ok": 4, "of": 5} and r["scoreCondensed"]["ernst"] == {"ok": 5, "of": 5} for r in res), res[0].get("scoreCondensed"))
    check("Block nur aus Spaß: KEINE MELDUNG erkannt", all(r["onlyFunNothing"] for r in res))
    ev = tool.inner_text("#eval")
    check("Auswertung zeigt Summen über beide Läufe", "10/10" in ev and "8/10" in ev and "2/2 Läufe" in ev, ev[:300])
    tool.screenshot(path=os.path.join(OUT, "spassfilter.png"), full_page=True)

    # 3b) Überlastung (503, „high demand“): zwei Wiederholungen, dann weiter; bei dreimal hintereinander Abbruch des Laufs
    tool.fill("#runs", "1"); tool_bodies.clear(); state["overload"] = 2
    tool.click("#btn-run")
    tool.wait_for_function("document.getElementById('run-status').textContent === 'Fertig.'", timeout=60000)
    check("Überlastung: 2 Wiederholungen, Lauf vollständig", len(tool_bodies) == 7 and not tool.evaluate("results[0].error"), len(tool_bodies))
    tool_bodies.clear(); state["overload"] = 3
    tool.click("#btn-run")
    tool.wait_for_function("document.getElementById('run-status').textContent === 'Fertig.'", timeout=60000)
    check("Dreimal überlastet: Lauf mit Fehlermeldung beendet", len(tool_bodies) == 3 and "high demand" in (tool.evaluate("results[0].error") or ""))
    tool.fill("#runs", "2")
    tool.click("#btn-run")
    tool.wait_for_function("document.getElementById('run-status').textContent === 'Fertig.'", timeout=60000)

    # 4) Export ohne Schlüssel, nichts gespeichert
    with tool.expect_download() as dl:
        tool.click("#btn-export")
    path = dl.value.path(); data = open(path, encoding="utf-8").read()
    check("Export: Format und Ergebnisse, ohne Schlüssel", json.loads(data)["format"] == "bdu-spassfilter" and len(json.loads(data)["results"]) == 2 and "GEHEIM-TESTKEY" not in data)
    check("Schlüssel nicht im Browser-Speicher", tool.evaluate("localStorage.length") == 0)
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
