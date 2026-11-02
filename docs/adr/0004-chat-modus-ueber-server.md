# ADR 0004: Chat-Modus über den Companion-Server

## Status
Angenommen als Plan; Nutzer bestätigt (02.11.2026). Noch nicht umgesetzt.

## Kontext
Zuschauer sollen dem BdU aus dem Twitch-Chat Funksprüche schicken können und eine Antwort im Chat bekommen, mit derselben KI und demselben Kontext wie die Meldungen des Kaleu. Der „Twitch Companion JS server“ liest den Chat bereits per EventSub und sendet Nachrichten per Helix. Das Widget ist öffentlich und muss ohne Server unverändert funktionieren (ADR 0002).

## Entscheidung
- **Server:** erkennt `!BdU …`, kürzt den Text, prüft Limits und Funkstille, reicht angenommene Anfragen an das Widget weiter, postet Antworten, Warnungen und Funkstille-Ansagen in den Chat. Spec im Server-Repository (`docs/specs/bdu-chat.md`).
- **Widget:** erzeugt nur die Antwort mit der KI, mit demselben Kontext wie bei eigenen Meldungen. Chat-Anfragen und -Antworten gehen nicht in Verlauf oder Zusammenfassung und erscheinen nicht im Display. Spec `docs/specs/chat-modus.md`.
- **Übertragung:** Server → Widget per Server-Sent Events (dauerhafte Verbindung), Widget → Server per POST. Das Widget braucht dafür keinen Twitch-Token.
- **Schalter:** Chat-Modus in den Einstellungen, standardmäßig aus.

## Verworfene Alternativen
- Widget sendet selbst per Helix in den Chat (Muster SpargelPoll): bräuchte Twitch-Token und Twitch-Logik im öffentlichen Widget; Warnungen und Funkstille kämen dann aus zwei Stellen.
- Widget fragt den Server alle paar Sekunden ab: Chrome bremst Timer in Hintergrund-Tabs auf einmal pro Minute, und der Server wüsste nicht, ob ein Widget läuft.
- Server ruft die KI selbst auf: doppelte Pflege von Prompt, Kontext und Verlauf; der Kontext liegt im Browser des Widgets.

## Konsequenzen
- Das Widget muss im Stream laufen und verbunden sein; ohne verbundenes Widget ignoriert der Server `!BdU` still.
- In OBS: Einbindung per `file:///…/index.html` (Anfragen an `localhost` sind von „Lokale Datei“ aus gesperrt). Einstellungen und Verlauf sind dort einmal neu einzutragen (andere Speicher-Herkunft). Die Quelle muss auch ausgeblendet weiterlaufen (Option „Quelle herunterfahren, wenn nicht sichtbar“ aus).
- Feste Regeln für Chat-Anfragen stehen im Code neben `SAFETY_RULES` (ADR 0003), nicht im editierbaren Prompt; die Prompt-Version (B8) bleibt unberührt.
