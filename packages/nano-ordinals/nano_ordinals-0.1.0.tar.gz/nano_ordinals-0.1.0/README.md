# nano-ordinals
[![PyPI](https://img.shields.io/pypi/v/nano-ordinals.svg?color=blue)](https://pypi.org/project/nano-ordinals/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Size](https://img.shields.io/badge/size-~1KB-lightgrey.svg)
[![CI](https://github.com/ozgunlu/nano-ordinals/actions/workflows/ci.yml/badge.svg)](https://github.com/ozgunlu/nano-ordinals/actions)

Tiny **ordinal ↔ cardinal** converter — ~1 KB, zero deps.
`1 → 1st`, `2 → 2nd`, `11 → 11th`, `-3 → -3rd` … and back. Perfect for code-golf, minimal containers, or just for fun.

---

## ✨ Features
- ✅ Cardinal → ordinal (English suffix rules incl. `11/12/13 → th`)
- ✅ Ordinal → cardinal (case-insensitive: `21st`, `101ST`, `42nd`)
- ✅ Negative numbers supported (`-3 → -3rd`)
- ✅ Zero dependencies, single tiny file; CLI included

---

## 🚀 Usage
```bash
# Local (from repo)
python app_min.py 1      # 1st
python app_min.py 11     # 11th
python app_min.py -3     # -3rd
python app_min.py 21st   # 21
```

After installing:

```bash
# CLI
pip install nano-ordinals
nano-ordinals 42      # -> 42nd
nano-ordinals 101     # -> 101st
nano-ordinals 101st   # -> 101
```

---

## 🤓 Why so small?

- Minimal suffix rule: th unless endswith 1/2/3 and not 11/12/13
- Tiny regex: ([+-]?\d+)(st|nd|rd|th)?
- Single tiny file + tiny CLI: perfect for scripts, containers, CI.

---

## 🎉 Fun Ideas

- **Generate a calendar day label**
```bash
date +%d | sed 's/^0//' | xargs nano-ordinals       # 1 -> 1st, 21 -> 21st
```
```powershell
(Get-Date).Day | % { nano-ordinals $_ }              # 14 -> 14th
```
- **Ordinal list (1..20)**
```bash
seq 1 20 | xargs -I{} nano-ordinals {}
```
```powershell
1..20 | % { nano-ordinals $_ }
```
- **Rankings / leaderboards**
```bash
for n in 1 2 3 4; do echo "Player $n: $(nano-ordinals $n) place"; done
# Player 1: 1st place, Player 2: 2nd place, ...
```
- **Git commit count → ordinal**
```bash
nano-ordinals $(git rev-list --count HEAD)
# e.g., 42 -> 42nd commit
```
- **Rename files with ordinal indices**
```bash
i=1; for f in *.png; do mv "$f" "$(nano-ordinals $i)-$f"; i=$((i+1)); done
# 1st-image.png, 2nd-image.png, ...
```
- **Sort plain ordinal tokens numerically**
```bash
# lines like: 1st, 21st, 3rd...
awk '{print $0 "|" system("nano-ordinals "$0)}' ordinals.txt >/dev/null   # sanity check
paste <(cat ordinals.txt) <(sed 's/$//' ordinals.txt | xargs -n1 nano-ordinals) \
  | sort -k2,2n | cut -f1
```
- **Reverse conversion (ordinal → number)**
```bash
for x in 21st 101st 42nd; do echo "$x -> $(nano-ordinals $x)"; done
# 21st -> 21, 101st -> 101, 42nd -> 42
```

---

> **Tip: Input that contains letters is treated as ordinal → cardinal; digits-only is cardinal → ordinal.

---

## 📜 License

MIT © 2025

