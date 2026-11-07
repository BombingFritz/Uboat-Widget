# Benchmark: Antwortqualität verschiedener Modelle vergleichen

## Ziel
Feststellen, welches kostenlose Modell die besten BdU-Antworten liefert und ob Schwächen am Modell oder am Kontext (Prompt, Boot-Kontext, Status, Verlauf, Zusammenfassung) liegen. Grundlage für die Wahl des Standardmodells und für Änderungen am Kontext. Anlass: Eindruck des Nutzers, dass die Antworten mit `gemini-2.5-flash-lite` besser waren als mit `gemini-3.5-flash-lite` (02.11.2026).

Entscheidungen des Nutzers (07.11.2026): zuerst nur Gemini (Flash-Lite-Varianten), danach Kontext schärfen, danach Mistral und Groq über den Universal-Modus. Nach dem ersten Durchlauf: Groq und Mistral öffnen, Benchmark mit Beispielkontext in ein künftiges Release aufnehmen, in der Doku erwähnen, eigener Unterordner. Kein Claude (API kostet extra, nicht im Pro-Abo enthalten). Kein Ollama (Grafikspeicher wird vom Spiel gebraucht).

## Verhalten
Eigene Seite `benchmark/bench.html` (eigener Ordner, damit sie nicht mit dem Widget verwechselt wird), lokal im Browser geöffnet. Gehört nicht zum Widget; `index.html` bleibt unverändert.

0. **Anbieter:** Gemini (wie im Widget); Groq (`https://api.groq.com/openai`), OpenRouter (`https://openrouter.ai/api`, Liste nur Modelle mit `:free`), Mistral (`https://api.mistral.ai`, seit Oktober 2026 kostenpflichtig) und **eigene Adresse** (Base-URL wie im Universal-Modus, normalisiert wie `normalizeBaseUrl`; Schlüssel optional, ohne Schlüssel kein `Authorization`-Header) über die OpenAI-kompatible Schnittstelle wie `callUniversal`. Je Anbieter ein Schlüsselfeld; Schlüssel nur im Arbeitsspeicher. Modell-IDs: Gemini ohne Präfix (wie im ersten Durchlauf), sonst `<anbieter>:<Modell>` (`groq`, `openrouter`, `mistral`, `custom`); bei eigener Adresse wird die Adresse im Ergebnis gespeichert. Ob Groq, OpenRouter und Mistral Aufrufe direkt aus dem Browser zulassen (CORS), ist [UNGEKLÄRT] (Nutzer konnte Groq am 07.11.2026 nicht anmelden; Mistral ohne Gratis-Schlüssel); blockierte Anfragen nennen CORS als wahrscheinliche Ursache.

1. **Kontext:** ein oder mehrere Exporte des Widgets (`enigma-bdu-funk`, Format 1) als Datei laden oder als Text einfügen. Wer noch keinen eigenen Verlauf hat, nimmt `benchmark/beispiel-kontext.json` (Standard-Persönlichkeit und -Chat-Persönlichkeit des Widgets, erfundenes Beispielboot U-68/Typ IXc/Oktober 1941 vor Westafrika, 10 erfundene Verlaufseinträge, Zusammenfassung mit U-74 für die Gedächtnisfrage; auch im Widget importierbar). Jeder Export ist ein eingefrorener Kontext. Mehrere Exporte = Gegenversuch mit verändertem Kontext (z. B. neu geschriebene Zusammenfassung). Ein API-Schlüssel im Export wird verworfen, nie gespeichert.
2. **Testfragen:** 10 Standardfragen (6 Kaleu-Meldungen, 4 Chat-Funksprüche), in der Seite bearbeitbar. Jede Frage wird unabhängig gegen den eingefrorenen Kontext gestellt; der Verlauf wächst nicht mit.
3. **Modelle:** Listen der Anbieter zum Ankreuzen (Gemini: Filter „flash-lite“, abschaltbar; Groq/Mistral: ohne Audio-, Embedding-, OCR- und Prüfmodelle), eigene Namen mit Anbieter ergänzbar. Meldet die API ein Modell als nicht vorhanden (HTTP 404, „no longer available“, „does not exist“ u. a.), wird es nach dem ersten Versuch für den Durchlauf übersprungen (Lauf 1: `gemini-2.0-flash-lite` lieferte 20 Fehler).
4. **Durchlauf:** Kontext × Frage × Modell × Wiederholungen (Standard 2). Pause zwischen Aufrufen (Standard 7 s, wegen etwa 10 Anfragen/Minute im Gratis-Kontingent). Bei HTTP 429 eine Minute warten und bis zu zweimal neu versuchen; meldet die API das Tageslimit, wird das Modell für diesen Durchlauf übersprungen. Erfolgreiche Ergebnisse bleiben erhalten; ein neuer Start holt nur Fehlendes nach (z. B. am nächsten Tag).
5. **Anfrage wie im Widget:** Systemtext, Verlauf (`getContextHistory`), Chat-Regeln, Chat-Persönlichkeit, `safetySettings`, `temperature` 1.0, `maxOutputTokens` 450 bzw. 200 (Chat) genau wie `callGemini` ohne Cache; bei Groq/Mistral genau wie `callUniversal` (`max_tokens`, `temperature` 1.0, Rollen `system`/`user`/`assistant`). Gemini-Antworten aus allen Text-Teilen ohne Denk-Teile wie im Widget seit 1.2.2 (BUGS B21); die Zahl der Text-Teile wird mitgeschrieben. „Status:“-Meldungen ersetzen vorher den Status wie in `sendMessage`. Chat-Antworten werden wie im Widget bereinigt (`cleanChatAnswer`). Abweichung: Das Widget nutzt bei 2.5-Modellen den expliziten Cache; dort stehen Chat-Regeln vor der Meldung statt im Systemtext. Der Benchmark nutzt für alle Modelle den Weg ohne Cache, damit alle denselben Text bekommen.
6. **Messwerte je Antwort:** Text, `finishReason`, Dauer, Tokens (Prompt, Antwort, Denken), Fehler.
7. **Blind bewerten:** je Frage alle Antworten in zufälliger, fester Reihenfolge, nur mit Buchstaben. Je Antwort: Punkte 1–5, Mängel zum Ankreuzen, „im Stream so zeigen“ ja/nein, Notiz. (Statt Rangfolge, weil bei 4 Modellen × 2 Läufen 8 Antworten je Frage zu viele zum Ordnen sind.)
8. **Automatische Prüfungen:** Länge, abgeschnitten (`MAX_TOKENS` bzw. `length`), mehrere Text-Teile, Chat über 400 Zeichen, Chat-Formatfehler vor der Bereinigung (Zeilenumbruch, Sternchen, Kopfzeile „BdU an …“), Floskel (Chat-Antwort mit höchstens 3 Wörtern), „Heil“.
9. **Auswertung:** erst nach „Auflösen“ mit Modellnamen. Je Kontext und Modell: Ø Punkte (Kaleu/Chat), Anteil stream-tauglich, Mängel, automatische Befunde, Ø Länge, Dauer und Tokens, Fehler; dazu Punkte je Frage und Modell und der Unterschied zwischen den Wiederholungen.
10. **Speichern:** Stand (ohne Schlüssel) im `localStorage` der Seite; Export/Import als JSON zur Weitergabe an die Auswertung.

