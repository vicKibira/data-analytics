# Storytelling Exercises

Notebook `04_business_analysis.ipynb` walks 5 findings using this
framework live. These exercises are additional practice — use them after
that notebook, either standalone or as a supplement to Module 10.

## The framework

```
Observation   — what happened? (a specific, verifiable fact from the data)
Explanation   — what pattern in the data explains it?
Implication   — why might this matter to the business?
Next question — what would you investigate next?
```

A finding is not complete until all four steps are written out. "Revenue
was $817,860" is an Observation, not a finding.

## Weak vs. strong — calibrate your ear first

**Weak:** "The Large size generates the most revenue."
*(True, but so what? No implication, no next step.)*

**Strong:** "Large pizzas generate $375,319 — 45.9% of all revenue — from
just one of five sizes. Combined with the fact that only one flavor (The
Greek) is offered in XL/XXL, this suggests the menu is implicitly steering
customers toward Large as the default 'big' option. If management wants to
test whether an even bigger size sells elsewhere, XL/XXL would need to be
offered on at least 2-3 more flavors before concluding there's no demand
for it — right now we only have one flavor's worth of evidence."

Notice what makes the second one strong: a specific number, a pattern
(not just a fact), a stated implication, AND an honest acknowledgment of
what the data can't yet tell you.

## Exercises

For each, produce a query or chart (your choice of SQL or Python) and
write all four framework steps. Don't skip to Implication without a solid
Observation and Explanation first.

### 1. The Independence Day check (🟡 Analyst)
We found a clear Thanksgiving-week revenue spike (`sql/07_advanced_analysis.sql`,
Notebook 04 Finding 5). Does 2015-07-04 (U.S. Independence Day) show the
same pattern? Write the finding either way — "no spike found" is a
legitimate, useful finding if you can show you checked correctly.

### 2. Order value by time of day (🟡 Analyst)
Notebook 03 found order value barely varies by day of week. Does it vary
by `time_of_day` (Morning/Lunch/Afternoon/Dinner/Late Night) instead? If
yes, is dinner really "bigger" orders, or just more of them?

### 3. Define "sells frequently but earns little" (🔴 Business Challenge)
Business Request 5 asks this exact question, but never defines a
threshold. Using `flavor_stats` from Notebook 04 (or your own SQL), pick
and justify a specific, numeric definition (e.g. "top-third by units AND
bottom-third by revenue-per-unit"), then produce a named list of flavors
that meet it. Defend your threshold choice in one sentence — why that cut
point and not another?

### 4. The size vs. flavor question (🔴 Business Challenge)
We found flavor choice explains relatively little of the revenue spread
(top 5 of 32 flavors = only 24.5%), but size (Module 9/10) explains a lot
more (L alone = 45.9%). Build a finding that directly compares these two
"levers" and recommends which one management should think about first
when planning a menu change — and be explicit about what evidence would
change your recommendation.

### 5. Write the one finding you'd lead with (🔴 Business Challenge)
If you had 60 seconds with the owner of Plato's Pizza and could share
exactly ONE finding from this entire project, which would it be and why?
Write it as a complete 4-step finding. There's no single right answer —
you're being evaluated on whether your choice is well-argued and
genuinely the most decision-relevant one you found, not on which fact you
pick.

## Self-check before you call a finding "done"

- [ ] Does the Observation include a specific number, not just a direction?
- [ ] Does the Explanation point to an actual pattern in the data, not a guess?
- [ ] Does the Implication say what a decision-maker should DO or consider?
- [ ] Have you stated what would need to be true for your implication to
      be wrong, or what data you'd need to be more confident?
- [ ] Would a stakeholder who read only your 4 sentences understand the
      finding without seeing your code or chart?
