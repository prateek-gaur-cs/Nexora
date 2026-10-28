from customer_segmentation import show_customer_segmentation
from network_analysis import show_network_analysis
from route_optimization import show_route_optimization
from priority_queue import PriorityQueue
import order_database
import order_database
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime


def suggest_order_priority(status):
    """Suggest a queue priority from the current order status."""
    status = str(status).strip().lower()

    if status in {"pending", "processing", "delayed", "on hold"}:
        return 1
    elif status in {"packed", "dispatched"}:
        return 2
    elif status in {"shipped", "in transit"}:
        return 3
    elif status in {"delivered", "completed"}:
        return 5
    elif status in {"cancelled", "canceled", "returned"}:
        return 5
    else:
        return 3




def apply_saved_order_statuses(df, order_col, status_col):
    """Overlay saved NEXORA statuses without changing the source dataset."""
    if not order_col or not status_col or df.empty:
        return df.copy()

    result = df.copy()
    updates = order_database.get_all_order_updates()

    if not updates:
        return result

    status_map = {
        str(item["order_id"]): item["status"]
        for item in updates
    }

    result[status_col] = result[order_col].astype(str).map(
        status_map
    ).fillna(result[status_col])

    return result


st.set_page_config(
    page_title="NEXORA | Commerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ===== Main Dashboard ===== */
.stApp {
    background-color: #F5F4EF;
    color: #252923;
}

[data-testid="stAppViewContainer"] {
    background-color: #F5F4EF;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background-color: #252923;
}

[data-testid="stSidebar"] * {
    color: #F5F4EF !important;
}

/* ===== Main Content Text ===== */
[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4 {
    color: #252923;
}

/* ===== Input Fields ===== */
[data-testid="stAppViewContainer"] .main input,
[data-testid="stAppViewContainer"] .main textarea {
    color: #252923 !important;
    background-color: #FFFFFF !important;
}

[data-testid="stAppViewContainer"] .main [data-baseweb="select"] * {
    color: #252923 !important;
}

/* ===== Premium Hero Banner ===== */
.hero {
    background: linear-gradient(120deg, #252923, #41483B);
    padding: 30px 32px;
    border-radius: 18px;
    margin-bottom: 26px;
    box-shadow: 0 8px 24px rgba(37, 41, 35, 0.12);
}

.hero h1 {
    color: #E5BD72 !important;
    margin: 0;
    font-size: 36px;
    font-weight: 750;
    letter-spacing: 1px;
}

.hero p {
    color: #E4E5DC !important;
    margin: 8px 0 0 0;
    font-size: 15px;
}

/* ===== Premium Metric Cards ===== */
.metric-card {
    background: linear-gradient(145deg, #FFFFFF, #F9F8F4);
    color: #252923;
    border: 1px solid #E4E2D9;
    border-radius: 16px;
    padding: 24px;
    min-height: 135px;
    box-shadow: 0 4px 14px rgba(37, 41, 35, 0.05);
    transition: transform 0.25s ease,
                box-shadow 0.25s ease,
                border-color 0.25s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 26px rgba(37, 41, 35, 0.10);
    border-color: #B7BCA9;
}

.metric-label {
    color: #77796F !important;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.metric-value {
    color: #252923 !important;
    font-size: 30px;
    font-weight: 750;
    line-height: 1.25;
    letter-spacing: -0.8px;
    margin-top: 8px;
}

/* ===== Section Headings ===== */
.section-title {
    color: #252923;
    font-size: 21px;
    font-weight: 650;
    margin: 20px 0 14px;
}

/* ===== Buttons ===== */
.stButton > button,
.stDownloadButton > button {
    background-color: #41483B;
    color: #FFFFFF !important;
    border: 1px solid #41483B;
    border-radius: 9px;
    padding: 8px 18px;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #59634F;
    color: #FFFFFF !important;
    border-color: #59634F;
}

/* ===== Tables ===== */
[data-testid="stDataFrame"] {
    border: 1px solid #E4E2D9;
    border-radius: 10px;
    overflow: hidden;
}

/* ===== Layout ===== */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* ===== Alerts ===== */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* ===== GLOBAL TEXT VISIBILITY FIX ===== */

/* Main page text */
.stApp,
[data-testid="stAppViewContainer"] .main {
    color: #252923 !important;
}

/* Input boxes and text areas */
.stApp input,
.stApp textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    color: #252923 !important;
    background-color: #FFFFFF !important;
    -webkit-text-fill-color: #252923 !important;
    caret-color: #252923 !important;
}

/* Dropdowns and selected values */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
}

[data-baseweb="select"] *,
[data-baseweb="select"] input {
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
}

/* Dropdown menus and options */
[role="listbox"],
[role="option"],
[data-baseweb="menu"],
[data-baseweb="popover"] {
    background-color: #FFFFFF !important;
    color: #252923 !important;
}

[role="option"] *,
[data-baseweb="menu"] *,
[data-baseweb="popover"] * {
    color: #252923 !important;
}

/* Number inputs, date fields and other controls */
.stNumberInput input,
.stDateInput input,
.stTimeInput input {
    color: #252923 !important;
    background-color: #FFFFFF !important;
    -webkit-text-fill-color: #252923 !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    color: #252923 !important;
}

/* Keep sidebar readable */
[data-testid="stSidebar"] {
    background-color: #252923 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #F5F4EF !important;
}

/* Placeholder text */
.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #77796F !important;
    -webkit-text-fill-color: #77796F !important;
    opacity: 1;
}


/* ===== NEXORA READABILITY FIX ===== */

/* Main dashboard */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #F5F4EF !important;
    color: #252923 !important;
}

