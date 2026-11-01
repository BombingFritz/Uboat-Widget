# Funkverkehr

## Ziel
Meldung des Kaleu an den BdU senden und die Antwort als Funkspruch ausgeben.

## Verhalten
- Enter oder „SENDEN“ ruft `sendMessage` auf. Ohne API-Schlüssel erscheint ein Hinweis, es wird nichts gesendet.
- Beginnt die Meldung mit „Status:“ (Groß-/Kleinschreibung egal), wird der Rest als aktueller Status gespeichert, im Display bestätigt und der Cache invalidiert. Die Meldung wird trotzdem an den BdU gesendet.
- Die Meldung erscheint als `> …`, Statuslicht blinkt, der Sende-Ton läuft vollständig ab, dann folgt der API-Aufruf.
- Die Antwort wird mit Kopf „FT von BdU an <Boot>:“ zeichenweise (45 ms) ausgegeben, solange läuft der Empfangs-Ton (optional als Loop). Der Bootsname stammt aus der Zeile `U-Boot:` im Boot-Kontext.
- Bei Fehlern: Meldung „FUNKSTÖRUNG: …“ (derzeit nicht sichtbar, siehe `docs/BUGS.md`), bei „not found“ Hinweis auf die Modellsuche.
- Antworten mit `finishReason` `SAFETY` gelten als Fehler; bei `MAX_TOKENS` wird der Text mit „...“ ausgegeben.

## Nicht-Ziele
Streaming der Antwort; Abbruch einer laufenden Ausgabe.

## Akzeptanzkriterien
- Meldung, Ton, Antwort und Ton-Ende erfolgen in dieser Reihenfolge.
- „Status: …“ aktualisiert das Statusfeld in den Einstellungen.
- Nach Neuladen sind Meldungen und Antworten wieder im Display.

## Berührte Dateien/Funktionen
`index.html`: `sendMessage`, `callApi`, `appendLog`, `typewriterEffect`, `playSendSound`, `playReceiveSound`, `stopReceiveSound`.

## Status
umgesetzt (1.0.0). Akzeptanzkriterien sind Prüfanforderungen, kein Nachweis einer hier durchgeführten Laufzeitprüfung.
