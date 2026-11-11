# Anleitung: Enigma-BdU-Funk einrichten

Schritt für Schritt vom Herunterladen bis zum ersten Funkspruch, mit Erklärungen zu Modellen, Kontingenten und Gedächtnis. Für den schnellen Überblick reicht die [README](README.md); hier steht alles ausführlicher. Stand: Version 1.4.0, November 2026.

## Was du brauchst
- Einen aktuellen Browser (Chrome, Edge, Firefox) – oder OBS, wenn du streamst.
- Ein kostenloses Google-Konto für den API-Schlüssel.
- Etwa 10 Minuten.

Installieren musst du nichts: Das Widget ist eine einzige Datei (`index.html`). Bilder, Schriften und Töne lädt es aus dem Internet nach.

---

## Schritt 1: Herunterladen
1. Auf der GitHub-Seite rechts auf **Releases** klicken und das neueste Release öffnen (ganz oben, „Latest“).
2. Unter „Assets“ die Datei **`index.html`** herunterladen.
3. Die Datei an einen festen Ort legen, z. B. `Dokumente\BdU-Funk\index.html`.

**Wichtig:** Ort und Dateiname später möglichst nicht mehr ändern. Der Browser speichert Einstellungen und Funkverlauf **je Speicherort** – liegt die Datei woanders, beginnt das Widget mit leeren Einstellungen (Abhilfe: Export/Import, siehe Schritt 7).

## Schritt 2: Öffnen
- **Im Browser:** Doppelklick auf `index.html`. Das Funkgerät erscheint, im Display steht „WARTEN AUF MELDUNG, HERR KALEU.“
- **In OBS** (für Streamer):
  1. Neue Quelle **„Browser“** anlegen.
  2. **„Lokale Datei“ nicht anhaken**, sondern bei „URL“ die Datei als Adresse eintragen, z. B. `file:///C:/Users/<Name>/Documents/BdU-Funk/index.html` (Schrägstriche nach rechts, `file:///` mit drei Strichen).
  3. Breite **520**, Höhe **520**.
  4. Bedienen: Quelle mit Rechtsklick → **„Interagieren“**. Dort tippst du Funksprüche und öffnest die Einstellungen.
  - Warum `file:///` statt „Lokale Datei“? Nur so kann das Widget später mit dem Companion-Server sprechen (Chat-Modus). Wer keinen Chat-Modus braucht, kann auch „Lokale Datei“ nehmen – aber dann dauerhaft dabei bleiben (siehe „Wichtig“ in Schritt 1).
  - In OBS erscheinen keine Browser-Dialoge. Rückfragen stellt das Widget deshalb auf dem Button selbst („SICHER? NOCHMAL KLICKEN“): einfach ein zweites Mal klicken.