/* Main page text */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main .stMarkdown {
    color: #252923 !important;
}

/* Text inputs, number inputs and text areas */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
    caret-color: #252923 !important;
}

/* Dropdown closed state */
.stApp [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #252923 !important;
}

.stApp [data-baseweb="select"] *,
.stApp [data-baseweb="select"] input {
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
}

/* Dropdown menu and choices */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
    background-color: #FFFFFF !important;
    color: #252923 !important;
}

[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[role="listbox"] *,
[role="option"] * {
    color: #252923 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #252923 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F5F4EF !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background-color: #41483B !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Placeholder text */
.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #77796F !important;
    -webkit-text-fill-color: #77796F !important;
    opacity: 1 !important;
}




/* ===== NEXORA READABILITY FIX ===== */

/* Main dashboard */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #F5F4EF !important;
    color: #252923 !important;
}

/* Main page text */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main .stMarkdown {
    color: #252923 !important;
}

/* Text inputs, number inputs and text areas */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
    caret-color: #252923 !important;
}

/* Dropdown closed state */
.stApp [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #252923 !important;
}

.stApp [data-baseweb="select"] *,
.stApp [data-baseweb="select"] input {
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
}

/* Dropdown menu and choices */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
    background-color: #FFFFFF !important;
    color: #252923 !important;
}

[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[role="listbox"] *,
[role="option"] * {
    color: #252923 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #252923 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F5F4EF !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background-color: #41483B !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Placeholder text */
.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #77796F !important;
    -webkit-text-fill-color: #77796F !important;
    opacity: 1 !important;
}


/* ===== FINAL NEXORA TEXT CONTRAST OVERRIDE ===== */

/* Main page: dark text on ivory background */
[data-testid="stAppViewContainer"] .main {
    background-color: #F5F4EF !important;
    color: #252923 !important;
}

/* Headings, paragraphs, captions and ordinary content */
[data-testid="stAppViewContainer"] .main h1,
[data-testid="stAppViewContainer"] .main h2,
[data-testid="stAppViewContainer"] .main h3,
[data-testid="stAppViewContainer"] .main h4,
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main [data-testid="stCaptionContainer"] {
    color: #252923 !important;
}

/* Markdown content */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em {
    color: #252923 !important;
}

/* Input boxes: white background, dark entered text */
[data-testid="stAppViewContainer"] .main input,
[data-testid="stAppViewContainer"] .main textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
    caret-color: #252923 !important;
}

/* Select boxes and multiselects */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] input,
[data-baseweb="select"] div {
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
}

/* Open dropdown menus */
[data-baseweb="popover"],
[data-baseweb="popover"] *,
[role="listbox"],
[role="listbox"] *,
[role="option"],
[role="option"] * {
    background-color: #FFFFFF;
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
}

/* Checkboxes and radio labels */
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label,
[data-testid="stMultiSelect"] label {
    color: #252923 !important;
}

