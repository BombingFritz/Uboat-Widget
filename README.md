Enigma BdU Funk - U-Boot Funkverkehr Simulator
Ein authentischer Funkverkehr-Simulator für U-Boot-Spiele

Kurz gesagt: index.html aus dem neuesten Release herunterladen, im Browser öffnen, über das Zahnrad ⚙️ einen kostenlosen Gemini-API-Schlüssel eintragen (Google AI Studio) und die erste Meldung an den BdU senden. Mehr braucht es nicht. Alles Weitere – Benchmark zur Modellwahl und Chat-Modus für Twitch-Streamer – ist optional und steht weiter unten.

1. Was ist das?
Dieses HTML-Widget simuliert den Funkverkehr zwischen dem Befehlshaber der Uboote und einem U-Boot auf Feindfahrt. Es ist gedacht, um das Gameplay von Uboootsimulationen zu bereichern – kostenlos und einfach einzusetzen. Die Antworten sind KI-generiert, die KI wird aber mit ausführlichem Kontext aus realen Funkkladden der Zeit sowie mit Marine-Begriffen und technischen Details gefüttert, was sie deutlich authentischer antworten lässt. Dazu wird eine (beliebige) KI-API benötigt. Grundsätzlich geht das mit jeder KI, entwickelt und zugeschnitten wurde es aber für die kostenlosen Modelle der Google Gemini API (Flash-Lite).
Das Widget läuft in einem separaten Browserfenster und kann parallel zum Spiel verwendet werden. Es funktioniert auch hervorragend auf Tablets oder Smartphones als zweiten Bildschirm.
Die wichtigsten Bootsdaten können gespeichert werden und die KI merkt sie sich. Zusätzlich kann man den aktuellen Status durchgeben. Die KI bezieht bei den Antworten alle diese Dinge mit ein – inklusive (je nach Modell mehr oder weniger ausführlich) die letzten Nachrichten als Volltext und die gesamte Konversation als Zusammenfassung. So begleitet einen der fiktive BdU tatsächlich durch den Einsatz. Je nachdem, wie viel man ihm mitteilt…

2. Features
•	Authentischer Marinejargon basierend auf echten Kriegstagebüchern
•	Historisch korrekter Kontext für  Funksprüche mit über 100 recherchierten Begriffen und Wendungen
•	An Enigma M4 angelehntes, aber simples Design 
•	KI-gesteuerte Antworten des BdU (Befehlshaber der U-Boote)
•	Vollständig anpassbar - Kontext, Bootsdaten, Status editierbar
•	Responsive Design - funktioniert auf Desktop, Tablet und Smartphone
•	Kurzzeit & Langzeitgedächtnis bei längerem Einsatz

3. Schnellstart
A.	Datei herunterladen: Lade die index.html aus dem neuesten Release herunter (rechts unter „Releases“), die Assets (Bild & Ton) werden online bezogen
B.	Im Browser öffnen: Einfach die HTML-Datei in einem Browser öffnen
C.	API-Key einrichten:
•	Klicke auf das Zahnrad-Symbol ⚙️
•	Trage deinen API-Schlüssel ein (siehe unten)
•	Wähle ein Modell aus
•	Passe den Kontext auf dein Boot, den Namen deines Kaleu und weitere, für dich wichtige Details an
D.	Loslegen: Sende deine erste Meldung an den BdU! 
E.	Falls er nicht antwortet, liegt es vermutlich am falsch ausgewählten Modell – öffne die Konsole des Browsers und checke den Log.

