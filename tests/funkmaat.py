"""1.5.0: Funkmaat-Meldungen statt [SYS] und Zweitfrequenz bei erschöpftem Kontingent (Spec funkmaat-zweitfrequenz.md)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import WIDGET, BEEP, OUT, Checks, reload_keeping_storage
from playwright.sync_api import sync_playwright

check = Checks()
calls = []
behavior = {}   # Modell -> "ok" | Fehlerart


def err(code, status, message):
    return {"status": code, "content_type": "application/json", "body": json.dumps({"error": {"code": code, "status": status, "message": message}})}


ERRORS = {
    "quota": err(429, "RESOURCE_EXHAUSTED", "You exceeded your current quota. Quota exceeded for metric generate_content_free_tier_requests, limit: 20"),
    "overload": err(503, "UNAVAILABLE", "This model is currently experiencing high demand. Spikes in demand are usually temporary."),
    "key": err(400, "INVALID_ARGUMENT", "API key not valid. Please pass a valid API key."),
    "model": err(404, "NOT_FOUND", "models/gemini-9 is not found for API version v1beta"),
    "other": err(500, "INTERNAL", "Internal error encountered."),
}


def handle(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    if ":generateContent" in u:
        model = u.split("/models/")[1].split(":")[0]
        calls.append(model)
        b = behavior.get(model, "ok")
        if b == "network": return route.abort()
        if b != "ok": return route.fulfill(**ERRORS[b])
        return route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "candidates": [{"content": {"parts": [{"text": f"Antwort von {model}."}]}, "finishReason": "STOP"}]}))
    return route.fulfill(status=404, body="")


def send(pg, text):
    calls.clear()
    pg.fill("#user-input", text); pg.evaluate("sendMessage()")
    pg.wait_for_function("!document.getElementById('status-light').classList.contains('transmitting')", timeout=60000)


def sys_lines(pg):
    return pg.locator("#chat-log .msg-sys").all_inner_texts()


def hist_len(pg):
    return pg.evaluate("conversationHistory.length")


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('bdu_api_key','K'); localStorage.setItem('bdu_current_model','gemini-2.5-flash-lite');")
    pg.goto(WIDGET); pg.wait_for_timeout(300); pg.evaluate("typewriterSpeedPatch = true")

    # 1) Ohne zweites Modell: Kontingent erschöpft
    behavior.clear(); behavior["gemini-2.5-flash-lite"] = "quota"
    send(pg, "Meldung 1")
    check("Ohne zweites Modell: 1 Aufruf, Meldung des Funkmaats", calls == ["gemini-2.5-flash-lite"] and sys_lines(pg)[-1] == "Funkmaat: Funkfrequenz gestört, Meldung nicht durchgekommen. Später erneut versuchen.", (calls, sys_lines(pg)[-1:]))
    check("Ohne zweites Modell: nichts im Verlauf", hist_len(pg) == 0)
    info = pg.inner_text("#incident-info")
    check("Letzte Störung: Modell und technische Meldung", "gemini-2.5-flash-lite" in info and "limit: 20" in info, info)
    check("Technische Meldung nicht im Display", "quota" not in pg.inner_text("#chat-log").lower())

    # 2) Mit zweitem Modell: Zweitfrequenz, Funkspruch im Hintergrund erneut gesendet
    pg.evaluate("toggleSettings()"); pg.fill("#secondary-model-input", "gemini-3.5-flash-lite"); pg.evaluate("saveSettings()")
    check("Gespeichert: Funkmaat-Meldung", sys_lines(pg)[-1] == "Funkmaat: Funkgerät neu eingestellt.")
    send(pg, "Meldung 2")
    lines = sys_lines(pg)
    check("Wechsel: 2 Aufrufe (aktiv, zweites)", calls == ["gemini-2.5-flash-lite", "gemini-3.5-flash-lite"], calls)
    check("Wechsel: Meldung „Zweitfrequenz“", lines[-1] == "Funkmaat: Funkfrequenz gestört, wechsele auf Zweitfrequenz.", lines[-1:])
    last = pg.locator("#chat-log .msg-bdu").last.inner_text()
    check("Wechsel: Antwort des zweiten Modells im Display", "Antwort von gemini-3.5-flash-lite." in last, last)
    check("Wechsel: nur eine Kaleu-Zeile", pg.locator("#chat-log .msg-user", has_text="Meldung 2").count() == 1)
    check("Wechsel: Meldung und Antwort im Verlauf", hist_len(pg) == 2)
    check("Modell-Badge zeigt das genutzte Modell", "3.5-FLASH-LITE" in pg.inner_text("#model-badge"), pg.inner_text("#model-badge"))
    check("Einstellungen: Zweitfrequenz aktiv", "Zweitfrequenz aktiv: gemini-3.5-flash-lite" in pg.inner_text("#incident-info"))
    send(pg, "Meldung 3")
    check("Nächster Funkspruch direkt über das zweite Modell", calls == ["gemini-3.5-flash-lite"] and hist_len(pg) == 4, calls)

    # 3) Auch das zweite Modell erschöpft
    behavior["gemini-3.5-flash-lite"] = "quota"
    send(pg, "Meldung 4")
    check("Zweitfrequenz erschöpft: 1 Aufruf, „Sendeanlage unklar …“", calls == ["gemini-3.5-flash-lite"] and sys_lines(pg)[-1] == "Funkmaat: Sendeanlage unklar, Meldung wiederholt nicht durchgekommen und unbestätigt.", (calls, sys_lines(pg)[-1:]))
    check("… und nichts im Verlauf", hist_len(pg) == 4)

    # 4) SPEICHERN beendet die Zweitfrequenz
    pg.evaluate("toggleSettings(); saveSettings()")
    behavior.clear()
    send(pg, "Meldung 5")
    check("Nach SPEICHERN wieder das aktive Modell", calls == ["gemini-2.5-flash-lite"] and "2.5-FLASH-LITE" in pg.inner_text("#model-badge"), calls)

    # 5) Beide erschöpft direkt beim ersten Versuch
    behavior.update({"gemini-2.5-flash-lite": "quota", "gemini-3.5-flash-lite": "quota"})
    send(pg, "Meldung 6")
    lines = sys_lines(pg)
    check("Beide erschöpft: Wechsel, dann „Sendeanlage unklar …“", calls == ["gemini-2.5-flash-lite", "gemini-3.5-flash-lite"]
          and lines[-2:] == ["Funkmaat: Funkfrequenz gestört, wechsele auf Zweitfrequenz.", "Funkmaat: Sendeanlage unklar, Meldung wiederholt nicht durchgekommen und unbestätigt."], (calls, lines[-2:]))

    # 6) Neuladen beendet die Zweitfrequenz
    reload_keeping_storage(pg); pg.evaluate("typewriterSpeedPatch = true")
    behavior.clear()
    send(pg, "Meldung 7")
    check("Nach Neuladen wieder das aktive Modell", calls == ["gemini-2.5-flash-lite"] and not pg.evaluate("fallbackActive"), calls)

    # 7) Andere Fehlerarten: Funkmaat je Art, kein Modellwechsel
    expect = {
        "overload": ["Funkmaat: Starke atmosphärische Störungen, BdU nicht erreichbar. Meldung später wiederholen.",
                     "Funkmaat: Frequenz nicht sicher, verdächtige Aktivitäten, Feind peilt vermutlich ein. Meldung später absetzen, möglichst kurz halten!"],
        "key": ["Funkmaat: Code-Schlüssel passt nicht, bitte Codebuch und Einstellungen der Funkanlage überprüfen!"],
        "model": ["Funkmaat: Frequenz nicht besetzt. Modell in den Einstellungen prüfen („MODELLE SUCHEN“)."],
        "network": ["Funkmaat: Keine Verbindung zur Sendeanlage. Internetverbindung prüfen."],
        "other": ["Funkmaat: Funkspruch nicht durchgekommen. Einzelheiten in den Einstellungen."],
    }
    for kind, texts in expect.items():
        behavior.clear(); behavior["gemini-2.5-flash-lite"] = kind
        send(pg, f"Test {kind}")
        check(f"Fehlerart {kind}: Funkmaat-Text, 1 Aufruf, kein Wechsel", sys_lines(pg)[-1] in texts and calls == ["gemini-2.5-flash-lite"] and not pg.evaluate("fallbackActive"), (sys_lines(pg)[-1:], calls))
    seen = set()
    behavior["gemini-2.5-flash-lite"] = "overload"
    for _ in range(12):
        send(pg, "Überlast"); seen.add(sys_lines(pg)[-1])
    check("Überlastung: beide Fassungen kommen vor", len(seen) == 2, seen)
    behavior.clear()

    # 8) Status-Meldung und keine [SYS]-Zeilen
    send(pg, "Status: Brennstoff 60 %, 4 Aale")
    check("Status: „In KTB notiert, Lagemeldung weitergegeben: …“", "Funkmaat: In KTB notiert, Lagemeldung weitergegeben: Brennstoff 60 %, 4 Aale" in sys_lines(pg))
    log = pg.inner_text("#chat-log")
    check("Nirgends „[SYS]“ oder „FUNKSTÖRUNG“ im Display", "[SYS]" not in log and "FUNKSTÖRUNG" not in log)
    check("Technische Meldungen nicht im Display", "high demand" not in log and "API key not valid" not in log and "Internal error" not in log)
    pg.evaluate("toggleSettings()")
    pg.locator("#incident-info").scroll_into_view_if_needed()
    pg.screenshot(path=os.path.join(OUT, "funkmaat_settings.png"))
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
