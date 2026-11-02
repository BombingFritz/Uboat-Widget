# Offene Punkte

## Server-Modus (geplant, noch nicht spezifiziert)
Ziel laut Nutzer (02.11.2026): BdU-Eingaben aus dem Twitch-Chat erkennen und im Chat beantworten, mit derselben API und demselben Kontext wie das Widget. Das läuft im Hintergrund, nicht über die grafische Oberfläche. Details folgen vom Nutzer; vor der Umsetzung eine Spec in `docs/specs/` anlegen.

Rahmen aus ADR 0002 und 0003:
- Standardmäßig aus; ohne Server keine Fehlermeldungen und kein Warten.
- `SAFETY_RULES` auch für Chat-Eingaben.
- Twitch-Zugangsdaten bleiben im Server; das Widget holt nur, was es braucht (Muster wie bei SpargelPoll und Coinflip über `/token`).

Vor der Umsetzung zu klären:
1. **Wer erkennt die Chat-Eingabe?** Der Server (EventSub, z. B. Präfix wie `!bdu`) und reicht sie ans Widget weiter, oder das Widget hört selbst mit. Laut Projektregeln laufen neue Events über den Server.
2. **Rückweg der Antwort:** Chat-Versand per Helix als Broadcaster (wie SpargelPoll) oder über einen Server-Endpunkt.
3. **Gemeinsames Gedächtnis:** Gehen Chat-Funksprüche in denselben Verlauf und dieselbe Zusammenfassung wie die eigenen Meldungen? Erscheinen sie im Display?
4. **Missbrauchsschutz:** Rate-Limit pro Nutzer und insgesamt, Längenbegrenzung, ggf. nur bestimmte Rollen; Antworten an das Twitch-Limit von 500 Zeichen anpassen. Chat-Eingaben sind fremde Eingaben (Prompt-Injection), daher vorher BUGS B4 beheben.
5. **Gleichzeitigkeit:** Eigene Meldung und Chat-Anfrage gleichzeitig; Warteschlange im Widget nötig.
6. **API-Schlüssel:** Bleibt im Browser oder zieht in die `.env` des Servers, mit Server als Vermittler zur KI-API. Letzteres entfernt den Klartext-Schlüssel aus dem Browser.
7. **OBS-Einbindung:** Sobald das Widget `localhost` anfragt, sperrt OBS die Einbindung als „Lokale Datei“. Dann URL `file:///…/index.html` verwenden. Achtung: Das ist eine andere Speicher-Herkunft, Einstellungen und Verlauf müssen einmal neu eingetragen werden (siehe `docs/ARCHITEKTUR.md`).

## Prompt-Version
`WIDGET_VERSION` bestimmt heute, wann der gespeicherte Prompt ersetzt wird (BUGS B8). Vorschlag: Konstante in `PROMPT_VERSION` umbenennen, App-Version nur über `CHANGELOG.md`/Tags führen. Bei neuer Prompt-Version nachfragen bzw. nur ersetzen, wenn der gespeicherte Prompt unverändert der alte Standard war. Entscheidung des Nutzers offen.

## Arbeitskopie des Nutzers
Der Nutzer arbeitet lokal mit einer älteren Fassung (`WIDGET_VERSION = "2.1"`, ohne Universal-Modus und Caching-Schalter). `index.html` 1.0.0 enthält deren Funktionen vollständig; Unterschiede sind Titel, Standard-Boot-Kontext und die Auslagerung der Sicherheitsregeln in `SAFETY_RULES`. Für die Weiterentwicklung ist `index.html` aus `main` die Basis. Beim Umstieg: Datei am selben Pfad und mit derselben OBS-Einbindung ersetzen, sonst sind Einstellungen weg; der Versionsabgleich ersetzt den gespeicherten Prompt durch den neuen Standard.

## Weitere Punkte
1. **Lizenzdatei:** `LICENSE-CC-BY-4.0.txt` wird von GitHub nicht als Lizenz erkannt (Repository zeigt keine Lizenz). Umbenennen in `LICENSE` wäre möglich; Entscheidung des Nutzers.
2. **Wachsende Zusammenfassung:** `historySummary` wird nur angehängt, nie verdichtet. Bei langen Einsätzen steigt der Token-Verbrauch. Mögliche Lösung: Zusammenfassung ab einer Länge selbst zusammenfassen.
3. **Caching-Erkennung über Modellnamen** („1.5“, „2.5“) passt nicht zu neueren Modellen. Besser: Fehler der Cache-Erstellung auswerten statt Namen raten.
4. **Release-Anhänge:** Das Release `v1.0` enthält zusätzlich `Enigma.Bdu.Readme.1.docx`. Künftig README als einzige Anleitung, Release nur mit `index.html`.
5. **Externe Abhängigkeiten:** Hintergrundbild (Unsplash) und Schriften (Google Fonts) werden online geladen. Ohne Internet fehlen sie; die Funktion bleibt.
