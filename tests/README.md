# Tests

Headless-Tests für Widget und Benchmark. Sie laufen in Chromium (Playwright) gegen **simulierte** APIs: keine echten KI-Aufrufe, kein Schlüssel nötig, kein privater Funkverlauf (Testdaten werden aus `benchmark/beispiel-kontext.json` erzeugt).

## Einrichten (einmalig)
```
pip install playwright
python -m playwright install chromium
```
Ist Chromium schon vorinstalliert (z. B. in Claude Code in der Cloud: Playwright 1.63.0), stattdessen die passende Paketversion installieren (`pip install playwright==1.63.0`) und `playwright install` weglassen.

## Ausführen
Im Hauptordner des Repositorys:
```
python tests/run_all.py
```
Ergebnis: „ALLE TESTS BESTANDEN“ oder die Liste der fehlgeschlagenen Tests mit den einzelnen `FAIL`-Zeilen. Screenshots und Testdaten landen in einem temporären Ordner (wird am Ende genannt) bzw. in `BDU_TEST_OUT`, falls gesetzt.

Einzelne Tests: `python tests/<name>.py`.

| Test | Prüft |
|---|---|
| `widget_regression.py` | Senden/Empfangen mit Ton, Verlauf, Status-Meldungen, Gemini mit und ohne Cache, Universal-Modus, Reset |
| `export_import.py` | Export/Import zwischen zwei Herkünften (zwei lokale Server auf Port 8701/8702), Update von älterer Version, Prompt-Sicherung, Download `Funk-Export.json` |
| `obs_dialogs.py` | Alles ohne Browser-Dialoge wie in OBS: Import, Reset, Verlauf löschen, Hinweise (BUGS B20) |
| `gemini_parts.py` | Gemini-Antworten aus mehreren Teilen, Denk-Teile, Download-Name (BUGS B21) |
| `chat_section.py` | Chat-Modus-Bereich ein- und ausklappen |
| `history_pairs.py` | „LETZTEN FUNKSPRUCH LÖSCHEN“ entfernt Meldung und Antwort als Paar (BUGS B19) |
| `benchmark_gemini.py` | Benchmark: Anfrage identisch zum Widget (Gemini), Kontingent, Fortsetzen, Blindbewertung, Export |
| `benchmark_providers.py` | Benchmark: Groq, OpenRouter, Mistral, eigene Adresse; Anfrage identisch zu `callUniversal` |

Nicht enthalten: der Ende-zu-Ende-Test mit dem Companion-Server (braucht dessen Repository; Server-Tests liegen dort in `test/`).

Neue Funktionen bekommen einen eigenen Test hier und einen Eintrag in `run_all.py`.
