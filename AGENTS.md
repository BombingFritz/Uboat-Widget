# Regeln für KI-Assistenten

- Vor Änderungen `docs/ARCHITEKTUR.md`, `docs/adr/`, `docs/BUGS.md` und `docs/OFFEN.md` lesen.
- Bei Konflikt mit einem ADR erst nachfragen.
- Referenz ist immer `index.html` im aktuellen Stand von `main`. Lokale Arbeitskopien mit anderem Stand sind keine Referenz.
- Das Widget ist öffentlich und wird von anderen genutzt (ADR 0002). Der eigenständige Betrieb ohne Server bleibt immer der Standard; Server-Funktionen nur als abschaltbarer, standardmäßig ausgeschalteter Modus.
- Versionen nur über `CHANGELOG.md` und Git-Tags (`vX.Y.Z`), nie über den Dateinamen. Tags und Releases legt der Nutzer in der GitHub-Oberfläche an.
- `WIDGET_VERSION` ist im aktuellen Code faktisch eine Prompt-Version: Jede Änderung überschreibt beim Nutzer den gespeicherten Persönlichkeits-Prompt. Nur bewusst und mit Eintrag im Changelog ändern (siehe `docs/OFFEN.md`).
- Dateipfade im Wurzelverzeichnis nicht verändern: `index.html`, `morse_Fritz_an_BdU_outgoing.wav`, `morse_BDU_anFritz_1930s_far.wav`. Heruntergeladene Widgets laden die WAVs direkt aus diesem Repository (ADR 0001).
- `SAFETY_RULES` bleibt fest im Code, wird jedem Aufruf vorangestellt und ist nicht über die Oberfläche änderbar (ADR 0003).
- Im Repository nie echte API-Schlüssel, Tokens, IDs oder Secrets. Keine Secrets ausgeben.
- Nur beauftragte, gezielte Änderungen; kein Neuaufbau der Datei aus Suchsnippets.
- Design (Holzgehäuse, Ecken, Schrauben, Display, Schriften) ohne Auftrag unverändert lassen.
- Persönlichkeits-Prompt, Chronologie und Vokabular sind inhaltliche Arbeit des Nutzers: nur auf ausdrücklichen Auftrag ändern, Vorlagen 1:1 übernehmen.

## Pflichtchecks vor Auslieferung

- Script extrahieren und mit einem echten JS-Parser prüfen (`node --check`); Klammerzählen reicht nicht.
- Vollständigkeit: HTML-Body, Script, alle Funktionsdefinitionen und `window.onload` vorhanden.
- Diff zur tatsächlichen Ausgangsdatei prüfen; unerwartete Änderungen ausschließen, besonders an CSS und Prompt-Texten.
- WAV-Dateien und ihre URLs im Code unverändert (Hash- bzw. Textvergleich).
- Keine echten Schlüssel, Tokens oder IDs im gesamten Repo-Stand.
- Im Browser testen: Senden/Empfangen mit Ton, Einstellungen speichern, Neuladen (Verlauf bleibt), „Status:“-Meldung, beide API-Typen soweit verfügbar.
- Neue `localStorage`-Schlüssel auch in `clearSettings` und in `docs/ARCHITEKTUR.md` eintragen.
- `CHANGELOG.md` und betroffene Docs im selben Commit aktualisieren.
- Lieferung als vollständige Dateien, nicht als Fragmente.
- Tests, Nutzerbestätigungen und Vermutungen klar unterscheiden; „behoben“ nur mit Nachweis.