/* Buttons intentionally use dark green backgrounds */
.stButton button,
.stDownloadButton button,
[data-testid="stFormSubmitButton"] button {
    background-color: #41483B !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Metric cards: light background, dark values */
.metric-card,
.metric-card * {
    color: #252923 !important;
}

.metric-label {
    color: #77796F !important;
}

/* Hero banner: preserve gold and ivory text on dark background */
.hero h1 {
    color: #E5BD72 !important;
}

.hero p {
    color: #E4E5DC !important;
}

/* Sidebar: preserve ivory text on graphite background */
[data-testid="stSidebar"] {
    background-color: #252923 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #F5F4EF !important;
}

/* Plotly charts: readable axis labels, tick labels and legends */
.js-plotly-plot .plotly text,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .legend text {
    fill: #252923 !important;
}

/* Placeholder text */
input::placeholder,
textarea::placeholder {
    color: #77796F !important;
    -webkit-text-fill-color: #77796F !important;
    opacity: 1 !important;
}



/* ===== FIX KPI DIGITS ON ALL ANALYTICS PAGES ===== */

/* Metric card backgrounds */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E4E2D9 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 14px rgba(37, 41, 35, 0.06) !important;
}

/* Main metric numbers */
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricValue"] * {
    color: #252923 !important;
    -webkit-text-fill-color: #252923 !important;
    font-size: 30px !important;
    font-weight: 750 !important;
}

/* Metric labels */
[data-testid="stMetric"] [data-testid="stMetricLabel"],
[data-testid="stMetric"] [data-testid="stMetricLabel"] * {
    color: #65685E !important;
    -webkit-text-fill-color: #65685E !important;
    font-size: 13px !important;
}

/* Metric deltas and captions */
[data-testid="stMetric"] [data-testid="stMetricDelta"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] * {
    -webkit-text-fill-color: currentColor;
}

/* Ensure analytics page containers use dark text */
[data-testid="stAppViewContainer"] .main [data-testid="stHorizontalBlock"] {
    color: #252923 !important;
}

</style>
""", unsafe_allow_html=True)


st.sidebar.markdown("# NEXORA")
st.sidebar.caption("COMMERCE INTELLIGENCE")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Sales Analytics",
        "Order Management",
        "Inventory Insights",
        "Data Explorer",
        "Order Updates",
        "Customer Analytics",
        "Priority Queue",
        "Route Optimization",
        "Network Analysis",
        "Customer Segmentation"
    ]
)

st.sidebar.divider()
st.sidebar.caption("E-COMMERCE ANALYTICS SYSTEM")
st.markdown("""
<div class="hero">
    <h1>NEXORA</h1>
    <p>E-Commerce Analytics & Intelligent Order Management System</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(uploaded_file, local_path):
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        if file_name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        return pd.read_excel(uploaded_file)
    if local_path and Path(local_path).exists():
        path = Path(local_path)
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
        return pd.read_excel(path)
    return pd.DataFrame()

st.sidebar.markdown("### Dataset")
uploaded = st.sidebar.file_uploader(
    "Upload your e-commerce dataset",
    type=["csv", "xlsx"]
)
default_path = "data/nexora_ecommerce_50000.xlsx"
data = load_data(uploaded, default_path)

if data.empty:
    st.info(
        "Upload your CSV/Excel dataset using the sidebar. "
        "You can also place your Excel file in the project folder "
        "as data/nexora_ecommerce_50000.xlsx."
    )
    st.markdown("### Get started")
    st.write("Once a dataset is loaded, NEXORA will display sales KPIs, "
             "order status, product performance and inventory insights.")
    st.stop()

data.columns = [str(c).strip() for c in data.columns]
lower_columns = {c.lower().replace(" ", "_"): c for c in data.columns}

def find_column(candidates):
    for candidate in candidates:
        key = candidate.lower().replace(" ", "_")
        if key in lower_columns:
            return lower_columns[key]
    return None

order_col = find_column(["order_id", "orderid", "order_number"])
sales_col = find_column(["sales", "revenue", "total_amount", "order_value",
                         "amount", "total", "price"])
qty_col = find_column(["quantity", "qty", "units_sold"])
status_col = find_column(["order_status", "status", "delivery_status"])
product_col = find_column(["product_name", "product", "product_category",
                           "category", "item"])
date_col = find_column(["order_date", "date", "purchase_date",
                         "created_at", "order_timestamp"])
customer_col = find_column(["customer_id", "customerid", "customer_name"])
region_col = find_column(["region", "state", "city", "location"])

if sales_col:
    data[sales_col] = pd.to_numeric(data[sales_col], errors="coerce")
if qty_col:
    data[qty_col] = pd.to_numeric(data[qty_col], errors="coerce")
