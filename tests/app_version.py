"""1.5.0: Programmversion APP_VERSION gleich der neuesten Version im CHANGELOG, im Export und in der Konsole."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BEEP, Checks
from playwright.sync_api import sync_playwright

check = Checks()
changelog = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
newest = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M).group(1)
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
m = re.search(r'const APP_VERSION = "([^"]+)";', src)
check("APP_VERSION vorhanden", m is not None)
check(f"APP_VERSION = neueste Version im CHANGELOG ({newest})", m and m.group(1) == newest, m and m.group(1))
check("WIDGET_VERSION (Prompt-Version) unverändert getrennt", 'const WIDGET_VERSION = "3.0";' in src)


def handle(route):
    u = route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200, content_type="audio/wav", body=BEEP)
    return route.fulfill(status=404, body="")


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route("**/*", handle)
    logs = []; pg.on("console", lambda msg: logs.append(msg.text))
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(WIDGET); pg.wait_for_timeout(300)
    check("Konsole nennt die Version beim Start", any(f"Enigma-BdU-Funk {newest}" in l for l in logs), [l for l in logs if "INIT" in l][:2])
    exp = pg.evaluate("buildExportData()")
    check("Export enthält appVersion und promptVersion", exp.get("appVersion") == newest and exp.get("promptVersion") == "3.0", (exp.get("appVersion"), exp.get("promptVersion")))
    d = pg.evaluate("raw => parseImportData(raw)", json.dumps(exp))
    check("Import eines Exports mit appVersion klappt", d is not None and isinstance(d.get("history"), list))
    check("Keine JS-Fehler", not errs, errs)
    b.close()
check.finish()
