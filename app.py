
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Superstore | Sales & Profitability",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .hero {
        padding: 24px 28px;
        border-radius: 16px;
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: white;
        margin-bottom: 20px;
    }

    .hero h1 {
        margin: 0;
        font-size: 32px;
        letter-spacing: -0.5px;
    }

    .hero p {
        margin: 7px 0 0 0;
        color: #d1d5db;
        font-size: 15px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin: 10px 0 12px 0;
    }

    .section-subtitle {
        color: #6b7280;
        margin-top: -5px;
        margin-bottom: 18px;
    }

    .kpi-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px 20px;
        min-height: 112px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .kpi-label {
        color: #6b7280;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .kpi-value {
        color: #111827;
        font-size: 27px;
        font-weight: 750;
        margin-top: 8px;
    }

    .insight-box {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #334155;
        border-radius: 10px;
        padding: 16px 19px;
        margin: 4px 0 18px 0;
        line-height: 1.55;
        color: #1f2937 !important;
    }

    .insight-heading {
        font-size: 16px;
        font-weight: 750;
        color: #111827 !important;
        margin-bottom: 7px;
    }

    .insight-text {
        font-size: 14px;
        color: #374151 !important;
    }

    .decision-box {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 17px 20px;
        margin-top: 12px;
        color: #1f2937 !important;
    }

    .decision-title {
        font-weight: 750;
        color: #111827 !important;
        margin-bottom: 5px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    .small-note {
        color: #6b7280;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_data():
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "samplesuperstore_cleaned.csv"
    )

    if not os.path.exists(file_path):
        st.error(
            "Dataset not found. Put 'samplesuperstore_cleaned.csv' "
            "in the same folder as app.py."
        )
        st.stop()

    data = pd.read_csv(file_path)

    data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    data["Ship Date"] = pd.to_datetime(data["Ship Date"], errors="coerce")

    data["Year"] = data["Order Date"].dt.year
    data["Month"] = data["Order Date"].dt.to_period("M").astype(str)

    return data


df = load_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("Dashboard Controls")
st.sidebar.caption("Use the filters to explore performance interactively.")

years = sorted(df["Year"].dropna().unique().tolist())
regions = sorted(df["Region"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())
segments = sorted(df["Segment"].dropna().unique().tolist())

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)

if not selected_years:
    selected_years = years
if not selected_regions:
    selected_regions = regions
if not selected_categories:
    selected_categories = categories
if not selected_segments:
    selected_segments = segments

filtered = df[
    df["Year"].isin(selected_years)
    & df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
    & df["Segment"].isin(selected_segments)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters. Please broaden your selection.")
    st.stop()

# ============================================================
# HELPERS
# ============================================================

def money(x):
    return f"${x:,.0f}"

def pct(x):
    return f"{x:.1f}%"

def render_justification(question, why, finding, interpretation, implication, recommendation):
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-heading">What This Indicates</div>
            <div class="insight-text"><b>Finding:</b> {finding}</div>
            <div class="insight-text"><b>What it indicates:</b> {interpretation}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("View Visualization Justification", expanded=False):
        st.markdown(f"**1. Business Question**  \n{question}")
        st.markdown(f"**2. Why this visualization?**  \n{why}")
        st.markdown(f"**3. Finding**  \n{finding}")
        st.markdown(f"**4. Interpretation**  \n{interpretation}")
        st.markdown(f"**5. Managerial Implication**  \n{implication}")
        st.markdown(f"**6. Recommended Action**  \n{recommendation}")

def chart_layout(fig, height=460, key=None):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=65, b=30),
        hovermode="closest",
        legend_title_text=""
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True},
        key=key
    )

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>Superstore Sales & Profitability</h1>
        <p>Executive decision dashboard | From sales data to managerial action</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TABS
# ============================================================

tabs = st.tabs([
    "Executive Overview",
    "1 · Product Performance",
    "2 · Sales Trend",
    "3 · Sales Distribution",
    "4 · Discount & Profit",
    "5 · Customer Segments",
    "6 · Geographic Performance",
    "7 · Profit Outliers",
    "8 · Region × Category"
])

