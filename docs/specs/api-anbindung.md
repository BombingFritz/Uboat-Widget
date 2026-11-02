# API-Anbindung und Caching

## Ziel
Antworten über Google Gemini (Standard) oder eine OpenAI-kompatible API erzeugen, bei Gemini mit möglichst wenig Token-Verbrauch.

## Verhalten
- API-Typ per Radiobutton: Gemini oder Universal. Universal blendet Caching-Einstellungen aus und zeigt das Feld für die Base-URL (Standard `https://api.openai.com`; Angabe mit oder ohne `/v1`, z. B. Ollama `http://localhost:11434`).
- „MODELLE SUCHEN“ listet bei Gemini die Modelle mit `generateContent`, im Universal-Modus die Einträge von `{base}/v1/models`; Klick übernimmt den Namen.
- Gemini mit Modellnamen „1.5“ oder „2.5“ und aktiviertem Caching: Systemtext wird als Cache (TTL 1 h) angelegt und wiederverwendet. Scheitert das (z. B. unter 2.048 Tokens), läuft die Anfrage ohne Cache, und bis zum nächsten Speichern, „RESET“ oder Neuladen wird kein neuer Cache versucht.
- Token-Verbrauch und gecachte Tokens stehen in der Konsole; die Einstellungen zeigen eine Schätzung (Zeichen ÷ 4).
- Das Modell-Badge unten zeigt „POWERED BY GEMINI <Modell>“ bzw. „UNIVERSAL API · <Modell>“.

## Nicht-Ziele
Anthropic- oder andere nicht OpenAI-kompatible Formate; Abrechnung oder Kontingentanzeige.

## Akzeptanzkriterien
- Gemini mit gültigem Schlüssel und gefundenem Modell antwortet.
- Bei aktivem Caching meldet die Konsole „Cached: … Tokens“ ab der zweiten Anfrage.
- Universal mit OpenAI-kompatiblem Endpunkt antwortet (vom Autor nicht getestet).

## Berührte Dateien/Funktionen
`index.html`: `callApi`, `callGemini`, `callUniversal`, `handleGeminiResponse`, `createOrUpdateCache`, `updateCacheStatus`, `updateTokenEstimate`, `fetchModels`, `toggleApiTypeUI`, `updateModelBadge`, `normalizeBaseUrl`.

## Status
umgesetzt (1.0.0), Fehlerbehebungen in 1.0.1; Universal-Modus nur mit simulierter API getestet.