## Schritt 3: API-Schlüssel holen
Die Antworten des BdU schreibt eine KI. Dafür braucht das Widget einen Schlüssel für eine KI-Schnittstelle (API). Empfohlen ist Google Gemini, weil es dafür ein kostenloses Kontingent gibt.
1. [Google AI Studio](https://aistudio.google.com) öffnen und mit dem Google-Konto anmelden.
2. **„Get API key“ / „API-Schlüssel erstellen“** wählen und den Schlüssel kopieren.
3. Den Schlüssel wie ein Passwort behandeln: nicht im Stream zeigen, nicht weitergeben. Ist er doch einmal sichtbar geworden, in AI Studio löschen und einen neuen erstellen.

## Schritt 4: Einstellungen
Zahnrad ⚙️ unten rechts am Funkgerät anklicken.
1. **Google Gemini API Key:** Schlüssel einfügen.
2. **API-Typ:** „Google Gemini“ lassen.
3. **Aktives Modell:** auf **„🔍 MODELLE SUCHEN“** klicken und ein Modell aus der Liste anklicken. Empfehlung: ein **Flash-Lite**-Modell, z. B. `gemini-3.5-flash-lite` (Standard). Warum, steht unten unter „Modelle und Tageskontingent“.
4. **Zweites Modell** (optional): leer lassen oder ein anderes Flash-Lite-Modell eintragen – Erklärung ebenfalls unten.
5. **Boot-Kontext (Adressat):** dein Boot eintragen, z. B.
   ```
   U-Boot: U-68
   Bootstyp: Typ IXc
   Kommandant: Kptlt. Hansen
   Datum: Oktober 1941
   Ausgelaufen aus Lorient, Kampfraum vor Freetown.
   ```
   Die Zeile `U-Boot: …` bestimmt auch die Kopfzeile der Antworten („FT von BdU an U-68:“).
6. **Aktueller Status:** Brennstoff, Torpedos, Schäden – oder leer lassen und später per Funkspruch setzen (Schritt 5).
7. **Persönlichkeit (BdU):** der lange Text mit Rolle, Sprache und Chronologie des U-Boot-Kriegs. Für den Anfang unverändert lassen.
8. **SPEICHERN** (ohne Schlüssel lässt sich nicht speichern).

## Schritt 5: Funken
- Meldung ins Feld „NACHRICHT …“ tippen und **SENDEN**. Nach dem Morse-Ton antwortet der BdU zeichenweise im Display.
- Beispiele: „Geleitzug gesichtet, 8 Dampfer mit Bewachern, erbitte Befehle“, „Torpedoversager, zwei Aale verloren“.
- **Status-Meldung:** Beginnt eine Meldung mit `Status:`, übernimmt das Widget den Rest als aktuellen Status, z. B. `Status: Brennstoff 60 %, 4 Aale, leichte Schäden am Sehrohr`. Der BdU kennt ihn ab dann bei jeder Antwort.
- Hinweise und Störungen meldet der **Funkmaat** im Display, z. B. „Funkmaat: Funkfrequenz gestört …“. Die technische Ursache steht in den Einstellungen unter „Letzte Störung“; was zu tun ist, steht im Abschnitt „Wenn etwas nicht klappt“.

## Schritt 6: Das Gedächtnis des BdU
- Jeder Funkspruch und jede Antwort kommen in den **Verlauf** (bis 100 Einträge). Er bleibt nach dem Neuladen erhalten.
- Die letzten Funksprüche bekommt die KI wörtlich mit. Ältere fasst das Widget **alle 3 Funksprüche** in einer kurzen **Zusammenfassung** zusammen – so erinnert sich der BdU an frühere Versenkungen, Schäden und Befehle, ohne dass jede Anfrage immer größer wird.
- Wird die Zusammenfassung zu lang (über 2.000 Zeichen), **verdichtet** die KI sie zu einer kürzeren Gesamtzusammenfassung: die laufende Feindfahrt ausführlich, frühere Fahrten knapp.
- **Spaßmeldungen** ohne Bezug zur Feindfahrt („Bier ist alle!“) beantwortet der BdU zwar, sie kommen aber nicht ins Gedächtnis.
- Unter **History-Verwaltung** siehst du, wann und mit welchem Modell zuletzt zusammengefasst wurde und wie viele Funksprüche noch nicht zusammengefasst sind (eine Meldung samt Antwort zählt als ein Funkspruch; die Zahl pendelt zwischen 2 und 4). Die Zusammenfassung läuft erst nach der Antwort im Hintergrund und erscheint nicht im Display. „LETZTEN FUNKSPRUCH LÖSCHEN“ nimmt den letzten Funkspruch samt Antwort zurück, „HISTORY LÖSCHEN“ beginnt eine neue Feindfahrt mit leerem Gedächtnis.

## Schritt 7: Sichern und umziehen (Export/Import)
Unter **„Sichern & Übertragen“** in den Einstellungen:
- **ALS DATEI** speichert alles (Einstellungen, Persönlichkeit, Boot-Kontext, Verlauf, Zusammenfassung) als `Funk-Export.json` im Download-Ordner – auch aus OBS heraus, dort ohne Hinweis.
- **DATEI LADEN** und dann **IMPORT BESTÄTIGEN** holt einen Export zurück, z. B. in einem anderen Browser, nach dem Umzug der Datei oder beim Wechsel der OBS-Einbindung.
- Den API-Schlüssel nur mitexportieren, wenn die Datei auf deinen eigenen Geräten bleibt.
- Tipp: vor jedem Update und gelegentlich nach einem Stream exportieren.

---

## Modelle und Tageskontingent – warum zwei Modelle?
**Kontingent:** Im kostenlosen Gemini-Zugang zählt vor allem, **wie viele Anfragen pro Tag** ein Modell beantworten darf. Die Grenze gilt **je Modell** und wird gegen **9 Uhr deutscher Zeit** zurückgesetzt. Die Werte legt Google fest und ändert sie immer wieder; deine aktuellen Grenzen zeigt [Google AI Studio](https://aistudio.google.com) unter Nutzung/Rate Limits. Beispiel (November 2026): `gemini-2.5-flash-lite` erlaubte nur noch **20 Anfragen pro Tag**.

**Was eine Anfrage kostet:**
| Vorgang | Anfragen |
|---|---|
| Eigener Funkspruch | 1 |
| Zusammenfassung (alle 3 Funksprüche, läuft im Hintergrund) | 1 |
| Funkspruch aus dem Twitch-Chat (`!BdU`, nur Chat-Modus) | 1 |
| Benchmark (je Modell) | 20 |
| Spaßfilter-Test | 10 |

**Das zweite Modell** („Zweites Modell für Chat-Antworten und Zusammenfassungen“) verteilt die Arbeit auf zwei Kontingente:
- **Aktives Modell:** nur deine eigenen Funksprüche – die Antworten, die du im Display siehst. Hier lohnt das Modell, das am besten klingt.
- **Zweites Modell:** die Zusammenfassungen (siehst du nie direkt) und, im Chat-Modus, die Antworten an den Twitch-Chat.
- Weil jedes Modell sein eigenes Tageskontingent hat, bleiben dem aktiven Modell so mehr Anfragen. Schon ohne Chat-Modus spart das ein Viertel der Anfragen beim aktiven Modell.
- Leer gelassen läuft alles über das aktive Modell – das ist völlig in Ordnung, wenn dein Kontingent reicht.
- Welches Modell gerade gearbeitet hat, zeigt die Zeile „Letzte Anfrage (Modell): …“ in der Token-Schätzung.
- **Zweitfrequenz:** Ist das Tageskontingent des aktiven Modells aufgebraucht, wechselt das Widget von selbst auf das zweite Modell und schickt den Funkspruch dort noch einmal („Funkmaat: Funkfrequenz gestört, wechsele auf Zweitfrequenz.“). Bis zum Neuladen oder SPEICHERN bleibt es dabei.

## Benchmark und Spaßfilter-Test – wofür?
Beide liegen im Ordner `benchmark/` (im Release als eigene Dateien oder über „Code → Download ZIP“), werden per Doppelklick im Browser geöffnet und gehören nicht zum Widget. Ihre Aufrufe zählen gegen dasselbe Tageskontingent – am besten nicht direkt vor dem Spielen oder Streamen starten.
- **Benchmark (`bench.html`):** Welches Modell klingt am besten? Er stellt mehreren Modellen dieselben 10 Testfragen mit demselben Kontext und du bewertest die Antworten **blind**, ohne zu wissen, welches Modell geantwortet hat. Als Kontext dient dein eigener Export oder der mitgelieferte `beispiel-kontext.json`. Sinnvoll, wenn du das aktive Modell wählst oder wechseln musst, weil Google ein Modell abschaltet. Anleitung: [benchmark/README.md](benchmark/README.md).
- **Spaßfilter-Test (`spassfilter.html`):** Behält das Gedächtnis die wichtigen Fakten und lässt es Spaßmeldungen weg? Er fasst einen festen Testsatz mit genau den Anweisungen des Widgets zusammen und zählt automatisch nach. Sinnvoll, um ein Modell für die Zusammenfassungen (zweites Modell) zu prüfen.

## Für Streamer: Chat-Modus (optional)
Mit dem separaten **Companion-Server** des Autors können Zuschauer dem BdU über `!BdU <Meldung>` im Twitch-Chat funken; die Antwort erscheint im Chat, nicht im Widget. Das braucht deutlich mehr Einrichtung (Node.js, eigene Twitch-Anwendung) – Details in der [README](README.md) unter „Für Twitch-Streamer“. Im Widget: Zahnrad → „Für Streamer: Chat-Modus“, in OBS per `file:///` einbinden und „Quelle herunterfahren, wenn nicht sichtbar“ ausschalten. Für den Chat lohnt das zweite Modell besonders.

---

## Wenn etwas nicht klappt
| Meldung oder Verhalten | Ursache und Lösung |
|---|---|
| „Funkmaat: Funkfrequenz gestört, wechsele auf Zweitfrequenz.“ | Tageskontingent des aktiven Modells aufgebraucht. Das Widget funkt automatisch über das zweite Modell weiter und schickt deinen Funkspruch dort noch einmal. Das gilt bis zum Neuladen oder SPEICHERN; die Anzeige unten am Funkgerät zeigt das genutzte Modell. |
| „Funkmaat: Funkfrequenz gestört, Meldung nicht durchgekommen. Später erneut versuchen.“ | Tageskontingent aufgebraucht, kein zweites Modell eingetragen. Ab etwa 9 Uhr geht es wieder; für die Zukunft ein zweites Modell eintragen. |
| „Funkmaat: Sendeanlage unklar, Meldung wiederholt nicht durchgekommen und unbestätigt.“ | Auch das zweite Modell hat sein Tageskontingent verbraucht. Ab etwa 9 Uhr geht es wieder. |
| „Funkmaat: Starke atmosphärische Störungen …“ oder „Frequenz nicht sicher … Feind peilt vermutlich ein …“ | Google ist gerade überlastet („high demand“). Meist nach wenigen Minuten vorbei; Meldung später erneut senden. |
| „Funkmaat: Frequenz nicht besetzt …“ | Modellname falsch oder von Google abgeschaltet: „MODELLE SUCHEN“ und ein Modell aus der Liste wählen. |
| „Funkmaat: Code-Schlüssel passt nicht …“ | API-Schlüssel ungültig, falsch kopiert oder gelöscht: in AI Studio prüfen, neu einfügen, SPEICHERN. |
| „Funkmaat: Keine Verbindung zur Sendeanlage …“ | Keine Internetverbindung. |
| „Funkmaat: Schlüsselmaschine nicht eingestellt …“ | Noch kein API-Schlüssel eingetragen (Schritt 3 und 4). |
| „Funkmaat: Funkspruch nicht durchgekommen. Einzelheiten in den Einstellungen.“ | Anderer Fehler: die technische Meldung steht in den Einstellungen unter „Letzte Störung“. |
| „Funkmaat: Kladde konnte nicht abgeschrieben werden …“ | Die Zusammenfassung im Hintergrund ist gescheitert, meist am Kontingent des zweiten bzw. aktiven Modells. Das Widget versucht es nach 2 weiteren Funksprüchen erneut; der Verlauf geht nicht verloren. |
| „SPEICHERN“ zeigt „API-SCHLÜSSEL FEHLT“ | Ohne Schlüssel lässt sich nicht speichern. Für lokale KI (Universal-Modus) einen Platzhalter wie `lokal` eintragen. |
| Einstellungen und Verlauf sind plötzlich leer | Datei verschoben, umbenannt, anderer Browser oder andere OBS-Einbindung („Lokale Datei“ ↔ `file:///`). Datei an den alten Ort zurück oder Export importieren. |
| Kein Ton | Lautstärke in den Einstellungen und am Rechner prüfen. Ohne Internet fehlen die Töne; funken geht trotzdem. |
| Antworten zu lang oder albern | Anderes Modell probieren (Benchmark) oder die Persönlichkeit anpassen. |

Genauere Hinweise stehen in der Browser-Konsole (F12 → „Konsole“; in OBS nur mit Zusatzaufwand erreichbar – im Zweifel die Datei zum Testen im normalen Browser öffnen). Fragen und Fehler gern als Issue auf GitHub.

## Begriffe
- **API / API-Schlüssel:** Schnittstelle zur KI bzw. dein persönlicher Zugangscode dafür.
- **Modell:** die KI selbst, z. B. `gemini-3.5-flash-lite`. „Flash-Lite“ sind die kleinen, schnellen Modelle mit dem großzügigsten kostenlosen Kontingent.
- **Kontingent / Rate Limit:** wie viele Anfragen pro Minute und pro Tag kostenlos erlaubt sind.
- **Token:** Maßeinheit für Textmenge bei KIs, grob 3–4 Zeichen. Die Token-Schätzung in den Einstellungen zeigt, wie groß eine Anfrage ist.
- **FT:** Funktelegramm (Funkspruch). **BdU:** Befehlshaber der Unterseeboote. **Kaleu:** Kapitänleutnant, Kommandant des Bootes.
