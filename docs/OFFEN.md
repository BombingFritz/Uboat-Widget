# Offene Punkte

## Nächste Schritte (Stand 08.11.2026)
**1.4.0 umgesetzt** (Branch, noch nicht veröffentlicht): explizites Caching entfernt (ADR 0006), Zusammenfassung verdichten, Spaßmeldungen weglassen, Anzeige des automatisch zwischengespeicherten Anteils. Nutzertest in OBS (08.11.2026, `gemini-2.5-flash-lite`, kostenloses Kontingent):
- Anzeige: „Letzte Anfrage: 5.628 Tokens, davon 0 automatisch zwischengespeichert“ (Zusammenfassung 5.786 Zeichen). Googles automatisches Caching griff bei dieser Anfrage nicht; weitere Beobachtungen bei mehreren Anfragen kurz hintereinander nötig.
- Erste Verdichtung der alten Zusammenfassung scheiterte: „Zusammenfassung abgeschnitten (Token-Budget)“ bei 600 Tokens. Behoben im selben Branch: Budget 1.500, Vorgabe „etwa 10 kurze Sätze“, Übernahme nur, wenn kürzer; Konsole meldet Abschlussgrund und Verbrauch. Erneuter Nutzertest offen.
- Doppelte Kopfzeile in einer Antwort (BUGS B23), nicht durch 1.4.0 verursacht.

