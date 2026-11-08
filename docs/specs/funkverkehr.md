# Funkverkehr

## Ziel
Meldung des Kaleu an den BdU senden und die Antwort als Funkspruch ausgeben.

## Verhalten
- Enter oder „SENDEN“ ruft `sendMessage` auf. Ohne API-Schlüssel erscheint ein Hinweis, es wird nichts gesendet.
- Beginnt die Meldung mit „Status:“ (Groß-/Kleinschreibung egal), wird der Rest als aktueller Status gespeichert, und im Display bestätigt. Die Meldung wird trotzdem an den BdU gesendet.
- Die Meldung erscheint als `> …`, Statuslicht blinkt, der Sende-Ton läuft vollständig ab, dann folgt der API-Aufruf.
- Die Antwort wird mit Kopf „FT von BdU an <Boot>:“ zeichenweise (45 ms) ausgegeben, solange läuft der Empfangs-Ton (optional als Loop). Der Bootsname stammt aus der Zeile `U-Boot:` im Boot-Kontext.
- Bei Fehlern: rote Systemmeldung „FUNKSTÖRUNG: …“, bei „not found“ zusätzlich Hinweis auf die Modellsuche. Die Meldung bleibt im Display, kommt aber nicht in den Verlauf.
- Lässt sich ein Ton nicht laden oder abspielen, läuft der Funkverkehr ohne Ton weiter (Warnung in der Konsole).
- Antworttext und Bootsname werden als Text eingefügt, nie als HTML.
- Antworten mit `finishReason` `SAFETY` gelten als Fehler; bei `MAX_TOKENS` wird der Text mit „...“ ausgegeben.

## Nicht-Ziele
Streaming der Antwort; Abbruch einer laufenden Ausgabe.

## Akzeptanzkriterien
- Meldung, Ton, Antwort und Ton-Ende erfolgen in dieser Reihenfolge.
- „Status: …“ aktualisiert das Statusfeld in den Einstellungen.
- Nach Neuladen sind Meldungen und Antworten wieder im Display.
- Bei einem API-Fehler erscheint „FUNKSTÖRUNG“ und der Verlauf wächst nicht.
- Die neue Meldung steht genau einmal in der API-Anfrage.

## Berührte Dateien/Funktionen
`index.html`: `sendMessage`, `callApi`, `appendLog`, `typewriterEffect`, `createBduMessageDiv`, `appendTextWithBreaks`, `playSendSound`, `playReceiveSound`, `stopReceiveSound`.

## Status
umgesetzt (1.0.0), Fehlerbehebungen in 1.0.1. Akzeptanzkriterien sind Prüfanforderungen, kein Nachweis einer hier durchgeführten Laufzeitprüfung.
