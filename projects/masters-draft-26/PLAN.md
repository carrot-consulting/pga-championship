# Plan: masters-draft-26

## Context
6-person Masters 2026 sweepstake leaderboard. Each player drafts 4 golfers before the tournament. Live scores pulled from ESPN API, combined score determines ranking. Sunday captain mechanic doubles one golfer's R4 score.

**Live at:** `https://carrot-consulting.github.io/masters-draft-26/`

---

## Status: Built & Deployed ✓

### What's Done
- [x] Single-page `index.html` built — HTML, CSS, JS all in one file
- [x] ESPN unofficial API wired up (`site.api.espn.com`) — tested against Valero Texas Open
- [x] Score parsing fixed — uses `score.displayValue` (to-par string) not gross score
- [x] Leaderboard renders + sorts lowest-to-highest automatically
- [x] Click-to-expand team detail with round-by-round breakdown
- [x] Auto-refresh every 10 minutes with countdown timer
- [x] Captain R4 multiplier logic — doubles captain's Sunday score
- [x] Masters brand styling — Playfair Display font, Augusta green `#006747`, gold `#C9A84C`
- [x] Plain-English comments added throughout JS
- [x] Debug console.log removed (security fix)
- [x] GitHub repo created: `carrot-consulting/masters-draft-26`
- [x] GitHub Pages enabled and live
- [x] Security reviews completed (2026-04-06)

---

## To Do Before Thursday

### Wednesday April 8 — after the draft
- [ ] Send real Masters picks to Claude (6 sweepers, 4 golfers each)
- [ ] Claude updates `PICKS` in `index.html` with real names
- [ ] Verify golfer names match ESPN — open browser console, check for `⚠️ No match` warnings
- [ ] Fix any name mismatches (ESPN spelling takes priority)
- [ ] Set all `captain: null` (captains not picked until Saturday)
- [ ] Push to GitHub

### Thursday April 9 — tournament start
- [ ] Open the live page and confirm ESPN switches to Masters leaderboard
- [ ] If scores don't load: change `league=pga` → `league=masters` in `index.html` line ~360 and push
- [ ] Share the GitHub Pages link with all 6 sweepers

### Saturday April 12 — night before R4
- [ ] Send 6 captain picks to Claude (one per sweeper, must be from their 4 golfers)
- [ ] Claude updates each `captain: null` → `captain: "Golfer Name"`
- [ ] Push to GitHub before Sunday tee-off

---

## Architecture

### Data
ESPN unofficial API — free, no auth, CORS-friendly:
```
https://site.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga
```
Scores parsed from `score.displayValue` ("E", "-8", "+3") not raw value (gross score).

### Picks structure
```js
const PICKS = {
  "Simo": {
    golfers: ["Golfer 1", "Golfer 2", "Golfer 3", "Golfer 4"],
    captain: null  // → "Golfer Name" on Saturday night
  },
  // ... 6 total
};
```

### Captain R4 multiplier
```
sweeper total = sum of 4 golfers' totals + captain's R4 score (one extra copy)
```
Only activates once R4 data exists in ESPN response AND captain is set.

### Scoring
- Lower is better (golf)
- CUT players: score frozen at cut value
- Leaderboard auto-sorts on every refresh

---

## Visual Style
| Element | Value |
|---|---|
| Background | `#f0ede8` (warm cream) |
| Primary green | `#006747` (Augusta green) |
| Gold accent | `#C9A84C` |
| Heading font | Playfair Display (italic serif, Google Fonts) |
| Body font | Source Sans 3 |
| Mobile-first | Yes |

---

## Security Notes
- No secrets in tracked files
- Debug logging removed before go-live
- PAT removed from `.git/config` (switched to HTTPS auth)
- Google Fonts loads from external Google servers (low risk, acceptable for this use case)
- XSS via `thru` field (ESPN data → innerHTML) — low real-world risk, not fixed
