# Architektur

## Referenz und Struktur
Referenzdatei: `index.html`. Eine HTML-Datei mit Inline-CSS, DOM und klassischem Script am Body-Ende; Start über `window.onload`. Kein Framework, Paketmanager oder Build.

Externe Abhängigkeiten zur Laufzeit:
- Google Fonts: „Special Elite“ (Display) und „Share Tech Mono“ (Bedienelemente).
- Hintergrundbild (Holz) von `images.unsplash.com`.
- Zwei WAV-Dateien aus diesem Repository, direkt per GitHub-URL geladen:
  - Senden: `…/Uboat-Widget/raw/refs/heads/main/morse_Fritz_an_BdU_outgoing.wav`
  - Empfangen: `…/Uboat-Widget/raw/8d82631…/morse_BDU_anFritz_1930s_far.wav` (fester Commit)
- Die gewählte KI-API (Google Gemini oder OpenAI-kompatibel).

Gehäuse 520×520 px, transparenter Body. DOM: `radio-device` mit Metallecken und Schrauben, `header-bar` (Badge „ENIGMA M4“, `status-light`), `screen-container` mit `chat-log`, `controls` (`user-input`, Senden), `model-badge`, `gear-icon` und das Overlay `settings-panel`.

## Funktionsbereiche
| Bereich | Funktionen | Aufgabe |
|---|---|---|
| Start | `window.onload`, `loadSettings`, `restoreChatLog` | Einstellungen, Verlauf, Zusammenfassung und Cache-Info aus `localStorage` laden; Verlauf ohne Schreibmaschinen-Effekt anzeigen |
| Senden | `sendMessage` | „Status:“ erkennen, Meldung anzeigen, Ton, API-Aufruf; nur bei Erfolg Meldung und Antwort speichern, Antwort ausgeben, Zusammenfassung und Cache-Erneuerung anstoßen |
| API | `callApi`, `callGemini`, `callUniversal`, `handleGeminiResponse`, `normalizeBaseUrl` | Je nach `apiType` Gemini oder OpenAI-kompatibel aufrufen, Antwort und Token-Verbrauch auswerten |
| Caching | `createOrUpdateCache`, `updateCacheStatus`, `updateTokenEstimate` | Explizites Gemini-Caching des Systemkontexts, Statusanzeige, Token-Schätzung (Zeichen ÷ 4) |
| Gedächtnis | `addToHistory`, `trimHistory`, `getContextHistory`, `summarizeHistory`, `updateHistoryDisplay`, `clearHistory`, `clearLastFive` | Verlauf speichern und kürzen (Zusammenfassungsstand wandert mit), ältere Funksprüche zusammenfassen |
| Einstellungen | `toggleSettings`, `toggleApiTypeUI`, `saveSettings`, `clearSettings`, `fetchModels`, `updateModelBadge` | Overlay, Speichern mit Cache-Invalidierung, Zurücksetzen, Modellliste |
| Rückfragen | `confirmInWidget`, `cancelConfirm`, `flashButton` | Rückfragen und Hinweise im Widget statt `confirm()`/`alert()`, die eine OBS-Browserquelle nicht anzeigt (seit 1.2.1): erster Klick fragt auf dem Button, zweiter bestätigt |
| Ton | `playSendSound`, `playReceiveSound`, `stopReceiveSound` | Sende-Ton abwarten, Empfangs-Ton (optional Loop) während der Ausgabe; nicht ladbare Töne werden übersprungen |
| Chat-Modus | `applyChatMode`, `connectChat`, `getChatInstructions`, `processChatQueue`, `postChatResult`, `cleanChatAnswer`, `chatUserText`, `isQuotaError`, `normalizeChatServer`, `setChatStatus` | Verbindung zum Companion-Server (EventSource), Warteschlange mit Vorrang des Kaleu, Chat-Anfrage an die KI ohne Verlaufseintrag, Antwort oder Fehler an den Server |
| Export/Import | `buildExportData`, `exportData`, `downloadExport`, `loadImportFile`, `parseImportData`, `importData`, `updatePromptBackupInfo`, `restorePromptBackup` | Stand als JSON exportieren (Textfeld, Zwischenablage, Datei), prüfen und importieren, Prompt-Sicherung anzeigen und übernehmen |
| Anzeige | `appendLog`, `typewriterEffect`, `createBduMessageDiv`, `appendTextWithBreaks`, `scrollToBottom` | Meldungen ins Display schreiben, Antwort zeichenweise (45 ms); Inhalte nur als Text, nie als HTML |

