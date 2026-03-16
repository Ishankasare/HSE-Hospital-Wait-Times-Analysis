-- ============================================================
-- HSE Hospital Wait Times — SQL Analysis Queries
-- ============================================================
-- Author:      Ishan Kasare
-- GitHub:      https://github.com/Ishankasare/HSE-Hospital-Wait-Times-Analysis
--
-- Database:    SQLite (data/hse_waits.db)
-- Tables:
--   op_waiting          — Outpatient waits by hospital/month
--   ipdc_waiting        — Inpatient/Day Case by hospital/month
--   specialty_waiting   — All waits by specialty over time
--
-- Run in DB Browser for SQLite after clean_data.py
-- ============================================================


-- ============================================================
-- SECTION 1 — NATIONAL OVERVIEW
-- ============================================================

-- Q1: Total patients waiting nationally by year
SELECT
    year,
    wait_type,
    SUM(total_waiting)                          AS total_patients,
    LAG(SUM(total_waiting)) OVER (
        PARTITION BY wait_type ORDER BY year
    )                                           AS prev_year,
    ROUND(
        (SUM(total_waiting) - LAG(SUM(total_waiting)) OVER (
            PARTITION BY wait_type ORDER BY year)
        ) * 100.0 /
        NULLIF(LAG(SUM(total_waiting)) OVER (
            PARTITION BY wait_type ORDER BY year), 0)
    , 1)                                        AS yoy_change_pct
FROM op_waiting
GROUP BY year, wait_type
ORDER BY year, wait_type;


-- Q2: How did COVID-19 (2020-2021) affect waiting lists?
SELECT
    year,
    SUM(total_waiting) AS total_op_waiting,
    CASE
        WHEN year < 2020  THEN 'Pre-COVID'
        WHEN year = 2020  THEN 'COVID Year 1'
        WHEN year = 2021  THEN 'COVID Year 2'
        ELSE 'Post-COVID'
    END AS period
FROM op_waiting
GROUP BY year
ORDER BY year;


-- Q3: What % of patients are waiting over 12 months nationally?
SELECT
    year,
    wait_type,
    ROUND(AVG(pct_over_12m), 1) AS avg_pct_over_12_months,
    MAX(pct_over_12m)           AS worst_hospital_pct
FROM op_waiting
GROUP BY year, wait_type
ORDER BY year;


-- ============================================================
-- SECTION 2 — HOSPITAL PERFORMANCE
-- ============================================================

-- Q4: Top 20 hospitals with most patients waiting (latest year)
SELECT
    hospital,
    SUM(total_waiting) AS total_waiting,
    ROUND(AVG(pct_over_12m), 1) AS avg_pct_over_12m,
    RANK() OVER (ORDER BY SUM(total_waiting) DESC) AS national_rank
FROM op_waiting
WHERE year = (SELECT MAX(year) FROM op_waiting)
GROUP BY hospital
ORDER BY total_waiting DESC
LIMIT 20;


-- Q5: Which hospitals improved most year-on-year?
WITH yearly AS (
    SELECT
        hospital,
        year,
        SUM(total_waiting) AS total
    FROM op_waiting
    GROUP BY hospital, year
),
comparison AS (
    SELECT
        a.hospital,
        a.year AS current_year,
        a.total AS current_total,
        b.total AS prev_total,
        ROUND((a.total - b.total) * 100.0 / NULLIF(b.total, 0), 1) AS change_pct
    FROM yearly a
    JOIN yearly b ON a.hospital = b.hospital AND a.year = b.year + 1
)
SELECT * FROM comparison
ORDER BY change_pct ASC  -- Most improved (biggest reduction) first
LIMIT 20;


-- Q6: Which hospitals are performing worst for long waits?
SELECT
    hospital,
    year,
    SUM(total_waiting)          AS total_waiting,
    ROUND(AVG(pct_over_12m), 1) AS avg_pct_over_12m,
    MAX("18+ Months")           AS max_over_18m,
    RANK() OVER (
        PARTITION BY year
        ORDER BY AVG(pct_over_12m) DESC
    ) AS worst_wait_rank
FROM op_waiting
GROUP BY hospital, year
ORDER BY year DESC, avg_pct_over_12m DESC
LIMIT 30;


-- Q7: Hospital performance scorecard (latest full year)
-- Combines volume, long-wait % and year-on-year trend
WITH latest AS (
    SELECT hospital, SUM(total_waiting) AS total, AVG(pct_over_12m) AS avg_long
    FROM op_waiting
    WHERE year = (SELECT MAX(year) FROM op_waiting)
    GROUP BY hospital
),
prev AS (
    SELECT hospital, SUM(total_waiting) AS total
    FROM op_waiting
    WHERE year = (SELECT MAX(year) FROM op_waiting) - 1
    GROUP BY hospital
)
SELECT
    l.hospital,
    l.total                                                 AS current_total,
    ROUND(l.avg_long, 1)                                    AS pct_over_12m,
    p.total                                                 AS prev_total,
    ROUND((l.total - p.total) * 100.0 / NULLIF(p.total, 0), 1) AS yoy_change_pct,
    CASE
        WHEN l.avg_long < 10 AND (l.total - p.total) < 0 THEN '🟢 Improving'
        WHEN l.avg_long > 30 OR  (l.total - p.total) > 10 THEN '🔴 Critical'
        ELSE '🟡 Monitoring'
    END AS status
FROM latest l
LEFT JOIN prev p ON l.hospital = p.hospital
ORDER BY pct_over_12m DESC;


-- ============================================================
-- SECTION 3 — SPECIALTY ANALYSIS
-- ============================================================

