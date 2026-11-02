# API-Anbindung und Caching

## Ziel
Antworten über Google Gemini (Standard) oder eine OpenAI-kompatible API erzeugen, bei Gemini mit möglichst wenig Token-Verbrauch.

## Verhalten
- API-Typ per Radiobutton: Gemini oder Universal. Universal blendet Caching-Einstellungen aus und zeigt das Feld für die Base-URL (Standard `https://api.openai.com`).
- „MODELLE SUCHEN“ listet Gemini-Modelle mit `generateContent`; Klick übernimmt den Namen.
- Gemini mit Modellnamen „1.5“ oder „2.5“ und aktiviertem Caching: Systemtext wird als Cache (TTL 1 h) angelegt und wiederverwendet. Scheitert das (z. B. unter 2.048 Tokens), läuft die Anfrage ohne Cache.
- Token-Verbrauch und gecachte Tokens stehen in der Konsole; die Einstellungen zeigen eine Schätzung (Zeichen ÷ 4).
- Das Modell-Badge unten zeigt „POWERED BY GEMINI <Modell>“ bzw. „UNIVERSAL API · <Modell>“.

## Nicht-Ziele
Anthropic- oder andere nicht OpenAI-kompatible Formate; Abrechnung oder Kontingentanzeige.

## Akzeptanzkriterien
- Gemini mit gültigem Schlüssel und gefundenem Modell antwortet.
- Bei aktivem Caching meldet die Konsole „Cached: … Tokens“ ab der zweiten Anfrage.
- Universal mit OpenAI-kompatiblem Endpunkt antwortet (vom Autor nicht getestet).

## Berührte Dateien/Funktionen
`index.html`: `callApi`, `callGemini`, `callUniversal`, `handleGeminiResponse`, `createOrUpdateCache`, `updateCacheStatus`, `updateTokenEstimate`, `fetchModels`, `toggleApiTypeUI`, `updateModelBadge`.

## Status
umgesetzt (1.0.0); Universal-Modus ungetestet.
