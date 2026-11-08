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
| Start | `window.onload`, `loadSettings`, `restoreChatLog` | Einstellungen, Verlauf und Zusammenfassung aus `localStorage` laden, Reste des früheren Cachings entfernen; Verlauf ohne Schreibmaschinen-Effekt anzeigen |
| Senden | `sendMessage` | „Status:“ erkennen, Meldung anzeigen, Ton, API-Aufruf; nur bei Erfolg Meldung und Antwort speichern, Antwort ausgeben, Zusammenfassung anstoßen |
| API | `callApi`, `callGemini`, `callUniversal`, `handleGeminiResponse`, `normalizeBaseUrl` | Je nach `apiType` Gemini oder OpenAI-kompatibel aufrufen, Antwort und Token-Verbrauch auswerten |
| Token-Anzeige | `updateTokenEstimate`, `updateLastUsage` | Token-Schätzung (Zeichen ÷ 4); Verbrauch der letzten Anfrage und davon automatisch zwischengespeicherter Anteil (seit 1.4.0, nur im RAM) |
| Gedächtnis | `addToHistory`, `trimHistory`, `getContextHistory`, `summarizeHistory`, `requestSummary`, `trimSummaryBlocks`, `saveSummaryMeta`, `updateHistoryDisplay`, `clearHistory`, `clearLastExchange` | Verlauf speichern und kürzen (Zusammenfassungsstand wandert mit), ältere Funksprüche zusammenfassen |
| Einstellungen | `toggleSettings`, `toggleApiTypeUI`, `saveSettings`, `clearSettings`, `fetchModels`, `updateModelBadge` | Overlay, Speichern, Zurücksetzen, Modellliste |
| Chat-Bereich | `setChatSectionOpen`, `toggleChatSection` | Gruppe „Chat-Modus“ in den Einstellungen ein-/ausklappen; offen, wenn der Chat-Modus an ist (seit 1.3.0) |
| Rückfragen | `confirmInWidget`, `cancelConfirm`, `flashButton` | Rückfragen und Hinweise im Widget statt `confirm()`/`alert()`, die eine OBS-Browserquelle nicht anzeigt (seit 1.2.1): erster Klick fragt auf dem Button, zweiter bestätigt |
| Ton | `playSendSound`, `playReceiveSound`, `stopReceiveSound` | Sende-Ton abwarten, Empfangs-Ton (optional Loop) während der Ausgabe; nicht ladbare Töne werden übersprungen |
| Chat-Modus | `applyChatMode`, `connectChat`, `getChatInstructions`, `processChatQueue`, `postChatResult`, `cleanChatAnswer`, `chatUserText`, `isQuotaError`, `normalizeChatServer`, `setChatStatus` | Verbindung zum Companion-Server (EventSource), Warteschlange mit Vorrang des Kaleu, Chat-Anfrage an die KI ohne Verlaufseintrag, Antwort oder Fehler an den Server |
| Export/Import | `buildExportData`, `exportData`, `downloadExport`, `loadImportFile`, `parseImportData`, `importData`, `updatePromptBackupInfo`, `restorePromptBackup` | Stand als JSON exportieren (Textfeld, Zwischenablage, Datei), prüfen und importieren, Prompt-Sicherung anzeigen und übernehmen |
| Anzeige | `appendLog`, `typewriterEffect`, `createBduMessageDiv`, `stripAnswerHeader`, `appendTextWithBreaks`, `scrollToBottom` | Meldungen ins Display schreiben, Antwort zeichenweise (45 ms); Inhalte nur als Text, nie als HTML. Eine eigene Kopfzeile des Modells am Antwortanfang („**BdU an U-68:**“) wird entfernt, bevor die Antwort gespeichert und angezeigt wird; ältere gespeicherte Antworten nur in der Anzeige (seit 1.4.0, BUGS B23) |

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

**Benchmark:** `benchmark/bench.html` baut die Anfrage nach demselben Schema nach (Gemini: `callGemini`; Groq/Mistral: `callUniversal`) und übernimmt `SAFETY_RULES`, `CHAT_RULES`, `DEFAULT_CHAT_PERSONALITY`, `getContextHistory`, `chatUserText` und `cleanChatAnswer` als Kopie. Wer Kontextaufbau, diese Konstanten oder die Generierungswerte im Widget ändert, zieht den Benchmark nach (Spec `docs/specs/benchmark.md`); `tests/benchmark_gemini.py` und `tests/benchmark_providers.py` prüfen, dass die Anfragen gleich bleiben.

**Tests:** `tests/` enthält Headless-Tests (Python, Playwright, Chromium) mit simulierten APIs; keine echten Aufrufe, kein privater Funkverlauf (Testdaten werden aus `benchmark/beispiel-kontext.json` erzeugt). Aufruf `python tests/run_all.py`, Anleitung `tests/README.md`.

