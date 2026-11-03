# Offene Punkte

## Nächste Schritte (Stand 03.11.2026)
1. **Livestream-Test von 1.2.0** abwarten (Chat-Modus mit echtem Publikum, Ton der Chat-Antworten, Limits, Funkstille). Ergebnisse hier und in `docs/BUGS.md` festhalten.
2. **Release `v1.2.0`** danach in der GitHub-Oberfläche anlegen (Tag auf `main`, Anhang `index.html`). Bei Befunden vorher als 1.2.1 korrigieren.
3. **Bot-Account „DerBdu“** für die Chat-Antworten: Baustelle im Server (`Twitch-Companion-JS-server`, `docs/OFFEN.md` dort). Am Widget ändert sich dafür nichts.

## Chat-Modus (umgesetzt in 1.2.0)
Umgesetzt nach `docs/specs/chat-modus.md`, ADR 0004 und `docs/specs/bdu-chat.md` im Server-Repository. Entscheidungen des Nutzers (02.11.2026): `!BdU` im Chat, Limits ohne Ausnahmen (1 je 3 min, 3 je Nutzer in 30 min, Warnung höchstens 1× je 10 min), anonyme Antworten, nicht im Verlauf und nicht im Display, 60 s Vorrang des Kaleu, Funkstille nur für den Chat. Mit Standardwerten umgesetzt (im Server als Konstanten änderbar): Funkstille bei Tageskontingent bis Streamstart, Tagesobergrenze 60, Anfragen an das zuletzt verbundene Widget.

Noch offen:
1. ~~Test in OBS mit echtem Chat~~ erledigt (03.11.2026); Livestream-Test steht aus (siehe oben). Stolperstein beim ersten Test: Quelle noch als „Lokale Datei“ eingebunden (Anfrage an `localhost` von OBS gesperrt, im Server-Log keine Verbindung). Lösung `file:///`.
2. Ton der Chat-Antworten: seit 1.2.0 eigenes Feld „Chat-Persönlichkeit“; feste Chat-Regeln verlangen inhaltliche Antworten statt Floskeln (Nutzertest 03.11.2026: „klappt nun ganz gut“). Wortlaut nach Streams nachschärfen. Später ggf. Kontext „Meldung eines Mannschafters“.
3. Absendernamen bewusst nicht übergeben; bei Bedarf später entscheiden.

## Prompt-Version
`WIDGET_VERSION` bestimmt heute, wann der gespeicherte Prompt ersetzt wird (BUGS B8). Vorschlag: Konstante in `PROMPT_VERSION` umbenennen, App-Version nur über `CHANGELOG.md`/Tags führen. Bei neuer Prompt-Version nachfragen bzw. nur ersetzen, wenn der gespeicherte Prompt unverändert der alte Standard war. Entscheidung des Nutzers offen.

## Arbeitskopie des Nutzers
Der Nutzer arbeitet lokal mit einer älteren Fassung (`WIDGET_VERSION = "2.1"`, ohne Universal-Modus und Caching-Schalter). `index.html` 1.0.0 enthält deren Funktionen vollständig; Unterschiede sind Titel, Standard-Boot-Kontext und die Auslagerung der Sicherheitsregeln in `SAFETY_RULES`. Für die Weiterentwicklung ist `index.html` aus `main` die Basis. Beim Umstieg: Datei am selben Pfad und mit derselben OBS-Einbindung ersetzen, sonst sind Einstellungen weg; der Versionsabgleich ersetzt den gespeicherten Prompt durch den neuen Standard, sichert ihn seit 1.1.0 aber vorher. Für den Wechsel auf `file:///` Export/Import nutzen.

## Weitere Punkte
1. **Lizenzdatei:** `LICENSE-CC-BY-4.0.txt` wird von GitHub nicht als Lizenz erkannt (Repository zeigt keine Lizenz). Umbenennen in `LICENSE` wäre möglich; Entscheidung des Nutzers.
2. **Wachsende Zusammenfassung:** `historySummary` wird nur angehängt, nie verdichtet. Bei langen Einsätzen steigt der Token-Verbrauch. Mögliche Lösung: Zusammenfassung ab einer Länge selbst zusammenfassen.
3. **Caching-Erkennung über Modellnamen** („1.5“, „2.5“) passt nicht zu neueren Modellen: Das neue Standardmodell `gemini-3.5-flash-lite` nutzt kein explizites Caching. Besser: Caching für alle Gemini-Modelle versuchen und den Fehlschlag auswerten (seit 1.0.1 wird ein Fehlschlag nicht mehr bei jeder Meldung wiederholt).
4. **Release-Anhänge:** Das Release `v1.0` enthält zusätzlich `Enigma.Bdu.Readme.1.docx`. Künftig README als einzige Anleitung, Release nur mit `index.html`.
5. **Externe Abhängigkeiten:** Hintergrundbild (Unsplash) und Schriften (Google Fonts) werden online geladen. Ohne Internet fehlen sie; die Funktion bleibt.