# ============================================================
# TAB 0 — EXECUTIVE OVERVIEW / KPI SECTION
# ============================================================

with tabs[0]:

    st.markdown('<div class="section-title">Executive Performance Snapshot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">A manager should be able to understand the current business situation in seconds.</div>',
        unsafe_allow_html=True
    )

    total_sales = filtered["Sales"].sum()
    total_profit = filtered["Profit"].sum()
    margin = (total_profit / total_sales * 100) if total_sales else 0
    orders = filtered["Order ID"].nunique()
    quantity = filtered["Quantity"].sum()

    kpis = [
        ("Total Sales", money(total_sales)),
        ("Total Profit", money(total_profit)),
        ("Profit Margin", pct(margin)),
        ("Orders", f"{orders:,}"),
        ("Units Sold", f"{quantity:,}")
    ]

    cols = st.columns(5)
    for col, (label, value) in zip(cols, kpis):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("")
    st.markdown('<div class="section-title">Executive Takeaway</div>', unsafe_allow_html=True)

    sub_profit = filtered.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False)
    region_profit = filtered.groupby("Region")["Profit"].sum().sort_values(ascending=False)
    segment_sales = filtered.groupby("Segment")["Sales"].sum().sort_values(ascending=False)

    top_sub = sub_profit.index[0]
    low_sub = sub_profit.index[-1]
    top_region = region_profit.index[0]
    top_segment = segment_sales.index[0]

    st.markdown(
        f"""
        <div class="decision-box">
            <div class="decision-title">What This Indicates</div>
            Profitability is not evenly distributed across the business. 
            <b>{top_sub}</b> is the strongest profit-generating sub-category in the current selection,
            while <b>{low_sub}</b> is the weakest. <b>{top_region}</b> leads regional profitability,
            and <b>{top_segment}</b> contributes the highest sales among customer segments.
            These patterns should guide deeper product, regional and customer-level decisions.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown('<div class="section-title">Dashboard Guide</div>', unsafe_allow_html=True)

    guide = pd.DataFrame({
        "Tab": [
            "1 · Product Performance",
            "2 · Sales Trend",
            "3 · Sales Distribution",
            "4 · Discount & Profit",
            "5 · Customer Segments",
            "6 · Geographic Performance",
            "7 · Profit Outliers",
            "8 · Region × Category"
        ],
        "Purpose": [
            "Comparison",
            "Trend",
            "Distribution",
            "Relationship",
            "Composition",
            "Geographical analysis",
            "Outlier analysis",
            "Pattern / relationship"
        ]
    })

    st.dataframe(guide, use_container_width=True, hide_index=True)

# ============================================================
# TAB 1 — PRODUCT PERFORMANCE
# ============================================================

with tabs[1]:

    st.markdown('<div class="section-title">1. Product Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Compare product areas to identify where revenue translates into profit — and where it does not.</div>',
        unsafe_allow_html=True
    )

    metric = st.selectbox(
        "Choose performance measure",
        ["Profit", "Sales"],
        key="product_metric"
    )

    product_data = (
        filtered.groupby("Sub-Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
        .sort_values(metric, ascending=True)
    )

    fig = px.bar(
        product_data,
        x=metric,
        y="Sub-Category",
        orientation="h",
        title=f"{metric} by Product Sub-Category",
        text=metric
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    chart_layout(fig, 540, key="product_chart")

    top = product_data.iloc[-1]
    bottom = product_data.iloc[0]

    render_justification(
        "Which product sub-categories are the strongest and weakest contributors to business performance?",
        "A sorted horizontal bar chart makes ranking and comparison across many sub-categories easy and precise.",
        f"{top['Sub-Category']} has the highest {metric.lower()} at {money(top[metric])}, while {bottom['Sub-Category']} has the lowest at {money(bottom[metric])}.",
        "Performance is concentrated unevenly across product sub-categories. The strongest areas contribute more to the selected business measure, while weaker areas require closer investigation.",
        "Management should avoid treating every product area equally when allocating sales effort, pricing attention and resources.",
        "Prioritize strong product areas while reviewing pricing, discounting, costs and demand for consistently weak sub-categories."
    )

# ============================================================
# TAB 2 — TREND
# ============================================================

with tabs[2]:

    st.markdown('<div class="section-title">2. Sales & Profit Trend</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Track how business performance changes over time.</div>',
        unsafe_allow_html=True
    )

    trend_metric = st.selectbox(
        "Choose trend measure",
        ["Sales", "Profit"],
        key="trend_metric"
    )

    monthly = (
        filtered.groupby("Month")[trend_metric]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly,
        x="Month",
        y=trend_metric,
        markers=True,
        title=f"Monthly {trend_metric} Trend"
    )
    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(tickformat=",.0f")
    chart_layout(fig, 470, key="trend_chart")

    best_month = monthly.loc[monthly[trend_metric].idxmax()]
    worst_month = monthly.loc[monthly[trend_metric].idxmin()]

    render_justification(
        "How has the company's sales or profitability changed over time?",
        "A line chart is designed for ordered time-series data and makes increases, declines and changing patterns easy to identify.",
        f"The strongest month for {trend_metric.lower()} is {best_month['Month']} at {money(best_month[trend_metric])}, while the lowest is {worst_month['Month']} at {money(worst_month[trend_metric])}.",
        "Business performance varies over time rather than remaining constant. The pattern may indicate seasonality, changing demand or changes in the product mix.",
        "Management can use the trend to identify periods that require further investigation and to plan sales and inventory activities.",
        "Investigate unusually weak or strong periods and compare them with product mix, discounting and regional performance before making operational decisions."
    )

# ============================================================
# TAB 3 — DISTRIBUTION
# ============================================================

with tabs[3]:

    st.markdown('<div class="section-title">3. Sales Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Understand what a typical transaction looks like and whether a small number of orders dominate sales.</div>',
        unsafe_allow_html=True
    )

    bins = st.slider(
        "Histogram bins",
        min_value=10,
        max_value=60,
        value=30,
        step=5,
        key="hist_bins"
    )

    fig = px.histogram(
        filtered,
        x="Sales",
        nbins=bins,
        title="Distribution of Order-Level Sales",
        marginal="box"
    )
    fig.update_xaxes(title="Order Sales")
    fig.update_yaxes(title="Number of Orders")
    chart_layout(fig, 500, key="distribution_chart")

    median_sales = filtered["Sales"].median()
    mean_sales = filtered["Sales"].mean()
    high_sales = (filtered["Sales"] > filtered["Sales"].quantile(0.90)).sum()

    render_justification(
        "How are individual order sales distributed, and are most transactions concentrated in a particular range?",
        "A histogram shows how frequently different sales values occur and is appropriate for understanding distribution and concentration.",
        f"The median order value is {money(median_sales)}, compared with an average of {money(mean_sales)}. {high_sales:,} orders fall above the 90th percentile.",
        "If the mean is noticeably above the median, a smaller number of large transactions may be pulling the average upward. This helps distinguish typical transactions from unusually large ones.",
        "Management should understand whether overall sales depend heavily on a relatively small number of large orders.",
        "Use the distribution to segment customers and transactions and investigate what characteristics are associated with high-value orders."
    )

# ============================================================
# TAB 4 — DISCOUNT VS PROFIT
# ============================================================

with tabs[4]:

    st.markdown('<div class="section-title">4. Discount & Profit Relationship</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Examine whether higher discount levels are associated with weaker profitability.</div>',
        unsafe_allow_html=True
    )

    color_by = st.selectbox(
        "Color points by",
        ["Category", "Region", "Segment"],
        key="scatter_color"
    )

    fig = px.scatter(
        filtered,
        x="Discount",
        y="Profit",
        color=color_by,
        size="Sales",
        hover_data=["Product Name", "Sales", "Quantity", "Region"],
        opacity=0.65,
        title="Discount vs Profit"
    )
    fig.update_xaxes(tickformat=".0%")
    chart_layout(fig, 540, key="discount_chart")

    corr = filtered["Discount"].corr(filtered["Profit"])

    if pd.isna(corr):
        relationship = "could not be calculated for the current selection"
    elif abs(corr) < 0.20:
        relationship = "weak"
    elif abs(corr) < 0.50:
        relationship = "moderate"
    else:
        relationship = "strong"

    direction = "positive" if corr >= 0 else "negative"

    render_justification(
        "What is the relationship between discount levels and profit?",
        "A scatter plot is appropriate for examining the relationship between two numerical variables at the transaction level.",
        f"The correlation between discount and profit is {corr:.2f}, indicating a {relationship} {direction} association in the current selection.",
        "The pattern helps identify whether higher discount levels tend to occur with lower or higher profits. This is an association, not proof that discounting causes the change.",
        "If high discounts are concentrated around weak-profit transactions, management should review whether discount policies are eroding margins.",
        "Investigate high-discount, low-profit transactions and evaluate whether discount thresholds should differ by product, region or customer segment."
    )

# ============================================================
# TAB 5 — CUSTOMER SEGMENTS
# ============================================================

with tabs[5]:

    st.markdown('<div class="section-title">5. Customer Segment Composition</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Compare how customer segments contribute across product categories.</div>',
        unsafe_allow_html=True
    )

    composition_metric = st.selectbox(
        "Choose measure",
        ["Sales", "Profit"],
        key="composition_metric"
    )

    seg_cat = (
        filtered.groupby(["Segment", "Category"])[composition_metric]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        seg_cat,
        x="Segment",
        y=composition_metric,
        color="Category",
        barmode="stack",
        title=f"{composition_metric} Composition by Customer Segment"
    )
    chart_layout(fig, 470, key="segment_chart")

    segment_totals = filtered.groupby("Segment")[composition_metric].sum().sort_values(ascending=False)
    top_seg = segment_totals.index[0]
    top_value = segment_totals.iloc[0]

    render_justification(
        "How do customer segments contribute to sales or profit across product categories?",
        "A stacked bar chart shows both total segment contribution and the composition of that contribution by product category.",
        f"{top_seg} contributes the highest overall {composition_metric.lower()} at {money(top_value)} within the current selection.",
        "Customer segments do not necessarily have the same product mix. A segment may be valuable because of both its size and the categories it purchases.",
        "Understanding segment composition helps management target customers with more relevant products and sales strategies.",
        "Prioritize segments with strong value and identify category-specific opportunities for cross-selling, retention and targeted campaigns."
    )

# ============================================================
# TAB 6 — GEOGRAPHIC
# ============================================================

with tabs[6]:

    st.markdown('<div class="section-title">6. Geographic Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Identify geographic areas where profitability is strong or needs attention.</div>',
        unsafe_allow_html=True
    )

    geo_metric = st.selectbox(
        "Map measure",
        ["Profit", "Sales"],
        key="geo_metric"
    )

    # State abbreviation mapping for Plotly's USA-states map.
    state_map = {
        "Alabama":"AL","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO",
        "Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL",
        "Georgia":"GA","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA",
        "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
        "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
        "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH",
        "New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC",
        "North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA",
        "Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN",
        "Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
        "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
    }

    geo = (
        filtered.groupby("State/Province")[geo_metric]
        .sum()
        .reset_index()
    )
    geo["StateCode"] = geo["State/Province"].map(state_map)

    geo = geo.dropna(subset=["StateCode"])

    fig = px.choropleth(
        geo,
        locations="StateCode",
        locationmode="USA-states",
        color=geo_metric,
        scope="usa",
        hover_name="State/Province",
        hover_data={geo_metric: ":,.0f"},
        title=f"{geo_metric} by State"
    )
    fig.update_layout(height=540, margin=dict(l=0, r=0, t=65, b=0))
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True},
        key="geographic_chart"
    )

    top_state = geo.loc[geo[geo_metric].idxmax()]
    low_state = geo.loc[geo[geo_metric].idxmin()]

    render_justification(
        "Which states show the strongest and weakest sales or profitability?",
        "A choropleth map is useful for geographic analysis because it makes spatial differences easy to identify.",
        f"{top_state['State/Province']} has the highest {geo_metric.lower()} at {money(top_state[geo_metric])}, while {low_state['State/Province']} has the lowest at {money(low_state[geo_metric])}.",
        "Performance differs geographically, suggesting that the same product or sales strategy may not perform equally across all locations.",
        "Regional differences can affect sales planning, resource allocation, pricing and targeted sales activity.",
        "Investigate weak states using product mix, discount and customer-segment data before applying targeted regional interventions."
    )

# ============================================================
# TAB 7 — OUTLIERS
# ============================================================

with tabs[7]:

    st.markdown('<div class="section-title">7. Profitability Outliers</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Identify unusually high or low profit transactions without removing genuine business observations.</div>',
        unsafe_allow_html=True
    )

    box_group = st.selectbox(
        "Group profit by",
        ["Category", "Region", "Segment"],
        key="box_group"
    )

    fig = px.box(
        filtered,
        x=box_group,
        y="Profit",
        points="outliers",
        color=box_group,
        title=f"Profit Distribution and Outliers by {box_group}"
    )
    chart_layout(fig, 500, key="outlier_chart")

    q1 = filtered["Profit"].quantile(0.25)
    q3 = filtered["Profit"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier_count = int(((filtered["Profit"] < lower) | (filtered["Profit"] > upper)).sum())

    render_justification(
        "Which business groups contain unusually high or low profit observations?",
        "A box plot shows median, spread and potential outliers, making it suitable for comparing distributions across groups.",
        f"Using the 1.5×IQR rule, {outlier_count:,} transactions are flagged as potential profit outliers in the current selection.",
        "These observations may represent unusually profitable orders or significant losses. They should be investigated rather than automatically deleted because they can represent genuine business activity.",
        "Extreme losses can materially affect overall profitability and may reveal issues with pricing, discounting, product choice or transaction characteristics.",
        "Investigate large-loss transactions and compare their products, discounts, regions and customer segments to identify recurring risk patterns."
    )

# ============================================================
# TAB 8 — HEATMAP
# ============================================================

with tabs[8]:

    st.markdown('<div class="section-title">8. Region × Category Profitability</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Find specific region-category combinations that create opportunities or profitability concerns.</div>',
        unsafe_allow_html=True
    )

    heat_metric = st.selectbox(
        "Heatmap measure",
        ["Profit", "Sales"],
        key="heat_metric"
    )

    heat = filtered.pivot_table(
        index="Region",
        columns="Category",
        values=heat_metric,
        aggfunc="sum",
        fill_value=0
    )

    fig = px.imshow(
        heat,
        text_auto=".0f",
        aspect="auto",
        title=f"{heat_metric} by Region and Product Category",
        labels={"x": "Product Category", "y": "Region", "color": heat_metric}
    )
    chart_layout(fig, 450, key="heatmap_chart")

    stacked = heat.stack()

    strongest = stacked.idxmax()
    weakest = stacked.idxmin()

    render_justification(
        "Which region and product-category combinations are strongest and weakest?",
        "A heatmap compares two categorical dimensions simultaneously and makes high- and low-performing combinations easy to spot.",
        f"The strongest {heat_metric.lower()} combination is {strongest[0]} × {strongest[1]} at {money(stacked.max())}, while the weakest is {weakest[0]} × {weakest[1]} at {money(stacked.min())}.",
        "Overall regional or category averages can hide important differences. The heatmap exposes these specific intersections.",
        "Management can use this information to avoid one-size-fits-all strategies and focus resources on specific problem or opportunity areas.",
        "Investigate weak region-category combinations and develop targeted product, pricing, inventory or sales strategies."
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    '<div class="small-note">Superstore Sales & Profitability Analysis • Interactive Streamlit Executive Dashboard</div>',
    unsafe_allow_html=True
)
