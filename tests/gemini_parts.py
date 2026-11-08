"""1.2.2: mehrteilige Gemini-Antworten, Denk-Teile, Download-Name."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ROOT, WIDGET, BENCH, EXAMPLE, BEEP, OUT, EXPORT_NOKEY, EXPORT_TEST
import json, sys
from playwright.sync_api import sync_playwright
W=WIDGET
ok=[]
def check(n,c,i=""): ok.append(c); print(("PASS " if c else "FAIL ")+n+("" if c else "  "+str(i)))
resp={"parts":[{"text":"Rückmarsch wird"},{"text":" genehmigt. Kurs Lorient."}],"fin":"STOP"}
def h(route):
    u=route.request.url
    if u.startswith("file://"): return route.continue_()
    if u.endswith(".wav") or "/raw/" in u: return route.fulfill(status=200,content_type="audio/wav",body=BEEP)
    if ":generateContent" in u:
        return route.fulfill(status=200,content_type="application/json",body=json.dumps({"candidates":[{"content":{"parts":resp["parts"]},"finishReason":resp["fin"]}]}))
    return route.fulfill(status=404,body="")
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(accept_downloads=True); pg=c.new_page(); pg.route("**/*",h)
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); dl=[]; pg.on("download",lambda d: dl.append(d.suggested_filename))
    pg.goto(W); pg.wait_for_timeout(300)
    pg.evaluate("localStorage.setItem('bdu_api_key','K')"); pg.reload(); pg.wait_for_timeout(300)
    t=pg.evaluate("callApi('Test')")
    check("Zwei Text-Teile werden zusammengesetzt", t=="Rückmarsch wird genehmigt. Kurs Lorient.", t)
    resp["parts"]=[{"text":"Ich überlege...","thought":True},{"text":"Verstanden."},{"thoughtSignature":"abc"}]
    t=pg.evaluate("callApi('Test')")
    check("Denk-Teil und Teil ohne Text werden ignoriert", t=="Verstanden.", t)
    resp["parts"]=[{"text":"Angriff,"},{"text":" ran"}]; resp["fin"]="MAX_TOKENS"
    t=pg.evaluate("callApi('Test')")
    check("MAX_TOKENS: alle Teile + ...", t=="Angriff, ran...", t)
    resp["parts"]=[{"text":"Funkspruch aus"},{"text":" dem Chat beantwortet."}]; resp["fin"]="STOP"
    t=pg.evaluate("callApi('Hallo', {chat: true})")
    check("Chat-Antwort ebenfalls vollständig", t.endswith("dem Chat beantwortet."), t)
    resp["parts"]=[{"thoughtSignature":"x"}]
    e=pg.evaluate("callApi('Test').then(()=>'ok', e=>e.message)")
    check("Nur Teile ohne Text: Fehler „leerer Text“", "leeren Text" in e, e)
    pg.evaluate("toggleSettings()"); pg.evaluate("downloadExport()"); pg.wait_for_timeout(500)
    check("Download heißt Funk-Export.json", dl==["Funk-Export.json"], dl)
    st=pg.inner_text("#transfer-status")
    check("Hinweis: Download-Ordner, Rückfall Texteditor", "Download-Ordner" in st and "Texteditor" in st, st)
    c2=b.new_context(accept_downloads=True); p2=c2.new_page(); p2.route("**/*",h); p2.add_init_script("window.obsstudio={pluginVersion:'x'}")
    d2=[]; p2.on("download",lambda d: d2.append(d.suggested_filename)); p2.goto(W); p2.wait_for_timeout(300); p2.evaluate("toggleSettings(); downloadExport()"); p2.wait_for_timeout(500)
    check("Mit window.obsstudio wird trotzdem heruntergeladen", d2==["Funk-Export.json"], d2)
    check("Keine JS-Fehler", not errs, errs)
    b.close()
sys.exit(0 if all(ok) else 1)