if date_col:
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")



data = apply_saved_order_statuses(
    data, order_col, status_col
)

filtered = data.copy()



with st.sidebar:
    st.markdown("### Filters")
    if status_col:
        statuses = sorted(data[status_col].dropna().astype(str).unique())
        selected_statuses = st.multiselect(
            "Order status", statuses, default=statuses
        )
        filtered = filtered[
            filtered[status_col].astype(str).isin(selected_statuses)
        ]
    if region_col:
        regions = sorted(data[region_col].dropna().astype(str).unique())
        selected_regions = st.multiselect(
            "Region", regions, default=regions
        )
        filtered = filtered[
            filtered[region_col].astype(str).isin(selected_regions)
        ]

if page == "Executive Overview":
    st.markdown('<div class="section-title">Executive Overview</div>',
                unsafe_allow_html=True)
    total_orders = (filtered[order_col].nunique()
                    if order_col else len(filtered))
    total_sales = (filtered[sales_col].sum()
                   if sales_col else 0)
    avg_order = (total_sales / total_orders if total_orders else 0)
    total_customers = (filtered[customer_col].nunique()
                       if customer_col else 0)

    metrics = [
        ("TOTAL ORDERS", f"{total_orders:,.0f}"),
        ("TOTAL REVENUE", f"₹{total_sales:,.2f}" if sales_col else "N/A"),
        ("AVERAGE ORDER VALUE",
         f"₹{avg_order:,.2f}" if sales_col else "N/A"),
        ("UNIQUE CUSTOMERS",
         f"{total_customers:,.0f}" if customer_col else "N/A")
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">'
                f'{label}</div><div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True
            )

    left, right = st.columns(2)
    with left:
        st.subheader("Order Status Distribution")
        if status_col:
            status_counts = (
                filtered[status_col].fillna("Unknown")
                .astype(str).value_counts().rename_axis("Status")
                .reset_index(name="Orders")
            )
            fig = px.pie(status_counts, names="Status", values="Orders",
                         hole=0.62)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No order-status column detected.")
    with right:
        st.subheader("Revenue by Product")
        if sales_col and product_col:
            products = (
                filtered.groupby(product_col, dropna=False)[sales_col]
                .sum().nlargest(10).reset_index()
            )
            fig = px.bar(products, x=sales_col, y=product_col,
                         orientation="h", labels={sales_col: "Revenue"})
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Product and sales columns are needed for this chart.")

    st.subheader("Recent Records")
    st.dataframe(filtered.tail(10), use_container_width=True, hide_index=True)

elif page == "Sales Analytics":
    st.subheader("Sales Analytics")

    
    st.markdown("### Business Performance Insights")

    if sales_col and not filtered.empty:
        total_revenue = filtered[sales_col].sum()
        total_orders = (
            filtered[order_col].nunique()
            if order_col else len(filtered)
        )
        average_order_value = (
            total_revenue / total_orders if total_orders else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Revenue",
            f"₹{total_revenue:,.2f}"
        )
        col2.metric(
            "Total Orders",
            f"{total_orders:,}"
        )
        col3.metric(
            "Average Order Value",
            f"₹{average_order_value:,.2f}"
        )

        if product_col:
            product_sales = (
                filtered.groupby(product_col)[sales_col]
                .sum()
                .sort_values(ascending=False)
            )

            if not product_sales.empty:
                st.success(
                    f"Top-performing product/category: "
                    f"{product_sales.index[0]} "
                    f"(revenue ₹{product_sales.iloc[0]:,.2f})"
                )

                st.info(
                    f"Revenue represented by the top product/category: "
                    f"{product_sales.iloc[0] / total_revenue * 100:.1f}%"
                    if total_revenue else
                    "Revenue is zero; product revenue share is unavailable."
                )
    else:
        st.warning(
            "Sales insights require a valid sales/revenue column "
            "and at least one filtered record."
        )

    if sales_col:
        st.metric("Filtered Revenue", f"₹{filtered[sales_col].sum():,.2f}")
        if date_col:
            dated = filtered.dropna(subset=[date_col]).copy()
            if not dated.empty:
                dated["_period"] = dated[date_col].dt.to_period("M").astype(str)
                monthly = dated.groupby("_period")[sales_col].sum().reset_index()
                fig = px.line(monthly, x="_period", y=sales_col,
                              markers=True, title="Monthly Revenue Trend")
                st.plotly_chart(fig, use_container_width=True)
        if product_col:
            products = filtered.groupby(product_col)[sales_col].sum()
            st.subheader("Product Revenue Ranking")
            st.dataframe(products.sort_values(ascending=False).reset_index(
                name="Revenue"), use_container_width=True, hide_index=True)
    else:
        st.warning("Your dataset needs a sales/revenue/amount column.")

