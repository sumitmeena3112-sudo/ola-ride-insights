"""Clean OLA_DataSet.xlsx -> output/ola_clean.csv + output/ola.db (SQLite, table `rides`)."""
import sqlite3
import pandas as pd

df = pd.read_excel("OLA_DataSet.xlsx", sheet_name="July")
df.columns = [c.strip().replace(" ", "_") for c in df.columns]
df["Time"] = df["Time"].astype(str)
df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
df["Hour"] = df["Time"].str[:2].astype(int)
df["Day_Name"] = pd.to_datetime(df["Date"]).dt.day_name()
# Business-meaningful fills: nulls in cancel/incomplete columns mean "not applicable"
for c in ["Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver", "Incomplete_Rides_Reason"]:
    df[c] = df[c].fillna("Not Applicable")
df["Incomplete_Rides"] = df["Incomplete_Rides"].fillna("Not Applicable")
df["Payment_Method"] = df["Payment_Method"].fillna("Not Paid")
# Ratings/TAT stay NULL for rides that never completed (no rating exists)
df = df.drop_duplicates("Booking_ID")
df.to_csv("output/ola_clean.csv", index=False)
with sqlite3.connect("output/ola.db") as con:
    df.to_sql("rides", con, if_exists="replace", index=False)
print(df.shape)
