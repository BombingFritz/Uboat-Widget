# Funkmaat-Meldungen und Zweitfrequenz

## Status
Umgesetzt in 1.5.0 (Test `tests/funkmaat.py`, nur mit simulierter API). Wortlaut und offene Fragen vom Nutzer entschieden (11.11.2026). Grundlage: Wunsch des Nutzers vom 09.11.2026, Entscheidungen vom 11.11.2026 (siehe unten).

## Ziel
1. Ist das Tageskontingent des aktiven Modells erschöpft, funkt das Widget ohne Zutun über das zweite Modell weiter („Zweitfrequenz“).
2. Hinweise und Fehler im Display brechen die Immersion nicht: Sie kommen vom **Funkmaat** in der Sprache der Zeit. Technische Einzelheiten stehen nur in den Einstellungen und in der Konsole.

## Entscheidungen des Nutzers (11.11.2026)
- Nach dem Wechsel auf die Zweitfrequenz wird der gescheiterte Funkspruch **sofort im Hintergrund erneut gesendet**.
- Ist auch das zweite Modell erschöpft: Meldung „Funkmaat: Sendeanlage unklar, Meldung wiederholt nicht durchgekommen und unbestätigt.“
- Die Zweitfrequenz gilt bis zum Neuladen des Widgets.

## Verhalten (Vorschlag)
### Zweitfrequenz
- Auslöser: Ein eigener Funkspruch scheitert mit „Kontingent erschöpft“ (HTTP 429 bzw. `RESOURCE_EXHAUSTED`, wie `isQuotaError`).
- Ist ein zweites Modell eingetragen und vom aktiven verschieden und die Zweitfrequenz noch nicht aktiv:
  1. Display: „Funkmaat: Funkfrequenz gestört, wechsele auf Zweitfrequenz.“
  2. Zweitfrequenz aktiv (nur im Arbeitsspeicher): eigene Funksprüche laufen bis zum Neuladen über das zweite Modell.
  3. Derselbe Funkspruch geht sofort erneut hinaus, ohne zweite Kaleu-Zeile und ohne zweiten Sende-Ton; die Antwort erscheint wie gewohnt. Kosten: 1 Anfrage beim zweiten Modell.
- Scheitert auch das (oder ist die Zweitfrequenz schon aktiv und das zweite Modell erschöpft): „Funkmaat: Sendeanlage unklar, Meldung wiederholt nicht durchgekommen und unbestätigt.“ Der Funkspruch kommt wie heute nicht in den Verlauf.
- Ohne zweites Modell: „Funkmaat: Funkfrequenz gestört, Meldung nicht durchgekommen. Später erneut versuchen.“
- Chat-Antworten (`!BdU`) und Zusammenfassungen laufen ohnehin über das zweite Modell; dort ändert sich nichts (Kontingent erschöpft beim Chat → Funkstille im Server wie bisher).

### Funkmaat statt „[SYS]“
- `appendLog` stellt Systemmeldungen als „Funkmaat: …“ dar statt „[SYS] …“. Darstellung (Farbe, Schrift) unverändert.
- Fehler beim Senden werden nach Art unterschieden; die technische Meldung steht nicht mehr im Display.
- Neue Zeile in den Einstellungen (Bereich Modell/Token-Schätzung): **„Letzte Störung: 11.11., 20:15 · gemini-2.5-flash-lite · <technische Meldung>“** und, solange aktiv, **„Zweitfrequenz aktiv: gemini-3.5-flash-lite (bis zum Neuladen)“**. Nur im Arbeitsspeicher, kein neuer Speicherschlüssel. Die Konsole meldet wie bisher alles.