## Diagnose (Auswertung durch den Assistenten)
| Muster | Wahrscheinliche Ursache |
|---|---|
| Alle Modelle zeigen denselben Mangel | Kontext/Prompt |
| Nur ein Modell zeigt ihn | Modell |
| Mangel nur bei Fragen mit Verlaufsbezug | Verlauf/Zusammenfassung |
| Große Unterschiede zwischen den Wiederholungen | Zufall/Temperatur |

Verdacht auf den Kontext wird mit einem zweiten Export (veränderter Kontext) gegengeprüft.

Vorbefund aus dem Export des Nutzers (02.11.2026): Die Zusammenfassung beschreibt nur die Fahrten von U-4; von U-38 und U-68 steht nichts darin, obwohl `lastSummaryIndex` 96 von 100 Einträgen als zusammengefasst markiert. Die KI kennt von der laufenden Feindfahrt also nur Boot-Kontext, Status und die letzten 4 Einträge (Folge von B10 in der alten Fassung).

## Ergebnisse
Lauf 1 (Gemini, 07.11.2026) und Diagnose: `docs/OFFEN.md`, Abschnitt „Benchmark und Modellwahl“.

## Nicht-Ziele
Claude, Ollama und andere kostenpflichtige oder lokale Anbieter (Nutzerentscheidung); Änderungen am Widget; automatische Bewertung des Tons durch eine KI.

## Akzeptanzkriterien
- Für denselben Export, dasselbe Modell und dieselbe Meldung ist der Request-Body des Benchmarks gleich dem des Widgets (Kaleu-Meldung, „Status:“-Meldung, Chat-Funkspruch), bei Gemini und im Universal-Modus (Groq- bzw. Mistral-Adresse).
- Ohne „Auflösen“ ist in der Bewertung kein Modellname zu sehen.
- Abbruch und Neustart wiederholen keine erfolgreichen Aufrufe.
- Der API-Schlüssel steht weder im `localStorage` noch im Export.

## Berührte Dateien
`benchmark/bench.html`, `benchmark/README.md`, `benchmark/beispiel-kontext.json` (neu). `index.html` unverändert.

## Status
umgesetzt (Werkzeug, Gemini/Groq/OpenRouter/Mistral/eigene Adresse), Teil von 1.3.0. Tests in `tests/benchmark_gemini.py` und `tests/benchmark_providers.py`. Headless-Test der OpenAI-kompatiblen Anbieter mit simulierten APIs (52/52, dazu OpenRouter-Filter und eigene Adresse ohne Schlüssel): Request identisch zu `callUniversal` für alle Standardfragen, Modelllisten, Schlüssel je Anbieter, Überspringen nicht vorhandener Modelle, mehrteilige Gemini-Antworten, Beispielkontext in Benchmark und Widget. Headless-Test Gemini mit simulierter API (50/50): Request-Body für alle 10 Standardfragen identisch zum Widget (Export importiert, `sendMessage` bzw. Chat-Warteschlange), 429-Wiederholung, Tageslimit, Fortsetzen, Blindbewertung, Auflösen, Export ohne Schlüssel, Handybreite. Erster echter Durchlauf (Gemini) durch den Nutzer am 07.11.2026; Groq und Mistral mit echter API noch nicht erprobt.
