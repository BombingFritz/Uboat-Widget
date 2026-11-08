# Bugs und historische Probleme

## Offen

| Nr. | Symptom | Ursache | Vorschlag | Priorität |
|---|---|---|---|---|
| B8 | Eigene Prompt-Anpassungen werden nach einem Update ohne Rückfrage durch den Standard ersetzt | `WIDGET_VERSION`-Abgleich in `loadSettings` | Seit 1.1.0 abgemildert: alter Prompt wird gesichert und ist in den Einstellungen zurückholbar. Grundsätzliche Lösung siehe `docs/OFFEN.md`, Punkt „Prompt-Version“ | P3 |
| B22 | `!BdU`-Antwort kam erst 25 s nach Annahme (Server-Log, Nutzer 08.11.2026) | [UNGEKLÄRT]. Der Server reicht die Anfrage sofort weiter, die Zeit vergeht im Widget. Wahrscheinlich der Vorrang des Kaleu: `sendMessage` setzt `lastOwnSendAt` am Ende noch einmal, die 60 s laufen also ab Ende der Schreibmaschinen-Ausgabe (und ggf. der Zusammenfassung), nicht ab dem Senden, wie `docs/specs/chat-modus.md` es beschreibt. Alternativ eine langsame KI-Antwort. Nutzer, 08.11.2026: vermutlich der Timer; eine spätere Anfrage kam sofort | Beobachten. Offen bleibt die Abweichung zwischen Code und Spec beim Beginn der 60 s. Danach entscheiden: Code oder Spec angleichen; ggf. meldet das Widget Warte- und KI-Zeit mit der Antwort an den Server, der sie mitloggt | P3 |

Bereits zusammengefasste Funksprüche bleiben in der Zusammenfassung, auch wenn sie danach per „LETZTEN FUNKSPRUCH LÖSCHEN“ entfernt werden (erwartet, nicht korrigierbar ohne Neuberechnung).

## Behoben in 1.4.0
Nachweis: `tests/answer_header.py` 13/13, `tests/summary_condense.py` (Headless-Chromium, simulierte API).

| Nr. | Symptom | Ursache | Behebung |
|---|---|---|---|
| B23 | Antwort im Display mit doppelter Kopfzeile: „FT von BdU an U-68: **BdU an U-68:**“ (Nutzertest 08.11.2026) | Das Widget setzt die Kopfzeile selbst; das Modell schrieb zusätzlich eine eigene, vermutlich weil ältere Antworten im Verlauf sie enthalten | `stripAnswerHeader` entfernt eine eigene Kopfzeile (auch mit `**`) am Antwortanfang, bevor die Antwort gespeichert und angezeigt wird; ältere Verlaufseinträge nur in der Anzeige |
| – | Anzeige „Letzte Zusammenfassung: Vor 4 Nachrichten (4 neue)“ änderte sich scheinbar nie (Nutzertest 08.11.2026) | Beide Zahlen gleich berechnet (noch nicht zusammengefasste Einträge); im Normalfall pendeln sie nur zwischen 4 und 6, weil alle 2 Funksprüche zusammengefasst wird | Anzeige mit Zeitpunkt, Art, Länge und offenen Funksprüchen (`bdu_last_summary_meta`) |

## Entfallen mit 1.4.0

| Nr. | Symptom | Grund |
|---|---|---|
| B18 | Bei Gemini 1.5/2.5 mit explizitem Caching wurde der Cache etwa jede zweite Meldung neu erstellt (die Zusammenfassung stand im gecachten Systemtext) | Explizites Caching entfernt (ADR 0006). Die Zusammenfassung steht weiterhin hinter dem festen Anfang des Systemtexts, das automatische Caching von Google betrifft das nicht |

## Behoben in 1.3.2
Nachweis: `tests/history_pairs.py` (Headless-Chromium, simulierte Gemini-API), 15/15. Vom Nutzer in OBS getestet, funktioniert (08.11.2026: 100 → 98 Einträge).

| Nr. | Symptom | Ursache | Behebung |
|---|---|---|---|
| B19 | Nach „LETZTE 5 LÖSCHEN“ endete der Verlauf mit einer Meldung ohne Antwort; die nächste Anfrage enthielt zwei Nutzer-Einträge hintereinander | Verlauf besteht seit 1.0.1 nur aus Paaren; 5 ist ungerade | Button „LETZTEN FUNKSPRUCH LÖSCHEN“ (`clearLastExchange`) entfernt Meldung und Antwort als Paar; unbeantwortete Meldungen am Verlaufsende (aus älteren Fassungen) werden mit entfernt. Ob Gemini zwei aufeinanderfolgende Nutzer-Einträge abgelehnt hätte, bleibt [UNGEKLÄRT], ist aber nicht mehr relevant |

