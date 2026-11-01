# Gedächtnis (Verlauf und Zusammenfassung)

## Ziel
Der BdU bezieht frühere Funksprüche ein, ohne dass der Kontext unbegrenzt wächst.

## Verhalten
- Jede Meldung und Antwort wird mit Zeitstempel im Verlauf gespeichert (`localStorage`, höchstens 100 Einträge, älteste fallen weg).
- An die API gehen die letzten 4 (Gemini) bzw. 10 (Universal) Einträge im Volltext.
- Sind seit der letzten Zusammenfassung mindestens 8 Einträge dazugekommen, werden alle bis auf die letzten 4 im Telegrammstil zusammengefasst (höchstens 3 Sätze) und an die bestehende Zusammenfassung angehängt. Die Zusammenfassung steht im Systemtext.
- „LETZTE 5 LÖSCHEN“ entfernt die letzten fünf Einträge aus dem Verlauf; „HISTORY LÖSCHEN“ leert Verlauf und Zusammenfassung und invalidiert den Cache.

## Nicht-Ziele
Zusammenfassung der Zusammenfassung; serverseitige Speicherung (siehe `docs/OFFEN.md`).

## Akzeptanzkriterien
- Nach acht neuen Einträgen gibt es eine (längere) Zusammenfassung, Konsole meldet „[SUMMARY] ✅“.
- Nach Neuladen sind Verlauf und Zusammenfassung vorhanden.
- Nach „HISTORY LÖSCHEN“ zeigt das Display die Begrüßung, die Zusammenfassung ist leer.

## Berührte Dateien/Funktionen
`index.html`: `addToHistory`, `summarizeHistory`, `updateHistoryDisplay`, `clearHistory`, `clearLastFive`, `restoreChatLog`.

## Status
umgesetzt (1.0.0); bekannte Schwächen in `docs/BUGS.md` und `docs/OFFEN.md`.
