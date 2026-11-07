# Offene Punkte

## Nächste Schritte (Stand 07.11.2026, abends)
Releases `v1.2.1` und `v1.2.2` bleiben bewusst „Pre-release“: Ihre Änderungen nützen vor allem Nutzern des Companion-Servers. „Latest“ bleibt `v1.0.2` bis 1.3.0 (Nutzer, 07.11.2026). Nach 1.3.0 Umzug der Arbeit auf lokales Claude Code mit GitHub Desktop geplant.

Erledigt: Livestream-Test von 1.2.0 (03.11.2026, laut Server-Doku), Bot-Account „DerBdu“ im Server (Server 1.1.5, ADR 0017 dort), Releases `v1.2.1` (Import in OBS, BUGS B20) und `v1.2.2` (vollständige Gemini-Antworten, BUGS B21; Download in OBS). Erster Benchmark-Durchlauf Gemini 2.5 gegen 3.5 Flash-Lite (Ergebnis in PR #7).

### Plan für 1.3.0
1. **Benchmark** (PR #7): Ordner `benchmark/` mit `bench.html`, `README.md` und `beispiel-kontext.json`; Gemini, Groq, Mistral. Vor dem Merge: Test des Nutzers mit Groq und Mistral über die echte API (ob Aufrufe aus dem Browser zugelassen sind, ist [UNGEKLÄRT]). Release-Anhänge dann `index.html`, `bench.html`, `beispiel-kontext.json`.
2. **Chat-Modus einklappen:** Gruppe „Chat-Modus“ in den Einstellungen als eingeklappter Bereich „Für Streamer mit Companion-Server“; klappt von selbst auf, wenn der Chat-Modus eingeschaltet ist. Sonst keine Designänderung. Kein eigener Branch für eine einfache Fassung (Nutzer 07.11.2026, ADR 0002 bleibt).
3. **README-Startseite:** oben ein kurzer Schnellstart für alle (Datei laden, Schlüssel, Modell, loslegen); Streamer-Funktionen (Chat-Modus) und Benchmark weiter unten. Dazu ein kurzer Abschnitt zum Companion-Server: was er ist, nur für Twitch-Streamer interessant, braucht deutlich mehr Einrichtung, ist öffentlich (`BombingFritz/Twitch-Companion-JS-server`), bei Interesse am besten den Autor ansprechen.
4. **Tests ins Repository:** die bisherigen Headless-Tests (Playwright, simulierte APIs) in `tests/` mit kurzer Anleitung, damit jede Sitzung sie ausführen kann, auch lokal mit Claude Code und GitHub Desktop (Umzug erwogen).
5. **Kontext schärfen** (nach Messung, Umfang offen): 3.5 Flash-Lite mit 1.2.2 erneut messen; Zusammenfassung des Nutzers erneuern bzw. für die neue Feindfahrt leeren und gegenprüfen; ggf. Wortlaut der Chat-Persönlichkeit, falls 3.5 im Chat weiter zu verspielt antwortet.

6. **Universal-Modus: Voreinstellungen für Groq und Mistral** (Nutzer, 07.11.2026: ja, wenn sie im Benchmark gut abschneiden). Heute schon möglich durch Eintragen der Base-URL von Hand (`https://api.groq.com/openai` bzw. `https://api.mistral.ai`); geplant ist eine Auswahl, die die Adresse einträgt. Voraussetzung: Aufrufe aus dem Browser funktionieren (Benchmark-Test).
7. ~~Lizenzdatei~~ in `LICENSE` umbenannt (Nutzer, 07.11.2026).

## Benchmark und Modellwahl (geplant 07.11.2026)
Ablauf nach `docs/specs/benchmark.md`, Werkzeug `benchmark/bench.html`:
1. **Gemini Flash-Lite vergleichen** (3.5 gegen 2.5, ggf. weitere Flash-Lite-Variante) mit dem Export des Nutzers, 10 Testfragen × 2 Läufe, blind bewertet durch den Nutzer. Auswertung und Diagnose (Modell oder Kontext) durch den Assistenten.
2. **Kontext schärfen** je nach Befund; Gegenprobe mit zweitem Export.
3. **Mistral und Groq** über die OpenAI-kompatible Schnittstelle (Universal-Modus) ergänzen; dabei wird der Universal-Modus erstmals echt getestet. Zu prüfen: ob die Anbieter Aufrufe direkt aus dem Browser zulassen (CORS), sonst über den Companion-Server.
Nicht verfolgt (Nutzerentscheidung): Claude (API wird getrennt vom Pro-Abo bezahlt), Ollama (Grafikspeicher wird vom Spiel gebraucht).

**Ergebnis Lauf 1 (07.11.2026, Nutzer, blind bewertet, Kontext: Export vom 02.11., 10 Fragen × 2 Läufe):**
| Modell | Ø Punkte (1–5) | Kaleu | Chat | stream-tauglich | Ø Dauer |
|---|---|---|---|---|---|
| `gemini-2.5-flash-lite` | 4,1 | 4,25 | 3,9 | 19 von 19 | 0,8 s |
| `gemini-3.5-flash-lite` | 2,75 | 2,9 | 2,5 | 15 von 20 | 3,2 s |
| `gemini-2.0-flash-lite` | – | – | – | nicht mehr verfügbar | – |

Diagnose:
- 2.5 war bei 9 von 10 Fragen besser oder gleich. Der Abstand ist größer als die Streuung zwischen den Läufen.
- 3.5: 4 von 20 Antworten brachen mitten im Satz ab (BUGS B21, Fehler im Widget, behoben in 1.2.2). Ohne diese 4 liegt 3.5 bei Ø 2,9, also weiter klar hinter 2.5. Der Unterschied liegt also auch am Modell.
- 3.5 im Chat: oft zu lang und zu verspielt („aus der Rolle“ 4×, „zu lang“ 4×), nimmt „trockener Humor, Augenzwinkern“ aus der Chat-Persönlichkeit stärker wörtlich. 2.5 antwortet knapper.
- 3.5 wiederholt sich: bei 2 Fragen in beiden Läufen wortgleich, trotz `temperature` 1.0.
- Bei beiden Modellen: Frage nach U-74 (Gedächtnis) ohne Bezug auf den Verlauf, weil die Zusammenfassung keine Einträge zu U-68 enthält (Vorbefund unten). Das liegt am Kontext, nicht am Modell. Schnorchel-Frage (Anachronismus) bei beiden unsicher.
- Folgerung: Für den Nutzer bleibt `gemini-2.5-flash-lite` die Wahl, solange Google es anbietet. Für neue Nutzer ist 2.5 laut Google nicht mehr freigegeben, daher bleibt 3.5 der Standard im Widget. Nächste Schritte: 3.5 nach 1.2.2 erneut messen, Zusammenfassung erneuern und gegenprüfen, dann Groq und Mistral.

Vorbefund aus dem Export des Nutzers (Stand 02.11.2026): Die Zusammenfassung beschreibt nur die Fahrten von U-4; U-38 und U-68 kommen darin nicht vor, obwohl `lastSummaryIndex` 96 von 100 Einträgen als zusammengefasst markiert. Die KI kennt von der laufenden Feindfahrt also nur Boot-Kontext, Status und die letzten 4 Einträge (Folge von B10 in der alten Fassung). Kandidat für Schritt 2: Zusammenfassung neu erzeugen oder für die neue Feindfahrt leeren.

## Chat-Modus (umgesetzt in 1.2.0)
Umgesetzt nach `docs/specs/chat-modus.md`, ADR 0004 und `docs/specs/bdu-chat.md` im Server-Repository. Entscheidungen des Nutzers (02.11.2026): `!BdU` im Chat, Limits ohne Ausnahmen (1 je 3 min, 3 je Nutzer in 30 min, Warnung höchstens 1× je 10 min), anonyme Antworten, nicht im Verlauf und nicht im Display, 60 s Vorrang des Kaleu, Funkstille nur für den Chat. Mit Standardwerten umgesetzt (im Server als Konstanten änderbar): Funkstille bei Tageskontingent bis Streamstart, Tagesobergrenze 60, Anfragen an das zuletzt verbundene Widget.

Noch offen:
1. ~~Test in OBS mit echtem Chat~~ erledigt (03.11.2026); ~~Livestream-Test~~ erledigt (03.11.2026, siehe oben). Stolperstein beim ersten Test: Quelle noch als „Lokale Datei“ eingebunden (Anfrage an `localhost` von OBS gesperrt, im Server-Log keine Verbindung). Lösung `file:///`.
2. Ton der Chat-Antworten: seit 1.2.0 eigenes Feld „Chat-Persönlichkeit“; feste Chat-Regeln verlangen inhaltliche Antworten statt Floskeln (Nutzertest 03.11.2026: „klappt nun ganz gut“). Wortlaut nach Streams nachschärfen. Später ggf. Kontext „Meldung eines Mannschafters“.
3. Absendernamen bewusst nicht übergeben; bei Bedarf später entscheiden.

## Prompt-Version
`WIDGET_VERSION` bestimmt heute, wann der gespeicherte Prompt ersetzt wird (BUGS B8). Vorschlag: Konstante in `PROMPT_VERSION` umbenennen, App-Version nur über `CHANGELOG.md`/Tags führen. Bei neuer Prompt-Version nachfragen bzw. nur ersetzen, wenn der gespeicherte Prompt unverändert der alte Standard war. Entscheidung des Nutzers offen.

## Arbeitskopie des Nutzers
Der Nutzer arbeitet lokal mit einer älteren Fassung (`WIDGET_VERSION = "2.1"`, ohne Universal-Modus und Caching-Schalter). `index.html` 1.0.0 enthält deren Funktionen vollständig; Unterschiede sind Titel, Standard-Boot-Kontext und die Auslagerung der Sicherheitsregeln in `SAFETY_RULES`. Für die Weiterentwicklung ist `index.html` aus `main` die Basis. Beim Umstieg: Datei am selben Pfad und mit derselben OBS-Einbindung ersetzen, sonst sind Einstellungen weg; der Versionsabgleich ersetzt den gespeicherten Prompt durch den neuen Standard, sichert ihn seit 1.1.0 aber vorher. Für den Wechsel auf `file:///` Export/Import nutzen.

## Weitere Punkte
1. ~~**Lizenzdatei:**~~ `LICENSE-CC-BY-4.0.txt` in `LICENSE` umbenannt (07.11.2026), damit GitHub die Lizenz erkennt.
2. **Wachsende Zusammenfassung:** `historySummary` wird nur angehängt, nie verdichtet. Bei langen Einsätzen steigt der Token-Verbrauch. Mögliche Lösung: Zusammenfassung ab einer Länge selbst zusammenfassen.
3. **Caching-Erkennung über Modellnamen** („1.5“, „2.5“) passt nicht zu neueren Modellen: Das neue Standardmodell `gemini-3.5-flash-lite` nutzt kein explizites Caching. Besser: Caching für alle Gemini-Modelle versuchen und den Fehlschlag auswerten (seit 1.0.1 wird ein Fehlschlag nicht mehr bei jeder Meldung wiederholt).
4. **Release-Anhänge:** Das Release `v1.0` enthält zusätzlich `Enigma.Bdu.Readme.1.docx`. Künftig README als einzige Anleitung, Release nur mit `index.html`.
5. **Externe Abhängigkeiten:** Hintergrundbild (Unsplash) und Schriften (Google Fonts) werden online geladen. Ohne Internet fehlen sie; die Funktion bleibt.