-- Q8: Top 15 specialties with longest total waits (latest year)
SELECT
    specialty,
    SUM(total_waiting) AS total_waiting,
    RANK() OVER (ORDER BY SUM(total_waiting) DESC) AS national_rank
FROM specialty_waiting
WHERE year = (SELECT MAX(year) FROM specialty_waiting)
GROUP BY specialty
ORDER BY total_waiting DESC
LIMIT 15;


-- Q9: Which specialties have grown fastest since 2019?
WITH by_year AS (
    SELECT specialty, year, SUM(total_waiting) AS total
    FROM specialty_waiting
    GROUP BY specialty, year
),
base AS (SELECT specialty, total AS total_2019 FROM by_year WHERE year = 2019),
latest AS (SELECT specialty, total AS total_latest FROM by_year WHERE year = (SELECT MAX(year) FROM specialty_waiting))
SELECT
    b.specialty,
    b.total_2019,
    l.total_latest,
    ROUND((l.total_latest - b.total_2019) * 100.0 / NULLIF(b.total_2019, 0), 1) AS growth_since_2019_pct
FROM base b
JOIN latest l ON b.specialty = l.specialty
ORDER BY growth_since_2019_pct DESC
LIMIT 20;


-- Q10: Monthly trend for top 5 most-waited specialties
SELECT
    specialty,
    date,
    year,
    total_waiting
FROM specialty_waiting
WHERE specialty IN (
    SELECT specialty FROM specialty_waiting
    GROUP BY specialty
    ORDER BY SUM(total_waiting) DESC
    LIMIT 5
)
ORDER BY specialty, date;


-- ============================================================
-- SECTION 4 — INPATIENT/DAY CASE (IPDC)
-- ============================================================

-- Q11: IPDC waiting totals by year — trend analysis
SELECT
    year,
    SUM(total_waiting) AS total_ipdc_waiting,
    ROUND(AVG(pct_over_12m), 1) AS avg_long_wait_pct
FROM ipdc_waiting
GROUP BY year
ORDER BY year;


-- Q12: Top hospitals for IPDC waits
SELECT
    hospital,
    SUM(total_waiting) AS total_ipdc,
    ROUND(AVG(pct_over_12m), 1) AS pct_over_12m,
    RANK() OVER (ORDER BY SUM(total_waiting) DESC) AS rank
FROM ipdc_waiting
WHERE year = (SELECT MAX(year) FROM ipdc_waiting)
GROUP BY hospital
ORDER BY total_ipdc DESC
LIMIT 20;


-- ============================================================
-- SECTION 5 — WAIT TIME BAND ANALYSIS
-- ============================================================

-- Q13: National breakdown of waiting by time band (latest year)
SELECT
    year,
    ROUND(SUM("0-6 Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1)  AS pct_0_6m,
    ROUND(SUM("6-12 Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1) AS pct_6_12m,
    ROUND(SUM("12-18 Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1) AS pct_12_18m,
    ROUND(SUM("18+ Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1)  AS pct_18m_plus,
    SUM(total_waiting) AS grand_total
FROM op_waiting
GROUP BY year
ORDER BY year;


-- Q14: Has the wait band distribution improved since COVID?
SELECT
    CASE WHEN year <= 2019 THEN 'Pre-COVID (≤2019)'
         WHEN year IN (2020,2021) THEN 'During COVID (2020-21)'
         ELSE 'Post-COVID (2022+)'
    END AS period,
    ROUND(AVG(pct_over_12m), 1) AS avg_pct_over_12m,
    COUNT(DISTINCT hospital) AS hospitals_measured
FROM op_waiting
GROUP BY period
ORDER BY MIN(year);


-- ============================================================
-- SECTION 6 — SLAINTECARE TARGETS
-- ============================================================
-- Sláintecare target: no patient waits more than 10 weeks for
-- outpatient or 12 weeks for inpatient.
-- We use 0-6 months as proxy for within-target.

-- Q15: What % of patients are within Sláintecare targets each year?
SELECT
    year,
    ROUND(SUM("0-6 Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1) AS pct_within_target,
    ROUND(SUM("18+ Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1) AS pct_far_over_target,
    SUM(total_waiting) AS total_patients
FROM op_waiting
GROUP BY year
ORDER BY year;


-- Q16: Which hospitals are closest to meeting Sláintecare targets?
SELECT
    hospital,
    ROUND(SUM("0-6 Months") * 100.0 / NULLIF(SUM(total_waiting), 0), 1) AS pct_within_target,
    SUM(total_waiting) AS total_waiting,
    RANK() OVER (ORDER BY SUM("0-6 Months") * 100.0 / NULLIF(SUM(total_waiting), 0) DESC) AS target_rank
FROM op_waiting
WHERE year = (SELECT MAX(year) FROM op_waiting)
GROUP BY hospital
ORDER BY pct_within_target DESC
LIMIT 20;


-- ============================================================
-- SECTION 7 — SUMMARY STATISTICS
-- ============================================================

-- Q17: Executive summary — one row of key national stats
SELECT
    (SELECT SUM(total_waiting) FROM op_waiting WHERE year = (SELECT MAX(year) FROM op_waiting))
        AS current_op_waiting,
    (SELECT SUM(total_waiting) FROM ipdc_waiting WHERE year = (SELECT MAX(year) FROM ipdc_waiting))
        AS current_ipdc_waiting,
    (SELECT ROUND(AVG(pct_over_12m),1) FROM op_waiting WHERE year = (SELECT MAX(year) FROM op_waiting))
        AS avg_pct_over_12m,
    (SELECT COUNT(DISTINCT hospital) FROM op_waiting WHERE year = (SELECT MAX(year) FROM op_waiting))
        AS hospitals_reporting,
    (SELECT MAX(year) FROM op_waiting) AS latest_data_year;
