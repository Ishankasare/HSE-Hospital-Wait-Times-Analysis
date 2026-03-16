# Project Insights — HSE Hospital Waiting List Analysis

My personal observations from building this project and sitting with the data. These go deeper than the README summary.

---

## On the COVID Distortion

The most important thing to understand about this dataset is that 2020 and 2021 are not reliable baselines. When I first looked at the national trend, I noticed waiting lists appeared to drop during COVID. My instinct was to treat this as improvement. It is not.

What actually happened is that referrals collapsed. GPs stopped sending patients to hospital because hospitals were at capacity with COVID cases, and patients themselves stopped going to their GP. Procedures were cancelled. The waiting list shrank not because patients were treated but because patients disappeared from the system.

The implication for analysis is that any "improvement" shown between 2019 and 2021 is artificial, and any year-on-year comparison that uses 2020 or 2021 as a baseline will produce misleading results. The only honest comparison is 2019 vs 2022 onwards — pre-COVID actual state vs post-COVID recovery.

---

## On the €437 Million That Did Not Work

In 2024, the Irish government allocated €437 million specifically to reduce hospital waiting lists. The target was a 6% reduction. The actual result was an increase of 40,400 patients in the first six months alone.

This is one of the most analytically interesting findings in the project. It is a clear case where spending more money did not produce the intended outcome. Why?

The data points to a demand problem, not just a supply problem. The number of new referrals being added to waiting lists each month is growing faster than the system's capacity to treat them. This is driven by population growth, an ageing demographic, increased disease awareness, and post-COVID pent-up demand. More money for procedures helps, but if the number of new patients entering the system each month exceeds the number being treated, the list grows regardless.

The analyst's job here is not to report the number — it is to explain the mechanism. Why is demand exceeding capacity? Which specialties are the worst bottlenecks? Which hospitals are managing throughput most efficiently despite the pressure? Those are the questions that would actually inform policy.

---

## On Hospital-Level Variation

The national headline number — 911,500 waiting — is almost too large to be useful. It creates a sense of uniform crisis that obscures significant variation at the hospital level.

When I looked at the hospital-level data, I found hospitals in similar geographic contexts and of similar size performing very differently on long-wait percentages. Some hospitals have consistently reduced their 12+ month cohort year on year. Others have seen it grow. The difference is not always funding. It is often operational — theatre utilisation, outpatient scheduling efficiency, administrative backlogs.

The hospital scorecard query in this project (Q7 in the SQL file) attempts to capture this: it classifies hospitals as Improving, Critical or Monitoring based on their year-on-year change and long-wait percentage. This is the kind of output that would actually be useful to an HSE performance manager, not just a chart of total numbers.

---

## On Sláintecare and the Target Gap

Sláintecare is Ireland's 10-year health reform programme. Its waiting time targets — 10 weeks for outpatient, 12 weeks for inpatient — were set in 2017 and were described at the time as ambitious but achievable.

Eight years later, looking at this data, the targets appear further away than when they were set. The % of patients waiting within the target window has not shown consistent improvement. The 18+ months cohort — patients who have been waiting more than a year and a half — has grown.

This is not just a healthcare story. It is a policy accountability story. The data exists. The targets exist. The gap between them is measurable. The job of a data analyst in a policy or public sector context is exactly this: take the official target, measure the actual performance, and present the gap clearly enough that decision-makers cannot ignore it.

---

## On Using Official Government Data

One thing I found during this project is that official government data is often messier than Kaggle datasets. Column names changed between years. Date formats were inconsistent. Some hospital names changed over time (Children's Health Ireland was restructured in 2019). Small-volume data was suppressed for privacy.

This is actually more realistic training for a data analyst job than any cleaned dataset. In a real organisation, you will always be working with data that has quirks, legacy formats, and undocumented changes. The ability to detect and handle those inconsistencies without breaking your pipeline is a genuine professional skill.

---

*Built using official NTPF open data · ntpf.ie*