## Chat-Anfragen (Chat-Modus)
Gleicher Kontextaufbau wie oben, zusätzlich `CHAT_RULES` (feste Konstante neben `SAFETY_RULES`) und die editierbare Chat-Persönlichkeit (`getChatInstructions`): am Ende des Systemtexts. Die Meldung geht als „Funkspruch aus dem Chat (nicht vom Kaleu): …“, Antwortbudget 200 Tokens. `cleanChatAnswer` entfernt Markdown, eine eigene Kopfzeile („BdU an …:“) und Zeilenumbrüche. Chat-Anfragen ändern weder Verlauf, Zusammenfassung, Status noch Display. Sie warten, solange ein eigener Funkspruch läuft, und bis 60 s nach dem letzten eigenen Senden (`CHAT_KALEU_PRIORITY_MS`). HTTP 429 bzw. `RESOURCE_EXHAUSTED` meldet das Widget als `quota`, der Server verhängt dann Funkstille.

## Caching
Kein explizites Caching (seit 1.4.0, ADR 0006; vorher `cachedContents` für Modelle mit „1.5“/„2.5“ im Namen). Gemini ab 2.5 und einige OpenAI-kompatible Anbieter cachen gleichbleibende Anfänge von Anfragen automatisch. Deshalb gilt für den Kontextaufbau: **Festes vorne, Wechselndes hinten** (Reihenfolge oben). Wer etwas einfügt, das sich oft ändert, setzt es hinter den Boot-Kontext. Den Verbrauch der letzten Anfrage und den automatisch zwischengespeicherten Anteil zeigt die Token-Schätzung in den Einstellungen (Gemini `cachedContentTokenCount`, OpenAI-kompatibel `prompt_tokens_details.cached_tokens`). Ob Googles automatisches Caching im kostenlosen Kontingent greift, ist [UNGEKLÄRT].

## Gedächtnis
- Verlauf: Einträge `{role: "user"|"assistant", text, timestamp}`, höchstens 100 (`MAX_HISTORY_ITEMS`). Kürzen läuft über `trimHistory`, das `lastSummaryIndex` um die Zahl entfernter Einträge verringert; „LETZTEN FUNKSPRUCH LÖSCHEN“ (`clearLastExchange`, seit 1.3.2) entfernt Meldung und Antwort als Paar, so dass der Verlauf immer mit einer Antwort endet, und begrenzt den Index auf die Verlaufslänge.
- Nach jeder Antwort: Sind seit `lastSummaryIndex` mindestens 8 Einträge dazugekommen, fasst `summarizeHistory` alles ab `lastSummaryIndex` bis auf die letzten 4 Einträge zusammen (gleiches Modell, `temperature` 0.3, Budget 300 Tokens; abgeschnittene oder leere Ergebnisse gelten als Fehlschlag) und hängt das Ergebnis an `historySummary` an. Spaßmeldungen ohne Bezug zur Feindfahrt und die Antworten darauf lässt die KI weg (`SUMMARY_FUN_RULE`, Wortlaut vom Nutzer freigegeben); bestehen die Funksprüche nur daraus, antwortet sie „KEINE MELDUNG“, dann wird nichts angehängt und der Stand trotzdem weitergesetzt.
- **Verdichten** (seit 1.4.0): Würde die Zusammenfassung mit dem nächsten Teil (geschätzt `SUMMARY_PART_ESTIMATE_CHARS` = 400 Zeichen) länger als `SUMMARY_MAX_CHARS` (2.000 Zeichen), geht in derselben einen Anfrage die bisherige Zusammenfassung mit den neuen Funksprüchen und dem Boot-Kontext (nur zur Einordnung, nicht wiederholen) an die KI. Ergebnis: eine Gesamtzusammenfassung mit Ziel `SUMMARY_CONDENSE_TARGET_CHARS` (1.200 Zeichen, „etwa 10 kurze Sätze“), Budget 1.500 Tokens, aktuelle Feindfahrt ausführlicher, frühere Fahrten knapp, ohne Spaßmeldungen. Sie **ersetzt** `historySummary`. Abgeschnitten, leer, „KEINE MELDUNG“ oder nicht kürzer als vorher gilt als Fehlschlag. **Rückfall** in diesem Fall (Nutzerentscheidung 08.11.2026): `trimSummaryBlocks` entfernt die ältesten Abschnitte (durch Leerzeilen getrennt), bis höchstens 1.600 Zeichen übrig sind, ohne weiteren Aufruf; der nächste Versuch hängt dann wieder normal an. Bei API-Fehlern (Kontingent, Netz) wird nicht gekürzt. Die Konsole meldet Abschlussgrund und Token-Verbrauch jeder Zusammenfassung („[SUMMARY] 📊“).
- Zeitpunkt und Art der letzten Zusammenfassung (angehängt, verdichtet, nichts angehängt, gekürzt) speichert `saveSummaryMeta` nur für die Anzeige in den Einstellungen: „08.11., 17:42 (angehängt), 925 Zeichen; 2 Funksprüche noch nicht zusammengefasst“. Im Normalfall fasst das Widget alle 2 Funksprüche zusammen und behält die letzten 2 im Volltext; die Zahl pendelt deshalb zwischen 2 und 3.
- Schlägt die Zusammenfassung fehl, bleibt der Verlauf unverändert. Der nächste Versuch folgt erst nach 4 weiteren Einträgen (`summaryPauseEntries`, 2 Funksprüche); die Fehlermeldung erscheint einmal je Fehlerserie im Display. Bis dahin gehen bis zu 10 Einträge im Volltext mit; bei längerem Ausfall fallen die ältesten heraus. Pause und Meldungsmerker liegen nur im RAM.

