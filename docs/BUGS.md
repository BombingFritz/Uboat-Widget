# Bugs und historische Probleme

## Offen

| Nr. | Symptom | Ursache | Vorschlag | Priorität |
|---|---|---|---|---|
| B8 | Eigene Prompt-Anpassungen gehen nach einem Update ohne Rückfrage verloren | `WIDGET_VERSION`-Abgleich in `loadSettings` ersetzt den gespeicherten Prompt | Siehe `docs/OFFEN.md`, Punkt „Prompt-Version“; Entscheidung des Nutzers offen | P2 |
| B14 | Gemini-Modus: Bei jeder zweiten Meldung kennt die KI einen früheren Funkspruch weder im Volltext noch aus der Zusammenfassung (Beispiel: Bei Meldung 4 fehlt Meldung 1, bei Meldung 6 fehlt Meldung 3, bei Meldung 8 fehlt Meldung 5) | Gesendet werden starr die letzten 4 Einträge. Die Zusammenfassung läuft erst, wenn 8 Einträge offen sind, und umfasst dann alle bis auf die letzten 4. Dazwischen stehen bis zu 6 offene Einträge, von denen nur 4 gesendet werden | Statt der letzten 4 alle Einträge ab `lastSummaryIndex` senden (mindestens die letzten 4, höchstens z. B. 10). Gilt auch für den Chat-Modus | P1 |
| B15 | Universal-Modus: Bereits zusammengefasste Funksprüche gehen zusätzlich im Volltext mit (doppelte Tokens, keine Lücke) | Starr die letzten 10 Einträge, unabhängig von `lastSummaryIndex` | Gleiche Regel wie B14 | P3 |
| B16 | Scheitert die Zusammenfassung (z. B. Kontingent), wird sie nach jeder Antwort erneut versucht (zusätzlicher Aufruf je Meldung, wachsende Eingabe), „ZUSAMMENFASSUNG FEHLGESCHLAGEN“ erscheint jedes Mal im Display, und ältere Funksprüche fehlen der KI ganz, bis ein Versuch gelingt | Kein Merker für Fehlschläge; Volltext bleibt bei 4 Einträgen | Nach Fehlschlag Pause (z. B. 5 Antworten oder 10 min), Meldung nur einmal; mit B14 bleiben offene Einträge im Volltext (mit Obergrenze) | P2 |
| B17 | Zusammenfassungen können ungenau oder abgeschnitten sein | `temperature` 0.95 (für Zusammenfassungen zu hoch), `maxOutputTokens` 150; `finishReason` wird nicht geprüft. Bei Modellen mit Denkphase kann diese das Budget aufbrauchen [UNGEKLÄRT für `gemini-3.5-flash-lite`] | `temperature` ca. 0.3, Budget ca. 300, bei `MAX_TOKENS` oder leerem Text als Fehlschlag behandeln | P2 |
| B18 | Bei Gemini 1.5/2.5 mit explizitem Caching wird der Cache etwa jede zweite Meldung neu erstellt; das Caching spart dann kaum etwas und alte Caches laufen kostenpflichtig bis zum TTL-Ende weiter | Die Zusammenfassung steht im gecachten Systemtext; jede neue Zusammenfassung invalidiert den Cache | Zusammenfassung aus dem gecachten Teil nehmen (z. B. als erster Eintrag in `contents`), dann bleibt der Cache bis zu einer Stunde gültig. Das Standardmodell `gemini-3.5-flash-lite` ist nicht betroffen | P3 |
| B19 | Nach „LETZTE 5 LÖSCHEN“ endet der Verlauf mit einer Meldung ohne Antwort; die nächste Anfrage enthält zwei Nutzer-Einträge hintereinander | Verlauf besteht seit 1.0.1 nur aus Paaren; 5 ist ungerade | Paarweise löschen (z. B. „LETZTE 2 FUNKSPRÜCHE“ = 4 Einträge). Ob Gemini zwei aufeinanderfolgende Nutzer-Einträge ablehnt, ist [UNGEKLÄRT] | P3 |

Nachweis B14–B16: Headless-Test mit simulierter API über 10 Meldungen (02.11.2026), Protokoll je Anfrage: Volltext-Einträge, Zusammenfassung, Index. Bereits zusammengefasste Funksprüche bleiben in der Zusammenfassung, auch wenn sie danach per „LETZTE 5 LÖSCHEN“ entfernt werden (erwartet, nicht korrigierbar ohne Neuberechnung).

## Behoben in 1.0.1
Nachweis: Laufzeittest im Headless-Chromium mit simulierter Gemini- und OpenAI-API (keine echten API-Aufrufe), 26/26 Prüfungen bestanden. Gegenprobe mit unveränderter 1.0.0: die Fehler B1–B3, B5, B7, B9–B13 wurden dort reproduziert. Vom Nutzer getestet, funktioniert (02.11.2026); im Stream noch nicht erprobt.

