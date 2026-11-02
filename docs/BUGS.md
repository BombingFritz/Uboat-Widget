# Bugs und historische Probleme

## Offen (aus Code-Durchsicht 02.11.2026, nicht zur Laufzeit reproduziert)

| Nr. | Symptom | Ursache | Vorschlag | Priorität |
|---|---|---|---|---|
| B1 | Fehlermeldungen wie „FUNKSTÖRUNG: …“, „KONFIGURATION GESPEICHERT.“ oder „ZUSAMMENFASSUNG FEHLGESCHLAGEN“ erscheinen nicht im Display, nur eine leere Zeile | `appendLog` kennt nur die Absender `Kaleu` und `System`; Aufrufe mit `Funkmaat` bzw. `sys` landen im `else`-Zweig, der keinen Text setzt | `appendLog` um diese Absender ergänzen oder Aufrufe vereinheitlichen | P1 |
| B2 | Die neue Meldung geht doppelt an die API | `sendMessage` speichert die Meldung vor dem Aufruf im Verlauf; `callGemini`/`callUniversal` nehmen die letzten Einträge (inkl. dieser Meldung) und hängen sie noch einmal an | Verlauf vor dem Hinzufügen auslesen oder letzte Meldung beim Aufbau überspringen | P1 |
| B3 | Nach einem fehlgeschlagenen Aufruf steht eine Meldung ohne Antwort im Verlauf | Meldung wird vor dem Aufruf gespeichert, bei Fehler nicht entfernt | Bei Fehler entfernen oder als unbeantwortet markieren | P2 |
| B4 | KI-Antworten werden als HTML eingefügt (`innerHTML` im Schreibmaschinen-Effekt und beim Wiederherstellen). Spitze Klammern oder `&` können die Ausgabe verfälschen; Markup aus der Antwort wird ausgeführt | Zeichenweises `innerHTML +=` und Template-String mit `msg.text` | Text per `textContent`/Textknoten einfügen, Zeilenumbrüche getrennt behandeln. Vor einem Chat-Modus zwingend (fremde Eingaben) | P1 vor Server-Modus |
| B5 | „RESET“ löscht das Modell nicht und setzt andere Werte als ein Erststart | `clearSettings` entfernt `bdu_active_model` statt `bdu_current_model`; setzt Boot-Kontext und Status leer statt auf Standard, Loop aus statt an, Modell `gemini-2.5-flash` statt `gemini-1.5-flash`; `bdu_widget_version` bleibt | Schlüssel korrigieren, Standardwerte an einer Stelle definieren | P2 |
| B6 | „MODELLE SUCHEN“ im Universal-Modus schlägt fehl oder zeigt Gemini-Modelle | `fetchModels` fragt immer die Gemini-API ab | Im Universal-Modus `{base}/v1/models` abfragen oder Knopf ausblenden | P3 |
| B7 | Standardmodell beim Erststart ist `gemini-1.5-flash` | Fester Standardwert in `loadSettings`; Gemini-1.5-Modelle sind nach bisherigem Stand eingestellt (vor Änderung in der Modellliste prüfen) | Standard auf ein aktuelles Modell setzen (README empfiehlt `gemini-2.5-flash-lite`) | P2 |
| B8 | Eigene Prompt-Anpassungen gehen nach einem Update ohne Rückfrage verloren | `WIDGET_VERSION`-Abgleich in `loadSettings` ersetzt den gespeicherten Prompt | Siehe `docs/OFFEN.md`, Punkt „Prompt-Version“ | P2 |
| B9 | Label „Browsercash“ | Tippfehler im Einstellungsfeld des API-Schlüssels | „Browsercache“ | P3 |
| B10 | Nach „LETZTE 5 LÖSCHEN“ kann der Zusammenfassungsstand hinter dem Verlauf liegen | `lastSummaryIndex` wird nicht angepasst | Index auf höchstens Verlaufslänge begrenzen | P3 |

## Historisch (aus der Entwicklung, behoben)

| Symptom | Ursache | Fix | Regel zur Vermeidung |
|---|---|---|---|
| „Cached content is too small. total_token_count=832, min_total_token_count=2048“ | Systemtext unter dem Minimum für explizites Caching | Ausführlicher Prompt mit Chronologie; Fehler wird abgefangen, Anfrage läuft ohne Cache | Kontextlänge prüfen (Token-Schätzung in den Einstellungen) |
| Neuer Standard-Prompt erschien nicht im Einstellungsfeld | Alter Prompt im `localStorage` hatte Vorrang vor `DEFAULT_PROMPT` | `WIDGET_VERSION`-Abgleich (mit der Nebenwirkung B8) | Prompt-Updates über Versionierung, nicht über Defaults allein |
| Zusammenfassungs-Meldungen erschienen als Funkspruch im Display | `appendLog` in `summarizeHistory` | Nur noch Konsole | Interne Abläufe nicht ins Display schreiben |
| „Regelsatz wegen ungültigem Selektor ignoriert“ | `::-webkit-scrollbar` ohne Elementselektor (Firefox) | `*::-webkit-scrollbar` | In Firefox und Chromium prüfen |
| Umlaute als „Ã¤“ u. Ä. in einer frühen Fassung | Datei mit falscher Zeichenkodierung gespeichert | Datei als UTF-8 | Immer UTF-8 speichern, `<meta charset="UTF-8">` beibehalten |
| Prompt-Vorlage nur teilweise übernommen | Vorlage gekürzt statt 1:1 eingefügt | Vorlage vollständig übernommen | Zeichenzahl der Vorlage mit dem Ergebnis vergleichen |
