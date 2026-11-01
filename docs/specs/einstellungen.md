# Einstellungen

## Ziel
Schlüssel, Modell, Kontexte und Ton im Browser dauerhaft einstellen.

## Verhalten
- Zahnrad öffnet das Overlay „KONFIGURATION“. Felder: API-Typ, API-Schlüssel, Base-URL (Universal), Caching, Modell, Persönlichkeit, Boot-Kontext, aktueller Status, Verlaufsverwaltung, Empfangs-Ton-Loop, Lautstärke.
- „SPEICHERN“ verlangt einen API-Schlüssel, speichert alles im `localStorage` und invalidiert den Cache, wenn sich ein kontext- oder API-relevantes Feld geändert hat.
- „RESET“ löscht nach Rückfrage die Widget-Schlüssel und setzt Felder und Zustand auf dieselben Standardwerte wie beim Erststart (Modell `gemini-3.5-flash-lite`, Standard-Boot-Kontext und -Status, Loop an, Lautstärke 50 %).
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