## Kontextaufbau je Anfrage
Systemtext (bei beiden API-Typen gleich aufgebaut):

```
SAFETY_RULES
Persönlichkeits-Prompt (systemPrompt)
=== BOOT-INFORMATIONEN ===  bootContext
=== AKTUELLER STATUS ===    currentStatus
=== BISHERIGE FUNKSPRÜCHE (Zusammenfassung) ===  historySummary   (nur wenn vorhanden)
=== ENDE INFORMATIONEN ===
```

Dazu kommen Verlaufseinträge im Volltext (vor der neuen Meldung) und die neue Meldung. `getContextHistory` wählt dafür bei beiden API-Typen alle noch nicht zusammengefassten Einträge ab `lastSummaryIndex`, mindestens die letzten 4 (`CONTEXT_MIN_ENTRIES`), höchstens die letzten 10 (`CONTEXT_MAX_ENTRIES`), beginnend mit einer Kaleu-Meldung. Im Normalfall sind das 4–6 Einträge; jeder frühere Funkspruch steht damit genau einmal im Kontext, entweder im Volltext oder in der Zusammenfassung.
- Gemini: `maxOutputTokens` 450, `temperature` 1.0, Safety-Schwellen `BLOCK_ONLY_HIGH`.
- Universal: `max_tokens` 450, `temperature` 1.0, Endpunkt `<Base-URL>/v1/chat/completions` (Standard `https://api.openai.com`; `normalizeBaseUrl` entfernt abschließendes `/` und `/v1`), Schlüssel als `Bearer`.

Die neue Meldung kommt erst nach erfolgreicher Antwort in den Verlauf. Schlägt der Aufruf fehl, bleibt sie nur im Display stehen.

## Chat-Anfragen (Chat-Modus)
Gleicher Kontextaufbau wie oben, zusätzlich `CHAT_RULES` (feste Konstante neben `SAFETY_RULES`) und die editierbare Chat-Persönlichkeit (`getChatInstructions`): ohne Cache am Ende des Systemtexts, mit Gemini-Cache vor der Meldung (der Systemtext liegt dann im Cache). Die Meldung geht als „Funkspruch aus dem Chat (nicht vom Kaleu): …“, Antwortbudget 200 Tokens. `cleanChatAnswer` entfernt Markdown, eine eigene Kopfzeile („BdU an …:“) und Zeilenumbrüche. Chat-Anfragen ändern weder Verlauf, Zusammenfassung, Status noch Display. Sie warten, solange ein eigener Funkspruch läuft, und bis 60 s nach dem letzten eigenen Senden (`CHAT_KALEU_PRIORITY_MS`). HTTP 429 bzw. `RESOURCE_EXHAUSTED` meldet das Widget als `quota`, der Server verhängt dann Funkstille.

## Caching (nur Gemini)
- Nur wenn `cachingEnabled` und der Modellname „1.5“ oder „2.5“ enthält. Andere Modelle laufen ohne explizites Caching; bei „2.0“ wird implizites Caching angenommen.
- `createOrUpdateCache` legt den Systemtext als `cachedContents` mit TTL 3600 s an und speichert Name und Ablaufzeit. Fehler (z. B. weniger als 2.048 Tokens) führen ohne Abbruch zum Aufruf ohne Cache und setzen `cacheCreationFailed`: Bis zum nächsten Speichern der Einstellungen, „RESET“ oder Neuladen gibt es keinen weiteren Versuch (sonst kostet jede Meldung einen zusätzlichen Aufruf).
- Invalidiert wird bei geänderten Einstellungen, „Status:“-Meldung, neuer Zusammenfassung, gelöschtem Verlauf und nach 8 Antworten. Der alte Cache wird nicht gelöscht, er läuft bei Google aus.

## Gedächtnis
- Verlauf: Einträge `{role: "user"|"assistant", text, timestamp}`, höchstens 100 (`MAX_HISTORY_ITEMS`). Kürzen läuft über `trimHistory`, das `lastSummaryIndex` um die Zahl entfernter Einträge verringert; „LETZTE 5 LÖSCHEN“ begrenzt den Index auf die Verlaufslänge.
- Nach jeder Antwort: Sind seit `lastSummaryIndex` mindestens 8 Einträge dazugekommen, fasst `summarizeHistory` alles ab `lastSummaryIndex` bis auf die letzten 4 Einträge zusammen (gleiches Modell, `temperature` 0.3, Budget 300 Tokens; abgeschnittene oder leere Ergebnisse gelten als Fehlschlag) und hängt das Ergebnis an `historySummary` an. Die Zusammenfassung wächst damit unbegrenzt.
- Schlägt die Zusammenfassung fehl, bleibt der Verlauf unverändert. Der nächste Versuch folgt erst nach 4 weiteren Einträgen (`summaryPauseEntries`, 2 Funksprüche); die Fehlermeldung erscheint einmal je Fehlerserie im Display. Bis dahin gehen bis zu 10 Einträge im Volltext mit; bei längerem Ausfall fallen die ältesten heraus. Pause und Meldungsmerker liegen nur im RAM.