4. API-Schlüssel benötigt
Das Widget benötigt einen API-Schlüssel für eine KI. Empfohlen und getestet:
Google Gemini (Kostenlos)
•	Gehe zu Google AI Studio
•	Erstelle einen kostenlosen API-Schlüssel
•	Wähle über "MODELLE SUCHEN" ein aktuelles Flash-Lite-Modell, z. B. gemini-3.5-flash-lite (Standard). Ob es im kostenlosen Kontingent enthalten ist, legt Google fest.
•	Die Modelle entwickeln sich stetig weiter, probiere ruhig andere textbasierte Modelle aus. Falls keine Antwort kommt, öffne die Konsole in deinem Browser und checke den Log. Nicht alle Modelle haben kostenlose Kontingente und diese Kontingente können sich natürlich ändern.
Alternative Optionen (Zahnrad → API-Typ „Universal“, Base-URL eintragen, dann „MODELLE SUCHEN“)
•	Groq (kostenloses Kontingent): Base-URL https://api.groq.com/openai
•	OpenRouter (Modelle mit „:free“ kostenlos, ohne Guthaben nur 50 Anfragen pro Tag): Base-URL https://openrouter.ai/api
•	Mistral (seit Oktober 2026 nur noch kostenpflichtig): Base-URL https://api.mistral.ai
•	OpenAI (kostenpflichtig): Base-URL https://api.openai.com
•	Lokale KI (z. B. Ollama: Base-URL http://localhost:11434, LM Studio: http://localhost:1234) und jede andere OpenAI-kompatible API
Hinweis: Das Widget ist nur mit Google Gemini ausführlich getestet. Andere APIs sollten funktionieren, sind aber nicht garantiert. Ob ein Anbieter Aufrufe direkt aus dem Browser zulässt, zeigt am schnellsten der Benchmark (siehe unten).

Kostenlos oder lokal?
•	Kostenlose Kontingente sind stark eingeschränkt: wenige Anfragen pro Minute und pro Tag, oft nur kleine Modelle, und die Anbieter ändern die Bedingungen regelmäßig (Google stellt ältere Modelle ab, Mistral bietet seit Oktober 2026 keine kostenlosen API-Schlüssel mehr). Bei Gratis-Angeboten können Eingaben außerdem zur Verbesserung der Modelle genutzt werden.
•	Kostenlose Modelle liefern offenbar auch schlechtere Ergebnisse: Im ersten Benchmark (November 2026) klang das neue kostenlose gemini-3.5-flash-lite deutlich weniger authentisch als das ältere gemini-2.5-flash-lite. Größere, kostenpflichtige Modelle antworten in der Regel besser, wurden hier aber nicht verglichen.
•	Kostenlos und ohne Kontingent geht es mit einem lokalen Modell (z. B. Ollama oder LM Studio) auf dem eigenen PC. Dafür braucht es genug Arbeits- bzw. Grafikspeicher; wer nebenher ein anspruchsvolles Spiel streamt, merkt das. Einrichtung: API-Typ „Universal“, Base-URL des lokalen Programms eintragen, als API-Schlüssel einen beliebigen Platzhalter (z. B. „lokal“), dann „MODELLE SUCHEN“. Blockiert der Browser die Anfrage, in Ollama die Umgebungsvariable OLLAMA_ORIGINS=* setzen bzw. in LM Studio „CORS“ einschalten. Mit lokalen Modellen ist das Widget bisher nicht getestet.

Welches Modell passt? – Benchmark
Im Ordner benchmark/ liegt eine eigene Seite (bench.html, gehört nicht zum Widget), mit der man mehrere Modelle (Gemini, Groq, OpenRouter, Mistral oder jede andere OpenAI-kompatible Adresse) mit denselben 10 Testfragen und demselben Kontext vergleicht und die Antworten blind bewertet. Als Kontext dient ein Export aus dem Widget; wer noch keinen eigenen Funkverlauf hat, lädt den Beispielkontext beispiel-kontext.json aus demselben Ordner. Anleitung: benchmark/README.md. Erster Vergleich (Nov. 2026): gemini-2.5-flash-lite klang deutlich authentischer als gemini-3.5-flash-lite; 2.5 bietet Google aber nur noch bisherigen Nutzern an.

5. Verwendung
Während des Spiels
•	Öffne das Widget in einem separaten Browserfenster
•	Positioniere es neben deinem Spiel oder auf einem zweiten Monitor
•	Sende Meldungen wie:
"Feindkontakt in Sicht, erbitte Befehle"
"Geleitzug gesichtet, 8 Dampfer mit Bewachern"
"Torpedoversager, benötige neue Anweisungen"
Auf Tablet/Smartphone
•	Perfekt als "zweiter Bildschirm" während des Spielens
•	Vollständige Funktionalität auch auf kleinen Bildschirmen

6. Historischer Kontext
Der enthaltene Kontext basiert auf authentischen Quellen:
•	Echte U-Boot-Kriegstagebücher (1939-1945)
•	Originale Funksprüche und F.T.-Meldungen
•	Historischer Marinejargon und Fachbegriffe
•	Chronologie des U-Boot-Krieges

7. Anpassung
Das Widget ist vollständig anpassbar:
•	Boot-Kontext: Bootsnummer, Kommandant, Position
•	Aktueller Status: Brennstoff, Torpedos, Schäden
•	Persönlichkeit: BdU-Verhalten und Antworten
•	Historischer Zeitraum: Verschiedene Kriegsphasen

8. Lizenz
Dieses Projekt steht unter der Creative Commons Attribution 4.0 International (CC-BY 4.0) Lizenz, Volltext in der Datei LICENSE.
Das bedeutet:
✅ Kostenlos	verwenden
✅ Anpassen	und erweitern
✅ Weiterverbreiten	und forken
✅ Kommerziell	nutzen
Einzige Bedingung: Bitte erwähne die ursprüngliche Quelle, wenn du das Widget weiterentwickelst oder verbreitest.

9. Beitragen
Verbesserungen sind herzlich willkommen! Besonders:
•	Neue historische Begriffe und Wendungen
•	Zusätzliche Kontexte für verschiedene U-Boot-Typen
•	Übersetzungen in andere Sprachen
•	Bug-Fixes und Optimierungen

10. Technische Details
Grundlegende Technik
•	Reine HTML/CSS/JavaScript - keine Installation nötig
•	Lokale Speicherung - alle Einstellungen bleiben im Browser
Token-Verbrauch & Kostenoptimierung
Das Widget wurde speziell für kostenlosen Einsatz optimiert. Folgende Faktoren beeinflussen den Token-Verbrauch:
•	Kontextlänge: Der historische Kontext (~11.000 Zeichen) wird bei jeder Anfrage berücksichtigt, aber ggbf. gecached. 
•	Nachrichtenverlauf: Begrenzt auf die letzten Nachrichten und Zusammenfassungen, um Kosten niedrig zu halten
•	Context Caching: Gemini 2.0+ kann wiederkehrende Kontexte zwischenspeichern (spart bis zu 50% Tokens, leider aktuell nur in der kostenpflichtigen Version)
Anpassungsmöglichkeiten: Für intensivere Nutzung können Kontextlänge und Nachrichtenverlauf im Code leicht erweitert werden. Durch das Abspielen des Audios ist ein etwas langsamerer Nachrichtenverkehr schon vorgegeben. Kostenlos klappt es wunderbar, wenn – historisch akkurat – gelegentlich eine Nachricht gesendet wird und nicht alle 10 Sekunden.
Status-System
Das Widget erkennt automatisch Meldungen, die mit "Status:" begonnen werden und aktualisiert damit den Boot-Status:
•	Boot-Kontext: Bootsnummer, Kommandant, aktuelle Position, Datum
•	Aktueller Status: Brennstoff, Torpedos, Schäden, Wetter, Feindlage
Beispiel: "Status: Brennstoff 60%, 4 Aale, leichte Schäden am Sehrohr, gefechtsklar"
Datenspeicherung & Sicherheit
Im Browser Cache gespeichert:
•	API-Schlüssel (im localStorage, unverschlüsselt im Klartext)
•	Alle Einstellungen (Kontext, Boot-Daten, Status)
•	Nachrichtenverlauf (begrenzt auf letzte Nachrichten)
Cache löschen:
•	Im Widget: Zahnrad → "HISTORY LÖSCHEN" löscht nur den Nachrichtenverlauf
•	Im Widget: Zahnrad → "RESET" löscht auch den API-Schlüssel und die Einstellungen
•	Browser-weit: F12 → Application → Storage → Clear All
⚠️ SICHERHEITSHINWEIS: API-Schlüssel sind sensible Daten und werden lokal gespeichert. Bei geteilten Computern nach Nutzung Cache löschen! 

Für Twitch-Streamer: Chat-Modus und Companion-Server (optional)
Für alle anderen ist dieser Abschnitt nicht nötig – das Widget funktioniert ohne Server vollständig.
Der „Twitch Companion JS server“ ist ein eigenes, kleines Node.js-Programm des Autors, das auf dem Streaming-PC läuft und Twitch mit Stream-Overlays verbindet (Chat-Befehle, Raids, Vorhersagen u. a.). Er ist öffentlich auf GitHub (BombingFritz/Twitch-Companion-JS-server), braucht aber deutlich mehr Einrichtung als das Widget: eine eigene Twitch-Anwendung mit Zugangsdaten, Node.js und etwas Konfiguration. Wer ihn nutzen möchte, spricht am besten zuerst den Autor (BombingFritz) an.
Mit dem Server kann der BdU auch Funksprüche aus dem Twitch-Chat beantworten: Zuschauer schreiben „!BdU <Meldung>“, das Widget erzeugt im Hintergrund die Antwort mit demselben Kontext, der Server postet sie in den Chat (über einen eigenen Bot-Account, sonst als „FT vom BdU: …“ vom Streamer-Konto). Limits, Funkstille und Chat-Versand liegen im Server. Einschalten unter Zahnrad → „Für Streamer: Chat-Modus“ (der Bereich ist eingeklappt, solange der Chat-Modus aus ist). Details: docs/specs/chat-modus.md.

11. Support
Bei Fragen oder Problemen:
•	Erstelle ein Issue auf GitHub
•	Prüfe die Konsole des Browsers auf Fehlermeldungen
•	Stelle sicher, dass dein API-Schlüssel korrekt ist
Änderungen je Version stehen in CHANGELOG.md, technische Dokumentation und bekannte Fehler im Ordner docs/, automatische Tests im Ordner tests/.

12. Credits
Entwickelt von BombingFritz mit umfangreicher historischer Recherche basierend u.a. auf authentischen U-Boot-Kriegstagebüchern aus dem U-Boot-Archiv.
───────────────────────────────────
Ran an den Feind! 🚢⚓
Für alle U-Boot-Kommandanten, die das authentische Gefühl der Kriegsmarine erleben möchten.
