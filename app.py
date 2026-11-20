"""OLA Ride Insights - Streamlit app.

Structure follows the project brief:
  Overall | Vehicle Type | Revenue | Cancellation | Ratings   (the 5 required views)
  Business Insights
Run: streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
NA = "Not Applicable"
st.set_page_config(page_title="OLA Ride Insights", page_icon="🚖", layout="wide")


# ----------------------------------------------------------------- data layer
@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(BASE / "output" / "ola_clean.csv", parse_dates=["Date"])


def chart(fig, **kw):
    st.plotly_chart(fig, width="stretch", **kw)


df = load()

# -------------------------------------------------------------------- filters
st.sidebar.header("Filters")
d0, d1 = df.Date.min().date(), df.Date.max().date()
dates = st.sidebar.date_input("Date range", (d0, d1), min_value=d0, max_value=d1)
all_v, all_p = sorted(df.Vehicle_Type.unique()), sorted(df.Payment_Method.unique())
vehicles = st.sidebar.multiselect("Vehicle type", all_v, default=all_v)
pays = st.sidebar.multiselect("Payment method", all_p, default=all_p)
statuses = st.sidebar.multiselect("Booking status", sorted(df.Booking_Status.unique()),
                                  default=sorted(df.Booking_Status.unique()))
f = df
if len(dates) == 2:
    f = f[(f.Date.dt.date >= dates[0]) & (f.Date.dt.date <= dates[1])]
f = f[f.Vehicle_Type.isin(vehicles) & f.Payment_Method.isin(pays) & f.Booking_Status.isin(statuses)]
succ = f[f.Booking_Status == "Success"]
st.sidebar.caption(f"{len(f):,} of {len(df):,} bookings selected")

# ------------------------------------------------------------------ KPI strip
st.title("🚖 OLA Ride Insights")
st.caption("Ride-sharing & mobility analytics · July 2024 · all revenue figures count successful rides only")
k = st.columns(5)
k[0].metric("Total bookings", f"{len(f):,}")
k[1].metric("Success rate", f"{len(succ) / max(len(f), 1):.1%}")
k[2].metric("Revenue (successful)", f"₹{succ.Booking_Value.sum():,.0f}")
k[3].metric("Avg driver rating", f"{succ.Driver_Ratings.mean():.2f}" if len(succ) else "–")
k[4].metric("Avg customer rating", f"{succ.Customer_Rating.mean():.2f}" if len(succ) else "–")

tabs = st.tabs(["1 · Overall", "2 · Vehicle Type", "3 · Revenue", "4 · Cancellation",
                "5 · Ratings", "Business Insights"])

# ---------------------------------------------------------------- 1. Overall
with tabs[0]:
    st.subheader("Ride Volume Over Time")
    daily = f.groupby("Date").size().reset_index(name="Rides")
    chart(px.line(daily, x="Date", y="Rides", markers=True))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Booking Status Breakdown")
        chart(px.pie(f, names="Booking_Status", hole=0.45))
    with c2:
        st.subheader("Demand by Hour of Day (peak hours)")
        hourly = f.groupby("Hour").size().reset_index(name="Rides")
        chart(px.bar(hourly, x="Hour", y="Rides"))

# ----------------------------------------------------------- 2. Vehicle Type
with tabs[1]:
    st.subheader("Top 5 Vehicle Types by Ride Distance")
    top_v = succ.groupby("Vehicle_Type").Ride_Distance.sum().nlargest(5).reset_index()
    chart(px.bar(top_v, x="Vehicle_Type", y="Ride_Distance", text_auto=".3s",
                 labels={"Ride_Distance": "Total distance (km)"}))
    st.subheader("Average Ratings by Vehicle Type")
    avg = succ.groupby("Vehicle_Type")[["Customer_Rating", "Driver_Ratings"]].mean().round(3).reset_index()
    chart(px.bar(avg.melt("Vehicle_Type", var_name="Rating", value_name="Average"),
                 x="Vehicle_Type", y="Average", color="Rating", barmode="group",
                 range_y=[0, 5]))
    st.caption("Y-axis starts at 0 on purpose: ratings are almost identical across vehicle types.")

# ---------------------------------------------------------------- 3. Revenue
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Payment Method")
        pm = succ.groupby("Payment_Method").Booking_Value.sum().reset_index()
        chart(px.pie(pm, names="Payment_Method", values="Booking_Value", hole=0.4))
    with c2:
        st.subheader("Top 5 Customers by Total Booking Value")
        top_c = succ.groupby("Customer_ID").Booking_Value.sum().nlargest(5).reset_index()
        chart(px.bar(top_c, x="Booking_Value", y="Customer_ID", orientation="h")
              .update_yaxes(autorange="reversed"))
    st.subheader("Ride Distance Distribution Per Day")
    dist = succ.groupby("Date").Ride_Distance.sum().reset_index()
    chart(px.line(dist, x="Date", y="Ride_Distance", markers=True,
                  labels={"Ride_Distance": "Total km per day"}))
    chart(px.box(succ, x="Day_Name", y="Ride_Distance",
                 category_orders={"Day_Name": ["Monday", "Tuesday", "Wednesday", "Thursday",
                                               "Friday", "Saturday", "Sunday"]},
                 title="Per-ride distance by weekday"))

# ------------------------------------------------------------- 4. Cancellation
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cancelled Rides - Reasons (Customer)")
        cc = f[f.Canceled_Rides_by_Customer != NA].Canceled_Rides_by_Customer.value_counts().reset_index()
        chart(px.bar(cc, x="count", y="Canceled_Rides_by_Customer", orientation="h")
              .update_yaxes(autorange="reversed"))
    with c2:
        st.subheader("Cancelled Rides - Reasons (Drivers)")
        dc = f[f.Canceled_Rides_by_Driver != NA].Canceled_Rides_by_Driver.value_counts().reset_index()
        chart(px.bar(dc, x="count", y="Canceled_Rides_by_Driver", orientation="h")
              .update_yaxes(autorange="reversed"))
    st.subheader("Incomplete Rides - Reasons")
    ir = f[f.Incomplete_Rides == "Yes"].Incomplete_Rides_Reason.value_counts().reset_index()
    chart(px.bar(ir, x="Incomplete_Rides_Reason", y="count"))

# ------------------------------------------------------------------ 5. Ratings
with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Driver Ratings")
        chart(px.histogram(succ, x="Driver_Ratings", nbins=20))
    with c2:
        st.subheader("Customer Ratings")
        chart(px.histogram(succ, x="Customer_Rating", nbins=20))
    st.subheader("Customer vs. Driver Ratings")
    chart(px.density_heatmap(succ, x="Customer_Rating", y="Driver_Ratings", nbinsx=21, nbinsy=21,
                             color_continuous_scale="Blues"))
    if len(succ) > 2:
        st.caption(f"Correlation between customer and driver rating: "
                   f"{succ.Customer_Rating.corr(succ.Driver_Ratings):+.3f}")

# ----------------------------------------------------------- Business Insights
with tabs[5]:
    st.subheader("Business insights (update with the sidebar filters)")
    if len(succ) < 50:
        st.info("Select more data in the sidebar to see insights.")
    else:
        peak = f.groupby("Hour").size().sort_values(ascending=False)
        pk = peak.index[:3].tolist()
        wk = f.groupby("Day_Name").size()
        top_cc = f[f.Canceled_Rides_by_Customer != NA].Canceled_Rides_by_Customer.value_counts()
        top_dc = f[f.Canceled_Rides_by_Driver != NA].Canceled_Rides_by_Driver.value_counts()
        pay = succ.groupby("Payment_Method").Booking_Value.sum()
        s_km = succ.assign(fpk=succ.Booking_Value / succ.Ride_Distance.clip(lower=1))
        fare = s_km.groupby("Vehicle_Type").fpk.median().sort_values(ascending=False)
        lost = 1 - len(succ) / max(len(f), 1)

        st.markdown("#### 1 · Peak demand and driver allocation")
        st.write(f"The busiest hours are **{pk[0]:02d}:00, {pk[1]:02d}:00 and {pk[2]:02d}:00** "
                 f"({peak.iloc[0]:,} bookings at the top hour). The busiest weekday is **{wk.idxmax()}** "
                 f"and the quietest is **{wk.idxmin()}**. Rostering more drivers into these windows is the "
                 f"most direct lever on the **{lost:.1%}** of bookings that never complete.")
        st.markdown("#### 2 · Where rides are lost")
        if len(top_cc) and len(top_dc):
            st.write(f"Customers cancel mostly because **{top_cc.index[0].lower()}** ({top_cc.iloc[0]:,}); "
                     f"drivers cancel mostly for **{top_dc.index[0].lower()}** ({top_dc.iloc[0]:,}). "
                     "Both are operational and fixable (driver ETA tracking, car checks, rider-count "
                     "reminders) rather than demand problems.")
        st.markdown("#### 3 · Customer behaviour")
        cust = succ.groupby("Customer_ID").agg(rides=("Booking_ID", "count"), value=("Booking_Value", "sum"))
        st.write(f"**{len(cust):,}** customers took a successful ride, and the most active took "
                 f"**{cust.rides.max()}** rides. Repeat customers are rare "
                 f"(**{(cust.rides > 1).mean():.1%}** rode more than once), so retention offers for second "
                 "rides are a clear marketing opportunity. The highest-value customer spent "
                 f"**₹{cust.value.max():,.0f}**.")
        st.markdown("#### 4 · Payments and pricing")
        st.write(f"**{pay.idxmax()}** brings in the most revenue ({pay.max() / pay.sum():.1%} of the total). "
                 f"Median fare per km is highest for **{fare.index[0]}** (₹{fare.iloc[0]:.1f}/km) versus "
                 f"₹{fare.iloc[-1]:.1f}/km for {fare.index[-1]}"
                 + (f" ({fare.iloc[0] / fare.iloc[-1]:.1f}× higher)." if len(fare) > 1 else "."))
        if len(fare) > 2 and fare.iloc[1] > 0 and fare.iloc[0] / fare.iloc[1] > 1.5 \
                and fare.iloc[1] / fare.iloc[-1] < 1.2:
            st.write(f"The remaining vehicle types sit in a narrow band, so pricing is effectively "
                     f"two-tier: {fare.index[0]} versus everything else.")
        st.markdown("#### 5 · Service quality")
        st.write(f"Average driver rating is **{succ.Driver_Ratings.mean():.2f}** and customer rating "
                 f"**{succ.Customer_Rating.mean():.2f}**, nearly identical across vehicle types "
                 f"(spread {succ.groupby('Vehicle_Type').Customer_Rating.mean().agg(lambda x: x.max() - x.min()):.3f}). "
                 "Ratings do not separate good from poor service here, so complaints and cancellations are "
                 "better quality signals than stars.")

        st.markdown("#### 6 · Anomaly / fraud screen")
        st.caption("Flags successful rides whose fare per km is more than 5× the median for the same "
                   "vehicle type. These are candidates to review, not confirmed fraud.")
        s_km["median_fpk"] = s_km.groupby("Vehicle_Type").fpk.transform("median")
        flags = s_km[s_km.fpk > 5 * s_km.median_fpk]
        st.write(f"**{len(flags):,}** rides flagged ({len(flags) / len(s_km):.1%} of successful rides).")
        if len(flags):
            chart(px.histogram(flags, x="Vehicle_Type", title="Flagged rides by vehicle type"))
            st.dataframe(flags[["Booking_ID", "Customer_ID", "Vehicle_Type", "Ride_Distance",
                                "Booking_Value", "fpk"]].rename(columns={"fpk": "fare_per_km"})
                         .sort_values("fare_per_km", ascending=False).head(200), width="stretch")