elif page == "Order Management":
    st.subheader("Order Management")
    if status_col:
        counts = filtered[status_col].fillna("Unknown").astype(str).value_counts()
        st.dataframe(counts.rename_axis("Status").reset_index(name="Orders"),
                     use_container_width=True, hide_index=True)
        if order_col:
            search = st.text_input("Search order ID")
            view = filtered
            if search:
                view = view[view[order_col].astype(str).str.contains(
                    search, case=False, na=False)]
            st.dataframe(view, use_container_width=True, hide_index=True)
        else:
            st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption("This initial version is read-only; status changes are not persisted.")
    else:
        st.warning("No order-status column was detected.")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

elif page == "Inventory Insights":
    st.subheader("Inventory Insights")
    if product_col and qty_col:
        inventory = filtered.groupby(product_col)[qty_col].sum().reset_index()
        inventory.columns = ["Product", "Units"]
        inventory = inventory.sort_values("Units", ascending=False)
        fig = px.bar(inventory.head(15), x="Product", y="Units",
                     title="Top Products by Quantity")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(inventory, use_container_width=True, hide_index=True)
        st.caption("This view summarizes sales quantities; it does not represent live stock.")
    else:
        st.warning("Inventory summary requires product and quantity columns.")

elif page == "Data Explorer":
    st.subheader("Data Explorer")
    st.write(f"Rows: {len(filtered):,} · Columns: {len(filtered.columns)}")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv,
                       "nexora_filtered_data.csv", "text/csv")





    
elif page == "Order Updates":
    st.subheader("Order Status Management")
    st.write("Update an order status and save it in the NEXORA database.")

    order_database.initialize_database()

    if not order_col:
        st.warning("Your dataset needs an order ID column to manage orders.")
    elif filtered.empty:
        st.info("No orders match your current filters.")
    else:
        order_ids = (
            filtered[order_col]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

        selected_order = st.selectbox("Select Order ID", order_ids)

        order_rows = filtered[
            filtered[order_col].astype(str) == selected_order
        ]

        st.markdown("### Selected Order")
        st.dataframe(
            order_rows.head(1),
            use_container_width=True,
            hide_index=True
        )

        default_status = (
            str(order_rows.iloc[0][status_col])
            if status_col and pd.notna(order_rows.iloc[0][status_col])
            else "Pending"
        )

        current_status = order_database.get_saved_status(
            selected_order, default_status
        )

        status_options = [
            "Pending",
            "Processing",
            "Packed",
            "Dispatched",
            "Shipped",
            "In Transit",
            "Delivered",
            "Completed",
            "Cancelled",
            "Returned"
        ]

        if current_status not in status_options:
            status_options.insert(0, current_status)

        chosen_status = st.selectbox(
            "New Order Status",
            status_options,
            index=status_options.index(current_status)
        )

        if st.button("Save Order Status", type="primary"):
            order_database.update_order_status(
                selected_order, chosen_status
            )
            st.success(
                f"Order {selected_order} saved as {chosen_status}."
            )
            st.rerun()

        st.markdown("### Recently Saved Updates")
        updates = order_database.get_all_order_updates()

        
        
        if updates:
            st.dataframe(
                pd.DataFrame(updates),
                use_container_width=True,
                hide_index=True
            )

            updates_df = pd.DataFrame(updates)
            csv_data = updates_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Order Updates (CSV)",
                data=csv_data,
                file_name="nexora_order_updates.csv",
                mime="text/csv"
            )
        else:
            st.info("No manual order updates have been saved yet.")




            
