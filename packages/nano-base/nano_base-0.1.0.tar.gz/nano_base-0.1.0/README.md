# nano-base
[![PyPI](https://img.shields.io/pypi/v/nano-base.svg?color=blue)](https://pypi.org/project/nano-base/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Size](https://img.shields.io/badge/size-~1KB-lightgrey.svg)
[![CI](https://github.com/ozgunlu/nano-base/actions/workflows/ci.yml/badge.svg)](https://github.com/ozgunlu/nano-base/actions)

Tiny **base converter (2..36)** — ~1 KB, zero deps.
`255 → FF (base 10→16)`, `FF → 11111111 (16→2)`, negatives supported. Perfect for code-golf, minimal containers, or just for fun.

---

## ✨ Features
- ✅ Convert **between any bases 2..36** (digits `0-9A-Z`, case-insensitive)
- ✅ Two forms:
  - `<value> <to_base>` (assumes `from=10`)
  - `<value> <from_base> <to_base>`
- ✅ Handles negatives, `0`

---

## 🚀 Usage
```bash
# Local (from repo)
python app_min.py 255 16        # FF
python app_min.py FF 16 2       # 11111111
python app_min.py -42 10 16     # -2A
```

After installing:

```bash
# CLI
pip install nano-base
nano-base 255 16                # -> FF
nano-base FF 16 2               # -> 11111111
nano-base -2A 16 10             # -> -42
```

---

## 🤓 Why so small?

- Uses int(s, base) + tiny loop to format in target base
- No bigint libs; Python int already arbitrary precision
- Single tiny file + tiny CLI: perfect for scripts, containers, CI.

---

## 🎉 Fun Ideas

- **Hex table (0..255)**
```bash
for i in $(seq 0 255); do printf "%3d -> %s\n" $i "$(nano-base $i 16)"; done
```
- **Binary width (pad with printf)**
```bash
printf "%08d\n" "$(nano-base 42 2)"   # 000101010 (pad separately)
```
- **Base36 IDs**
```bash
nano-base 123456789 10 36   # -> 21I3V9
```

---

> **Note: Valid range is bases 2..36; input is case-insensitive (a..z ≡ A..Z).**

---

## 📜 License

MIT © 2025

