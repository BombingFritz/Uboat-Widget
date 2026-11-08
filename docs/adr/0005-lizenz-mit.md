# ADR 0005: MIT-Lizenz statt CC-BY 4.0

## Status
Angenommen (Nutzer, 08.11.2026). Gilt ab Release v1.3.1.

## Kontext
Das Widget wurde bis v1.2.2 unter Creative Commons Attribution 4.0 (CC-BY 4.0) veröffentlicht. Creative Commons empfiehlt seine Lizenzen nicht für Software, GitHub bietet sie nicht als Vorlage an und erkennt den Text nicht als Lizenz. Beim Versuch, die Lizenzdatei über die GitHub-Vorlage zu ersetzen, landete versehentlich die Mozilla Public License 2.0 im Tag `v1.3.0`. Alle Inhalte des Repositorys (Code, Persönlichkeits-Prompt, Chronologie, Morse-Töne) stammen vom Autor; Hintergrundbild (Unsplash) und Schriften (Google Fonts) werden nur online nachgeladen und liegen nicht im Repository.

## Entscheidung
Ab v1.3.1 steht das Repository unter der **MIT-Lizenz** (`LICENSE`, „Copyright (c) 2026 BombingFritz“), wie SpargelPoll.

## Folgen
- Nutzung, Änderung und Weitergabe bleiben frei; Namensnennung über den Copyright-Hinweis, wie bisher mit CC-BY.
- Geänderte Fassungen dürfen auch unter anderen Bedingungen weitergegeben werden (anders als bei der verworfenen MPL 2.0, die bei einer Ein-Datei-Anwendung jede geänderte Fassung offenlegen ließe).
- Wer v1.0 bis v1.2.2 unter CC-BY 4.0 bezogen hat, behält diese Rechte. Der Tag `v1.3.0` bleibt mit MPL-Text bestehen; maßgeblich ab v1.3.1 ist MIT (CHANGELOG).

## Verworfene Alternativen
- CC-BY 4.0 beibehalten: nicht für Software gedacht, von GitHub nicht erkannt.
- MPL 2.0: strenger als bisher (geänderte Dateien müssen offengelegt werden).