elif page == "Customer Analytics":
    st.subheader("Customer Analytics")
    st.caption("Understand customer activity and purchasing patterns.")

    if customer_col:
        customer_data = filtered.copy()

        customer_data[customer_col] = (
            customer_data[customer_col].astype(str)
        )

        total_customers = customer_data[customer_col].nunique()
        total_orders = (
            customer_data[order_col].nunique()
            if order_col else len(customer_data)
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Unique Customers", f"{total_customers:,}")
        col2.metric("Orders", f"{total_orders:,}")

        if sales_col:
            revenue = customer_data[sales_col].sum()
            col3.metric("Customer Revenue", f"₹{revenue:,.2f}")
        else:
            col3.metric("Customer Revenue", "N/A")

        if order_col:
            customer_orders = (
                customer_data.groupby(customer_col)[order_col]
                .nunique()
                .reset_index(name="Orders")
            )
        else:
            customer_orders = (
                customer_data.groupby(customer_col)
                .size()
                .reset_index(name="Orders")
            )

        st.markdown("### Repeat Customer Insights")

        repeat_customers = customer_orders[
            customer_orders["Orders"] > 1
        ]

        repeat_count = len(repeat_customers)
        repeat_rate = (
            repeat_count / total_customers * 100
            if total_customers else 0
        )

        col1, col2 = st.columns(2)
        col1.metric("Repeat Customers", f"{repeat_count:,}")
        col2.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

        if sales_col:
            customer_revenue = (
                customer_data.groupby(customer_col)[sales_col]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            st.markdown("### Top 10 Customers by Revenue")

            fig = px.bar(
                customer_revenue,
                x=sales_col,
                y=customer_col,
                orientation="h",
                title="Highest Revenue Customers"
            )
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Customer Purchase Summary")
        st.dataframe(
            customer_orders.sort_values(
                "Orders", ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning(
            "No customer ID column was detected. "
            "Your dataset needs a customer_id or customer_name column."
        )
        st.write("Available columns:", list(filtered.columns))




elif page == "Priority Queue":
    st.subheader("Intelligent Order Priority Queue")
    st.caption(
        "Urgent orders are processed first. "
        "Priority 1 is highest; priority 5 is lowest."
    )

    if order_col is None or filtered.empty:
        st.warning("No orders are available in the current dataset or filters.")
    else:
        if "nexora_priority_items" not in st.session_state:
            st.session_state.nexora_priority_items = {}

        order_ids = (
            filtered[order_col]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

        
        col1, col2 = st.columns(2)

        with col1:
            selected_order = st.selectbox(
                "Select an order",
                order_ids,
                key="priority_order_select"
            )

        # Determine the selected order's current status
        selected_rows = filtered[
            filtered[order_col].astype(str) == selected_order
        ]

        if status_col and not selected_rows.empty:
            current_status = str(
                selected_rows.iloc[0][status_col]
            )
        else:
            current_status = "Unknown"

        # Suggest priority from order status
        suggested_priority = suggest_order_priority(current_status)

        st.info(
            f"Order status: {current_status} | "
            f"Suggested priority: {suggested_priority}"
        )

        with col2:
            priority = st.selectbox(
                "Priority level",
                [1, 2, 3, 4, 5],
                index=suggested_priority - 1,
                format_func=lambda p: {
                    1: "1 — Critical",
                    2: "2 — High",
                    3: "3 — Medium",
                    4: "4 — Low",
                    5: "5 — Very Low"
                }[p]
            )

        if st.button("Add Order to Queue", type="primary"):
            st.session_state.nexora_priority_items[
                selected_order
            ] = priority

            st.success(
                f"Order {selected_order} added with priority {priority}."
            )

        queue_items = st.session_state.nexora_priority_items

        if queue_items:
            queue_df = pd.DataFrame([
                {"Order ID": oid, "Priority": p}
                for oid, p in queue_items.items()
            ])

            queue_df = queue_df.sort_values(
                by=["Priority", "Order ID"],
                ascending=[True, True]
            ).reset_index(drop=True)

            queue_df.insert(
                0, "Queue Position", range(1, len(queue_df) + 1)
            )

            st.markdown("### Sorted Processing Queue")

            st.dataframe(
                queue_df,
                use_container_width=True,
                hide_index=True
            )

            first_order = queue_df.iloc[0]

            st.info(
                f"Next order to process: {first_order['Order ID']} "
                f"(Priority {first_order['Priority']})"
            )

            if st.button("Process Highest-Priority Order"):
                processed_id = str(first_order["Order ID"])

                del st.session_state.nexora_priority_items[
                    processed_id
                ]

                st.success(f"Processed order {processed_id}.")
                st.rerun()

                if st.button("Clear Entire Queue"):

                    st.session_state.nexora_priority_items.clear()

                    st.rerun()




            else:
                     
                     
                    
                     st.info("The queue is empty. Select an order and add it above.")


elif page == "Route Optimization":
    show_route_optimization()



elif page == "Network Analysis":
    show_network_analysis()
