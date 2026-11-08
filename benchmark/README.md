# BdU-Benchmark

Werkzeug, um herauszufinden, welches KI-Modell für den BdU am besten klingt.
Erster Vergleich (November 2026, eigener Funkverlauf, blind bewertet): `gemini-2.5-flash-lite` 4,1 von 5 Punkten, `gemini-3.5-flash-lite` 2,75. Google bietet 2.5 aber nur noch bisherigen Nutzern an. Es stellt mehreren Modellen dieselben Testfragen mit demselben Kontext und lässt dich die Antworten blind bewerten. Gehört nicht zum Widget; `index.html` wird davon nicht berührt. Hintergrund und Regeln: [`docs/specs/benchmark.md`](../docs/specs/benchmark.md).

## Was du brauchst
- `bench.html` aus diesem Ordner, im Browser geöffnet (Doppelklick genügt, kein Server nötig).
- Mindestens einen API-Schlüssel (Stand November 2026):
  - **Gemini:** [Google AI Studio](https://aistudio.google.com), kostenlos (das Widget ist dafür gebaut; „alle Gemini-Modelle zeigen“ zeigt auch Googles offene Gemma-Modelle)
  - **Groq:** [console.groq.com](https://console.groq.com), kostenloses Kontingent (offene Modelle, sehr schnell)
  - **OpenRouter:** [openrouter.ai](https://openrouter.ai), ein Schlüssel für viele Anbieter; kostenlos sind nur Modelle mit „:free“ (ohne Guthaben 50 Anfragen pro Tag), der Benchmark zeigt nur diese
  - **Mistral:** [console.mistral.ai](https://console.mistral.ai), seit Oktober 2026 nur noch kostenpflichtig
  - **Eigene Adresse:** jede andere OpenAI-kompatible API mit Base-URL und (falls nötig) Schlüssel, genau wie im Universal-Modus des Widgets – auch ein **lokales Modell** (z. B. Ollama `http://localhost:11434`, LM Studio `http://localhost:1234`), kostenlos und ohne Kontingent, solange der PC genug Speicher hat
- Einen Kontext: deinen eigenen Export aus dem Widget (Zahnrad → „Sichern & Übertragen“ → „ALS DATEI“, ohne Schlüssel) **oder** den Beispielkontext `beispiel-kontext.json`, falls du das Widget noch nicht benutzt hast.

## Ablauf
1. Schlüssel eintragen und „Modelle laden“. Die Modelle deiner Schlüssel erscheinen zum Ankreuzen (bei Gemini zuerst nur Flash-Lite; „alle Gemini-Modelle zeigen“ zeigt den Rest). Fehlende Modelle lassen sich mit Anbieter von Hand ergänzen.
2. Kontext laden (Datei oder eingefügter Text). Ein Schlüssel im Export wird verworfen.
3. Testfragen prüfen: 6 Meldungen des Kaleu, 4 Funksprüche aus dem Chat. Sie passen zum Beispielkontext (U-68, 1941 vor Westafrika); für dein eigenes Boot die Fragen in der Seite anpassen.
4. „Start“. Pro Modell 10 Fragen × 2 Läufe = 20 Aufrufe. Mit 7 s Pause dauert das bei zwei Modellen rund 5–10 Minuten. Nicht vorhandene Modelle und erschöpfte Tageskontingente werden übersprungen; ein späterer Start holt nur Fehlendes nach.
5. „Blind bewerten“: Punkte 1–5, Mängel ankreuzen, „im Stream so zeigen“.
6. „Auflösen“ zeigt die Auswertung mit Modellnamen. „Ergebnisse exportieren“ speichert alles als JSON (ohne Schlüssel).

## Hinweise
- **Gleiche Anfrage wie im Widget:** Gemini wie im Widget, alle anderen wie im Universal-Modus. Was im Benchmark gut klingt, klingt im Widget genauso. Base-URLs für den Universal-Modus: Groq `https://api.groq.com/openai`, OpenRouter `https://openrouter.ai/api`, Mistral `https://api.mistral.ai`.
- **Browser-Aufrufe:** Ob Groq, OpenRouter und Mistral Aufrufe direkt aus einer lokal geöffneten Seite zulassen, ist noch nicht erprobt. Meldet der Benchmark eine blockierte Anfrage (CORS), funktioniert der Anbieter auch im Widget nicht direkt.
- **Kontingente:** Flash-Lite-Modelle erlauben im Gratis-Kontingent etwa 10 Anfragen pro Minute; größere Modelle teils nur wenige pro Tag. Kostenlose Modelle sind generell stärker eingeschränkt und lieferten im ersten Vergleich schwächere Ergebnisse; größere, kostenpflichtige Modelle wurden nicht verglichen.
- **Lokale Modelle:** Blockiert der Browser die Anfrage, in Ollama `OLLAMA_ORIGINS=*` setzen bzw. in LM Studio CORS einschalten.
- **Speicher:** Ergebnisse und Bewertungen liegen im Browser (`localStorage`, Schlüssel `bdu_bench_state_v1`); regelmäßig exportieren.
- **Verlauf:** Jede Frage wird unabhängig gegen den eingefrorenen Kontext gestellt; Antworten kommen nicht in den Verlauf.

# Spaßfilter-Test

`spassfilter.html` prüft einmalig mit echter API, ob das Gedächtnis des BdU ernste Meldungen behält und Spaßmeldungen (Spargel, Bier, Rammen …) weglässt. Hintergrund: [`docs/specs/benchmark.md`](../docs/specs/benchmark.md), Abschnitt „Spaßfilter-Test“.

1. `spassfilter.html` im Browser öffnen (Doppelklick).
2. Gemini-Schlüssel eintragen (wird nicht gespeichert), Modell prüfen (Standard `gemini-2.5-flash-lite`), Läufe (2) und Pause (5 s) lassen.
3. „Start“. Je Lauf 5 Aufrufe, insgesamt etwa 1 Minute. Die Aufrufe zählen gegen dein Tageskontingent bei Google wie die des Widgets; am besten nicht direkt vor einem Stream.
4. Auswertung lesen: „Fakten behalten“ und „Spaß entfernt“ sollten bei allen Läufen voll sein; „Grenzfälle behalten“ zeigt, ob Humor mit Bezug zur Fahrt erhalten bleibt. Darunter stehen alle Zusammenfassungen im Wortlaut.
5. „Ergebnisse exportieren“ speichert eine JSON-Datei (ohne Schlüssel) im Download-Ordner.
