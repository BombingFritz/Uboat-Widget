# Plan 1.4.0: Caching ausbauen, Zusammenfassung verdichten

## Status
Vom Nutzer geprüft, Entscheidungen D1–D4 getroffen (08.11.2026); Umsetzung folgt. Nach der Umsetzung gehen die Inhalte in `docs/specs/gedaechtnis.md` und `docs/specs/api-anbindung.md` auf, diese Datei entfällt dann.

## Ziel
1. Weniger Code und keine erfolglosen Aufrufe: explizites Gemini-Caching entfernen (ADR 0006).
2. Der Kontext bleibt auch bei langen Einsätzen schlank und aktuell: die Zusammenfassung wird ab einer Obergrenze verdichtet statt endlos verlängert.
3. Spaßmeldungen landen nicht im Gedächtnis: Zusammenfassen und Verdichten lassen sie weg.

Nicht Teil von 1.4.0 (Nutzerentscheidungen 08.11.2026): Button „älteste Hälfte löschen“, KI-Knopf zum Ausmisten des Verlaufs, Kürzen der Chronologie.

## A. Caching ausbauen
- Entfernen: `createOrUpdateCache`, `updateCacheStatus`, Variablen `cachingEnabled`, `cachedContentName`, `cacheExpiresAt`, `cacheCreationFailed`, `messagesSinceLastCache`, der Cache-Zweig in `callGemini` und alle Stellen, die den Cache verwerfen (Laden, Status-Meldung, Zusammenfassung, Verlauf löschen, Speichern, Reset, Import, nach 8 Antworten).
- Einstellungen: Gruppe „Explizites Caching“ und Zeile „Context Caching: …“ entfallen; in der Token-Schätzung entfällt „Minimum für Caching“. Sonst keine Änderung an Layout oder Design.
- Gemini-Aufruf: immer der heutige Weg ohne Cache (Systemtext als `systemInstruction`, Chat-Regeln am Ende des Systemtexts). Die Unterscheidung „2.0 = implizites Caching“ entfällt; alle Modelle laufen gleich.
- Beim Laden werden `bdu_caching_enabled`, `bdu_cache_name`, `bdu_cache_expires` entfernt, falls vorhanden. `clearSettings` braucht sie danach nicht mehr.
- Export ohne `cachingEnabled`; Import älterer Exporte mit dem Feld funktioniert weiter.
- Konsole: Token-Verbrauch wie bisher, `cachedContentTokenCount` als „automatisch zwischengespeichert“.

**Entscheidung D1 (Nutzer, 08.11.2026: ja):** Die Anzahl automatisch zwischengespeicherter Tokens der letzten Anfrage zusätzlich in der Token-Schätzung der Einstellungen stehen (eine Zeile, z. B. „Letzte Anfrage: 3.410 Tokens, davon 2.950 automatisch zwischengespeichert“). So ist ohne Browser-Konsole (OBS) sichtbar, ob Googles implizites Caching im kostenlosen Kontingent greift.

## B. Zusammenfassung verdichten
Heute: Alle 8 neuen Einträge fasst `summarizeHistory` die älteren zu höchstens 3 Sätzen zusammen und hängt sie an `historySummary` an. Die Zusammenfassung wächst unbegrenzt.

Neu:
- Konstante `SUMMARY_MAX_CHARS` (Vorschlag 2.000 Zeichen ≈ 500 Tokens, etwa 5–6 Einzelzusammenfassungen).
- Würde die Zusammenfassung mit dem neuen Teil die Obergrenze überschreiten, schickt `summarizeHistory` **in derselben einen Anfrage** die bisherige Zusammenfassung und die neuen Funksprüche und bittet um eine neue Gesamtzusammenfassung (Ziel höchstens ca. 1.200 Zeichen, damit danach wieder Platz zum Anhängen ist). Das Ergebnis **ersetzt** `historySummary`. Kein zusätzlicher Aufruf gegenüber heute.
- Budget für die Verdichtung eigene Konstante (Vorschlag 600 Tokens), `temperature` 0,3 wie bisher. Abgeschnittene (`MAX_TOKENS`/`length`) oder leere Ergebnisse gelten wie heute als Fehlschlag: Die alte Zusammenfassung bleibt unverändert, Pause und Meldung wie bisher.
- Inhaltliche Vorgabe für die Verdichtung: Aktuelle Feindfahrt ausführlicher, abgeschlossene frühere Fahrten und erledigte Episoden knapp (je höchstens ein Satz). Erhalten bleiben: Versenkungen und Erfolge, Schäden und Verluste, Befehle des BdU, Positionen und Ziele, wiederkehrende Personen.
- Wirkung bei bestehenden langen Zusammenfassungen (z. B. der des Nutzers mit den U-4-Fahrten): Die nächste fällige Zusammenfassung verdichtet automatisch. Ein eigener Knopf ist nicht nötig.

