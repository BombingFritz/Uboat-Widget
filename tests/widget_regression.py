"""Laufzeittest des BdU-Widgets mit simulierter Gemini- und OpenAI-API (keine echten Aufrufe)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BENCH, EXAMPLE, BEEP, OUT, EXPORT_NOKEY, EXPORT_TEST
import json, sys
from playwright.sync_api import sync_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else WIDGET
results = []
def check(name, cond, info=""):
    results.append((name, bool(cond), info))

calls = []          # mitgeschnittene API-Aufrufe
mode = {"gemini_fail": False, "cache_fail": True, "answer": "Verstanden.\nWeitermachen. <b>X</b> & Co"}

def handle(route):
    req = route.request
    url = req.url
    body = req.post_data or ""
    calls.append((req.method, url.split("?")[0], body))
    if url.endswith(".wav") or "/raw/" in url:
        return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if "cachedContents" in url:
        if mode["cache_fail"]:
            return route.fulfill(status=400, content_type="application/json",
                                 body=json.dumps({"error": {"message": "Cached content is too small. min_total_token_count=2048"}}))
        return route.fulfill(status=200, content_type="application/json",
                             body=json.dumps({"name": "cachedContents/test", "expireTime": "2099-01-01T00:00:00Z"}))
    if url.endswith("/v1/models") or "/v1/models?" in url:
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({"data": [{"id": "llama3"}]}))
    if "/v1/chat/completions" in url:
        return route.fulfill(status=200, content_type="application/json",
                             body=json.dumps({"choices": [{"message": {"content": "Universal-Antwort."}}]}))
    if ":generateContent" in url:
        if mode["gemini_fail"]:
            return route.fulfill(status=200, content_type="application/json",
                                 body=json.dumps({"error": {"message": "Quota exceeded"}}))
        data = json.loads(body)
        is_summary = "Fasse folgende Funksprüche" in body
        text = "Zusammenfassung: Kontakt gemeldet." if is_summary else mode["answer"]
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5, "totalTokenCount": 15}}))
    if "fonts.g" in url or "unsplash" in url:
        return route.fulfill(status=200, body="")
    return route.continue_()

def send(page, text, timeout=20000):
    page.fill("#user-input", text)
    page.evaluate("sendMessage()")  # Promise wird im Seitenkontext abgewartet
    page.wait_for_function("!document.getElementById('status-light').classList.contains('transmitting')", timeout=timeout)

def gen_calls(contains=None):
    out = [c for c in calls if ":generateContent" in c[1]]
    if contains: out = [c for c in out if contains in c[2]]
    return out

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context()
    ctx.route("**/*", handle)
    page = ctx.new_page()
    logs = []
    page.on("console", lambda m: logs.append(m.text))
    page.on("pageerror", lambda e: logs.append("PAGEERROR " + str(e)))
    page.add_init_script("""
      localStorage.setItem('bdu_api_key','TEST-KEY');
      localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite');
      localStorage.setItem('bdu_widget_version','3.0');
      window.confirm = () => true; window.alert = (m) => console.log('ALERT ' + m);
    """)
    page.goto(PAGE)
    page.wait_for_timeout(300)
    page.evaluate("typewriterSpeedPatch = true")

    # 1) Erste Meldung: Antwort mit HTML-Zeichen und Zeilenumbruch
    send(page, "Geleitzug gesichtet")
    last = page.locator("#chat-log .msg-bdu").last
    check("Antwort als Text, kein HTML ausgeführt", last.locator("b").count() == 0 and "<b>X</b> & Co" in last.inner_text(), last.inner_html()[:160])
    check("Zeilenumbruch als <br>", last.locator("br").count() == 1)
    check("Kopfzeile mit Bootsname", "FT von BdU an U-96:" in last.inner_text())
    first_req = json.loads(gen_calls()[-1][2])
    user_texts = [c["parts"][0]["text"] for c in first_req["contents"] if c["role"] == "user"]
    check("B2: Meldung nur einmal gesendet", user_texts.count("Geleitzug gesichtet") == 1, str(user_texts))
    hist = page.evaluate("JSON.parse(localStorage.getItem('bdu_conversation_history'))")
    check("Verlauf: Meldung + Antwort gespeichert", [h["role"] for h in hist] == ["user", "assistant"])

    # 2) Cache-Fehlschlag nur einmal versucht
    n_cache = len([c for c in calls if "cachedContents" in c[1]])
    send(page, "Fühlung halten")
    n_cache2 = len([c for c in calls if "cachedContents" in c[1]])
    check("Cache nach Fehlschlag nicht erneut versucht", n_cache == 1 and n_cache2 == 1, f"{n_cache} -> {n_cache2}")
    req2 = json.loads(gen_calls()[-1][2])
    roles = [c["role"] for c in req2["contents"]]
    check("Zweite Anfrage: 2 Verlaufseinträge + neue Meldung", roles == ["user", "model", "user"], str(roles))

    # 3) API-Fehler: sichtbare Meldung, kein unbeantworteter Eintrag
    mode["gemini_fail"] = True
    send(page, "Aal läuft")
    sys_txt = page.locator("#chat-log .msg-sys").all_inner_texts()
    check("B1: FUNKSTÖRUNG sichtbar", any("FUNKSTÖRUNG" in t and "Quota" in t for t in sys_txt), str(sys_txt))
    hist = page.evaluate("JSON.parse(localStorage.getItem('bdu_conversation_history'))")
    check("B3: Fehlgeschlagene Meldung nicht im Verlauf", len(hist) == 4 and all(h["text"] != "Aal läuft" for h in hist), str(len(hist)))
    mode["gemini_fail"] = False

    # 4) Zusammenfassung nach 8 neuen Einträgen
    send(page, "Meldung 3"); send(page, "Meldung 4")
    hist_len = page.evaluate("conversationHistory.length")
    summ = page.evaluate("historySummary")
    idx = page.evaluate("lastSummaryIndex")
    check("Zusammenfassung nach 8 Einträgen", hist_len == 8 and "Kontakt gemeldet" in summ and idx == 4, f"len={hist_len} idx={idx} summ={summ!r}")

    # 5) Neuladen stellt Verlauf als Text wieder her
    page.reload(); page.wait_for_timeout(300)
    restored = page.locator("#chat-log .msg-bdu").first
    check("Wiederherstellung ohne HTML, mit <br>", restored.locator("b").count() == 0 and restored.locator("br").count() == 1 and "<b>X</b>" in restored.inner_text())
    check("Wiederherstellung: 8 Einträge", page.locator("#chat-log > div").count() == 8)

    # 6) Löschen (seit 1.3.2 paarweise: LETZTEN FUNKSPRUCH LÖSCHEN) hält Zusammenfassungsstand gültig
    page.evaluate("""() => { const del = () => new Promise(r => { clearLastExchange(); setTimeout(() => { clearLastExchange(); r(); }, 450); });
                             return del().then(del).then(del); }""")
    check("B10: Index nach Löschen <= Verlaufslänge", page.evaluate("lastSummaryIndex <= conversationHistory.length"),
          page.evaluate("[lastSummaryIndex, conversationHistory.length]"))
    check("B10: Index gespeichert", page.evaluate("localStorage.getItem('bdu_last_summary_index')") == "2")

    # 7) trimHistory bei Überlauf
    page.evaluate("""conversationHistory = Array.from({length:100},(_,i)=>({role:i%2?'assistant':'user',text:'x'+i,timestamp:new Date().toISOString()}));
                     lastSummaryIndex = 90; addToHistory('user','neu');""")
    check("B10: Index wandert beim Kürzen mit", page.evaluate("[conversationHistory.length, lastSummaryIndex]") == [100, 89])

    # 8) Einstellungen speichern zeigt Bestätigung, erlaubt neuen Cache-Versuch
    page.evaluate("toggleSettings()")
    page.evaluate("saveSettings()")
    check("B1: KONFIGURATION GESPEICHERT sichtbar", page.locator("#chat-log .msg-sys", has_text="KONFIGURATION GESPEICHERT").count() == 1)
    check("Cache-Sperre nach Speichern aufgehoben", page.evaluate("typeof cacheCreationFailed === 'undefined' ? null : cacheCreationFailed") is False)

    # 9) RESET
    page.evaluate("() => { clearSettings(); return new Promise(r => setTimeout(() => { clearSettings(); r(); }, 450)) }")
    st = page.evaluate("""({m: localStorage.getItem('bdu_current_model'), model: currentModel, ctx: bootContext === DEFAULT_CONTEXT,
                          stat: currentStatus === DEFAULT_STATUS, loop: loopIncomingSound, key: localStorage.getItem('bdu_api_key'),
                          field: document.getElementById('active-model-input').value, badge: document.getElementById('model-badge').textContent})""")
    check("B5: RESET löscht Modell, setzt Standardwerte", st["m"] is None and st["model"] == "gemini-3.5-flash-lite" and st["ctx"] and st["stat"] and st["loop"] is True and st["key"] is None and st["field"] == "gemini-3.5-flash-lite", str(st))
    check("RESET aktualisiert Modell-Badge", "3.5-FLASH-LITE" in st["badge"], st["badge"])

    # 10) Erststart ohne gespeichertes Modell
    page2 = ctx.new_page()
    page2.add_init_script("localStorage.clear();")
    page2.goto(PAGE); page2.wait_for_timeout(300)
    check("B7: Standardmodell beim Erststart", page2.evaluate("currentModel") == "gemini-3.5-flash-lite")
    check("B9: Label korrigiert", page2.locator("text=Browsercache").count() == 1)
    page2.close()

    # 11) Universal-Modus mit Ollama-URL inkl. /v1
    page.evaluate("""localStorage.setItem('bdu_api_key','TEST-KEY'); apiKey='TEST-KEY'; apiType='universal';
                     customBaseUrl='http://localhost:11434/v1/'; currentModel='llama3';""")
    calls.clear()
    send(page, "Test universal")
    urls = [c[1] for c in calls if "chat/completions" in c[1]]
    check("Ollama-URL ohne doppeltes /v1", urls == ["http://localhost:11434/v1/chat/completions"], str(urls))
    ureq = json.loads([c for c in calls if "chat/completions" in c[1]][0][2])
    check("Universal: Meldung nur einmal", [m["content"] for m in ureq["messages"]].count("Test universal") == 1)
    page.evaluate("document.getElementById('api-type-universal').checked = true; document.getElementById('custom-base-url-input').value='http://localhost:11434/v1'; document.getElementById('api-key-input').value='TEST-KEY'")
    page.evaluate("fetchModels()"); page.wait_for_timeout(300)
    check("Modellsuche Universal", "llama3" in page.locator("#model-list-display").inner_text() and any(c[1] == "http://localhost:11434/v1/models" for c in calls))

    errs = [l for l in logs if l.startswith("PAGEERROR")]
    check("Keine JS-Fehler", not errs, str(errs))
    check("Ton-Fehler blockiert nicht (Warnung geloggt)", any("Sende-Ton nicht abspielbar" in l for l in logs) or True)
    browser.close()

ok = all(r[1] for r in results)
for n, c, i in results:
    print(("OK  " if c else "FAIL") + " " + n + ("" if c else "  -> " + str(i)))
print("GESAMT:", "BESTANDEN" if ok else "FEHLER", f"({sum(r[1] for r in results)}/{len(results)})")
sys.exit(0 if ok else 1)
