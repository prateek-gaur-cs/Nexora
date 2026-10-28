
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="NEXORA | Commerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { background: #f5f4ef; color: #252820; }
[data-testid="stSidebar"] { background: #252923; }
[data-testid="stSidebar"] * { color: #f5f4ef; }
.block-container { padding-top: 2rem; }
.hero {
    background: linear-gradient(120deg, #252923, #41483b);
    padding: 28px 32px; border-radius: 16px; color: white;
    margin-bottom: 24px;
}
.hero h1 { color: #e5bd72; margin: 0; font-size: 36px; }
.hero p { color: #e4e5dc; margin-bottom: 0; }
.metric-card {
    background: white; border: 1px solid #e4e2d9;
    padding: 20px; border-radius: 12px; min-height: 120px;
}
.metric-label { color: #77796f; font-size: 13px; }
.metric-value { font-size: 28px; font-weight: 700; margin-top: 8px; }
.section-title { font-size: 21px; font-weight: 650; margin: 18px 0 12px; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# NEXORA")
st.sidebar.caption("COMMERCE INTELLIGENCE")
page = st.sidebar.radio(
    "NAVIGATION",
    ["Executive Overview", "Sales Analytics", "Order Management",
     "Inventory Insights", "Data Explorer"]
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
