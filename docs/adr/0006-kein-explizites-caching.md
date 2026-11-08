# ADR 0006: Kein explizites Gemini-Caching mehr

## Status
Angenommen (Nutzer, 08.11.2026). Umsetzung geplant für 1.4.0 (`docs/specs/plan-1.4.0.md`).

## Kontext
Seit 1.0.0 legt das Widget bei Gemini-Modellen mit „1.5“ oder „2.5“ im Namen den Systemtext als `cachedContents` an (TTL 1 h) und verwendet ihn wieder. Befunde vom 08.11.2026:
- Laut Googles Preisseite gibt es explizites Caching für Flash-Lite im kostenlosen Kontingent nicht. Das Widget versucht es trotzdem standardmäßig; das kostet nach jedem Neuladen einen erfolglosen Aufruf (B13 begrenzt das nur).
- Das Standardmodell `gemini-3.5-flash-lite` nutzt den Weg ohnehin nicht (Erkennung über den Modellnamen, `docs/OFFEN.md`).
- Für bezahlte Nutzer ist die Ersparnis gering: Der Systemtext hat rund 3.000 Tokens, der Cache kostet eine stündliche Speichergebühr, und wegen B18 wird er etwa jede zweite Meldung neu angelegt (alter Cache läuft bis zum TTL-Ende weiter).
- Der Weg wurde nie mit echter API getestet. Er umfasst rund 160 Zeilen (Schalter, Statusanzeige, drei Speicherschlüssel, Export-Feld, Invalidierung an sieben Stellen) plus Tests.
- Google cacht ab Gemini 2.5 automatisch („implizites Caching“): gleichbleibende Anfänge von Anfragen werden ohne Code und ohne Speichergebühr wiederverwendet. Einige OpenAI-kompatible Anbieter machen das ebenso. Ob das implizite Caching im kostenlosen Kontingent greift, ist [UNGEKLÄRT]; dort kosten Tokens aber ohnehin nichts.
- Der Nutzer verwendet das Caching selbst nicht mehr.

## Entscheidung
- Explizites Caching wird vollständig entfernt: kein Aufruf von `cachedContents`, kein Schalter, keine Cache-Statusanzeige, keine Speicherschlüssel `bdu_caching_enabled`, `bdu_cache_name`, `bdu_cache_expires` (beim Laden werden vorhandene entfernt).
- Für das implizite Caching gilt als feste Regel im Kontextaufbau: **Was sich selten ändert, steht vorne; was sich oft ändert, hinten.** Reihenfolge wie heute: `SAFETY_RULES` → Persönlichkeit (mit vollständiger Chronologie) → Boot-Kontext → Status → Zusammenfassung → Verlauf → neue Meldung; im Chat-Modus `CHAT_RULES` und Chat-Persönlichkeit am Ende des Systemtexts.
- Die Konsole meldet weiterhin `cachedContentTokenCount` aus der Antwort (bei Gemini „automatisch zwischengespeichert“).
- Export enthält kein `cachingEnabled` mehr; der Import nimmt ältere Exporte mit dem Feld weiter an und ignoriert es. `formatVersion` bleibt 1.

## Verworfene Alternativen
- Caching behalten, aber standardmäßig aus: Pflegeaufwand und Fehler B18 bleiben, Nutzen für fast niemanden.
- Caching reparieren (B18, Erkennung über Fehlschlag statt Modellname): Aufwand ohne Nutzen im kostenlosen Kontingent, nicht testbar ohne bezahlten Schlüssel.
- Chronologie kürzen oder nur den Abschnitt zum aktuellen Jahr senden: verworfen vom Nutzer (08.11.2026), die Chronologie bleibt vollständig und steht im fest bleibenden Anfang.

## Konsequenzen
- B18 und der Punkt „Caching-Erkennung über Modellnamen“ in `docs/OFFEN.md` entfallen.
- Bezahlte Gemini-Nutzer verlieren die garantierte Ersparnis des expliziten Caches und sind auf das implizite Caching angewiesen.
- Wer den Kontextaufbau ändert, muss die Reihenfolge-Regel einhalten, sonst greift das implizite Caching nicht mehr.
- Ab 1.4.0 verweisen Kontextaufbau und Generierungswerte nur noch auf einen Gemini-Weg (heute „ohne Cache“); `benchmark/bench.html` bleibt dadurch unverändert.
