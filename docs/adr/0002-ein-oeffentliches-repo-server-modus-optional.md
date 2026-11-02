# ADR 0002: Ein öffentliches Repository, Server-Modus optional

## Status
Angenommen; Nutzer bestätigt (02.11.2026).

## Kontext
Das Widget ist öffentlich und wird von anderen ohne weitere Infrastruktur genutzt. Für den eigenen Stream soll es künftig mit dem lokalen „Twitch Companion JS server“ zusammenarbeiten (Funksprüche aus dem Twitch-Chat erkennen und im Chat beantworten, mit derselben API und demselben Kontext). In einem öffentlichen GitHub-Repository gibt es keine privaten Branches oder Releases, und Forks öffentlicher Repositories sind ebenfalls öffentlich.

## Entscheidung
- Es gibt nur dieses eine öffentliche Repository und eine `index.html`.
- Der eigenständige Betrieb (API-Schlüssel im Browser, keine Server-Abhängigkeit) bleibt der Standard und muss immer funktionieren.
- Die Server-Anbindung kommt als abschaltbarer Modus, standardmäßig aus. Ohne erreichbaren Server darf das Widget weder blockieren noch Fehler im Display zeigen.
- Persönliche Inhalte (eigener Prompt, Bootsdaten) bleiben im `localStorage` oder einer nicht eingecheckten lokalen Datei, nicht im Code.

## Verworfene Alternativen
- Separates privates Repository für die Stream-Fassung: zwei auseinanderlaufende Kopien einer großen Einzeldatei, jede Korrektur doppelt.
- „Privates Release“ im öffentlichen Repository: auf GitHub nicht möglich.

## Konsequenzen
Server-Funktionen müssen ohne Server unsichtbar bleiben. Öffentliche Nutzer profitieren von allen Fehlerbehebungen. Schnittstellen zum Server werden hier und im Server-Repository dokumentiert.
