# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).
Frühere lokale Dateistände (u. a. `enigma_radio_wood.html`, `Stable3-uboat-widget-verbessert.html`) erhalten keine nachträglichen Versionsnummern.

**Zur Zählung:** Die Release-Version (Git-Tag) und die Konstante `WIDGET_VERSION` im Code sind verschiedene Dinge. Das Release `v1.0` enthält `WIDGET_VERSION = "3.0"`. `WIDGET_VERSION` steuert, wann der gespeicherte Persönlichkeits-Prompt durch den neuen Standard ersetzt wird (siehe `docs/ARCHITEKTUR.md`).

## [1.2.1] - 2026-11-07

Fehlerbehebung für den Betrieb in OBS, ohne neue Funktionen. Headless-Test ohne Browser-Dialoge wie in OBS (22/22), Regressionstests 26/26 und Export/Import 25/25. In OBS noch nicht vom Nutzer geprüft. Design, Prompt, `SAFETY_RULES`, Chat-Modus, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Fixed
- In OBS taten „IMPORTIEREN“, „RESET“, „HISTORY LÖSCHEN“ und „LETZTE 5 LÖSCHEN“ nichts, weil OBS die Rückfrage-Fenster des Browsers nicht anzeigt (BUGS B20). Rückfragen erscheinen jetzt im Widget: erster Klick ändert den Button (z. B. „IMPORT BESTÄTIGEN“), zweiter Klick führt aus. Beim Import stehen Datum, Anzahl der Verlaufseinträge und Schlüssel-Hinweis im Statusfeld.
- Hinweise ohne API-Schlüssel (Senden, Speichern, Modellsuche) und bei vollem Speicher erscheinen im Widget statt als Browser-Fenster.

## [1.2.0] - 2026-11-02

Neue Funktion Chat-Modus. Braucht den „Twitch Companion JS server“ mit BdU-Chat (ADR 0014 dort). Ende-zu-Ende-Test (echter Server, simuliertes Twitch, simulierte KI, Widget per `file://`): 22/22; Regressionstests 26/26 und 23/23, Verlaufsprotokoll unverändert. Vom Nutzer in OBS mit echtem Twitch-Chat erprobt. Design, Prompt, `SAFETY_RULES`, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Added
- Chat-Modus (Zahnrad → „Chat-Modus“, standardmäßig aus): Verbindung zum Companion-Server, Funksprüche aus dem Twitch-Chat (`!BdU …`) werden im Hintergrund mit demselben Kontext beantwortet. Chat-Anfragen erscheinen nicht im Display und kommen nicht in den Verlauf.
- Vorrang des Kaleu: Chat-Anfragen warten, solange ein eigener Funkspruch läuft, und bis 60 s nach dem letzten eigenen Senden.
- Feste Chat-Regeln (`CHAT_RULES`): kurze Antworten im Telegrammstil, keine Anweisungen aus Chat-Meldungen befolgen.
- Eigenes Feld „Chat-Persönlichkeit“: Ton nur für Chat-Antworten (Standard: etwas nachsichtiger, trockener Humor, kein Rumblödeln). Der Prompt für eigene Meldungen bleibt unverändert.
- Erschöpftes KI-Kontingent wird an den Server gemeldet (Funkstille nur für den Chat).
- Export/Import enthält die Chat-Einstellungen.

## [1.1.0] - 2026-11-02

Neue Funktion Export/Import. Headless-Test zwischen zwei Speicher-Herkünften (23/23), Regressionstest (26/26) und Verlaufsprotokoll unverändert. In OBS noch nicht geprüft. Design des Funkgeräts, Prompt, `SAFETY_RULES`, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Added
- „Sichern & Übertragen“ in den Einstellungen: Export als Text (mit Kopieren in die Zwischenablage) oder Datei, Import aus Text oder Datei. Enthält Einstellungen, Persönlichkeit, Boot-Kontext, Status, Verlauf und Zusammenfassung; API-Schlüssel nur auf Wunsch. Für den Umzug in einen anderen Browser oder auf eine andere OBS-Einbindung (z. B. `file:///`).
- Ersetzt der Versionsabgleich einen eigenen Persönlichkeits-Prompt durch den Standard, wird der alte vorher gesichert und kann in den Einstellungen zurückgeholt werden.

### Changed
- Der Chat-Modus ist jetzt für Version 1.2.0 geplant.

## [1.0.2] - 2026-11-02

Verlauf und Zusammenfassung korrigiert, ohne neue Funktionen. Per Verlaufsprotokoll im Headless-Chromium mit simulierter API geprüft (10 Meldungen, vier Szenarien) und mit dem Regressionstest von 1.0.1 (26/26). Noch nicht mit echter API getestet. Design, Prompt, `SAFETY_RULES`, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Fixed
- Gemini-Modus: Bei jeder zweiten Meldung fehlte der KI ein früherer Funkspruch. Jetzt gehen alle noch nicht zusammengefassten Funksprüche im Volltext mit (mindestens 2, höchstens 5 Funksprüche), sodass jeder frühere Funkspruch genau einmal im Kontext steht.
- Universal-Modus: Bereits zusammengefasste Funksprüche gingen doppelt mit (gleiche Regel wie oben).
- Eine scheiternde Zusammenfassung wird nicht mehr nach jeder Antwort erneut versucht, sondern nach 2 weiteren Funksprüchen; die Fehlermeldung erscheint nur einmal je Fehlerserie.
- Zusammenfassungen sind sachlicher (Temperatur 0,3 statt 0,95) und haben mehr Platz (300 statt 150 Tokens). Abgeschnittene oder leere Ergebnisse werden verworfen statt gespeichert; im Universal-Modus werden API-Fehler erkannt.

