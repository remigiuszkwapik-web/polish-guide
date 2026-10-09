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
| `index.html` | ganze App: Inhalte, FSRS, Oberfläche |
| `sw.js` | Service Worker für Offline-Betrieb. **Bei jeder Änderung `VERSION` hochzählen**, sonst sehen installierte Apps die alte Fassung. |
| `manifest.webmanifest` | Name, Farben, Icons für die Installation |
| `icons/` | App-Icons (SVG + PNG) |

In `index.html`:
| Block | Inhalt |
| --- | --- |
| `STAGES` | Grammatik-Leiter, 10 Stufen |
| `RULES` | Regeln mit Erklärung („Warum?“) und Muster |
| `NOUNS`, `VERBS` | Wortschatz Kapitel Küche, Level 1–3; Verben als Aspektpaar |
| `DRILLS` | Grammatikaufgaben (Lücke tippen oder Aspekt wählen) |
| `TEST` | Einstiegstest, 3 Fragen pro Stufe 1–7 |
| FSRS-Block | FSRS-5 mit Standardgewichten, wie in Anki |
| `buildQueue` | fällige Karten zuerst, dann neue bis zum Tageslimit (Standard 20) |

## Veröffentlichen
Jeder Push auf `main` geht automatisch live (GitHub Pages, „Deploy from a branch“, `main` / root).

## Roadmap
- Inhalte in JSON-Dateien pro Kapitel auslagern (`content/kueche.json` …)
- Kapitel 2 und 3, Grammatik-Leiter bis Verbaspekt ausbauen
- Tatoeba-Sätze für Lückenaufgaben importieren
- Sync zwischen Geräten (z. B. über ein privates GitHub-Gist oder Supabase)
