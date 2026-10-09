#!/usr/bin/env bash
# Lädt die offenen Prüfdaten nach .data/ (nicht im Repo, siehe .gitignore).
#  - Hunspell-Wörterbuch pl_PL (LibreOffice, Basis sjp.pl): Rechtschreibung jeder Form
#  - Universal Dependencies UD_Polish-PDB und -LFG: Fall, Person, Aspekt, Genus aus echten Texten
#  - FrequencyWords pl (OpenSubtitles 2018): Häufigkeitsrang
#  - spylls: Hunspell in reinem Python
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .data && cd .data

sparse() { # repo dir pfad
  [ -d "$2" ] && return
  git clone -q --depth 1 --filter=blob:none --sparse "$1" "$2"
  git -C "$2" sparse-checkout set "$3"
}
sparse https://github.com/LibreOffice/dictionaries lo pl_PL
sparse https://github.com/hermitdave/FrequencyWords fw content/2018/pl
[ -d ud ] || git clone -q --depth 1 https://github.com/UniversalDependencies/UD_Polish-PDB ud
[ -d ud-lfg ] || git clone -q --depth 1 https://github.com/UniversalDependencies/UD_Polish-LFG ud-lfg
[ -d spylls ] || git clone -q --depth 1 https://github.com/zverok/spylls spylls
echo "Prüfdaten liegen in .data/"
