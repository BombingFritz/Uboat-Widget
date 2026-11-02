# Bugs und historische Probleme

## Offen

| Nr. | Symptom | Ursache | Vorschlag | Priorität |
|---|---|---|---|---|
| B8 | Eigene Prompt-Anpassungen gehen nach einem Update ohne Rückfrage verloren | `WIDGET_VERSION`-Abgleich in `loadSettings` ersetzt den gespeicherten Prompt | Siehe `docs/OFFEN.md`, Punkt „Prompt-Version“; Entscheidung des Nutzers offen | P2 |

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
