# Poll Math

Poll margin of error arithmetic. A poll of 1,000 people has a margin of ±3.10 points at 95% confidence.

## What it computes

- **The margin truth** - the margin of error for a poll of a given size and share, and the range the whole group's share could fall in.
- **The size truth** - the smallest sample whose margin is no wider than a margin you choose (exact fraction arithmetic, rounded up to whole people).
- **The gap truth** - the margin on the difference between two separate polls, and whether the gap is larger than that margin.

Sample sizes are whole numbers from 1 to 10000000. Shares are percents from 1 to 99 with up to 1 decimal. Margins are 0.1 to 50 points with up to 2 decimals. Confidence is 90, 95 or 99 percent, using the fixed z values 1.645, 1.96 and 2.576. Margins are rounded half up to 2 decimals.

## Boundary

Arithmetic only, for a simple random sample. It does not know how any real poll was run (weighting, non-response, question wording, design effects) and says nothing about whether a poll is good. Every figure is the owner's own entry.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (floating point for the margin, BigInt fractions for the sample size).
- `oracle.py` - the Python mirror (50-digit Decimal square roots, exact Fractions) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (72 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/pollmath/
Repo: https://github.com/iLanis-agent/pollmath
