# Krok – Polnischtrainer

Polnisch lernen mit Karteikarten wie in Anki (FSRS) und Grammatikaufgaben mit Erklärung.
Installierbare Web-App (PWA), läuft offline, kostenlos gehostet über GitHub Pages.

**Live:** https://remigiuszkwapik-web.github.io/polish-guide/

## Auf dem Handy installieren
- **iPhone (Safari):** Seite öffnen → Teilen → „Zum Home-Bildschirm“
- **Android (Chrome):** Seite öffnen → Menü ⋮ → „App installieren“

Der Lernstand liegt auf dem Gerät (localStorage). Unter Einstellungen → Backup lässt er sich als Datei sichern und auf einem anderen Gerät wieder einlesen.

## Lokal entwickeln
Kein Build nötig.
```bash
python3 -m http.server 8000   # oder: npx serve .
```
Dann http://localhost:8000 öffnen.

## Aufbau
| Datei | Inhalt |
| --- | --- |
| `index.html` | App: Oberfläche, FSRS, Session-Logik |
| `content/grammar.js` | Grammatik-Leiter (10 Stufen), Erklärungen mit Beispielen, Regeln für „Warum?“, Einstiegstest |
| `content/kueche.js` | Kapitel 1 „Küche & Essen“: 10 Level, 80 Nomen, 40 Aspektpaare, 125 Grammatikaufgaben |
| `tools/validate.py` | Prüfskript für alle polnischen Inhalte |
| `tools/pruefbericht.md` | letzter Prüfbericht |
| `tools/geprueft.tsv` | von Hand bestätigte Formen mit Begründung |
| `sw.js` | Service Worker für Offline-Betrieb. **Bei jeder Änderung `VERSION` hochzählen**, sonst sehen installierte Apps die alte Fassung. |
| `manifest.webmanifest`, `icons/` | Installation als App |

Neue Kapitel: eine Datei `content/<kapitel>.js` nach dem Muster von `kueche.js` anlegen, in `index.html` und `sw.js` eintragen.

## Inhalte prüfen
```bash
bash tools/fetch-data.sh      # einmalig: Prüfdaten nach .data/ laden (ca. 90 MB)
python3 tools/validate.py     # schreibt tools/pruefbericht.md, Exit-Code 1 bei Fehlern
```
Geprüft wird jede polnische Form auf drei Wegen:
1. **Rechtschreibung** gegen das Hunspell-Wörterbuch pl_PL (LibreOffice, Basis sjp.pl)
2. **Grammatik** gegen die annotierten Textsammlungen UD_Polish-PDB und UD_Polish-LFG: Fall, Person, Aspekt, Genus. Fehlt eine Form im Korpus, prüft das Skript per **Analogie** (ähnliche Wörter mit gleicher Endung).
3. **Häufigkeit** aus FrequencyWords (OpenSubtitles 2018), nur zur Info

Jede Grammatikaufgabe trägt dafür ein Feld `m` mit Lemma und Merkmalen, z. B. `m:"lodówka|Case=Loc|Number=Sing"`. Was weder Korpus noch Analogie bestätigen, steht mit Begründung in `tools/geprueft.tsv`.

## Veröffentlichen
Jeder Push auf `main` geht automatisch live (GitHub Pages, „Deploy from a branch“, `main` / root).

## Roadmap
- Kapitel 2–10 nach dem Muster von Küche füllen
- Tatoeba-Sätze für Lückenaufgaben importieren
- Sync zwischen Geräten (z. B. über ein privates GitHub-Gist oder Supabase)
