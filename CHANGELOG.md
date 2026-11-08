# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).
Frühere lokale Dateistände (u. a. `enigma_radio_wood.html`, `Stable3-uboat-widget-verbessert.html`) erhalten keine nachträglichen Versionsnummern.

**Zur Zählung:** Die Release-Version (Git-Tag) und die Konstante `WIDGET_VERSION` im Code sind verschiedene Dinge. Das Release `v1.0` enthält `WIDGET_VERSION = "3.0"`. `WIDGET_VERSION` steuert, wann der gespeicherte Persönlichkeits-Prompt durch den neuen Standard ersetzt wird (siehe `docs/ARCHITEKTUR.md`).

## [1.4.0] - 2026-11-08

Weniger Ballast im Gedächtnis und kein überflüssiges Caching mehr. Tests: `python tests/run_all.py`, alle bestanden (Regression 29, Export/Import 25, ohne Browser-Dialoge 22, Gemini-Teile 9, Chat-Bereich 7, Funkspruch-Paare 15, Verdichten 42, Kopfzeile 13, Spaßfilter-Test 22, Benchmark Gemini 50, Benchmark andere Anbieter 52). Persönlichkeits-Prompt, Chronologie, `SAFETY_RULES`, `CHAT_RULES`, Chat-Modus, Audiodateien, Benchmark und `WIDGET_VERSION` („3.0“) unverändert.

### Added
- **Zusammenfassung verdichten:** Wird die Zusammenfassung des Funkverlaufs länger als 2.000 Zeichen, fasst die KI sie zusammen mit den neuen Funksprüchen zu einer kürzeren Gesamtzusammenfassung (Ziel 1.200 Zeichen) zusammen, statt sie endlos zu verlängern. Übernommen wird sie nur, wenn sie vollständig und kürzer als die bisherige ist. Klappt das nicht, fallen stattdessen die ältesten Abschnitte der Zusammenfassung weg (ohne weiteren Aufruf), damit sie nicht unbegrenzt wächst. Die laufende Feindfahrt bleibt ausführlicher, frühere Fahrten werden knapp; was schon im Boot-Kontext steht, wird nicht wiederholt. Kein zusätzlicher API-Aufruf. Bestehende lange Zusammenfassungen werden beim nächsten Mal automatisch verdichtet.
- **Spaßmeldungen** ohne Bezug zur Feindfahrt (z. B. leere Spargel- oder Biervorräte) und die Antworten darauf kommen nicht mehr in die Zusammenfassung. Der Verlauf selbst bleibt unverändert.
- Einstellungen, Token-Schätzung: neue Zeile „Letzte Anfrage: … Tokens, davon … automatisch zwischengespeichert“. Zeigt, ob der Anbieter den festen Teil der Anfrage automatisch zwischenspeichert. Die Token-Schätzung ist jetzt auch im Universal-Modus sichtbar.

- Einstellungen, „Letzte Zusammenfassung“: zeigt jetzt Zeitpunkt, Art (angehängt, verdichtet, gekürzt), Länge und wie viele Funksprüche noch nicht zusammengefasst sind. Vorher stand dort „Vor 4 Nachrichten (4 neue)“, was sich scheinbar nie änderte.

- Spaßfilter-Test `benchmark/spassfilter.html` (nicht Teil des Widgets): fasst einen festen Testsatz aus ernsten Funksprüchen, Spaßmeldungen und Grenzfällen mit genau den Anweisungen des Widgets zusammen (Gemini, echte API) und zeigt, ob Fakten bleiben und Spaß verschwindet, auch nach dem Verdichten.

### Fixed
- Antworten zeigten teils eine doppelte Kopfzeile („FT von BdU an U-68: **BdU an U-68:**“). Eine eigene Kopfzeile des Modells am Antwortanfang wird jetzt entfernt, auch bei älteren Antworten im Display (BUGS B23).

### Removed
- **Explizites Gemini-Caching** samt Schalter und Statusanzeige (ADR 0006). Es war im kostenlosen Kontingent nicht verfügbar, kostete dort nach jedem Neuladen einen erfolglosen Aufruf und wurde vom Standardmodell nicht genutzt. Ersatz ist das automatische Caching der Anbieter; der feste Teil der Anfrage (Sicherheitsregeln, Persönlichkeit, Boot-Kontext) steht dafür immer vorne. Alte Einstellungen dazu werden beim Laden entfernt; Exporte älterer Versionen lassen sich weiter importieren.
- Fehler B18 (Cache wurde zu oft neu angelegt) entfällt damit.

## [1.3.2] - 2026-11-08

### Fixed
- Verlauf: „LETZTE 5 LÖSCHEN“ heißt jetzt „LETZTEN FUNKSPRUCH LÖSCHEN“ und entfernt die letzte Meldung samt Antwort. Vorher konnte der Verlauf mit einer unbeantworteten Meldung enden; die nächste Anfrage enthielt dann zwei Meldungen des Kaleu hintereinander (BUGS B19). Unbeantwortete Meldungen am Verlaufsende aus älteren Fassungen werden mit entfernt. Test `tests/history_pairs.py`. Prompt, `SAFETY_RULES`, Chat-Modus, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

## [1.3.1] - 2026-11-08

Nur Lizenz und Dokumentation; `index.html`, Benchmark und Tests unverändert gegenüber 1.3.0.

### Changed
- **Lizenz: MIT statt CC-BY 4.0** (Entscheidung des Autors, 08.11.2026). CC-Lizenzen sind nicht für Software gedacht; MIT erlaubt wie bisher freie Nutzung, Änderung und Weitergabe mit Namensnennung (Copyright-Hinweis) und entspricht der Lizenz von SpargelPoll. Alle Inhalte des Repositorys (Code, Prompt-Texte, Töne) stammen vom Autor. Releases bis v1.2.2 bleiben unter CC-BY 4.0 bezogen.

