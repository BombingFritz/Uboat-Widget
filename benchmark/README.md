# BdU-Benchmark

Werkzeug, um herauszufinden, welches KI-Modell für den BdU am besten klingt. Es stellt mehreren Modellen dieselben Testfragen mit demselben Kontext und lässt dich die Antworten blind bewerten. Gehört nicht zum Widget; `index.html` wird davon nicht berührt. Hintergrund und Regeln: [`docs/specs/benchmark.md`](../docs/specs/benchmark.md).

## Was du brauchst
- `bench.html` aus diesem Ordner, im Browser geöffnet (Doppelklick genügt, kein Server nötig).
- Mindestens einen kostenlosen API-Schlüssel:
  - **Gemini:** [Google AI Studio](https://aistudio.google.com) (das Widget ist dafür gebaut)
  - **Groq:** [console.groq.com](https://console.groq.com) (offene Modelle, sehr schnell)
  - **Mistral:** [console.mistral.ai](https://console.mistral.ai), Gratis-Tarif „Experiment“ (Eingaben können dort zum Training genutzt werden)
- Einen Kontext: deinen eigenen Export aus dem Widget (Zahnrad → „Sichern & Übertragen“ → „ALS DATEI“, ohne Schlüssel) **oder** den Beispielkontext `beispiel-kontext.json`, falls du das Widget noch nicht benutzt hast.

## Ablauf
1. Schlüssel eintragen und „Modelle laden“. Die Modelle deiner Schlüssel erscheinen zum Ankreuzen (bei Gemini zuerst nur Flash-Lite; „alle Gemini-Modelle zeigen“ zeigt den Rest). Fehlende Modelle lassen sich mit Anbieter von Hand ergänzen.
2. Kontext laden (Datei oder eingefügter Text). Ein Schlüssel im Export wird verworfen.
3. Testfragen prüfen: 6 Meldungen des Kaleu, 4 Funksprüche aus dem Chat. Sie passen zum Beispielkontext (U-68, 1941 vor Westafrika); für dein eigenes Boot die Fragen in der Seite anpassen.
4. „Start“. Pro Modell 10 Fragen × 2 Läufe = 20 Aufrufe. Mit 7 s Pause dauert das bei zwei Modellen rund 5–10 Minuten. Nicht vorhandene Modelle und erschöpfte Tageskontingente werden übersprungen; ein späterer Start holt nur Fehlendes nach.
5. „Blind bewerten“: Punkte 1–5, Mängel ankreuzen, „im Stream so zeigen“.
6. „Auflösen“ zeigt die Auswertung mit Modellnamen. „Ergebnisse exportieren“ speichert alles als JSON (ohne Schlüssel).

## Hinweise
- **Gleiche Anfrage wie im Widget:** Gemini wie im Widget ohne Cache, Groq und Mistral wie im Universal-Modus. Was im Benchmark gut klingt, klingt im Widget genauso. Im Widget trägst du für Groq bzw. Mistral im Universal-Modus die Base-URL `https://api.groq.com/openai` bzw. `https://api.mistral.ai` ein.
- **Browser-Aufrufe:** Ob Groq und Mistral Aufrufe direkt aus einer lokal geöffneten Seite zulassen, ist noch nicht erprobt. Meldet der Benchmark eine blockierte Anfrage (CORS), funktioniert der Anbieter auch im Widget nicht direkt.
- **Kontingente:** Flash-Lite-Modelle erlauben im Gratis-Kontingent etwa 10 Anfragen pro Minute; größere Modelle teils nur wenige pro Tag.
- **Speicher:** Ergebnisse und Bewertungen liegen im Browser (`localStorage`, Schlüssel `bdu_bench_state_v1`); regelmäßig exportieren.
- **Verlauf:** Jede Frage wird unabhängig gegen den eingefrorenen Kontext gestellt; Antworten kommen nicht in den Verlauf.
