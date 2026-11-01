# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).
Frühere lokale Dateistände (u. a. `enigma_radio_wood.html`, `Stable3-uboat-widget-verbessert.html`) erhalten keine nachträglichen Versionsnummern.

**Zur Zählung:** Die Release-Version (Git-Tag) und die Konstante `WIDGET_VERSION` im Code sind verschiedene Dinge. Das Release `v1.0` enthält `WIDGET_VERSION = "3.0"`. `WIDGET_VERSION` steuert, wann der gespeicherte Persönlichkeits-Prompt durch den neuen Standard ersetzt wird (siehe `docs/ARCHITEKTUR.md`).

## [Unreleased]

### Added
- Dokumentation: `AGENTS.md`, `CHANGELOG.md`, `docs/ARCHITEKTUR.md`, ADRs, Specs, `docs/BUGS.md`, `docs/OFFEN.md`.

### Fixed
- README: Der API-Schlüssel wird im `localStorage` im Klartext gespeichert, nicht verschlüsselt. Die Angabe war falsch.

Keine Änderung an `index.html` oder den Audiodateien.

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
