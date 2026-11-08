# Export / Import (Sichern & Übertragen)

## Ziel
Einstellungen, Kontexte, Verlauf und Zusammenfassung in einen anderen Browser oder eine andere OBS-Einbindung mitnehmen. Der `localStorage` gilt je Herkunft: „Lokale Datei“ in OBS (`http://absolute`), eine `file:///`-URL und jeder Browser haben getrennte Speicher.

## Verhalten
- Gruppe „Sichern & Übertragen“ in den Einstellungen.
- **EXPORTIEREN:** schreibt den gespeicherten Stand als JSON in das Textfeld, markiert ihn und versucht, ihn in die Zwischenablage zu kopieren. Gelingt das nicht (z. B. in OBS), kopiert man den markierten Text mit Strg+C.
- **ALS DATEI:** lädt denselben Inhalt als `Funk-Export.json` herunter (seit 1.2.2; vorher mit Datum). Auch in OBS landet die Datei im Download-Ordner, dort ohne Hinweis (Nutzertest 07.11.2026); als Rückfall nennt das Statusfeld den Weg über EXPORTIEREN und Texteditor.
- **API-Schlüssel** nur, wenn das Häkchen gesetzt ist (Standard aus). Ohne Schlüssel behält der Import den vorhandenen Schlüssel.
- **IMPORTIEREN:** liest das Textfeld; **DATEI LADEN** liest eine Datei und importiert sie. Nach Rückfrage im Widget (Angaben im Statusfeld, Button wird zu „IMPORT BESTÄTIGEN“, zweiter Klick binnen 60 s) werden die Werte gespeichert und das Widget neu geladen. Seit 1.2.1 ohne Browser-Dialog, weil OBS `confirm()` nicht anzeigt (BUGS B20); ändert sich der Text oder ist er ungültig, wird die Rückfrage aufgehoben.
- Der importierte Persönlichkeits-Prompt gilt als aktuell (`bdu_widget_version` = aktuelle `WIDGET_VERSION`), er wird beim Neuladen nicht durch den Standard ersetzt.
- Ungültiges JSON, fremdes Format oder ein Export einer neueren Formatversion wird mit Meldung abgelehnt; nichts wird verändert. Verlaufseinträge werden geprüft (Rolle, Text), auf 100 gekürzt, der Zusammenfassungsstand passend begrenzt. Ein `cachingEnabled` aus Exporten bis 1.3.x wird ignoriert; neue Exporte enthalten es nicht mehr (seit 1.4.0, `formatVersion` bleibt 1).
- **Prompt-Sicherung:** Ersetzt der Versionsabgleich beim Laden einen eigenen Prompt durch den Standard, wird der alte vorher in `bdu_system_prompt_backup` gesichert. Ein Hinweis mit „GESICHERTEN PROMPT ÜBERNEHMEN“ setzt ihn ins Feld „Persönlichkeit“ (bestätigen mit SPEICHERN). Die Sicherung ist im Export enthalten; RESET löscht sie.

### Format (Version 1)
```json
{
  "format": "enigma-bdu-funk", "formatVersion": 1, "exportedAt": "…", "promptVersion": "3.0",
  "settings": { "apiType", "customBaseUrl", "model", "loopSound", "volume",
                "systemPrompt", "bootContext", "currentStatus", "chatEnabled", "chatServerUrl", "chatPersonality", "apiKey (optional)" },
  "memory": { "history": [{ "role", "text", "timestamp" }], "summary", "lastSummaryIndex" },
  "promptBackup": "optional"
}
```

## Nicht-Ziele
Automatische Synchronisation zwischen Geräten; Verschlüsselung des Exports; Teil-Importe.

## Akzeptanzkriterien
- Export in Herkunft A, Import in leerer Herkunft B: Prompt, Kontext, Status, Modell, Ton, Verlauf (im Display) und Zusammenfassung sind gleich; die nächste Anfrage enthält Verlauf und Zusammenfassung.
- Export ohne Häkchen enthält keinen Schlüssel; Import behält den vorhandenen Schlüssel.
- Ungültiger Import ändert nichts.
- Update von einer älteren Version mit eigenem Prompt: Prompt gesichert, Hinweis sichtbar, übernehmbar.

## Berührte Dateien/Funktionen
`index.html`: Einstellungen (neue Gruppe), `buildExportData`, `exportData`, `downloadExport`, `loadImportFile`, `parseImportData`, `importData`, `updatePromptBackupInfo`, `restorePromptBackup`, `loadSettings` (Sicherung), `clearSettings`.

## Status
umgesetzt (1.1.0). Headless-Test zwischen zwei Herkünften: 23/23. In OBS noch nicht geprüft (Zwischenablage, Strg+A/Strg+C im Fenster „Interagieren“).
