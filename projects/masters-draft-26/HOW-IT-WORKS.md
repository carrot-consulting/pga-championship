# How It Works — Masters Draft 2026

## Data Source

The page hits ESPN's unofficial API every 10 minutes:
```
https://site.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga
```

> **Masters week:** ESPN may serve the tournament under `league=masters` instead of `league=pga`. If scores don't load Thursday morning, change `league=pga` → `league=masters` in the `API_URL` constant at the top of the script in `index.html`.

A manual page refresh always pulls fresh data from ESPN immediately, regardless of the 10-minute auto-refresh timer.

---

## Flow

1. **`fetchScores()`** — calls the ESPN API on page load and every 10 minutes
2. **`parseScores()`** — builds a lookup table of every golfer's scores, keyed by name:
   - `total` — overall score to par
   - `rounds[]` — per-round scores (R1–R4)
   - `thru` — current hole or "F" if finished
   - `isCut`, `isWD`, `isWinner` — status flags
3. **`calcSweeper()`** — adds up each drafter's combined score from their 4 golfers
4. **`renderLeaderboard()`** — sorts drafters lowest-to-highest and draws the table

---

## Scoring Rules

| Situation | Effect |
|---|---|
| Normal | Golfer's total score to par |
| Missed cut | Golfer's total + **+5 penalty** |
| Winner | Golfer's total - **5 bonus** |
| Captain (R4 only) | Captain's R4 score counted twice (doubles their R4 contribution) |

Captain logic only activates once `captain:` is set in `PICKS` and the golfer has a Round 4 score in the API. Safe to leave `null` until Saturday night.

---

## Golfer Name Matching

Golfer names in `PICKS` must match ESPN's `displayName` exactly. If a golfer shows "–" for all scores, it's a name mismatch. Open the browser console — mismatches are logged as warnings.

---

## Things to Do During the Tournament

| When | Action |
|---|---|
| Thursday morning | Check scores load. If not, switch `league=pga` → `league=masters` in `API_URL` |
| Saturday night (before R4) | Set `captain: "Golfer Name"` for each drafter in `PICKS` |

---

## Auto-Refresh

- Scores refresh automatically every 10 minutes
- A countdown timer in the header shows when the next refresh is
- Manual page refresh always fetches fresh data immediately