**Entscheidung D2 (Nutzer, 08.11.2026: ja):** Obergrenze 2.000 Zeichen, Ziel nach dem Verdichten ca. 1.200 Zeichen.

**Entscheidung D3 (Nutzer, 08.11.2026: ja):** Die Verdichtung bekommt den Boot-Kontext mit. Damit erkennt die KI die aktuelle Feindfahrt (z. B. U-68 statt U-4), und die Zusammenfassung wiederholt nichts, was schon im Boot-Kontext steht (Boot, Typ, Kommandant, Einsatzgebiet usw.). Kostet nur die Zeichen des Boot-Kontexts in dieser einen Anfrage.

## C. Spaßmeldungen weglassen
Sowohl die normale Zusammenfassung als auch die Verdichtung bekommen die Anweisung, Spaßmeldungen ohne Bezug zur Feindfahrt und die Antworten darauf wegzulassen, ohne darauf hinzuweisen. Der Verlauf selbst bleibt unverändert (Anzeige, Export); die zuletzt 4–6 Einträge im Volltext gehen weiterhin mit, auch wenn sie Spaß enthalten.

Vorgeschlagener Wortlaut (zur Freigabe durch den Nutzer, Beispiele vom Nutzer, 08.11.2026):

> Lass Spaß- und Scherzmeldungen ohne Bezug zur laufenden Feindfahrt weg, ebenso die Antworten darauf. Beispiele: „Kaleu Fritz weigert sich, die Ziele zu rammen. Fordere die Enthebung seines Kommandos“, „Spargelvorräte sind leer, wir benötigen dringend mehr Spargel“, „Bier ist alle, wir brauchen Hilfe!“. Erwähne nicht, dass etwas weggelassen wurde.

**Entscheidung D4 (Nutzer, 08.11.2026: Wortlaut so übernehmen).** Risiko: Ein Rollenspiel-Witz mit Bedeutung für die Geschichte kann mit wegfallen; dann über den Wortlaut nachschärfen.

## Kontextaufbau (Regel aus ADR 0006)
Reihenfolge bleibt: `SAFETY_RULES` → Persönlichkeit (vollständige Chronologie) → Boot-Kontext → Status → Zusammenfassung → Verlauf → neue Meldung. Damit bleibt der lange, feste Anfang für Googles implizites Caching gleich; Status und Zusammenfassung ändern sich nur am Ende des Systemtexts.

## Akzeptanzkriterien (Headless, simulierte API)
- In keinem Ablauf (Senden, Chat, Zusammenfassung, Speichern, Reset, Import, Neuladen) geht eine Anfrage an `cachedContents`.
- Alte Speicherschlüssel des Caches sind nach dem Laden entfernt; Import eines Exports mit `cachingEnabled` gelingt; neuer Export enthält das Feld nicht.
- Unter der Obergrenze: Zusammenfassung wird wie bisher angehängt.
- Über der Obergrenze: genau eine Anfrage mit bisheriger Zusammenfassung und neuen Funksprüchen; das Ergebnis ersetzt die Zusammenfassung; `lastSummaryIndex` wie bisher.
- Verdichtung abgeschnitten oder leer: alte Zusammenfassung unverändert, Meldung einmal je Fehlerserie.
- Zusammenfassungs- und Verdichtungsanfrage enthalten die Anweisung zu Spaßmeldungen.
- Systemtext beginnt bei aufeinanderfolgenden Anfragen mit demselben Text bis einschließlich Boot-Kontext.
- Benchmark-Tests unverändert bestanden (Anfrage identisch zum Widget).
- Bestehende Tests angepasst (Cache-Prüfungen in `widget_regression.py`, Schalter in `gemini_parts.py`, Feld in `_common.py`); neuer Test `tests/summary_condense.py`.

## Berührte Dateien
`index.html`; `tests/` (siehe oben); `README.md` (Abschnitt Token-Verbrauch/Caching); `docs/ARCHITEKTUR.md` (Caching-Abschnitt, Gedächtnis, Speicherschlüssel); `docs/specs/api-anbindung.md`, `docs/specs/gedaechtnis.md`, `docs/specs/einstellungen.md`, `docs/specs/export-import.md`; `docs/BUGS.md` (B18 entfällt); `docs/OFFEN.md`; `CHANGELOG.md`. `WIDGET_VERSION` bleibt „3.0“ (Persönlichkeits-Prompt unverändert).

## Version
1.4.0 (Minor): entfernt eine Einstellung und ändert das Gedächtnis. Release regulär und „Latest“, weil alle Nutzer betroffen sind.
