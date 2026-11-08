# API-Anbindung und Token-Verbrauch

## Ziel
Antworten über Google Gemini (Standard) oder eine OpenAI-kompatible API erzeugen, mit möglichst wenig Token-Verbrauch und ohne zusätzliche Aufrufe.

## Verhalten
- API-Typ per Radiobutton: Gemini oder Universal. Universal zeigt das Feld für die Base-URL (Standard `https://api.openai.com`; Angabe mit oder ohne `/v1`, z. B. Ollama `http://localhost:11434`). Bekannte Adressen (README, Stand 1.3.0): Groq `https://api.groq.com/openai`, OpenRouter `https://openrouter.ai/api`, Mistral `https://api.mistral.ai`. Eine Auswahlliste dafür ist erwogen, aber erst sinnvoll, wenn ein Anbieter im Benchmark aus dem Browser funktioniert (`docs/OFFEN.md`).
- „MODELLE SUCHEN“ listet bei Gemini die Modelle mit `generateContent`, im Universal-Modus die Einträge von `{base}/v1/models`; Klick übernimmt den Namen.
- Kein explizites Caching (seit 1.4.0, ADR 0006). Der Systemtext ist so aufgebaut, dass sein langer, fester Anfang (Sicherheitsregeln, Persönlichkeit mit vollständiger Chronologie, Boot-Kontext) bei jeder Anfrage gleich bleibt; Gemini ab 2.5 und manche OpenAI-kompatiblen Anbieter speichern ihn dann automatisch zwischen.
- Die Token-Schätzung in den Einstellungen (Zeichen ÷ 4, beide API-Typen) zeigt zusätzlich den Verbrauch der letzten Anfrage und den davon automatisch zwischengespeicherten Anteil (Gemini `usageMetadata.cachedContentTokenCount`, OpenAI-kompatibel `usage.prompt_tokens_details.cached_tokens`). Der Wert liegt nur im RAM; nach dem Neuladen steht dort „noch keine seit dem Laden“.
- Das Modell-Badge unten zeigt „POWERED BY GEMINI <Modell>“ bzw. „UNIVERSAL API · <Modell>“.

## Nicht-Ziele
Anthropic- oder andere nicht OpenAI-kompatible Formate; Abrechnung oder Kontingentanzeige; explizites Caching (ADR 0006).

## Akzeptanzkriterien
- Gemini mit gültigem Schlüssel und gefundenem Modell antwortet.
- In keinem Ablauf geht eine Anfrage an `cachedContents`; Reste früherer Fassungen (`bdu_caching_enabled`, `bdu_cache_name`, `bdu_cache_expires`) sind nach dem Laden entfernt.
- Zwei aufeinanderfolgende Anfragen mit geändertem Status oder geänderter Zusammenfassung beginnen bis einschließlich Boot-Kontext mit demselben Text.
- Nach einer Antwort zeigt die Token-Schätzung „Letzte Anfrage: … Tokens, davon … automatisch zwischengespeichert“.
- Universal mit OpenAI-kompatiblem Endpunkt antwortet (vom Autor nicht getestet).

## Berührte Dateien/Funktionen
`index.html`: `callApi`, `callGemini`, `callUniversal`, `handleGeminiResponse`, `updateTokenEstimate`, `updateLastUsage`, `fetchModels`, `toggleApiTypeUI`, `updateModelBadge`, `normalizeBaseUrl`, `loadSettings` (`LEGACY_CACHE_KEYS`).

## Status
umgesetzt (1.0.0), Fehlerbehebungen in 1.0.1; explizites Caching entfernt und Verbrauchsanzeige ergänzt in 1.4.0 (`tests/summary_condense.py`, `tests/widget_regression.py`). Universal-Modus nur mit simulierter API getestet. Ob Googles automatisches Caching im kostenlosen Kontingent greift, ist [UNGEKLÄRT]; die Anzeige in den Einstellungen macht es sichtbar.
