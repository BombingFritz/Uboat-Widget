# Einstellungen

## Ziel
Schlüssel, Modell, Kontexte und Ton im Browser dauerhaft einstellen.

## Verhalten
- Zahnrad öffnet das Overlay „KONFIGURATION“. Felder: API-Typ, API-Schlüssel, Base-URL (Universal), Modell, zweites Modell für Chat-Antworten und Zusammenfassungen (optional, seit 1.4.0), Token-Schätzung (seit 1.4.0 auch Verbrauch der letzten Anfrage, davon automatisch zwischengespeichert; in beiden API-Typen sichtbar), Persönlichkeit, Boot-Kontext, aktueller Status, Verlaufsverwaltung, Empfangs-Ton-Loop, Lautstärke.
- „SPEICHERN“ verlangt einen API-Schlüssel, speichert alles im `localStorage`. Den Schalter „Explizites Caching“ gibt es seit 1.4.0 nicht mehr (ADR 0006).
- „RESET“ löscht nach Rückfrage im Widget (zweiter Klick, seit 1.2.1 ohne Browser-Dialog, BUGS B20) die Widget-Schlüssel und setzt Felder und Zustand auf dieselben Standardwerte wie beim Erststart (Modell `gemini-3.5-flash-lite`, Standard-Boot-Kontext und -Status, Loop an, Lautstärke 50 %).
- Weicht die gespeicherte `bdu_widget_version` von `WIDGET_VERSION` ab, wird beim Laden der Persönlichkeits-Prompt durch den Standard ersetzt.

## Nicht-Ziele
Synchronisation zwischen Geräten; Verschlüsselung des Schlüssels.

## Akzeptanzkriterien
- Nach Speichern und Neuladen stehen alle Werte wieder in den Feldern.
- Nach „RESET“ ist kein Schlüssel und kein Modell mehr gespeichert; Felder und Modell-Badge zeigen die Standardwerte.

## Berührte Dateien/Funktionen
`index.html`: `toggleSettings`, `loadSettings`, `saveSettings`, `clearSettings`, `saveToLocalStorage`.

## Status
umgesetzt (1.0.0), Reset korrigiert in 1.0.1.
