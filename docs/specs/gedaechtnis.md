# Gedächtnis (Verlauf und Zusammenfassung)

## Ziel
Der BdU bezieht frühere Funksprüche ein, ohne dass der Kontext unbegrenzt wächst.

## Verhalten
- Jede erfolgreich beantwortete Meldung wird zusammen mit der Antwort und Zeitstempel im Verlauf gespeichert (`localStorage`, höchstens 100 Einträge, älteste fallen weg; der Zusammenfassungsstand wandert dabei mit).
- An die API gehen alle noch nicht zusammengefassten Einträge im Volltext, mindestens die letzten 4, höchstens die letzten 10 (beide API-Typen). Jeder frühere Funkspruch steht genau einmal im Kontext.
- Sind seit der letzten Zusammenfassung mindestens 10 Einträge dazugekommen (seit 1.4.0, vorher 8; also alle 3 statt alle 2 Funksprüche, spart Anfragen pro Tag), werden alle bis auf die letzten 4 im Telegrammstil zusammengefasst (über das zweite Modell, falls eingetragen) (höchstens 3 Sätze) und an die bestehende Zusammenfassung angehängt. Die Zusammenfassung steht im Systemtext hinter Boot-Kontext und Status.
- **Spaßmeldungen** ohne Bezug zur laufenden Feindfahrt und die Antworten darauf kommen nicht in die Zusammenfassung (seit 1.4.0; Wortlaut und Beispiele vom Nutzer freigegeben, 08.11.2026). Bestehen die Funksprüche nur daraus, antwortet die KI „KEINE MELDUNG“: Es wird nichts angehängt, der Stand rückt trotzdem weiter. Der Verlauf selbst (Anzeige, Export, die letzten 4–6 Einträge im Volltext) bleibt unverändert.
- **Verdichten** (seit 1.4.0): Würde die Zusammenfassung mit dem nächsten Teil länger als 2.000 Zeichen (≈ 500 Tokens), gehen in derselben einen Anfrage die bisherige Zusammenfassung, die neuen Funksprüche und der Boot-Kontext (nur zur Einordnung, nicht wiederholen) an die KI. Die KI liefert eine Gesamtzusammenfassung mit Ziel 1.200 Zeichen (Budget 1.500 Tokens; 600 reichten im Nutzertest vom 08.11.2026 nicht): laufende Feindfahrt ausführlicher, frühere Fahrten und erledigte Episoden je höchstens ein Satz; erhalten bleiben Versenkungen und Erfolge, Schäden und Verluste, Befehle des BdU, Positionen und Ziele, wiederkehrende Personen. Sie ersetzt die bisherige Zusammenfassung. Bestehende lange Zusammenfassungen werden bei der nächsten fälligen Zusammenfassung automatisch verdichtet (Nutzertest 08.11.2026: 5.786 → 500 Zeichen).
- **Rückfall** (Nutzerentscheidung 08.11.2026): Ist das Ergebnis der Verdichtung unbrauchbar (abgeschnitten, leer, „KEINE MELDUNG“, nicht kürzer), fallen ohne weiteren Aufruf die ältesten Abschnitte der Zusammenfassung weg, bis höchstens 1.600 Zeichen übrig sind. Die Zusammenfassung kann so auch bei Fehlern nicht unbegrenzt wachsen. Bei API-Fehlern (Kontingent, Netz) wird nicht gekürzt.
- Anzeige „Letzte Zusammenfassung“ in den Einstellungen: Zeitpunkt, Art (angehängt, verdichtet, nichts angehängt, gekürzt), Modell (seit 1.4.1), Länge und Zahl der noch nicht zusammengefassten Funksprüche (Meldung und Antwort zählen zusammen als einer). Die Zusammenfassung läuft erst nach der Antwort im Hintergrund; sie selbst erscheint nicht im Display.
- Scheitert die Zusammenfassung oder Verdichtung (Fehler, leer, abgeschnitten, beim Verdichten auch „KEINE MELDUNG“ oder ein Ergebnis, das nicht kürzer ist als die bisherige Zusammenfassung), bleibt die bisherige Zusammenfassung unverändert, und der nächste Versuch folgt nach 2 weiteren Funksprüchen; „ZUSAMMENFASSUNG FEHLGESCHLAGEN“ erscheint einmal je Fehlerserie.
- „LETZTEN FUNKSPRUCH LÖSCHEN“ entfernt die letzte Meldung samt Antwort (seit 1.3.2; vorher „LETZTE 5 LÖSCHEN“ mit fünf Einträgen, BUGS B19). Unbeantwortete Meldungen am Verlaufsende fallen mit weg, der Verlauf endet danach immer mit einer Antwort; „HISTORY LÖSCHEN“ leert Verlauf und Zusammenfassung.

## Nicht-Ziele
Zusammenfassung oder Verlauf per KI-Knopf ausmisten, Button „älteste Hälfte löschen“ (beides verworfen, Nutzer 08.11.2026); serverseitige Speicherung (siehe `docs/OFFEN.md`).

## Akzeptanzkriterien
- Nach acht neuen Einträgen noch keine Zusammenfassung, nach zehn eine (längere), Konsole meldet „[SUMMARY] ✅“.
- Ist die Zusammenfassung so lang, dass sie mit dem nächsten Teil 2.000 Zeichen überschritte, ersetzt eine Gesamtzusammenfassung sie, mit genau einer Anfrage; scheitert das, bleibt die alte unverändert.
- Zusammenfassungs- und Verdichtungsanfrage enthalten die Regel zu Spaßmeldungen mit den Beispielen des Nutzers.
- Unbrauchbare Verdichtung: Zusammenfassung danach höchstens 1.600 Zeichen, neueste Abschnitte erhalten; der nächste Versuch hängt normal an.
- Nach Neuladen sind Verlauf und Zusammenfassung vorhanden.
- Über 10 Meldungen fehlt in keiner Anfrage ein früherer Funkspruch, und keiner steht doppelt drin.
- Dauerhaft scheiternde Zusammenfassung: höchstens ein Versuch je 2 Funksprüche, eine Meldung im Display.
- Nach „LETZTEN FUNKSPRUCH LÖSCHEN“ wechseln sich in der nächsten Anfrage Kaleu und BdU ab (keine zwei Meldungen hintereinander).
- Nach „HISTORY LÖSCHEN“ zeigt das Display die Begrüßung, die Zusammenfassung ist leer.

## Berührte Dateien/Funktionen
`index.html`: `addToHistory`, `trimHistory`, `getContextHistory`, `summarizeHistory`, `requestSummary`, `trimSummaryBlocks`, `saveSummaryMeta`, `updateHistoryDisplay`, `clearHistory`, `clearLastExchange`, `restoreChatLog`.

## Status
umgesetzt (1.0.0), Fehlerbehebungen in 1.0.1, 1.0.2 und 1.3.2, Verdichten und Spaß-Regel in 1.4.0 (`tests/summary_condense.py`, nur mit simulierter API; Qualität der echten Verdichtung prüft der Nutzer); offene Schwächen in `docs/OFFEN.md`.