### Fixed
- `LICENSE` im Tag `v1.3.0` enthielt versehentlich die Mozilla Public License 2.0 (Auswahl in der GitHub-Vorlage). Ab v1.3.1 gilt die MIT-Lizenz.

### Documentation
- README und Benchmark-Anleitung: Hinweis, dass kostenlose Modelle stärker eingeschränkt sind und im ersten Vergleich schwächere Ergebnisse lieferten; lokale Modelle (Ollama, LM Studio) als kostenlose Alternative mit Einrichtungshinweisen (Platzhalter-Schlüssel, CORS).

## [1.3.0] - 2026-11-07

Erste Version für alle seit 1.0.2, die auch ohne Companion-Server etwas bringt: Benchmark zur Modellwahl, einfachere Einstellungen, überarbeitete Anleitung und automatische Tests. Fasst für Nutzer ohne Server auch 1.1.0–1.2.2 zusammen (Export/Import, Fehlerbehebungen). Tests: `python tests/run_all.py`, alle bestanden (Regression 26, Export/Import 25, ohne Browser-Dialoge 22, Gemini-Teile 9, Chat-Bereich 7, Benchmark Gemini 50, Benchmark andere Anbieter 52). Prompt, `SAFETY_RULES`, Chat-Logik, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Added
- Benchmark im Ordner `benchmark/` (nicht Teil des Widgets): dieselben 10 Testfragen und derselbe Kontext an mehrere Modelle, blinde Bewertung, Auswertung je Modell. Anbieter Gemini, Groq, OpenRouter (nur kostenlose Modelle), Mistral und jede eigene OpenAI-kompatible Adresse wie im Universal-Modus. Mit Beispielkontext `benchmark/beispiel-kontext.json` für alle ohne eigenen Funkverlauf. Anfrage identisch zum Widget. Spec `docs/specs/benchmark.md`. Erster echter Durchlauf durch den Nutzer am 07.11.2026 (Gemini 2.5 gegen 3.5 Flash-Lite).
- Automatische Tests im Ordner `tests/` (Python, Playwright, simulierte APIs) mit Anleitung.

### Changed
- Einstellungen: Der Chat-Modus steht in einem eingeklappten Bereich „Für Streamer: Chat-Modus“. Er öffnet sich von selbst, wenn der Chat-Modus eingeschaltet ist.
- README: Kurzanleitung ganz oben, Base-URLs für Groq, OpenRouter, Mistral und OpenAI im Universal-Modus, Abschnitt zum Benchmark und zum Companion-Server (was er ist, für wen er sich lohnt, dass er mehr Einrichtung braucht).
- Lizenzdatei `LICENSE-CC-BY-4.0.txt` heißt jetzt `LICENSE`. Inhalt unverändert.

## [1.2.2] - 2026-11-07

Fehlerbehebungen nach dem ersten Benchmark und dem Export-Test in OBS. Headless geprüft: mehrteilige Antworten, Denk-Teile und Download 9/9, ohne Browser-Dialoge 22/22, Regression 26/26, Export/Import 25/25. Design, Prompt, `SAFETY_RULES`, Chat-Modus, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Fixed
- Gemini: Antworten brachen bei `gemini-3.5-flash-lite` gelegentlich mitten im Satz ab (Benchmark: 4 von 20 Antworten). Gemini liefert die Antwort teils in mehreren Teilen; das Widget las nur den ersten. Jetzt werden alle Text-Teile zusammengesetzt (Denk-Teile ausgenommen). Betrifft auch Chat-Antworten (BUGS B21).
- „ALS DATEI“ in OBS: Der Download funktioniert dort doch (die Datei landet ohne Hinweis im Download-Ordner, Nutzertest 07.11.2026). Der Sonderweg aus 1.2.1, der in OBS nur das Textfeld füllte, ist entfernt.

### Changed
- Export-Datei heißt jetzt einfach `Funk-Export.json` (vorher mit Datum).

## [1.2.1] - 2026-11-07

Fehlerbehebung für den Betrieb in OBS, ohne neue Funktionen. Headless-Test ohne Browser-Dialoge wie in OBS (22/22), Regressionstests 26/26, Export/Import 25/25, Datei-Export in OBS und Browser 7/7. Import in OBS vom Nutzer bestätigt (07.11.2026). Design, Prompt, `SAFETY_RULES`, Chat-Modus, Audiodateien und `WIDGET_VERSION` („3.0“) unverändert.

### Fixed
- In OBS taten „IMPORTIEREN“, „RESET“, „HISTORY LÖSCHEN“ und „LETZTE 5 LÖSCHEN“ nichts, weil OBS die Rückfrage-Fenster des Browsers nicht anzeigt (BUGS B20). Rückfragen erscheinen jetzt im Widget: erster Klick ändert den Button (z. B. „IMPORT BESTÄTIGEN“), zweiter Klick führt aus. Beim Import stehen Datum, Anzahl der Verlaufseinträge und Schlüssel-Hinweis im Statusfeld.
- Hinweise ohne API-Schlüssel (Senden, Speichern, Modellsuche) und bei vollem Speicher erscheinen im Widget statt als Browser-Fenster.

### Changed
- „ALS DATEI“ in OBS (dort sind keine Downloads möglich): stellt den Export im Textfeld bereit und erklärt, wie man ihn per Kopieren und Einfügen in einem Texteditor als `.json`-Datei speichert.

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
