#!/usr/bin/env python3
# Poll Math oracle - mirrors engine.js. Margins use 50-digit Decimal square roots rounded half up; sample sizes use exact Fractions.
import json, re
from decimal import Decimal, getcontext, ROUND_HALF_UP
from fractions import Fraction
from math import ceil
getcontext().prec = 50

N_ERR = "sample size must be a whole number from 1 to 10000000"
P_ERR = "share must be a percent from 1 to 99 with at most 1 decimal"
M_ERR = "margin must be from 0.1 to 50 points with at most 2 decimals"
C_ERR = "confidence must be 90, 95 or 99"
ZS = {"90": "1.645", "95": "1.96", "99": "2.576"}

def people(n): return f"{n:,} " + ("person" if n == 1 else "people")

def num(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,8}", t) or not 1 <= int(t) <= 10000000:
        raise ValueError(N_ERR)
    return int(t)

def share(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,2}(\.[0-9])?", t):
        raise ValueError(P_ERR)
    f = Fraction(t)
    if f < 1 or f > 99:
        raise ValueError(P_ERR)
    return f  # percent

def conf(t):
    t = t.strip() if isinstance(t, str) else ""
    if t not in ZS:
        raise ValueError(C_ERR)
    return t

def pct(f):
    s = f"{float(f):.1f}"
    return s[:-2] if s.endswith(".0") else s

def q2(d): return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def moe(var, c): return Decimal(ZS[c]) * 100 * var.sqrt()

def margin_truth(n, s, c):
    N = num(n); f = share(s); c = conf(c)
    p = Decimal(f.numerator) / Decimal(f.denominator) / 100
    m = moe(p * (1 - p) / N, c)
    centre = Decimal(f.numerator) / Decimal(f.denominator)
    lo = max(Decimal(0), centre - m); hi = min(Decimal(100), centre + m)
    return (f"A poll of {people(N)} with {pct(f)}% on one side has a margin of \u00b1{q2(m)} points at {c}% confidence, "
            f"so the whole group's share could be anywhere from {q2(lo)}% to {q2(hi)}%.")

def size_truth(m, s, c):
    mt = m.strip() if isinstance(m, str) else ""
    if not re.fullmatch(r"[0-9]{1,2}(\.[0-9]{1,2})?", mt):
        raise ValueError(M_ERR)
    mf = Fraction(mt)
    if mf < Fraction(1, 10) or mf > 50:
        raise ValueError(M_ERR)
    f = share(s); c = conf(c)
    z = Fraction(ZS[c]); p = f / 100
    n = ceil(z * z * p * (1 - p) / ((mf / 100) ** 2))
    shown = mt.rstrip("0").rstrip(".") if "." in mt else mt
    return f"To get a margin of \u00b1{shown} points at {c}% confidence with {pct(f)}% on one side, a poll needs {people(n)}."

def gap_truth(n1, p1, n2, p2, c):
    a = num(n1); x = share(p1); b = num(n2); y = share(p2); c = conf(c)
    pa = Decimal(x.numerator) / Decimal(x.denominator) / 100
    pb = Decimal(y.numerator) / Decimal(y.denominator) / 100
    m = moe(pa * (1 - pa) / a + pb * (1 - pb) / b, c)
    gap = abs(x - y)
    gd = Decimal(gap.numerator) / Decimal(gap.denominator)
    word = "larger than" if gd > m else "not larger than"
    return (f"Poll A has {pct(x)}% of {people(a)} and poll B has {pct(y)}% of {people(b)}. The gap is {q2(gd)} points and its margin is "
            f"\u00b1{q2(m)} points at {c}% confidence, so the gap is {word} its margin.")

