# BdU-Benchmark

Werkzeug zum Vergleich der Antwortqualität verschiedener Gemini-Modelle mit demselben Kontext. Gehört nicht zum Widget; `index.html` wird davon nicht berührt. Hintergrund und Regeln: [`docs/specs/benchmark.md`](../docs/specs/benchmark.md).

## Ablauf
1. `bench.html` herunterladen und im Browser öffnen (Doppelklick genügt, kein Server nötig).
2. Im Widget einen Export als Datei erstellen (Zahnrad → „Sichern & Übertragen“, ohne Schlüssel) und in der Benchmark-Seite unter „Kontext“ laden. Ein Schlüssel im Export wird verworfen.
3. Gemini-API-Schlüssel eingeben und „Modelle laden“. Er bleibt nur im Arbeitsspeicher der Seite.
4. Testfragen prüfen und bei Bedarf anpassen (10 Standardfragen: 6 Kaleu-Meldungen, 4 Chat-Funksprüche).
5. Modelle auswählen (Standard: `gemini-3.5-flash-lite` und `gemini-2.5-flash-lite`), „Start“. Pro Modell 10 Fragen × 2 Läufe = 20 Aufrufe; mit 7 s Pause dauert das bei zwei Modellen rund 5–10 Minuten.
6. Unter „Blind bewerten“ jede Antwort bewerten: Punkte 1–5, Mängel, „im Stream so zeigen“.
7. „Auflösen“ zeigt die Auswertung mit Modellnamen. „Ergebnisse exportieren“ speichert alles als JSON (ohne Schlüssel) zur gemeinsamen Auswertung.

## Hinweise
- **Kontingent:** Flash-Lite-Modelle haben im Gratis-Kontingent etwa 10 Anfragen pro Minute; größere Flash-Modelle nur wenige Anfragen pro Tag. Meldet die API das Tageslimit, wird das Modell übersprungen. Ein späterer Start holt nur die fehlenden Antworten nach.
- **Gleiche Anfrage wie im Widget:** Systemtext, Verlauf, Chat-Regeln und Einstellungen entsprechen `callGemini()` ohne Cache. Das Widget nutzt bei 2.5-Modellen zusätzlich den Cache; der Inhalt der Anfrage ist bis auf die Stelle der Chat-Regeln derselbe.
- **Speicher:** Ergebnisse und Bewertungen liegen im `localStorage` des Browsers (Schlüssel `bdu_bench_state_v1`). Bei Öffnen per `file://` teilt Chromium diesen Speicher mit dem Widget; die Schlüssel kommen sich nicht in die Quere. Zur Sicherheit regelmäßig exportieren.
- **Verlauf:** Jede Frage wird unabhängig gegen den eingefrorenen Kontext gestellt; Antworten kommen nicht in den Verlauf.
