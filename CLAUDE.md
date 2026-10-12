# Krok – Polnischtrainer

Persönliche Lern-App für Polnisch: Karteikarten mit FSRS (wie Anki) plus Grammatikaufgaben mit Erklärung.
Installierbare Web-App (PWA), gehostet über GitHub Pages: https://remigiuszkwapik-web.github.io/polish-guide/
Der Besitzer (Remi, UX-Designer) lernt täglich damit auf dem iPhone, als App auf dem Home-Bildschirm.
Produktkonzept mit Lernlogik, Entscheidungen und Roadmap: https://claude.ai/code/artifact/ca8796ac-813d-41a6-885a-4813fe5e7d70

## Aufbau
- `index.html`: ganze App (Oberfläche, FSRS-5, Session-Logik), kein Build, keine Abhängigkeiten
- `content/grammar.js`: Grammatik-Leiter (10 Stufen), Stufen-Erklärungen, Regeln für „Warum?“, Einstiegstest
- `content/kueche.js`: Kapitel 1, 10 Level. Neue Kapitel als eigene Datei nach diesem Muster, in `index.html` und `sw.js` eintragen
- `sw.js`: Service Worker (Offline)
- `tools/validate.py`: Prüfskript für alle polnischen Formen. Bericht in `tools/pruefbericht.md`, Ausnahmen mit Begründung in `tools/geprueft.tsv`
- README.md beschreibt Aufbau, Speicherformat und Prüfung ausführlicher

## Pflicht bei jeder Änderung
1. **`VERSION` in `sw.js` hochzählen** (`krok-vN` → `krok-vN+1`). Sonst zeigt die installierte App weiter die alte Fassung.
2. **Nach Änderungen an `content/`**: `bash tools/fetch-data.sh` (einmalig pro Umgebung) und `python3 tools/validate.py`. Es dürfen 0 Fehler und 0 „prüfen“ übrig bleiben. Den aktualisierten `tools/pruefbericht.md` mit committen.
3. **Testen** vor dem Push: Skript-Syntax prüfen (`node --check` auf die Inhalte und den Inline-Script-Block), App lokal starten (`python3 -m http.server`) und in Handybreite (390 px) hell und dunkel ansehen. Keine Konsolenfehler, kein seitliches Scrollen.
4. Push auf `main` geht sofort live auf Remis Handy. Größere oder riskante Änderungen erst auf einem eigenen Branch.

## Lernstand: niemals kaputt machen
- Der Lernstand liegt nur im localStorage des Geräts, nie im Repo. Zwei Einträge: `krok-state-v1` (Karten, Tage, Einstellungen) und `krok-revlog-v1` (vollständiger Antwort-Verlauf, Format in der README).
- **Karten-IDs nie umbenennen oder neu vergeben.** Lernstand und Verlauf hängen an den IDs (`n:<id>:dp`, `v:<id>:pair`, `d:<id>` …). Inhalte nur ergänzen, korrigieren oder neue IDs anlegen. Neue Aufgaben fortlaufend nummerieren (`d126`, `d127` …).
- Formatänderungen nur mit Umwandlung beim Start (siehe `initStore`) und so, dass alte Backups weiter einlesbar bleiben. Die Umwandlung mit einem realistischen alten Lernstand testen.
- Der Verlauf ist die Grundlage für die geplante FSRS-Anpassung an den eigenen Verlauf (ab ca. 1.000 Antworten). Nie kürzen.

## Inhalte schreiben
- Nomen: `{id, pl, de, g, lvl}`, g = m/f/n. Verben als Aspektpaar: `{id, impf, pf, de, ja, ty, rule, lvl}`.
- Grammatikaufgaben: `q` mit `___`, `base` (Grundform, bei Verben „verb · Person“), `a`, `de`, `rule`, optional `mc` (Auswahl) und `note`. Jede Aufgabe bekommt `m` mit Lemma und UD-Merkmalen für das Prüfskript, z. B. `"lodówka|Case=Loc|Number=Sing"` oder `"gotować|Person=1|Number=Sing|Tense=Pres|VerbForm=Fin"`.
- Jede `rule` muss in `KROK.rules` existieren, mit `why` und `pattern`.
- Jedes Level führt eine Grammatikstufe ein (Tabelle im Konzept). Pro Level etwa 8 Nomen, 4 Aspektpaare, 10–14 Aufgaben. Beispielsätze natürlich und alltagsnah, Übersetzung auf Deutsch.

## Sprache und Stil
- Oberfläche, Erklärungen, Commit-Nachrichten und Dokumentation auf Deutsch, Anrede „du“.
- Kurze, klare Sätze. Knöpfe sagen, was passiert. Fehlermeldungen sagen, was zu tun ist.
- Design: Farben nur über die Tokens in `:root` (hell und dunkel), Schriften Literata / IBM Plex. Mobile first, Bedienelemente unten.