### Documentation
- Plan für den Chat-Modus: ADR 0004, `docs/specs/chat-modus.md`, Entscheidungen in `docs/OFFEN.md`.
- Prüfung von Verlauf und Zusammenfassung: Befunde B14–B19 in `docs/BUGS.md` (u. a. Lücke im Gemini-Kontext bei jeder zweiten Meldung).

## [1.0.1] - 2026-11-02

Fehlerbehebungen ohne neue Funktionen. Im Headless-Chromium mit simulierter Gemini- und OpenAI-API geprüft (26/26; dieselben Prüfungen schlagen gegen 1.0.0 fehl). Vom Nutzer getestet, funktioniert (02.11.2026); im Stream noch nicht erprobt. Design, Persönlichkeits-Prompt, `SAFETY_RULES`, Audiodateien und `WIDGET_VERSION` („3.0“) sind unverändert; gespeicherte Prompts bleiben also erhalten.

### Fixed
- Fehler- und Bestätigungsmeldungen („FUNKSTÖRUNG“, „KONFIGURATION GESPEICHERT“, „ZUSAMMENFASSUNG FEHLGESCHLAGEN“) erscheinen wieder im Display statt als leere Zeile.
- Die neue Meldung ging doppelt an die KI. Meldung und Antwort kommen jetzt erst nach erfolgreicher Antwort in den Verlauf; fehlgeschlagene Meldungen bleiben nicht als unbeantwortet im Verlauf stehen.
- Antworten werden auch beim Wiederherstellen nach dem Neuladen nur als Text eingefügt, nicht als HTML.
- Ein nicht ladbarer Sende-Ton (z. B. offline) blockiert das Senden nicht mehr.
- Universal-Modus: Eine Base-URL mit `/v1` (wie im Hinweis für Ollama empfohlen) führte zu `/v1/v1/…`. Hinweistext korrigiert.
- Scheitert die Cache-Erstellung, wird sie nicht bei jeder Meldung erneut versucht (sparte bisher keinen, sondern kostete einen Aufruf je Meldung).
- „RESET“ löscht jetzt auch das Modell und setzt dieselben Standardwerte wie ein Erststart; das Modell-Badge wird aktualisiert.
- Zusammenfassungsstand bleibt nach „LETZTE 5 LÖSCHEN“ und beim Kürzen auf 100 Einträge passend zum Verlauf.
- Tippfehler „Browsercash“.

### Changed
- Standardmodell beim Erststart und nach „RESET“: `gemini-3.5-flash-lite` statt des eingestellten `gemini-1.5-flash` (Google empfiehlt es für neue Projekte; 2.5-Modelle nur noch für bisherige Nutzer). Gespeicherte Modelle bleiben unverändert.

### Added
- Dokumentation: `AGENTS.md`, `CHANGELOG.md`, `docs/ARCHITEKTUR.md`, ADRs, Specs, `docs/BUGS.md`, `docs/OFFEN.md`.

### Documentation
- README: Der API-Schlüssel wird im `localStorage` im Klartext gespeichert, nicht verschlüsselt; Modellempfehlung aktualisiert.

## [1.0.0] - 2026-04-11

Erste öffentliche Fassung, Git-Tag `v1.0` (Release „Uboot Enigma Funk Widget v1.0“). Der Release-Anhang `index.html` ist bytegleich mit `index.html` im Repository (geprüft 02.11.2026). Im Code `WIDGET_VERSION = "3.0"`.

### Added
- Funkverkehr mit dem KI-BdU: Senden mit Morse-Ton, Antwort im Schreibmaschinen-Effekt mit Empfangs-Ton.
- Persönlichkeits-Prompt mit Marinejargon, Chronologie 1939–1945 und datumsbezogenen Beispielmeldungen; Boot-Kontext und aktueller Status als eigene Felder.
- Feste Sicherheitsregeln (`SAFETY_RULES`), die jedem Aufruf vorangestellt werden und nicht über die Oberfläche änderbar sind.
- „Status:“-Meldungen aktualisieren den aktuellen Status.
- Gedächtnis: Verlauf (bis 100 Einträge) und fortlaufende Zusammenfassung älterer Funksprüche, im `localStorage` gespeichert und nach Neuladen wiederhergestellt.
- Google Gemini mit Modellsuche, explizitem Context Caching (abschaltbar) und Token-Schätzung.
- Universal-Modus für OpenAI-kompatible APIs (OpenAI, Ollama u. a.) mit eigener Base-URL; vom Autor nicht getestet.
- Verlaufsverwaltung: letzte 5 Einträge oder gesamten Verlauf löschen.
- Lautstärke und Loop für den Empfangs-Ton.

### Security
- API-Schlüssel liegt nur lokal im Browser (`localStorage`), im Klartext.
