
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show_customer_segmentation(data, customer_col, order_col, sales_col, date_col):
    st.title("Customer Segmentation — RFM Analysis")
    st.write("Debug: Customer Segmentation function is running.")
    st.write("Rows received:", len(data))
    st.write("Columns received:", list(data.columns))
    st.write("Customer column:", customer_col)
    st.write("Order column:", order_col)
    st.write("Sales column:", sales_col)
    st.write("Date column:", date_col)
    st.write(
        "Group customers using Recency, Frequency, and Monetary value."
    )

    if data.empty:
        st.warning("No data is available with the current filters.")
        return

    required = [customer_col, order_col, sales_col, date_col]

    if any(col is None or col not in data.columns for col in required):
        st.error(
            "RFM analysis requires customer, order, sales, and order-date columns. "
            "Check the column names in your dataset."
        )
        return

    df = data[required].copy()
    df.columns = ["Customer", "Order", "Sales", "OrderDate"]

    df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df = df.dropna(subset=["Customer", "Order", "Sales", "OrderDate"])

    if df.empty:
        st.warning("No valid customer, sales, and date records were found.")
        return

    # Use the day after the latest recorded order as the reference date.
    reference_date = df["OrderDate"].max().normalize() + pd.Timedelta(days=1)

    rfm = df.groupby("Customer").agg(
        Recency=("OrderDate", lambda dates:
                 (reference_date - dates.max().normalize()).days),
        Frequency=("Order", "nunique"),
        Monetary=("Sales", "sum")
    ).reset_index()

    if len(rfm) < 2:
        st.warning("At least two customers are needed for useful segmentation.")
        st.dataframe(rfm, use_container_width=True)
        return

    # Rank-based scoring adapts to the size and distribution of the dataset.
    # Lower recency is better; higher frequency and monetary value are better.
    rfm["R_Score"] = pd.qcut(
        rfm["Recency"].rank(method="first", ascending=True),
        q=min(4, len(rfm)),
        labels=False
    ) + 1

    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        q=min(4, len(rfm)),
        labels=False
    ) + 1

    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        q=min(4, len(rfm)),
        labels=False
    ) + 1

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(int).astype(str)
        + rfm["F_Score"].astype(int).astype(str)
        + rfm["M_Score"].astype(int).astype(str)
    )

    def segment_customer(row):
        if row["R_Score"] >= 3 and row["F_Score"] >= 3 and row["M_Score"] >= 3:
            return "High Value"
        elif row["R_Score"] >= 3 and row["F_Score"] >= 3:
            return "Loyal"
        elif row["R_Score"] <= 2 and row["F_Score"] <= 2:
            return "Needs Attention"
        elif row["R_Score"] <= 2:
            return "At Risk"
        else:
            return "Regular"

    rfm["Segment"] = rfm.apply(segment_customer, axis=1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Customers Analyzed", len(rfm))
    col2.metric("High Value Customers", int((rfm["Segment"] == "High Value").sum()))
    col3.metric("At-Risk Customers", int((rfm["Segment"] == "At Risk").sum()))

    st.subheader("Customer Segments")

    segment_counts = (
        rfm["Segment"].value_counts()
        .rename_axis("Segment")
        .reset_index(name="Customers")
    )

    st.bar_chart(segment_counts.set_index("Segment"))

    st.subheader("RFM Customer Details")
    st.dataframe(
        rfm.sort_values("Monetary", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download RFM Report (CSV)",
        data=rfm.to_csv(index=False).encode("utf-8"),
        file_name="nexora_rfm_customer_report.csv",
        mime="text/csv"
    )

    st.caption(
        "Segments are based on relative quartile scores in the selected data. "
        "They are analytical categories, not predictions of future behaviour."
    )
