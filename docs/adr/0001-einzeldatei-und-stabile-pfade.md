# ADR 0001: Einzeldatei und stabile Pfade

## Status
Angenommen; entspricht dem veröffentlichten Stand 1.0.0.

## Kontext
Das Widget wird von anderen heruntergeladen und als einzelne Datei im Browser oder in OBS geöffnet. Die Audiodateien werden nicht mitgeliefert, sondern zur Laufzeit direkt aus diesem Repository geladen.

## Entscheidung
- Eine HTML-Datei mit Inline-CSS/JS, ohne Build und ohne Paketmanager.
- `index.html` und die beiden WAV-Dateien bleiben im Wurzelverzeichnis und behalten ihre Namen.
- Die Audio-URLs im Code werden nur zusammen mit einem Plan für bereits verteilte Dateien geändert.

## Verworfene Alternativen
- Assets in einen Unterordner verschieben: würde bei allen bereits heruntergeladenen Widgets den Ton abschalten.
- Mehrere Dateien oder Build-Schritt: erschwert das einfache Herunterladen und Öffnen.

## Konsequenzen
Dokumentation liegt in `docs/`, ohne Einfluss auf die ausgelieferte Datei. Strukturänderungen am Widget sind kein Teil von Feature-Arbeit.
