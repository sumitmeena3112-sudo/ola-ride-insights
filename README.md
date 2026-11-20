# OLA Ride Insights

## 🌐 Live website
**[Open the OLA Ride Insights app](https://sumitmeena3112-sudo-ola-ride-insights-app-necfnq.streamlit.app/)**

https://sumitmeena3112-sudo-ola-ride-insights-app-necfnq.streamlit.app/

_(Hosted on Streamlit Community Cloud. If the page shows a "wake up" button, click it and wait about 30 seconds.)_

Streamlit app, SQL answers and BI dashboards for the OLA ride-sharing dataset (July 2024, 103,024 bookings).

## App structure (follows the project brief)
| Tab | Content |
|---|---|
| 1 Overall | Ride volume over time, booking status breakdown, demand by hour |
| 2 Vehicle Type | Top 5 vehicle types by ride distance, average ratings by vehicle type |
| 3 Revenue | Revenue by payment method, top 5 customers by booking value, ride distance per day |
| 4 Cancellation | Cancellation reasons (customers, drivers), incomplete-ride reasons |
| 5 Ratings | Driver ratings, customer ratings, customer vs driver ratings |
| Business Insights | Written findings generated from the filtered data, plus fare-per-km anomaly screen |

Sidebar filters: date range, vehicle type, payment method, booking status.

## Files
`app.py` app · `ola_queries.sql` SQL answers · `clean_data.py` cleaning · `output/ola_clean.csv` cleaned data · `dashboards_pdf/` exports.

## Notes
- Revenue figures count successful rides only (cancelled rides carry a booking value in the raw data).
- The 10 SQL answers live in `ola_queries.sql` (SQLite syntax); they are not part of the app.
- Run locally: `pip install -r requirements.txt` then `streamlit run app.py`.