## Datenhaltung (`localStorage`)
| Schlüssel | Inhalt |
|---|---|
| `bdu_api_key` | API-Schlüssel (Klartext) |
| `bdu_api_type` | `gemini` oder `universal` |
| `bdu_custom_base_url` | Base-URL im Universal-Modus |
| `bdu_current_model` | Modellname |
| `bdu_caching_enabled` | Explizites Caching an/aus |
| `bdu_system_prompt` | Persönlichkeits-Prompt |
| `bdu_boot_context` | Boot-Kontext |
| `bdu_current_status` | Aktueller Status |
| `bdu_loop_sound`, `bdu_sound_volume` | Ton-Einstellungen |
| `bdu_conversation_history` | Verlauf (JSON) |
| `bdu_history_summary`, `bdu_last_summary_index` | Zusammenfassung und Stand |
| `bdu_cache_name`, `bdu_cache_expires` | Gemini-Cache |
| `bdu_widget_version` | Zuletzt geladene `WIDGET_VERSION` |
| `bdu_system_prompt_backup` | Eigener Prompt, gesichert bevor der Versionsabgleich ihn ersetzt hat |
| `bdu_chat_enabled`, `bdu_chat_server_url` | Chat-Modus an/aus, Adresse des Companion-Servers (Standard `http://localhost:3000`) |
| `bdu_chat_personality` | Ton nur für Chat-Antworten (Standard `DEFAULT_CHAT_PERSONALITY`) |

Der Speicher hängt an der Herkunft der Seite. In OBS sind „Lokale Datei“ (`http://absolute`) und eine `file:///`-URL verschiedene Herkünfte; ein Wechsel der Einbindung startet mit leeren Einstellungen. Übertragen lässt sich der Stand mit Export/Import (`docs/specs/export-import.md`).

## Standardwerte
`DEFAULT_PROMPT`, `DEFAULT_CONTEXT`, `DEFAULT_STATUS`, `DEFAULT_MODEL` (`gemini-3.5-flash-lite`), `DEFAULT_LOOP_SOUND` (an) und `DEFAULT_VOLUME` (0,5) gelten für den Erststart und für „RESET“ gleichermaßen.

## Versionierung im Code
`loadSettings` vergleicht `bdu_widget_version` mit `WIDGET_VERSION`. Bei Abweichung wird der gespeicherte Persönlichkeits-Prompt durch `DEFAULT_PROMPT` ersetzt, der Cache wird invalidiert. Seit 1.1.0 wird ein eigener Prompt vorher in `bdu_system_prompt_backup` gesichert und lässt sich in den Einstellungen zurückholen. Ein Import setzt `bdu_widget_version` auf die aktuelle Version, damit der importierte Prompt bleibt.

## Schnittstellen
| Ziel | Aufruf | Zweck |
|---|---|---|
| Gemini | `GET /v1beta/models` | Modellliste (auch im Universal-Modus, siehe `docs/BUGS.md`) |
| Gemini | `POST /v1beta/models/{model}:generateContent` | Antwort und Zusammenfassung |
| Gemini | `POST /v1beta/cachedContents` | Kontext-Cache anlegen |
| OpenAI-kompatibel | `POST {base}/v1/chat/completions` | Antwort und Zusammenfassung |
| Companion-Server (nur Chat-Modus) | `GET {server}/api/bdu/stream` (Server-Sent Events, Ereignis `request` mit `{id, text}`) | Chat-Anfragen empfangen |
| Companion-Server (nur Chat-Modus) | `POST {server}/api/bdu/answer` mit `{id, status: ok/quota/error, text?, error?}` | Antwort oder Fehler melden |

Ohne Chat-Modus kein Kontakt zum Companion-Server und keine Twitch-Anbindung. Im Chat-Modus kennt das Widget keine Twitch-Zugangsdaten; Limits, Funkstille und Chat-Versand liegen im Server (ADR 0004).