## Behoben in 1.2.2

| Nr. | Symptom | Ursache | Behebung |
|---|---|---|---|
| B21 | Mit `gemini-3.5-flash-lite` brachen Antworten gelegentlich mitten im Satz ab („Rückmarsch wird“), obwohl `finishReason` STOP meldete (Benchmark 07.11.2026: 4 von 20 Antworten; bei `gemini-2.5-flash-lite` 0 von 20) | `handleGeminiResponse` las nur `parts[0].text`; Gemini liefert die Antwort teils in mehreren Teilen. Beleg: Bei den abgebrochenen Antworten passten Zeichenzahl und Token-Zählung nicht zusammen (etwa 1,5 statt 3,5 Zeichen je Token) | Alle Text-Teile ohne Denk-Teile (`thought`) zusammensetzen, wie schon bei der Zusammenfassung seit 1.0.2 |

## Behoben in 1.2.1

| Nr. | Symptom | Ursache | Behebung |
|---|---|---|---|
| B20 | In OBS („Interagieren“) tat „IMPORTIEREN“ nichts: Nach „DATEI LADEN“ stand der Export im Textfeld, übernommen wurde er nicht. Ebenso blieben „RESET“, „HISTORY LÖSCHEN“ und „LETZTE 5 LÖSCHEN“ ohne Wirkung; Hinweise wie „API Key fehlt!“ erschienen nicht (Nutzer, 07.11.2026). Im normalen Browser ging es (Import am 02.11.2026) | Rückfragen per `confirm()`, Hinweise per `alert()`. Die OBS-Browserquelle zeigt diese Fenster nicht an; `confirm()` gilt dort als abgelehnt | Rückfragen im Widget (`confirmInWidget`): Erster Klick ändert den Button („IMPORT BESTÄTIGEN“ bzw. „SICHER? NOCHMAL KLICKEN“), zweiter Klick frühestens nach 0,4 s und binnen 10 s (Import 60 s) führt aus. Beim Import stehen die Angaben im Statusfeld. Hinweise im Display, auf dem Button oder in der Modellliste statt `alert()` |

## Behoben in 1.0.2
Nachweis: Verlaufsprotokoll im Headless-Chromium mit simulierter Gemini- und OpenAI-API über 10 Meldungen, je Anfrage Volltext-Einträge, Zusammenfassung und Index (02.11.2026). Gemini und Universal: jeder frühere Funkspruch ist genau einmal enthalten (Volltext oder Zusammenfassung). Dauerhaft scheiternde Zusammenfassung: 4 statt 10 Versuche, eine Meldung im Display. Einmal scheiternde Zusammenfassung: holt den Rückstand beim nächsten Versuch nach. Abgeschnittene Zusammenfassung (`MAX_TOKENS`) wird verworfen. Regressionstest von 1.0.1: 26/26. Noch nicht mit echter API getestet.

| Nr. | Symptom | Ursache | Fix |
|---|---|---|---|
| B14 | Gemini-Modus: Bei jeder zweiten Meldung kannte die KI einen früheren Funkspruch weder im Volltext noch aus der Zusammenfassung (bei Meldung 4 fehlte Meldung 1, bei 6 fehlte 3, bei 8 fehlte 5) | Starr die letzten 4 Einträge; die Zusammenfassung läuft erst bei 8 offenen Einträgen | `getContextHistory`: alle noch nicht zusammengefassten Einträge, mindestens 4, höchstens 10, beginnend mit einer Kaleu-Meldung |
| B15 | Universal-Modus: Zusammengefasste Funksprüche gingen zusätzlich im Volltext mit | Starr die letzten 10 Einträge | Gleiche Regel wie B14 |
| B16 | Scheiternde Zusammenfassung wurde nach jeder Antwort erneut versucht, die Fehlermeldung erschien jedes Mal, ältere Funksprüche fehlten der KI ganz | Kein Merker für Fehlschläge; Volltext nur 4 Einträge | Nächster Versuch erst nach 2 weiteren Funksprüchen; Meldung im Display einmal je Fehlerserie; bis dahin bis zu 10 Einträge im Volltext (die ältesten fallen bei längerem Ausfall heraus) |
| B17 | Zusammenfassungen konnten ungenau oder abgeschnitten sein | `temperature` 0.95, Budget 150, kein Prüfen von `finishReason`; Universal ohne Fehlerprüfung | `temperature` 0.3, Budget 300; `MAX_TOKENS`/`length` oder leerer Text gilt als Fehlschlag; Universal prüft HTTP-Status und Fehler. Ob Modelle mit Denkphase das Budget aufbrauchen, bleibt [UNGEKLÄRT]; der Fall wird jetzt als Fehlschlag erkannt statt gespeichert |

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