### Vorgeschlagener Wortlaut (zur Entscheidung durch den Nutzer)
| Anlass | Heute | Vorschlag |
|---|---|---|
| Kontingent erschöpft, Wechsel | „FUNKSTÖRUNG: You exceeded your current quota …“ | „Funkmaat: Funkfrequenz gestört, wechsele auf Zweitfrequenz.“ (entschieden) |
| Auch Zweitfrequenz erschöpft | wie oben | „Funkmaat: Sendeanlage unklar, Meldung wiederholt nicht durchgekommen und unbestätigt.“ (entschieden) |
| Kontingent erschöpft, kein zweites Modell | wie oben | „Funkmaat: Funkfrequenz gestört, Meldung nicht durchgekommen. Später erneut versuchen.“ |
| Überlastung bei Google („high demand“, 503) | „FUNKSTÖRUNG: This model is currently experiencing high demand …“ | zufällig eine von zwei Fassungen: „Funkmaat: Starke atmosphärische Störungen, BdU nicht erreichbar. Meldung später wiederholen.“ oder „Funkmaat: Frequenz nicht sicher, verdächtige Aktivitäten, Feind peilt vermutlich ein. Meldung später absetzen, möglichst kurz halten!“ (Nutzer) |
| Ungültiger Schlüssel | „FUNKSTÖRUNG: API key not valid …“ | „Funkmaat: Code-Schlüssel passt nicht, bitte Codebuch und Einstellungen der Funkanlage überprüfen!“ (Nutzer) |
| Modell nicht gefunden | „FUNKSTÖRUNG: … not found“ + „HINWEIS: Modell nicht gefunden …“ | „Funkmaat: Frequenz nicht besetzt. Modell in den Einstellungen prüfen („MODELLE SUCHEN“).“ |
| Keine Internetverbindung | „FUNKSTÖRUNG: Failed to fetch“ | „Funkmaat: Keine Verbindung zur Sendeanlage. Internetverbindung prüfen.“ |
| Sonstiger Fehler | „FUNKSTÖRUNG: …“ | „Funkmaat: Funkspruch nicht durchgekommen. Einzelheiten in den Einstellungen.“ |
| Kein API-Schlüssel beim Senden | „KEIN API-SCHLÜSSEL. BITTE ZAHNRAD ÖFFNEN …“ | „Funkmaat: Schlüsselmaschine nicht eingestellt. Bitte Zahnrad öffnen und API-Schlüssel eintragen.“ |
| Status-Meldung | „[SYS] [STATUS AKTUALISIERT] …“ | „Funkmaat: In KTB notiert, Lagemeldung weitergegeben: …“ (Nutzer) |
| Einstellungen gespeichert | „KONFIGURATION GESPEICHERT.“ | „Funkmaat: Funkgerät neu eingestellt.“ |
| Verlauf gelöscht | „HISTORY GELÖSCHT.“ | „Funkmaat: Funkkladde geleert. Bereit für die neue Feindfahrt.“ |
| Letzten Funkspruch gelöscht | „Letzter Funkspruch aus der History gelöscht (2 Einträge).“ | „Funkmaat: Letzter Funkspruch aus der Kladde gestrichen.“ |
| Nichts zu löschen | „Keine History zum Kürzen vorhanden.“ | „Funkmaat: Die Funkkladde ist leer.“ |
| Zusammenfassung fehlgeschlagen | „⚠️ ZUSAMMENFASSUNG FEHLGESCHLAGEN: …“ | „Funkmaat: Kladde konnte nicht abgeschrieben werden, neuer Versuch später.“ (beim Rückfall: „… älteste Seiten ausgeheftet.“) |
| Browser-Speicher voll | „SPEICHER VOLL. ÄLTERE FUNKSPRÜCHE WERDEN GELÖSCHT.“ | „Funkmaat: Kladde voll, älteste Seiten ausgeheftet.“ |

Meldungen beim Einrichten (Schlüssel, Modell, Internet) nennen weiterhin, was zu tun ist; sie erscheinen vor allem bei Neulingen und selten im Stream.

## Entscheidungen zu den offenen Fragen (Nutzer, 11.11.2026)
1. Wortlaut: wie in der Tabelle, mit den drei Änderungen des Nutzers (Überlastung zweite Fassung, Status-Meldung, ungültiger Schlüssel). Meldungen beim Einrichten nennen weiterhin, was zu tun ist.
2. Modell-Badge zeigt bei aktiver Zweitfrequenz das tatsächlich genutzte Modell: ja.
3. Die Zweitfrequenz endet auch beim SPEICHERN: ja.

## Nicht-Ziele
Automatischer Wechsel bei anderen Fehlern als „Kontingent erschöpft“; Wechsel des Chat-Modells; Zählen der verbleibenden Anfragen (Google liefert die Zahl nicht mit).

## Akzeptanzkriterien (Headless, simulierte API)
- Aktives Modell 429, zweites Modell frei: Display zeigt die Wechselmeldung und danach die Antwort; genau 2 Anfragen (aktiv, zweites); Meldung und Antwort im Verlauf; der nächste Funkspruch geht direkt an das zweite Modell; nach Neuladen wieder an das aktive.
- Beide 429: Wechselmeldung, dann „Sendeanlage unklar …“; nichts im Verlauf.
- Ohne zweites Modell: entsprechende Meldung, kein zweiter Aufruf.
- Kein „[SYS]“ mehr im Display; jede Fehlerart zeigt ihren Funkmaat-Text; die technische Meldung steht in „Letzte Störung“.
- Chat-Modus, Zusammenfassungen und Benchmark unverändert.

## Berührte Dateien
`index.html` (`sendMessage`, `appendLog`, `modelFor`, neue Hilfen für Fehlerart und Anzeige), `tests/` (neuer Test, Anpassung bestehender Prüfungen auf „[SYS]“/„FUNKSTÖRUNG“), `ANLEITUNG.md` und `README.md` (Fehlertabelle), `docs/ARCHITEKTUR.md`, `docs/BUGS.md` (B1 erwähnt die alten Texte), `CHANGELOG.md`.