| Nr. | Symptom | Ursache | Fix |
|---|---|---|---|
| B1 | Fehlermeldungen wie „FUNKSTÖRUNG: …“, „KONFIGURATION GESPEICHERT.“ oder „ZUSAMMENFASSUNG FEHLGESCHLAGEN“ erschienen nur als leere Zeile | `appendLog` kannte nur `Kaleu` und `System`; `Funkmaat` und `sys` landeten ohne Text im `else`-Zweig | `appendLog` behandelt `Funkmaat` und `sys` als Systemmeldung |
| B2 | Die neue Meldung ging doppelt an die API | Meldung stand vor dem Aufruf schon im Verlauf und wurde zusätzlich angehängt | Meldung und Antwort kommen erst nach erfolgreichem Aufruf in den Verlauf |
| B3 | Nach einem fehlgeschlagenen Aufruf blieb eine unbeantwortete Meldung im Verlauf | wie B2 | wie B2; die Meldung bleibt nur im Display sichtbar |
| B4 | KI-Antworten wurden beim Wiederherstellen nach dem Neuladen als HTML eingefügt (Markup aus der Antwort wurde ausgeführt) | `innerHTML` mit `msg.text` in `restoreChatLog`. Im Schreibmaschinen-Effekt wurde Markup durch das zeichenweise Einfügen faktisch maskiert (Gegenprobe), war aber fragil | Beide Wege schreiben nur noch Textknoten und `<br>` (`createBduMessageDiv`, `appendTextWithBreaks`); auch der Bootsname in der Kopfzeile |
| B5 | „RESET“ löschte das Modell nicht und setzte andere Werte als ein Erststart | Schlüssel `bdu_active_model` statt `bdu_current_model`; Boot-Kontext und Status leer, Loop aus, abweichende Modellnamen | Richtiger Schlüssel; Standardwerte `DEFAULT_MODEL`, `DEFAULT_LOOP_SOUND`, `DEFAULT_VOLUME`, `DEFAULT_CONTEXT`, `DEFAULT_STATUS` für Erststart und Reset; Modell-Badge wird aktualisiert |
| B7 | Standardmodell beim Erststart war `gemini-1.5-flash` | Fester Wert; Gemini 1.5 ist eingestellt, 2.5 laut Google nur noch für bisherige Nutzer | `DEFAULT_MODEL = "gemini-3.5-flash-lite"` (laut Google-Deprecation-Seite, Stand 22.10.2026, Empfehlung für neue Projekte) |
| B9 | Label „Browsercash“ | Tippfehler | „Browsercache“ |
| B10 | Zusammenfassungsstand passte nach „LETZTE 5 LÖSCHEN“ oder nach dem Kürzen auf 100 Einträge nicht mehr zum Verlauf (Nachrichten wurden übersprungen oder doppelt zusammengefasst) | `lastSummaryIndex` wurde beim Löschen und Kürzen nicht angepasst | `trimHistory` verschiebt den Index beim Kürzen mit; „LETZTE 5 LÖSCHEN“ begrenzt ihn auf die Verlaufslänge; Index wird gespeichert |
| B11 | Ließ sich der Sende-Ton nicht laden (z. B. offline oder GitHub nicht erreichbar), wurde gar nichts gesendet und das Statuslicht blinkte weiter | `await outgoingSound.play()` warf einen Fehler außerhalb des `try` in `sendMessage` | Ton-Fehler werden abgefangen und geloggt; der Funkspruch wird trotzdem gesendet |
| B12 | Universal-Modus mit dem empfohlenen Ollama-Wert `http://localhost:11434/v1` rief `…/v1/v1/chat/completions` auf | Hinweistext nannte `/v1`, der Code hängt `/v1` selbst an | `normalizeBaseUrl` entfernt abschließendes `/` und `/v1`; Hinweistext ohne `/v1` |
| B13 | Schlug die Cache-Erstellung fehl (z. B. Kontext zu kurz, kein Caching im kostenlosen Kontingent), kostete jede weitere Meldung einen zusätzlichen, erfolglosen API-Aufruf | Kein Merker für den Fehlschlag | `cacheCreationFailed`: kein neuer Versuch bis zum nächsten Speichern der Einstellungen, „RESET“ oder Neuladen |

**Korrektur zur Code-Durchsicht vom 02.11.2026:** Der dort als B6 geführte Befund („Modellsuche im Universal-Modus fragt Gemini ab“) war falsch. `fetchModels` fragt im Universal-Modus bereits `{base}/v1/models` ab. Gefunden wurde dabei stattdessen B12.

## Historisch (aus der Entwicklung, behoben)

| Symptom | Ursache | Fix | Regel zur Vermeidung |
|---|---|---|---|
| „Cached content is too small. total_token_count=832, min_total_token_count=2048“ | Systemtext unter dem Minimum für explizites Caching | Ausführlicher Prompt mit Chronologie; Fehler wird abgefangen, Anfrage läuft ohne Cache | Kontextlänge prüfen (Token-Schätzung in den Einstellungen) |
| Neuer Standard-Prompt erschien nicht im Einstellungsfeld | Alter Prompt im `localStorage` hatte Vorrang vor `DEFAULT_PROMPT` | `WIDGET_VERSION`-Abgleich (mit der Nebenwirkung B8) | Prompt-Updates über Versionierung, nicht über Defaults allein |
| Zusammenfassungs-Meldungen erschienen als Funkspruch im Display | `appendLog` in `summarizeHistory` | Nur noch Konsole | Interne Abläufe nicht ins Display schreiben |
| „Regelsatz wegen ungültigem Selektor ignoriert“ | `::-webkit-scrollbar` ohne Elementselektor (Firefox) | `*::-webkit-scrollbar` | In Firefox und Chromium prüfen |
| Umlaute als „Ã¤“ u. Ä. in einer frühen Fassung | Datei mit falscher Zeichenkodierung gespeichert | Datei als UTF-8 | Immer UTF-8 speichern, `<meta charset="UTF-8">` beibehalten |
| Prompt-Vorlage nur teilweise übernommen | Vorlage gekürzt statt 1:1 eingefügt | Vorlage vollständig übernommen | Zeichenzahl der Vorlage mit dem Ergebnis vergleichen |