FNS = {"marginTruth": margin_truth, "sizeTruth": size_truth, "gapTruth": gap_truth}
CASES = [
    ("marginTruth", ["1000", "50", "95"]), ("marginTruth", ["1000", "50", "90"]), ("marginTruth", ["1000", "50", "99"]), ("marginTruth", ["400", "50", "95"]),
    ("marginTruth", ["1", "50", "95"]), ("marginTruth", ["2", "5", "99"]), ("marginTruth", ["10000000", "50", "95"]), ("marginTruth", ["1000", "10", "95"]),
    ("marginTruth", ["1000", "90", "95"]), ("marginTruth", ["1000", "1", "95"]), ("marginTruth", ["1000", "99", "99"]), ("marginTruth", ["1500", "47.5", "95"]),
    ("marginTruth", ["600", "30.5", "90"]), ("marginTruth", [" 1000 ", " 50 ", " 95 "]), ("marginTruth", ["12345", "62", "95"]), ("marginTruth", ["100", "50", "99"]),
    ("marginTruth", ["10", "3", "99"]), ("marginTruth", ["250", "75", "90"]), ("marginTruth", ["2500", "50", "95"]), ("marginTruth", ["800", "20", "95"]),
    ("marginTruth", ["0", "50", "95"]), ("marginTruth", ["10000001", "50", "95"]), ("marginTruth", ["1.5", "50", "95"]), ("marginTruth", ["abc", "50", "95"]),
    ("marginTruth", ["1000", "0.9", "95"]), ("marginTruth", ["1000", "99.5", "95"]), ("marginTruth", ["1000", "50.55", "95"]), ("marginTruth", ["1000", "x", "95"]),
    ("marginTruth", ["1000", "50", "80"]), ("marginTruth", ["1000", "50", ""]),
    ("sizeTruth", ["3", "50", "95"]), ("sizeTruth", ["5", "50", "95"]), ("sizeTruth", ["1", "50", "95"]), ("sizeTruth", ["3", "50", "99"]),
    ("sizeTruth", ["3", "50", "90"]), ("sizeTruth", ["0.1", "50", "99"]), ("sizeTruth", ["50", "50", "90"]), ("sizeTruth", ["3", "10", "95"]),
    ("sizeTruth", ["3.5", "50", "95"]), ("sizeTruth", ["3.50", "50", "95"]), ("sizeTruth", ["10", "50", "95"]), ("sizeTruth", ["10.0", "50", "95"]),
    ("sizeTruth", ["2", "30.5", "95"]), ("sizeTruth", ["4", "99", "95"]), ("sizeTruth", ["4", "1", "99"]), ("sizeTruth", ["0.25", "50", "95"]),
    ("sizeTruth", ["25", "50", "90"]), ("sizeTruth", ["1.5", "70", "99"]), ("sizeTruth", ["0.05", "50", "95"]), ("sizeTruth", ["51", "50", "95"]),
    ("sizeTruth", ["abc", "50", "95"]), ("sizeTruth", ["3", "0", "95"]), ("sizeTruth", ["3", "50", "97"]), ("sizeTruth", ["", "50", "95"]),
    ("sizeTruth", ["-3", "50", "95"]), ("sizeTruth", ["3.123", "50", "95"]),
    ("gapTruth", ["800", "52", "1200", "48", "95"]), ("gapTruth", ["1000", "50", "1000", "50", "95"]), ("gapTruth", ["1000", "55", "1000", "45", "95"]), ("gapTruth", ["1000", "52", "1000", "48", "90"]),
    ("gapTruth", ["1000", "52", "1000", "48", "99"]), ("gapTruth", ["1", "50", "1", "50", "95"]), ("gapTruth", ["500", "30", "700", "35.5", "95"]), ("gapTruth", ["10000000", "50", "10000000", "50.1", "95"]),
    ("gapTruth", ["10000000", "50", "10000000", "50.1", "99"]), ("gapTruth", ["300", "10", "300", "20", "90"]), ("gapTruth", ["1200", "47", "900", "51", "95"]), ("gapTruth", ["0", "50", "100", "50", "95"]),
    ("gapTruth", ["100", "50", "x", "50", "95"]), ("gapTruth", ["100", "0", "100", "50", "95"]), ("gapTruth", ["100", "50", "100", "100", "95"]), ("gapTruth", ["100", "50", "100", "50", "85"]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(len(out), "cases")