Zweiter Nutzertest (08.11.2026, nach PR #19): keine Fehlermeldung, Verdichtung 5.786 → 500 Zeichen, danach normal angehängt (925 Zeichen nach 5 Funksprüchen). „Letzte Anfrage“ weiter mit 0 automatisch zwischengespeicherten Tokens. Anzeige „Letzte Zusammenfassung“ wirkte eingefroren (siehe BUGS, behoben in 1.4.0).

Entscheidungen des Nutzers (08.11.2026): Blöcke als Rückfall beim Verdichten (umgesetzt), B23 beheben wie vorgeschlagen (umgesetzt), Spaßfilter einmalig mit festem Testsatz und echter API prüfen (Werkzeug `benchmark/spassfilter.html`, gebaut; echter Durchlauf durch den Nutzer steht aus, Ergebnis hier eintragen).

Zahl der Aufrufe: Bis 1.3.x fasste das Widget alle 2 Funksprüche zusammen (Schwelle 8 offene Einträge). Entscheidung des Nutzers (08.11.2026): Schwelle 10, also alle 3 Funksprüche (`SUMMARY_TRIGGER_ENTRIES`, umgesetzt in 1.4.0). Höher geht nicht ohne Änderung an `CONTEXT_MAX_ENTRIES` (10), sonst fehlen Funksprüche im Kontext (B14).

Dritter Nutzertest (08.11.2026): Kopfzeile nicht mehr doppelt (B23 bestätigt). Zwei Meldungen: 3.986 bzw. 4.038 Tokens, jeweils 0 automatisch zwischengespeichert. Der Spaßfilter-Test brach am Tageskontingent ab („Generate content requests per day limit exceeded on Free Tier“, Neustart nach etwa 9,5 h, d. h. Mitternacht Pazifikzeit).

Danach Release `v1.4.0` (regulär, „Latest“). **Release `v1.3.2`** veröffentlicht (08.11.2026, „Latest“, Anhang `index.html` bytegleich mit `main`).

**Release `v1.3.0` veröffentlicht** (08.11.2026, reguläres Release, „Latest“; Anhänge `index.html`, `bench.html`, `beispiel-kontext.json` bytegleich mit `main`). `v1.2.1` und `v1.2.2` bleiben bewusst „Pre-release“.

**Lizenz:** Ab 1.3.1 MIT (Entscheidung des Nutzers, 08.11.2026; alle Inhalte inkl. Töne von ihm). Der Tag `v1.3.0` enthält versehentlich die MPL-2.0 (Auswahl in der GitHub-Vorlage); Releases bis v1.2.2 unter CC-BY 4.0. Release `v1.3.1` (nur Lizenz und Doku) legt der Nutzer an.

Danach: Umzug der Arbeit auf lokales Claude Code mit GitHub Desktop.
1. **Kontext schärfen:** 3.5 Flash-Lite mit 1.2.2 erneut messen; Zusammenfassung des Nutzers erneuern bzw. für die neue Feindfahrt leeren und gegenprüfen; ggf. Wortlaut der Chat-Persönlichkeit.
2. **Andere Anbieter** im Benchmark mit echter API (Groq, OpenRouter, Gemma über Gemini, lokale Modelle). Erst wenn einer aus dem Browser funktioniert und gut abschneidet: Auswahlliste der Base-URLs im Universal-Modus (Nutzer: ja).
3. **Universal-Modus ohne Schlüssel:** „SPEICHERN“ verlangt immer einen API-Schlüssel, auch für lokale Modelle, die keinen brauchen. Heute Platzhalter eintragen (README); später ggf. im Universal-Modus optional machen.

### Erledigt mit 1.3.0
Benchmark im Ordner `benchmark/` (Gemini, Groq, OpenRouter, Mistral, eigene Adresse), Chat-Modus eingeklappt, README mit Kurzanleitung und Companion-Server-Abschnitt, Tests in `tests/`, Lizenzdatei `LICENSE`.

## Caching, Gedächtnis und Verlauf (Entscheidungen 08.11.2026)
Entscheidungen des Nutzers (08.11.2026):
1. **Explizites Gemini-Caching ausgebaut** (umgesetzt in 1.4.0, ADR 0006). Gründe: im kostenlosen Kontingent laut Googles Preisseite nicht verfügbar, vom Standardmodell `gemini-3.5-flash-lite` ohnehin nicht genutzt, für bezahlte Nutzer wegen Speichergebühr und B18 kaum Ersparnis, nie mit echter API getestet, Nutzer verwendet es selbst nicht mehr. Ersatz ist Googles automatisches (implizites) Caching ab Gemini 2.5, das einen gleichbleibenden Anfang der Anfrage braucht. Damit entfallen B18 und Punkt 3 unter „Weitere Punkte“.
2. **Zusammenfassung verdichten** statt unbegrenzt anhängen (umgesetzt in 1.4.0, `docs/specs/gedaechtnis.md`).
3. **Chronologie bleibt vollständig** im Persönlichkeits-Prompt; kein Kürzen nach Jahr. Sie steht am festen Anfang der Anfrage und profitiert vom impliziten Caching.
4. **Paarweise löschen (B19):** umgesetzt in 1.3.2 als „LETZTEN FUNKSPRUCH LÖSCHEN“ (ein Paar je Klick; der Nutzer verwendet den Button selten).
5. ~~Button „älteste Hälfte der History löschen“~~: verworfen (Nutzer, 08.11.2026), nicht nötig, wenn Spaßmeldungen beim Verdichten wegfallen.
6. **Spaßmeldungen:** nur Stufe 1 (Nutzer, 08.11.2026): Zusammenfassen und Verdichten lassen sie weg, ohne zusätzliche Anfrage. Kein KI-Knopf zum Ausmisten. Umgesetzt in 1.4.0 mit den Beispielen des Nutzers (`SUMMARY_FUN_RULE`).
7. B19 vom Nutzer in OBS bestätigt (08.11.2026).

Detailentscheidungen zum Plan 1.4.0 (Nutzer, 08.11.2026), umgesetzt in 1.4.0:
- D1: Token-Schätzung zeigt den Verbrauch der letzten Anfrage und den automatisch zwischengespeicherten Anteil.
- D2: Obergrenze der Zusammenfassung 2.000 Zeichen, Ziel nach dem Verdichten 1.200 Zeichen.
- D3: Verdichtung bekommt den Boot-Kontext zur Einordnung; die Zusammenfassung wiederholt nichts, was dort schon steht.
- D4: Wortlaut der Spaß-Regel wie vorgeschlagen.

## Kontingent und Token-Verbrauch (Stand 08.11.2026)
**Automatisches Caching (Entscheidung des Nutzers, 08.11.2026: festhalten):** Bei allen bisher gemessenen Anfragen mit `gemini-2.5-flash-lite` im kostenlosen Kontingent 0 automatisch zwischengespeicherte Tokens (5 Anfragen, 3.986–5.742 Tokens). Google bietet das implizite Caching dort offenbar nicht an. Kosten entstehen dadurch nicht.
**Später erneut prüfen** (Auftrag des Nutzers): ob sich das automatische Caching doch nutzen lässt (Anzeige „Letzte Anfrage“ in den Einstellungen beobachten, auch mit `gemini-3.5-flash-lite`), und ob sich sonst Tokens sparen lassen, etwa durch einen kompakteren Persönlichkeits-Prompt mit Chronologie (rund 2.600 von 4.000 Tokens je Anfrage). Der Prompt ist Werk des Nutzers: Kürzen nur auf seinen Auftrag, Vorschläge zuerst als Entwurf, Wirkung mit dem Benchmark gegenprüfen.

**Tageskontingent (Requests per Day, RPD):** Im kostenlosen Kontingent zählt vor allem die Zahl der Anfragen pro Tag je Modell und Projekt; sie wird um Mitternacht Pazifikzeit (9 Uhr deutscher Zeit) zurückgesetzt. Die genauen Werte sind [UNGEKLÄRT]: Googles Tabelle ist aus der Cloud nicht lesbar, Drittquellen widersprechen sich (für `gemini-2.5-flash-lite` zwischen 20 und 1.500 RPD; eine Quelle vom 21.10.2026, laut eigener Angabe aus AI Studio abgelesen: 2.5 Flash-Lite 10 RPM / 20 RPD, 3.5 Flash-Lite 15 RPM / 500 RPD). Verbindlich ist die Anzeige in Google AI Studio für das eigene Projekt. Dass der Nutzer am 08.11.2026 nach wenigen Dutzend Aufrufen das Tageslimit erreichte, passt zu einem niedrigen Wert.

Aufrufe des Widgets seit 1.4.0: je eigenem Funkspruch 1, dazu alle 3 Funksprüche 1 Zusammenfassung (≈ 1,33 je Funkspruch); je `!BdU` 1 (Server-Grenze 60 je Tag, höchstens 1 je 3 min). Benchmark: 20 je Modell; Spaßfilter-Test: 10. Alle Werkzeuge mit demselben Schlüssel und Modell teilen sich das Kontingent.

**Bestätigt (Nutzer, 08.11.2026, Fehlermeldung im Widget):** `gemini-2.5-flash-lite` hat im kostenlosen Kontingent des Nutzers **20 Anfragen pro Tag** („Quota exceeded for metric … generate_content_free_tier_requests, limit: 20, model: gemini-2.5-flash-lite“). Der Wert für `gemini-3.5-flash-lite` ist weiter [UNGEKLÄRT] (Drittquelle: 500).

**Entscheidung des Nutzers (08.11.2026): zweites Modell**, umgesetzt in 1.4.0 (`bdu_secondary_model`): Chat-Antworten und Zusammenfassungen über `gemini-3.5-flash-lite`, eigene Funksprüche weiter über `gemini-2.5-flash-lite`. Getrennte Tageskontingente geben Puffer. Bekanntes Risiko: Im Benchmark vom 07.11.2026 war 3.5 gerade im Chat am schwächsten (Ø 2,5, oft zu lang und zu verspielt; teils durch B21, seit 1.2.2 behoben). Nutzertest 08.11.2026 (nach Merge von #21): Eigener Funkspruch scheiterte am 2.5-Tageskontingent, `!BdU` wurde über 3.5 beantwortet; die Trennung funktioniert. Dass Zusammenfassungen über das zweite Modell laufen, ist nur headless geprüft (`tests/secondary_model.py`); im Betrieb zeigt es die Konsole („[SUMMARY] 📊 gemini-3.5-flash-lite …“) bei der nächsten Zusammenfassung. Nächster Schritt des Nutzers: Benchmark mit 3.5 (vor allem die 4 Chat-Fragen) und Spaßfilter-Test mit 3.5 für die Zusammenfassungen. Bei schlechtem Ergebnis Feld leeren (zurück auf 2.5) oder Chat-Persönlichkeit für 3.5 nachschärfen (Wortlaut durch den Nutzer).

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
1. ~~**Lizenzdatei:**~~ `LICENSE`, ab 1.3.1 MIT (08.11.2026).
2. ~~**Wachsende Zusammenfassung**~~: erledigt in 1.4.0 (Verdichten ab 2.000 Zeichen).
3. ~~**Caching-Erkennung über Modellnamen**~~: entfallen mit 1.4.0 (explizites Caching entfernt, ADR 0006).
4. **Release-Anhänge:** Das Release `v1.0` enthält zusätzlich `Enigma.Bdu.Readme.1.docx`. Künftig README als einzige Anleitung, Release nur mit `index.html`.
5. **Externe Abhängigkeiten:** Hintergrundbild (Unsplash) und Schriften (Google Fonts) werden online geladen. Ohne Internet fehlen sie; die Funktion bleibt.
