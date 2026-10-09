#!/usr/bin/env python3
"""Prüft alle polnischen Inhalte in content/*.js gegen offene Sprachdaten.

Drei Prüfungen:
  1. Rechtschreibung: jedes polnische Wort muss im Hunspell-Wörterbuch pl_PL stehen.
  2. Grammatik: Fall, Person, Aspekt und Genus werden gegen die annotierte Textsammlung
     UD_Polish-PDB geprüft. Kommt ein Wort dort mit den verlangten Merkmalen vor, muss
     die Lösung eine der belegten Formen sein. Sonst gilt es als „nicht belegt“.
  3. Häufigkeit: Rang des Wortes in der OpenSubtitles-Liste (nur Info).

Aufruf:  bash tools/fetch-data.sh && python3 tools/validate.py
Ergebnis: tools/pruefbericht.md, Exit-Code 1 bei Fehlern.
"""
import json, os, re, subprocess, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, ".data")
sys.path.insert(0, os.path.join(DATA, "spylls"))
from spylls.hunspell import Dictionary  # noqa: E402

WORD = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+")

# ---------- Daten laden ----------
content = json.loads(subprocess.check_output(["node", os.path.join(ROOT, "tools", "dump-content.js")]))
hun = Dictionary.from_files(os.path.join(DATA, "lo", "pl_PL", "pl_PL"))

def feats_of(s):
    return dict(kv.split("=", 1) for kv in s.split("|")) if s and s != "_" else {}

# UD-Index: lemma -> Counter((form, upos, frozenset(feats)))
idx = defaultdict(Counter)
def add(lemma, form, upos, feats):
    idx[lemma.lower()][(form.lower(), upos, frozenset(feats.items()))] += 1

UD_DIRS = [d for d in ("ud", "ud-lfg") if os.path.isdir(os.path.join(DATA, d))]
for fp in sorted(os.path.join(DATA, d, f) for d in UD_DIRS for f in os.listdir(os.path.join(DATA, d)) if f.endswith(".conllu")):
    lines = [l.rstrip("\n").split("\t") for l in open(fp, encoding="utf8") if l.strip() and not l.startswith("#")]
    i = 0
    while i < len(lines):
        c = lines[i]
        if "-" in c[0]:  # Mehrwort-Token, z. B. byłem = był + em
            a, b = map(int, c[0].split("-"))
            parts = lines[i + 1:i + 2 + (b - a)]
            head = parts[0]
            f = feats_of(head[5])
            for p in parts[1:]:
                pf = feats_of(p[5])
                if "Person" in pf: f["Person"] = pf["Person"]
                if "Number" in pf and "Number" not in f: f["Number"] = pf["Number"]
            add(head[2], c[1], head[3], f)
            for p in parts:
                add(p[2], p[1], p[3], feats_of(p[5]))
            i += 1 + len(parts)
            continue
        if c[0].isdigit():
            add(c[2], c[1], c[3], feats_of(c[5]))
        i += 1

rank = {}
for n, line in enumerate(open(os.path.join(DATA, "fw", "content", "2018", "pl", "pl_50k.txt"), encoding="utf8"), 1):
    w = line.split(" ")[0]
    rank.setdefault(w, n)

# ---------- Prüffunktionen ----------
def spell(text):
    bad = []
    for w in WORD.findall(text):
        if not (hun.lookup(w) or hun.lookup(w.lower()) or hun.lookup(w.capitalize())):
            bad.append(w)
    return bad

def forms(lemma, req):
    out = Counter()
    for (form, upos, fs), n in idx.get(lemma.lower(), {}).items():
        d = dict(fs)
        if all(d.get(k) == v for k, v in req.items()):
            out[form] += n
    return out

def morph(lemma, req, expected, gender=None):
    """-> (status, detail); status: ok | analogie | prüfen | fehler | unbelegt"""
    f = forms(lemma, req)
    exp = expected.lower()
    if f:
        if exp in f:
            return "ok", f"belegt {f[exp]}×"
        return "fehler", f"erwartet „{expected}“, Korpus hat: " + ", ".join(f"{k} ({v}×)" for k, v in f.most_common(3))
    if " " not in exp:
        a = analogy(lemma, req, expected, gender)
        if a:
            return a
    if lemma.lower() in idx:
        return "unbelegt", "Wort bekannt, diese Form nicht belegt"
    return "unbelegt", "Wort nicht im Korpus"

