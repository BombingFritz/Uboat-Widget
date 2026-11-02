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
| Senden | `sendMessage` | „Status:“ erkennen, Meldung anzeigen und speichern, Ton, API-Aufruf, Antwort ausgeben, Zusammenfassung und Cache-Erneuerung anstoßen |
| API | `callApi`, `callGemini`, `callUniversal`, `handleGeminiResponse` | Je nach `apiType` Gemini oder OpenAI-kompatibel aufrufen, Antwort und Token-Verbrauch auswerten |
| Caching | `createOrUpdateCache`, `updateCacheStatus`, `updateTokenEstimate` | Explizites Gemini-Caching des Systemkontexts, Statusanzeige, Token-Schätzung (Zeichen ÷ 4) |
| Gedächtnis | `addToHistory`, `summarizeHistory`, `updateHistoryDisplay`, `clearHistory`, `clearLastFive` | Verlauf speichern und kürzen, ältere Funksprüche zusammenfassen |
| Einstellungen | `toggleSettings`, `toggleApiTypeUI`, `saveSettings`, `clearSettings`, `fetchModels`, `updateModelBadge` | Overlay, Speichern mit Cache-Invalidierung, Zurücksetzen, Modellliste |
| Ton | `playSendSound`, `playReceiveSound`, `stopReceiveSound` | Sende-Ton abwarten, Empfangs-Ton (optional Loop) während der Ausgabe |
| Anzeige | `appendLog`, `typewriterEffect`, `scrollToBottom` | Meldungen ins Display schreiben, Antwort zeichenweise (45 ms) |

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

Dazu kommen die letzten Verlaufseinträge im Volltext und die neue Meldung:
- Gemini: letzte 4 Einträge, `maxOutputTokens` 450, `temperature` 1.0, Safety-Schwellen `BLOCK_ONLY_HIGH`.
- Universal: letzte 10 Einträge, `max_tokens` 450, `temperature` 1.0, Endpunkt `<Base-URL>/v1/chat/completions` (Standard `https://api.openai.com`), Schlüssel als `Bearer`.

Die neue Meldung steht zu diesem Zeitpunkt schon im Verlauf und wird dadurch doppelt gesendet (siehe `docs/BUGS.md`).

## Caching (nur Gemini)
- Nur wenn `cachingEnabled` und der Modellname „1.5“ oder „2.5“ enthält. Andere Modelle laufen ohne explizites Caching; bei „2.0“ wird implizites Caching angenommen.
- `createOrUpdateCache` legt den Systemtext als `cachedContents` mit TTL 3600 s an und speichert Name und Ablaufzeit. Fehler (z. B. weniger als 2.048 Tokens) führen ohne Abbruch zum Aufruf ohne Cache.
- Invalidiert wird bei geänderten Einstellungen, „Status:“-Meldung, neuer Zusammenfassung, gelöschtem Verlauf und nach 8 Antworten. Der alte Cache wird nicht gelöscht, er läuft bei Google aus.

## Gedächtnis
- Verlauf: Einträge `{role: "user"|"assistant", text, timestamp}`, höchstens 100 (`MAX_HISTORY_ITEMS`).
- Nach jeder Antwort: Sind seit `lastSummaryIndex` mindestens 8 Einträge dazugekommen, fasst `summarizeHistory` alles ab `lastSummaryIndex` bis auf die letzten 4 Einträge zusammen (höchstens 150 Tokens, gleiches Modell) und hängt das Ergebnis an `historySummary` an. Die Zusammenfassung wächst damit unbegrenzt.
- Schlägt die Zusammenfassung fehl, bleibt der Verlauf unverändert; der nächste Versuch folgt nach der nächsten Antwort.

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

Der Speicher hängt an der Herkunft der Seite. In OBS sind „Lokale Datei“ (`http://absolute`) und eine `file:///`-URL verschiedene Herkünfte; ein Wechsel der Einbindung startet mit leeren Einstellungen.

## Versionierung im Code
`loadSettings` vergleicht `bdu_widget_version` mit `WIDGET_VERSION`. Bei Abweichung wird der gespeicherte Persönlichkeits-Prompt verworfen und durch `DEFAULT_PROMPT` ersetzt, der Cache wird invalidiert. Eigene Prompt-Anpassungen gehen dabei ohne Rückfrage verloren.

## Schnittstellen
| Ziel | Aufruf | Zweck |
|---|---|---|
| Gemini | `GET /v1beta/models` | Modellliste (auch im Universal-Modus, siehe `docs/BUGS.md`) |
| Gemini | `POST /v1beta/models/{model}:generateContent` | Antwort und Zusammenfassung |
| Gemini | `POST /v1beta/cachedContents` | Kontext-Cache anlegen |
| OpenAI-kompatibel | `POST {base}/v1/chat/completions` | Antwort und Zusammenfassung |

Kein Kontakt zum Auth-Server („Twitch Companion JS server“) und keine Twitch-Anbindung. Geplanter Server-Modus siehe `docs/OFFEN.md`.
