# Offene Punkte

## Chat-Modus (geplant für 1.1.0)
Spezifiziert in `docs/specs/chat-modus.md` (Widget), ADR 0004 und `docs/specs/bdu-chat.md` im Server-Repository. Entscheidungen des Nutzers (02.11.2026):
- `!BdU <Text>` im Chat; Server erkennt, kürzt (200 Zeichen), prüft Limits; Widget erzeugt die Antwort; Server postet „FT vom BdU: …“ als Antwort auf die Chat-Nachricht.
- Limits ohne Ausnahmen (auch Broadcaster und Mods): eine Anfrage je 3 Minuten insgesamt, je Nutzer 3 in 30 Minuten. Bei Verstoß „Funkverkehr einschränken, Feind peilt ein!“, höchstens einmal je 10 Minuten, sonst keine Antwort.
- Antworten anonym, ohne Absendernamen. Später eventuell Kontext „Meldung eines Mannschafters“.
- Chat-Anfragen und -Antworten nicht im Verlauf, nicht im Display.
- Nach einer eigenen Meldung werden Chat-Anfragen eine Minute zurückgehalten (nicht verworfen).
- Funkstille bei erschöpftem KI-Kontingent: betrifft nur den Chat; eigene Meldungen laufen weiter.
- Widget läuft im Stream als OBS-Browser-Source und wird auf `file:///` umgestellt; Einstellungen dort einmal neu eintragen.

Vor der Umsetzung:
1. BUGS B14 beheben (Chat-Anfragen nutzen denselben Kontextaufbau).
2. Zu bestätigen: Funkstille bei Minutenlimit 30 Minuten, bei Tageslimit bis zum nächsten Streamstart; optionale Tagesobergrenze für Chat-Antworten (Vorschlag 60). Details in der Server-Spec.

## Prompt-Version
`WIDGET_VERSION` bestimmt heute, wann der gespeicherte Prompt ersetzt wird (BUGS B8). Vorschlag: Konstante in `PROMPT_VERSION` umbenennen, App-Version nur über `CHANGELOG.md`/Tags führen. Bei neuer Prompt-Version nachfragen bzw. nur ersetzen, wenn der gespeicherte Prompt unverändert der alte Standard war. Entscheidung des Nutzers offen.

## Arbeitskopie des Nutzers
Der Nutzer arbeitet lokal mit einer älteren Fassung (`WIDGET_VERSION = "2.1"`, ohne Universal-Modus und Caching-Schalter). `index.html` 1.0.0 enthält deren Funktionen vollständig; Unterschiede sind Titel, Standard-Boot-Kontext und die Auslagerung der Sicherheitsregeln in `SAFETY_RULES`. Für die Weiterentwicklung ist `index.html` aus `main` die Basis. Beim Umstieg: Datei am selben Pfad und mit derselben OBS-Einbindung ersetzen, sonst sind Einstellungen weg; der Versionsabgleich ersetzt den gespeicherten Prompt durch den neuen Standard.

## Weitere Punkte
1. **Lizenzdatei:** `LICENSE-CC-BY-4.0.txt` wird von GitHub nicht als Lizenz erkannt (Repository zeigt keine Lizenz). Umbenennen in `LICENSE` wäre möglich; Entscheidung des Nutzers.
2. **Wachsende Zusammenfassung:** `historySummary` wird nur angehängt, nie verdichtet. Bei langen Einsätzen steigt der Token-Verbrauch. Mögliche Lösung: Zusammenfassung ab einer Länge selbst zusammenfassen.
3. **Caching-Erkennung über Modellnamen** („1.5“, „2.5“) passt nicht zu neueren Modellen: Das neue Standardmodell `gemini-3.5-flash-lite` nutzt kein explizites Caching. Besser: Caching für alle Gemini-Modelle versuchen und den Fehlschlag auswerten (seit 1.0.1 wird ein Fehlschlag nicht mehr bei jeder Meldung wiederholt).
4. **Release-Anhänge:** Das Release `v1.0` enthält zusätzlich `Enigma.Bdu.Readme.1.docx`. Künftig README als einzige Anleitung, Release nur mit `index.html`.
5. **Externe Abhängigkeiten:** Hintergrundbild (Unsplash) und Schriften (Google Fonts) werden online geladen. Ohne Internet fehlen sie; die Funktion bleibt.