## Datenhaltung (`localStorage`)
| Schlüssel | Inhalt |
|---|---|
| `bdu_api_key` | API-Schlüssel (Klartext) |
| `bdu_api_type` | `gemini` oder `universal` |
| `bdu_custom_base_url` | Base-URL im Universal-Modus |
| `bdu_current_model` | Modellname |
| `bdu_system_prompt` | Persönlichkeits-Prompt |
| `bdu_boot_context` | Boot-Kontext |
| `bdu_current_status` | Aktueller Status |
| `bdu_loop_sound`, `bdu_sound_volume` | Ton-Einstellungen |
| `bdu_conversation_history` | Verlauf (JSON) |
| `bdu_history_summary`, `bdu_last_summary_index` | Zusammenfassung und Stand |
| `bdu_widget_version` | Zuletzt geladene `WIDGET_VERSION` |
| `bdu_system_prompt_backup` | Eigener Prompt, gesichert bevor der Versionsabgleich ihn ersetzt hat |
| `bdu_chat_enabled`, `bdu_chat_server_url` | Chat-Modus an/aus, Adresse des Companion-Servers (Standard `http://localhost:3000`) |
| `bdu_chat_personality` | Ton nur für Chat-Antworten (Standard `DEFAULT_CHAT_PERSONALITY`) |
| `bdu_last_summary_meta` | Zeitpunkt und Art der letzten Zusammenfassung (JSON `{at, type}`), nur Anzeige; nicht im Export (seit 1.4.0) |

Entfallen seit 1.4.0 (werden beim Laden entfernt, `LEGACY_CACHE_KEYS`): `bdu_caching_enabled`, `bdu_cache_name`, `bdu_cache_expires`.

Der Speicher hängt an der Herkunft der Seite. In OBS sind „Lokale Datei“ (`http://absolute`) und eine `file:///`-URL verschiedene Herkünfte; ein Wechsel der Einbindung startet mit leeren Einstellungen. Übertragen lässt sich der Stand mit Export/Import (`docs/specs/export-import.md`).

## Standardwerte
`DEFAULT_PROMPT`, `DEFAULT_CONTEXT`, `DEFAULT_STATUS`, `DEFAULT_MODEL` (`gemini-3.5-flash-lite`), `DEFAULT_LOOP_SOUND` (an) und `DEFAULT_VOLUME` (0,5) gelten für den Erststart und für „RESET“ gleichermaßen.

## Versionierung im Code
`loadSettings` vergleicht `bdu_widget_version` mit `WIDGET_VERSION`. Bei Abweichung wird der gespeicherte Persönlichkeits-Prompt durch `DEFAULT_PROMPT` ersetzt. Seit 1.1.0 wird ein eigener Prompt vorher in `bdu_system_prompt_backup` gesichert und lässt sich in den Einstellungen zurückholen. Ein Import setzt `bdu_widget_version` auf die aktuelle Version, damit der importierte Prompt bleibt.

## Schnittstellen
| Ziel | Aufruf | Zweck |
|---|---|---|
| Gemini | `GET /v1beta/models` | Modellliste (auch im Universal-Modus, siehe `docs/BUGS.md`) |
| Gemini | `POST /v1beta/models/{model}:generateContent` | Antwort und Zusammenfassung |
| OpenAI-kompatibel | `POST {base}/v1/chat/completions` | Antwort und Zusammenfassung |
| Companion-Server (nur Chat-Modus) | `GET {server}/api/bdu/stream` (Server-Sent Events, Ereignis `request` mit `{id, text}`) | Chat-Anfragen empfangen |
| Companion-Server (nur Chat-Modus) | `POST {server}/api/bdu/answer` mit `{id, status: ok/quota/error, text?, error?}` | Antwort oder Fehler melden |

Ohne Chat-Modus kein Kontakt zum Companion-Server und keine Twitch-Anbindung. Im Chat-Modus kennt das Widget keine Twitch-Zugangsdaten; Limits, Funkstille und Chat-Versand liegen im Server (ADR 0004).
