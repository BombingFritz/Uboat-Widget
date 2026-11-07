"""Export/Import zwischen zwei Herkünften (http://127.0.0.1:8701 und :8702) inkl. Update von einer älteren Version."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BENCH, EXAMPLE, BEEP, OUT, EXPORT_NOKEY, EXPORT_TEST
import json, sys, subprocess, time, os
from playwright.sync_api import sync_playwright

WEB = sys.argv[1] if len(sys.argv) > 1 else ROOT
res = []
def check(n, c, info=""): res.append((n, bool(c), info))

srv = [subprocess.Popen([sys.executable, "-m", "http.server", str(p), "--bind", "127.0.0.1", "-d", WEB],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for p in (8701, 8702)]
time.sleep(1)
A, B = "http://127.0.0.1:8701/index.html", "http://127.0.0.1:8702/index.html"

def handle(route):
    u = route.request.url
    if "127.0.0.1:87" in u: return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=404, body="")
    if ":generateContent" in u:
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "Verstanden."}]}, "finishReason": "STOP"}]}))
    return route.fulfill(status=200, body="")

hist = [{"role": "user", "text": f"Meldung {i}", "timestamp": "2026-11-01T20:00:00Z"} if i % 2 == 0 else
        {"role": "assistant", "text": f"Antwort {i}", "timestamp": "2026-11-01T20:00:00Z"} for i in range(6)]
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(accept_downloads=True); ctx.route("**/*", handle)
        errs = []
        # --- Herkunft A: Altbestand einer älteren Version mit eigenem Prompt ---
        pa = ctx.new_page(); pa.on("pageerror", lambda e: errs.append(str(e)))
        pa.on("dialog", lambda d: (errs.append("Dialog: "+d.message[:40]), d.dismiss()))
        pa.goto(A + "?seed")
        pa.evaluate(f"""localStorage.clear();
            localStorage.setItem('bdu_widget_version','2.1');
            localStorage.setItem('bdu_system_prompt','MEIN EIGENER PROMPT');
            localStorage.setItem('bdu_api_key','KEY-A');
            localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite');
            localStorage.setItem('bdu_boot_context','U-Boot: U-4\\nKommandant: Fischer');
            localStorage.setItem('bdu_current_status','Brennstoff 60%');
            localStorage.setItem('bdu_loop_sound','false');
            localStorage.setItem('bdu_sound_volume','0.3');
            localStorage.setItem('bdu_conversation_history', JSON.stringify({json.dumps(hist)}));
            localStorage.setItem('bdu_history_summary','Kontakt gemeldet.');
            localStorage.setItem('bdu_last_summary_index','2');""")
        pa.reload(); pa.wait_for_timeout(400)
        check("Update: Prompt durch Standard ersetzt", pa.evaluate("systemPrompt === DEFAULT_PROMPT"))
        check("Update: eigener Prompt gesichert", pa.evaluate("localStorage.getItem('bdu_system_prompt_backup')") == "MEIN EIGENER PROMPT")
        pa.evaluate("toggleSettings()")
        check("Hinweis auf gesicherten Prompt sichtbar", pa.locator("#prompt-backup-info").is_visible())
        pa.evaluate("restorePromptBackup()")
        check("Sicherung ins Feld übernehmbar", pa.input_value("#system-prompt-input") == "MEIN EIGENER PROMPT")
        pa.evaluate("saveSettings()")
        check("Nach SPEICHERN eigener Prompt aktiv", pa.evaluate("systemPrompt") == "MEIN EIGENER PROMPT")

        pa.evaluate("toggleSettings()"); pa.evaluate("exportData()"); pa.wait_for_timeout(200)
        exp = json.loads(pa.input_value("#transfer-text"))
        check("Export ohne Schlüssel (Standard)", "apiKey" not in exp["settings"])
        check("Export enthält Prompt, Kontext, Status, Verlauf, Zusammenfassung",
              exp["settings"]["systemPrompt"] == "MEIN EIGENER PROMPT" and "U-4" in exp["settings"]["bootContext"]
              and exp["settings"]["currentStatus"] == "Brennstoff 60%" and len(exp["memory"]["history"]) == 6
              and exp["memory"]["summary"] == "Kontakt gemeldet." and exp["memory"]["lastSummaryIndex"] == 2)
        check("Statusmeldung nach Export", "Exportiert" in pa.inner_text("#transfer-status"))
        pa.check("#export-key-checkbox"); pa.evaluate("exportData()"); pa.wait_for_timeout(200)
        exp_key = pa.input_value("#transfer-text")
        check("Export mit Schlüssel auf Wunsch", json.loads(exp_key)["settings"].get("apiKey") == "KEY-A")
        with pa.expect_download() as dl:
            pa.evaluate("downloadExport()")
        check("Datei-Download", dl.value.suggested_filename == "Funk-Export.json")

        # --- Herkunft B: leer, eigener Schlüssel ---
        pb = ctx.new_page(); pb.on("pageerror", lambda e: errs.append(str(e)))
        pb.on("dialog", lambda d: (errs.append("Dialog: "+d.message[:40]), d.dismiss()))
        pb.goto(B); pb.evaluate("localStorage.clear(); localStorage.setItem('bdu_api_key','KEY-B')"); pb.reload(); pb.wait_for_timeout(300)
        check("B startet leer (Standard-Prompt)", pb.evaluate("systemPrompt === DEFAULT_PROMPT && conversationHistory.length === 0"))
        pb.evaluate("toggleSettings()")
        pb.fill("#transfer-text", "kein json"); pb.evaluate("importData()")
        check("Ungültiger Import wird abgelehnt", "❌" in pb.inner_text("#transfer-status") and pb.evaluate("localStorage.getItem('bdu_current_model')") is None)
        pb.fill("#transfer-text", json.dumps({"format": "anderes"})); pb.evaluate("importData()")
        check("Fremdes Format wird abgelehnt", "Kein Export dieses Widgets" in pb.inner_text("#transfer-status"))

        pb.fill("#transfer-text", json.dumps(exp))  # ohne Schlüssel
        pb.evaluate("importData()")
        check("Import fragt erst im Widget nach (Status, Button)", "BESTÄTIGEN" in pb.inner_text("#import-btn") and "Verlaufseinträge" in pb.inner_text("#transfer-status"))
        pb.wait_for_timeout(450)
        with pb.expect_navigation():
            pb.evaluate("importData()")
        pb.wait_for_timeout(400)
        st = pb.evaluate("""({p: systemPrompt, k: apiKey, m: currentModel, c: bootContext, s: currentStatus, l: loopIncomingSound,
                             v: soundVolume, h: conversationHistory.length, sum: historySummary, i: lastSummaryIndex,
                             ver: localStorage.getItem('bdu_widget_version'), bk: localStorage.getItem('bdu_system_prompt_backup'),
                             shown: document.querySelectorAll('#chat-log > div').length})""")
        check("Import: eigener Prompt übernommen (kein Ersetzen beim Neuladen)", st["p"] == "MEIN EIGENER PROMPT" and st["ver"] == "3.0", st)
        check("Import ohne Schlüssel behält vorhandenen Schlüssel", st["k"] == "KEY-B")
        check("Import: Modell, Kontext, Status, Ton", st["m"] == "gemini-2.5-flash-lite" and "U-4" in st["c"] and st["s"] == "Brennstoff 60%" and st["l"] is False and st["v"] == 0.3, st)
        check("Import: Verlauf und Zusammenfassung, im Display sichtbar", st["h"] == 6 and st["sum"] == "Kontakt gemeldet." and st["i"] == 2 and st["shown"] == 6, st)
        check("Import: Prompt-Sicherung mitgenommen", st["bk"] == "MEIN EIGENER PROMPT")

        pb.reload(); pb.wait_for_timeout(300)
        check("Nach erneutem Laden bleibt importierter Prompt", pb.evaluate("systemPrompt") == "MEIN EIGENER PROMPT")
        # Funkverkehr nach Import nutzt importierten Verlauf
        reqs = []
        pb.on("request", lambda r: reqs.append(r.post_data) if ":generateContent" in r.url else None)
        pb.fill("#user-input", "Neue Meldung"); pb.evaluate("sendMessage()")
        pb.wait_for_function("!document.getElementById('status-light').classList.contains('transmitting')", timeout=20000)
        body = json.loads(reqs[-1])
        texts = [c["parts"][0]["text"] for c in body["contents"]]
        check("Anfrage nach Import enthält importierten Verlauf und Zusammenfassung",
              "Meldung 2" in texts and "Kontakt gemeldet." in body["systemInstruction"]["parts"][0]["text"]
              and "MEIN EIGENER PROMPT" in body["systemInstruction"]["parts"][0]["text"], texts)

        # Import mit Schlüssel
        pb.evaluate("toggleSettings()"); pb.fill("#transfer-text", exp_key)
        pb.evaluate("importData()")
        check("Import fragt erst im Widget nach (Status, Button)", "BESTÄTIGEN" in pb.inner_text("#import-btn") and "Verlaufseinträge" in pb.inner_text("#transfer-status"))
        pb.wait_for_timeout(450)
        with pb.expect_navigation():
            pb.evaluate("importData()")
        pb.wait_for_timeout(300)
        check("Import mit Schlüssel setzt Schlüssel", pb.evaluate("apiKey") == "KEY-A")
        # RESET entfernt Sicherung
        pb.evaluate("() => { clearSettings(); return new Promise(r => setTimeout(() => { clearSettings(); r(); }, 450)) }")
        check("RESET entfernt Prompt-Sicherung", pb.evaluate("localStorage.getItem('bdu_system_prompt_backup')") is None and not pb.locator("#prompt-backup-info").is_visible())
        check("Keine JS-Fehler", not errs, errs)
        b.close()
finally:
    for s in srv: s.terminate()

ok = all(r[1] for r in res)
for n, c, i in res: print(("OK  " if c else "FAIL") + " " + n + ("" if c else f"  -> {i}"))
print("GESAMT:", "BESTANDEN" if ok else "FEHLER", f"({sum(r[1] for r in res)}/{len(res)})")