GMAP = {"m": "Masc", "f": "Fem", "n": "Neut"}

def analogy(lemma, req, expected, gender=None):
    """Prüft eine im Korpus fehlende Form über ähnliche Wörter: gleiche Endung, gleiche Merkmale.
    Beispiel: lodówka → lodówce, weil półka → półce, ławka → ławce … im Korpus belegt sind."""
    lemma = lemma.lower(); exp = expected.lower()
    upos = "NOUN" if "Case" in req else "VERB"
    for k in (4, 3, 2):
        if len(lemma) <= k:
            continue
        end = lemma[-k:]
        preds = Counter(); support = 0
        for cl, entries in idx.items():
            if cl == lemma or not cl.endswith(end):
                continue
            best = Counter()
            for (form, up, fs), c in entries.items():
                d = dict(fs)
                if up != upos or not all(d.get(a) == b for a, b in req.items()):
                    continue
                if gender and d.get("Gender") != gender:
                    continue
                best[form] += c
            if not best:
                continue
            f = best.most_common(1)[0][0]
            p = os.path.commonprefix([cl, f])
            lsuf, fsuf = cl[len(p):], f[len(p):]
            if lemma.endswith(lsuf):
                preds[lemma[:len(lemma) - len(lsuf)] + fsuf] += 1
                support += 1
        if support >= 3:
            top, n = preds.most_common(1)[0]
            if top == exp:
                return "analogie", f"wie {preds[exp]} von {support} Wörtern auf -{end}"
            if preds[exp] >= max(2, support // 4):
                return "analogie", f"wie {preds[exp]} von {support} Wörtern auf -{end} (häufiger: {top})"
            return "prüfen", f"ähnliche Wörter auf -{end} ergeben eher „{top}“ ({n} von {support})"
    return None

def parse_m(m):
    lemma, *fs = m.split("|")
    return lemma, dict(x.split("=", 1) for x in fs)

GENDER = {"Masc": "m", "Fem": "f", "Neut": "n"}

# Von Hand bestätigte Formen (tools/geprueft.tsv)
MANUAL = {}
for line in open(os.path.join(ROOT, "tools", "geprueft.tsv"), encoding="utf8"):
    if line.strip() and not line.startswith("#"):
        w, why = line.rstrip("\n").split("\t", 1)
        MANUAL[w.lower()] = why

# ---------- Prüfen ----------
rows = []  # (bereich, element, prüfung, status, detail)
def r(area, item, check, status, detail="", key=None):
    if status in ("prüfen", "unbelegt") and key and key.lower() in MANUAL:
        status, detail = "manuell", MANUAL[key.lower()]
    rows.append((area, item, check, status, detail))

def spell_row(area, item, text):
    bad = spell(text)
    r(area, item, "Rechtschreibung", "fehler" if bad else "ok", ("unbekannt: " + ", ".join(bad)) if bad else "")

GENDER_OF = {n["pl"].lower(): GMAP[n["g"]] for ch in content["chapters"] for n in ch["nouns"]}
for ch in content["chapters"]:
    A = ch["name"]
    for n in ch["nouns"]:
        item = f"L{n['lvl']} {n['pl']}"
        spell_row(A, item, n["pl"])
        g = Counter()
        for (form, upos, fs), c in idx.get(n["pl"].lower(), {}).items():
            if upos == "NOUN":
                gg = dict(fs).get("Gender")
                if gg: g[GENDER.get(gg, gg)] += c
        if g:
            top = g.most_common(1)[0][0]
            r(A, item, "Genus", "ok" if top == n["g"] else "fehler", f"Korpus: {dict(g)}" if top != n["g"] else "")
        else:
            r(A, item, "Genus", "unbelegt", "Wort nicht im Korpus", key=n["pl"])
    for v in ch["verbs"]:
        item = f"L{v['lvl']} {v['impf']}/{v['pf']}"
        spell_row(A, item, " ".join([v["impf"], v["pf"], v["ja"], v["ty"]]))
        for lem, asp, name in ((v["impf"], "Imp", "imperfektiv"), (v["pf"], "Perf", "perfektiv")):
            f = forms(lem, {"Aspect": asp})
            other = forms(lem, {"Aspect": "Perf" if asp == "Imp" else "Imp"})
            if f:
                r(A, item, f"Aspekt {lem}", "ok", "")
            elif other:
                r(A, item, f"Aspekt {lem}", "fehler", f"Korpus führt {lem} als {'perfektiv' if asp == 'Imp' else 'imperfektiv'}")
            else:
                r(A, item, f"Aspekt {lem}", "unbelegt", "Wort nicht im Korpus", key=lem)
        for form, person in ((v["ja"], "1"), (v["ty"], "2")):
            st, d = morph(v["impf"], {"Person": person, "Number": "Sing", "Tense": "Pres", "VerbForm": "Fin"}, form)
            r(A, item, f"Präsens {person}. Person ({form})", st, d, key=form)
    for d in ch["drills"]:
        item = f"L{d['lvl']} {d['id']}: {d['q']}"
        spell_row(A, item, " ".join([d["q"].replace("___", d["a"])] + d.get("mc", [])))
        if d.get("m"):
            lemma, req = parse_m(d["m"])
            st, det = morph(lemma, req, d["a"], GENDER_OF.get(lemma.lower()) if "Case" in req else None)
            r(A, item, f"Form {d['a']} ({d['m']})", st, det, key=d["a"])
        elif not d.get("mc"):
            r(A, item, "Form", "unbelegt", "keine Merkmale (m) angegeben")

for n, info in content["stageInfo"].items():
    for de, pl in info["ex"]:
        spell_row("Grammatik-Erklärungen", f"Stufe {n}: {pl}", pl)
for t in content["test"]:
    spell_row("Einstiegstest", f"Stufe {t['s']}: {t['q']}", " ".join([t["q"].replace("___", t["o"][0])] + t["o"]))

# ---------- Bericht ----------
cnt = Counter(s for *_, s, _ in rows)
freq = []
for ch in content["chapters"]:
    for n in ch["nouns"]:
        freq.append((n["lvl"], n["pl"], rank.get(n["pl"].lower())))
    for v in ch["verbs"]:
        freq.append((v["lvl"], v["impf"], rank.get(v["impf"].lower())))

out = ["# Prüfbericht Inhalte", "",
       f"{len(rows)} Prüfungen: **{cnt['ok']} im Korpus belegt**, **{cnt['analogie']} per Analogie bestätigt**, **{cnt['fehler']} Fehler**, {cnt['manuell']} von Hand bestätigt, {cnt['prüfen']} zum Nachprüfen, {cnt['unbelegt']} nicht belegt (nur Rechtschreibung geprüft).", "",
       "Analogie heißt: Die Form ist im Korpus nicht belegt, aber ähnliche Wörter mit derselben Endung bilden sie genauso.", "",
       "Erzeugt mit `python3 tools/validate.py`. Quellen: Hunspell pl_PL (LibreOffice/sjp.pl), UD_Polish-PDB und UD_Polish-LFG (CC BY-SA 4.0 bzw. GPL 3), FrequencyWords (OpenSubtitles 2018).", ""]
for title, keep in (("Fehler", "fehler"), ("Zum Nachprüfen", "prüfen"), ("Nicht belegt", "unbelegt"), ("Von Hand bestätigt (tools/geprueft.tsv)", "manuell"), ("Per Analogie bestätigt", "analogie")):
    sel = [x for x in rows if x[3] == keep]
    out += [f"## {title} ({len(sel)})", ""]
    if sel:
        out += ["| Bereich | Element | Prüfung | Detail |", "| --- | --- | --- | --- |"]
        out += [f"| {a} | {i} | {c} | {d} |" for a, i, c, s, d in sel]
    else:
        out.append("Keine.")
    out.append("")
out += ["## Häufigkeit", "", "Rang in den 50.000 häufigsten Wortformen (kleiner = häufiger).", "", "| Level | Wort | Rang |", "| --- | --- | --- |"]
out += [f"| {l} | {w} | {rk if rk else '> 50.000'} |" for l, w, rk in sorted(freq, key=lambda x: (x[0], x[2] or 10**9))]
open(os.path.join(ROOT, "tools", "pruefbericht.md"), "w", encoding="utf8").write("\n".join(out) + "\n")

print(f"{len(rows)} Prüfungen: {cnt['ok']} belegt, {cnt['analogie']} Analogie, {cnt['manuell']} von Hand, {cnt['fehler']} Fehler, {cnt['prüfen']} prüfen, {cnt['unbelegt']} nicht belegt → tools/pruefbericht.md")
for a, i, c, s, d in rows:
    if s in ("fehler", "prüfen"):
        print(f"  {s.upper():7} {i} · {c} · {d}")
sys.exit(1 if cnt["fehler"] else 0)
