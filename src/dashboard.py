# ============================================================
# HSE Hospital Wait Times — Streamlit Dashboard
# ============================================================
# Author:      Ishan Kasare
# GitHub:      https://github.com/Ishankasare/HSE-Hospital-Wait-Times-Analysis
# LinkedIn:    https://www.linkedin.com/in/ishan-kasare/
#
# Run:  streamlit run src/dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sqlite3

st.set_page_config(
    page_title="HSE Hospital Wait Times",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.kpi-card {
    background: linear-gradient(135deg, #0d1b2a, #1b2838);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 22px 18px;
    text-align: center;
    margin-bottom: 8px;
}
.kpi-value { font-size: 2rem; font-weight: 700; color: #4fc3f7; }
.kpi-label { font-size: 0.82rem; color: #90a4ae; margin-top: 4px; }
.kpi-delta { font-size: 0.78rem; margin-top: 6px; }
.section-title {
    font-size: 1.35rem; font-weight: 700; color: #e0f2fe;
    border-left: 4px solid #0288d1;
    padding-left: 12px; margin: 28px 0 14px 0;
}
.insight {
    background: #0d1b2a; border-left: 3px solid #0288d1;
    border-radius: 8px; padding: 14px 18px;
    color: #b0bec5; font-size: 0.93rem; line-height: 1.65;
    margin: 10px 0 20px 0;
}
.warning-box {
    background: #1a0a00; border-left: 3px solid #f57c00;
    border-radius: 8px; padding: 14px 18px;
    color: #ffcc80; font-size: 0.93rem; margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Data Loading ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    db = "data/hse_waits.db"
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        op = pd.read_sql("SELECT * FROM op_waiting", conn)
        try:
            ipdc = pd.read_sql("SELECT * FROM ipdc_waiting", conn)
        except:
            ipdc = pd.DataFrame()
        try:
            spec = pd.read_sql("SELECT * FROM specialty_waiting", conn)
        except:
            spec = pd.DataFrame()
        conn.close()
        return op, ipdc, spec

    # Fall back to CSVs
    op = pd.read_csv("data/processed/op_waiting.csv") if os.path.exists("data/processed/op_waiting.csv") else pd.DataFrame()
    ipdc = pd.read_csv("data/processed/ipdc_waiting.csv") if os.path.exists("data/processed/ipdc_waiting.csv") else pd.DataFrame()
    spec = pd.read_csv("data/processed/specialty_waiting.csv") if os.path.exists("data/processed/specialty_waiting.csv") else pd.DataFrame()
    return op, ipdc, spec


op_df, ipdc_df, spec_df = load_data()

if op_df.empty:
    st.error("No data found. Run `python src/download_data.py` then `python src/clean_data.py` first.")
    st.stop()

# Convert date
if "date" in op_df.columns:
    op_df["date"] = pd.to_datetime(op_df["date"], errors="coerce")


# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.markdown("## 🏥 HSE Wait Times")
st.sidebar.markdown("**Ireland · NTPF Open Data**")
st.sidebar.markdown("---")

years = sorted(op_df["year"].dropna().unique().tolist(), reverse=True)
selected_years = st.sidebar.multiselect("Years", years, default=years[:3])

hospitals = ["All"] + sorted(op_df["hospital"].dropna().unique().tolist())
selected_hospital = st.sidebar.selectbox("Hospital", hospitals)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data source:** [NTPF Open Data](https://www.ntpf.ie/waiting-list-data/open-data/)")
st.sidebar.markdown(f"**Updated:** Monthly")

# Apply filters
filtered = op_df[op_df["year"].isin(selected_years)]
if selected_hospital != "All":
    filtered = filtered[filtered["hospital"] == selected_hospital]

latest_year = max(selected_years) if selected_years else op_df["year"].max()
latest = op_df[op_df["year"] == latest_year]
prev = op_df[op_df["year"] == latest_year - 1]


# ── Header ────────────────────────────────────────────────────
st.markdown("""
<h1 style='color:#e0f2fe; font-size:2rem; font-weight:700; margin-bottom:2px;'>
    🏥 HSE Hospital Waiting List Analysis
</h1>
<p style='color:#78909c; font-size:0.97rem; margin-bottom:28px;'>
    Ireland · National Treatment Purchase Fund (NTPF) Open Data · 2019–2026
</p>
""", unsafe_allow_html=True)


# ── KPI Row ───────────────────────────────────────────────────
total_now = int(latest["total_waiting"].sum())
total_prev = int(prev["total_waiting"].sum()) if not prev.empty else 0
change = total_now - total_prev
change_pct = round(change / total_prev * 100, 1) if total_prev > 0 else 0
hospitals_n = latest["hospital"].nunique()
avg_long = round(latest["pct_over_12m"].mean(), 1)
over_18m = int(latest["18+ Months"].sum()) if "18+ Months" in latest.columns else 0

col1, col2, col3, col4, col5 = st.columns(5)

kpis = [
    (col1, f"{total_now:,}", "Total Outpatients Waiting", f"{'▲' if change > 0 else '▼'} {abs(change_pct)}% vs prev year", "red" if change > 0 else "green"),
    (col2, f"{hospitals_n}", "Hospitals Reporting", "", ""),
    (col3, f"{avg_long}%", "Avg % Waiting 12+ Months", "", ""),
    (col4, f"{over_18m:,}", "Waiting 18+ Months", "Most urgent cohort", ""),
    (col5, str(latest_year), "Latest Data Year", "NTPF monthly update", ""),
]

for col, val, label, delta, color in kpis:
    with col:
        delta_color = "color:#ef9a9a" if color == "red" else ("color:#a5d6a7" if color == "green" else "color:#78909c")
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{val}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-delta' style='{delta_color}'>{delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── National Trend ────────────────────────────────────────────
st.markdown("<div class='section-title'>National Waiting List Trend</div>", unsafe_allow_html=True)

trend = op_df.groupby("year")["total_waiting"].sum().reset_index()
trend.columns = ["Year", "Total Waiting"]

fig = px.line(
    trend, x="Year", y="Total Waiting",
    markers=True,
    title="Total Outpatients Waiting Nationally (2019–2026)",
    color_discrete_sequence=["#4fc3f7"]
)
fig.add_vrect(x0=2019.5, x1=2021.5, fillcolor="#f57c00", opacity=0.07,
              annotation_text="COVID-19 Period", annotation_position="top left")
fig.update_layout(
    plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
    font_color="#cfd8dc", height=380,
    xaxis=dict(dtick=1), yaxis_title="Patients Waiting"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class='insight'>
    💡 <strong>Insight:</strong> The COVID-19 period (2020–2021) caused a temporary reduction in recorded
    waiting lists — not because patients were treated faster, but because elective care was suspended and
    referrals dropped. The post-COVID rebound reveals the true scale of suppressed demand.
    By 2024, Ireland's waiting list reached a record 911,500 patients — the highest ever recorded.
</div>
""", unsafe_allow_html=True)


# ── Top Hospitals ─────────────────────────────────────────────
st.markdown("<div class='section-title'>Hospital Performance</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    top_hosp = latest.groupby("hospital")["total_waiting"].sum().nlargest(15).reset_index()
    top_hosp.columns = ["Hospital", "Waiting"]
    fig = px.bar(
        top_hosp, x="Waiting", y="Hospital", orientation="h",
        color="Waiting", color_continuous_scale="Blues",
        title=f"Top 15 Hospitals by Total Waiting ({latest_year})"
    )
    fig.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="#cfd8dc", coloraxis_showscale=False,
        height=480, yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    long_wait = latest.groupby("hospital")["pct_over_12m"].mean().nlargest(15).reset_index()
    long_wait.columns = ["Hospital", "% Over 12 Months"]
    fig = px.bar(
        long_wait, x="% Over 12 Months", y="Hospital", orientation="h",
        color="% Over 12 Months", color_continuous_scale="Reds",
        title=f"Hospitals with Highest % Waiting 12+ Months ({latest_year})"
    )
    fig.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="#cfd8dc", coloraxis_showscale=False,
        height=480, yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class='insight'>
    💡 <strong>Insight:</strong> Volume and long-wait % tell different stories. A hospital with high total volume
    is not necessarily performing badly — it may be a large national centre serving more patients.
    The more telling metric is % waiting over 12 months, which reveals structural access problems
    regardless of hospital size.
</div>
""", unsafe_allow_html=True)


# ── Wait Band Distribution ────────────────────────────────────
st.markdown("<div class='section-title'>Wait Time Band Analysis</div>", unsafe_allow_html=True)

band_cols = ["0-6 Months", "6-12 Months", "12-18 Months", "18+ Months"]
available_bands = [b for b in band_cols if b in op_df.columns]

if available_bands:
    band_trend = op_df.groupby("year")[available_bands + ["total_waiting"]].sum().reset_index()
    for band in available_bands:
        band_trend[f"pct_{band}"] = (band_trend[band] / band_trend["total_waiting"] * 100).round(1)

    fig = go.Figure()
    colors = ["#4fc3f7", "#29b6f6", "#f57c00", "#ef5350"]
    for band, color in zip(available_bands, colors):
        fig.add_trace(go.Bar(
            x=band_trend["year"],
            y=band_trend[f"pct_{band}"],
            name=band,
            marker_color=color
        ))
    fig.update_layout(
        barmode="stack",
        title="Wait Time Band Distribution by Year (%)",
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="#cfd8dc", height=400,
        legend=dict(orientation="h", y=-0.15),
        xaxis=dict(dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='insight'>
        💡 <strong>Insight:</strong> The Sláintecare reform programme set a target that no patient should wait
        more than 10 weeks for an outpatient appointment. Tracking the 0–6 month band over time shows
        how far Ireland is from meeting this target. The growth in the 18+ months cohort is the
        most clinically urgent signal in the dataset.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Wait band columns not available in this dataset view.")


# ── Specialty Analysis ────────────────────────────────────────
if not spec_df.empty:
    st.markdown("<div class='section-title'>Specialty Waiting List Analysis</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    spec_latest = spec_df[spec_df["year"] == spec_df["year"].max()]

    with col1:
        top_spec = spec_latest.groupby("specialty")["total_waiting"].sum().nlargest(15).reset_index()
        top_spec.columns = ["Specialty", "Waiting"]
        fig = px.bar(
            top_spec, x="Waiting", y="Specialty", orientation="h",
            color="Waiting", color_continuous_scale="Blues",
            title="Top 15 Specialties by Total Waiting"
        )
        fig.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
            font_color="#cfd8dc", coloraxis_showscale=False,
            height=480, yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        spec_trend = spec_df.groupby(["year", "specialty"])["total_waiting"].sum().reset_index()
        top5 = spec_latest.groupby("specialty")["total_waiting"].sum().nlargest(5).index.tolist()
        spec_top5 = spec_trend[spec_trend["specialty"].isin(top5)]

        fig = px.line(
            spec_top5, x="year", y="total_waiting", color="specialty",
            markers=True, title="Top 5 Specialties — Waiting List Trend"
        )
        fig.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
            font_color="#cfd8dc", height=480,
            xaxis=dict(dtick=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='insight'>
        💡 <strong>Insight:</strong> Ophthalmology, Orthopaedics and Ear Nose & Throat consistently appear
        in the top waited specialties. These are largely elective procedures — high volume, not
        life-threatening, but significantly impacting quality of life. The gap between clinical urgency
        and waiting list reality is most visible in these specialties.
    </div>
    """, unsafe_allow_html=True)


# ── IPDC Analysis ─────────────────────────────────────────────
if not ipdc_df.empty:
    st.markdown("<div class='section-title'>Inpatient / Day Case (IPDC) Analysis</div>", unsafe_allow_html=True)

    ipdc_trend = ipdc_df.groupby("year")["total_waiting"].sum().reset_index()
    ipdc_trend.columns = ["Year", "IPDC Waiting"]

    fig = px.bar(
        ipdc_trend, x="Year", y="IPDC Waiting",
        color="IPDC Waiting", color_continuous_scale="Blues",
        title="Total IPDC Patients Waiting by Year"
    )
    fig.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="#cfd8dc", coloraxis_showscale=False,
        height=360, xaxis=dict(dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Sláintecare Target Tracker ────────────────────────────────
st.markdown("<div class='section-title'>Sláintecare Target Tracker</div>", unsafe_allow_html=True)

if "0-6 Months" in op_df.columns:
    target_df = op_df.groupby("year")[["0-6 Months", "total_waiting"]].sum().reset_index()
    target_df["pct_within_target"] = (target_df["0-6 Months"] / target_df["total_waiting"] * 100).round(1)
    target_df["pct_outside_target"] = 100 - target_df["pct_within_target"]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=target_df["year"], y=target_df["pct_within_target"],
                         name="Within Target (0–6m)", marker_color="#4fc3f7"))
    fig.add_trace(go.Bar(x=target_df["year"], y=target_df["pct_outside_target"],
                         name="Exceeds Target (6m+)", marker_color="#ef5350"))
    fig.add_hline(y=100, line_dash="dot", line_color="#a5d6a7",
                  annotation_text="Sláintecare Goal: 100% within target")
    fig.update_layout(
        barmode="stack", title="% of Patients Within vs Outside Sláintecare Targets",
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="#cfd8dc", height=380,
        xaxis=dict(dtick=1), legend=dict(orientation="h", y=-0.15)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='warning-box'>
        ⚠️ <strong>Policy Context:</strong> The Sláintecare reform programme targets that no patient waits
        more than 10 weeks for outpatient care and 12 weeks for inpatient care. Despite €437 million
        allocated to waiting list reduction in 2024, the total waiting list reached a record 911,500 —
        the highest ever. This chart tracks how far Ireland is from meeting its own stated targets year by year.
    </div>
    """, unsafe_allow_html=True)


# ── Raw Data Table ────────────────────────────────────────────
st.markdown("<div class='section-title'>Browse Data</div>", unsafe_allow_html=True)

search = st.text_input("🔍 Search by hospital name or specialty", "")
table = filtered[["hospital", "specialty", "year", "total_waiting", "pct_over_12m", "18+ Months", "wait_type"]].copy() if all(
    c in filtered.columns for c in ["hospital", "specialty", "year", "total_waiting", "pct_over_12m", "18+ Months", "wait_type"]
) else filtered

if search:
    mask = table.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
    table = table[mask]

table.columns = [c.replace("_", " ").title() for c in table.columns]
st.dataframe(table, use_container_width=True, height=380)

csv = filtered.to_csv(index=False)
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv,
    file_name="hse_wait_times_filtered.csv",
    mime="text/csv"
)

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style='color:#546e7a; font-size:0.82rem; text-align:center;'>
    Data: National Treatment Purchase Fund (NTPF) · ntpf.ie · Updated monthly ·
    Built by <a href='https://www.linkedin.com/in/ishan-kasare/' style='color:#4fc3f7;'>Ishan Kasare</a>
</p>
""", unsafe_allow_html=True)
