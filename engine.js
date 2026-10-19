// Poll Math engine: margin of error and sample size arithmetic for a simple random sample.
var N_ERR = "sample size must be a whole number from 1 to 10000000";
var P_ERR = "share must be a percent from 1 to 99 with at most 1 decimal";
var M_ERR = "margin must be from 0.1 to 50 points with at most 2 decimals";
var C_ERR = "confidence must be 90, 95 or 99";
var Z = { "90": 1.645, "95": 1.96, "99": 2.576 };
var Z2 = { "90": [2706025n, 1000000n], "95": [38416n, 10000n], "99": [6635776n, 1000000n] };

function _pl(n, w) { return n + " " + w + (n === 1 ? "" : "s"); }
function _ppl(n) { return _grp(n) + (String(n) === "1" ? " person" : " people"); }
function _grp(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
function _n(text) {
  var t = typeof text === "string" ? text.trim() : "";
  if (!/^[0-9]{1,8}$/.test(t) || parseInt(t, 10) < 1 || parseInt(t, 10) > 10000000) throw new Error(N_ERR);
  return parseInt(t, 10);
}
function _p(text) {
  var t = typeof text === "string" ? text.trim() : "";
  if (!/^[0-9]{1,2}(\.[0-9])?$/.test(t)) throw new Error(P_ERR);
  var tenths = Math.round(parseFloat(t) * 10);
  if (tenths < 10 || tenths > 990) throw new Error(P_ERR);
  return tenths;
}
function _c(text) {
  var t = typeof text === "string" ? text.trim() : "";
  if (!Object.prototype.hasOwnProperty.call(Z, t)) throw new Error(C_ERR);
  return t;
}
function _tenths(t) { var s = (t / 10).toFixed(1); return s.replace(/\.0$/, ""); }
function _moe(n, tenths, c) { var p = tenths / 1000; return Z[c] * 100 * Math.sqrt(p * (1 - p) / n); }

// The margin truth: how far a poll result can sit from the whole group's answer.
function marginTruth(n, share, conf) {
  var N = _n(n), t = _p(share), c = _c(conf);
  var m = _moe(N, t, c), centre = t / 10;
  var lo = Math.max(0, centre - m), hi = Math.min(100, centre + m);
  return "A poll of " + _ppl(N) + " with " + _tenths(t) + "% on one side has a margin of \u00b1" + m.toFixed(2) +
    " points at " + c + "% confidence, so the whole group's share could be anywhere from " + lo.toFixed(2) + "% to " + hi.toFixed(2) + "%.";
}

// The size truth: the smallest sample whose margin is no wider than the one asked for.
function sizeTruth(margin, share, conf) {
  var mt = typeof margin === "string" ? margin.trim() : "";
  if (!/^[0-9]{1,2}(\.[0-9]{1,2})?$/.test(mt)) throw new Error(M_ERR);
  var parts = mt.split("."), frac = parts.length > 1 ? parts[1] : "";
  var mn = BigInt(parts[0] + frac), md = 10n ** BigInt(frac.length);
  if (mn * 10n < md || mn > 50n * md) throw new Error(M_ERR);
  var t = _p(share), c = _c(conf);
  // n = z^2 * p * (1 - p) / (m / 100)^2, with p = t / 1000
  var zn = Z2[c][0], zd = Z2[c][1], T = BigInt(t);
  var num = zn * T * (1000n - T) * 10000n * md * md;
  var den = zd * 1000n * 1000n * mn * mn;
  var n = (num + den - 1n) / den;
  return "To get a margin of \u00b1" + mt.replace(/\.?0+$/, function (x) { return mt.indexOf(".") < 0 ? x : ""; }) + " points at " + c + "% confidence with " + _tenths(t) +
    "% on one side, a poll needs " + _ppl(n) + ".";
}

// The gap truth: the margin on the difference between two separate polls.
function gapTruth(n1, p1, n2, p2, conf) {
  var a = _n(n1), x = _p(p1), b = _n(n2), y = _p(p2), c = _c(conf);
  var pa = x / 1000, pb = y / 1000;
  var m = Z[c] * 100 * Math.sqrt(pa * (1 - pa) / a + pb * (1 - pb) / b);
  var gapT = Math.abs(x - y), gap = gapT / 10;
  return "Poll A has " + _tenths(x) + "% of " + _ppl(a) + " and poll B has " + _tenths(y) + "% of " +
    _ppl(b) + ". The gap is " + gap.toFixed(2) + " points and its margin is \u00b1" + m.toFixed(2) +
    " points at " + c + "% confidence, so the gap is " + (gap > m ? "larger than" : "not larger than") + " its margin.";
}
