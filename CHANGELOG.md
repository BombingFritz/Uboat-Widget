# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).
Frühere lokale Dateistände (u. a. `enigma_radio_wood.html`, `Stable3-uboat-widget-verbessert.html`) erhalten keine nachträglichen Versionsnummern.

**Zur Zählung:** Die Release-Version (Git-Tag) und die Konstante `WIDGET_VERSION` im Code sind verschiedene Dinge. Das Release `v1.0` enthält `WIDGET_VERSION = "3.0"`. `WIDGET_VERSION` steuert, wann der gespeicherte Persönlichkeits-Prompt durch den neuen Standard ersetzt wird (siehe `docs/ARCHITEKTUR.md`).

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
