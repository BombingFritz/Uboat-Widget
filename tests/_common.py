"""Gemeinsame Hilfen für die Headless-Tests (Playwright, simulierte APIs, keine echten Aufrufe).

Pfade relativ zum Repository; Testdaten werden beim Import erzeugt (kein privater Funkverlauf im Repo).
"""
import io, json, os, struct, tempfile, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDGET_PATH = os.path.join(ROOT, "index.html")
WIDGET = "file://" + WIDGET_PATH
BENCH = "file://" + os.path.join(ROOT, "benchmark", "bench.html")
EXAMPLE = os.path.join(ROOT, "benchmark", "beispiel-kontext.json")
OUT = os.environ.get("BDU_TEST_OUT") or tempfile.mkdtemp(prefix="bdu-tests-")


def _beep():
    """Kurzer, abspielbarer WAV-Ton als Ersatz für die Morse-Dateien."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"".join(struct.pack("<h", 3000 if (i // 8) % 2 else -3000) for i in range(800)))
    return buf.getvalue()


BEEP = _beep()


def make_export(path, api_key=None, entries=100, last_summary_index=96, with_chat_fields=False):
    """Export im Widget-Format mit erfundenem Verlauf (U-68). Ohne Chat-Felder = Export aus einer Version vor 1.2.0."""
    ex = json.load(open(EXAMPLE, encoding="utf-8"))
    st = ex["settings"]
    hist = []
    for i in range(entries // 2):
        hist.append({"role": "user", "text": f"Meldung {i}: U-68 meldet Position und Lage.", "timestamp": "2026-11-01T10:00:00.000Z"})
        hist.append({"role": "assistant", "text": f"**BdU an U-68:**\n\nAntwort {i}: Verstanden.", "timestamp": "2026-11-01T10:00:01.000Z"})
    settings = {k: st[k] for k in ("apiType", "customBaseUrl", "model", "cachingEnabled", "loopSound", "volume", "systemPrompt", "bootContext", "currentStatus")}
    if with_chat_fields:
        settings.update({k: st[k] for k in ("chatEnabled", "chatServerUrl", "chatPersonality")})
    if api_key:
        settings["apiKey"] = api_key
    data = {"format": "enigma-bdu-funk", "formatVersion": 1, "exportedAt": "2026-11-02T12:00:00.000Z", "promptVersion": "3.0",
            "settings": settings,
            "memory": {"history": hist, "summary": "Kaleu meldete frühere Feindfahrten. U-74 hatte sich zuletzt gemeldet.", "lastSummaryIndex": last_summary_index}}
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return path


EXPORT_NOKEY = make_export(os.path.join(OUT, "export-nokey.json"))
EXPORT_TEST = make_export(os.path.join(OUT, "export-test.json"), api_key="TESTKEY")


class Checks:
    def __init__(self):
        self.results = []

    def __call__(self, name, cond, info=""):
        self.results.append((name, bool(cond)))
        print(("PASS " if cond else "FAIL ") + name + ("" if cond or not info else "  " + str(info)[:300]))

    def finish(self):
        failed = [n for n, ok in self.results if not ok]
        print(f"\n{len(self.results) - len(failed)}/{len(self.results)} bestanden")
        raise SystemExit(1 if failed else 0)
