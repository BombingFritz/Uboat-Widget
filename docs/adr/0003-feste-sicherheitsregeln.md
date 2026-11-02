# ADR 0003: Feste Sicherheitsregeln

## Status
Angenommen; entspricht dem veröffentlichten Stand 1.0.0.

## Kontext
Das Szenario spielt im Zweiten Weltkrieg. Der Persönlichkeits-Prompt ist über die Oberfläche frei änderbar und wird im `localStorage` gespeichert.

## Entscheidung
Die Grundregeln (keine NS-Propaganda, kein „Heil“, keine politischen Inhalte, keine brutale Sprache) stehen als Konstante `SAFETY_RULES` im Code. Sie werden jedem Aufruf vorangestellt, auch der Cache-Erstellung, und sind weder im Einstellungsfeld noch im `localStorage` enthalten.

## Verworfene Alternativen
Regeln als Teil des editierbaren Prompts: würden beim Bearbeiten oder Zurücksetzen verloren gehen.

## Konsequenzen
Jeder neue Aufrufweg (z. B. ein künftiger Server- oder Chat-Modus) muss `SAFETY_RULES` ebenfalls voranstellen. Bei Eingaben aus dem Twitch-Chat gilt das besonders, weil dort Fremde schreiben.
