-- OLA Ride Insights: SQL answers (SQLite syntax; table `rides`, built by clean_data.py)

-- 1. All successful bookings
SELECT * FROM rides WHERE Booking_Status = 'Success';

-- 2. Average ride distance per vehicle type
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance),2) AS avg_distance
FROM rides GROUP BY Vehicle_Type ORDER BY avg_distance DESC;

-- 3. Total rides cancelled by customers
SELECT COUNT(*) AS cancelled_by_customers FROM rides WHERE Booking_Status = 'Canceled by Customer';

-- 4. Top 5 customers by number of rides
SELECT Customer_ID, COUNT(Booking_ID) AS total_rides
FROM rides GROUP BY Customer_ID ORDER BY total_rides DESC, Customer_ID LIMIT 5;

-- 5. Rides cancelled by drivers: personal & car related issues
SELECT COUNT(*) AS driver_cancel_personal_car
FROM rides WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- 6. Max / min driver rating for Prime Sedan
SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating
FROM rides WHERE Vehicle_Type = 'Prime Sedan' AND Driver_Ratings IS NOT NULL;

-- 7. Rides paid by UPI
SELECT * FROM rides WHERE Payment_Method = 'UPI';

-- 8. Average customer rating per vehicle type
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating),2) AS avg_customer_rating
FROM rides WHERE Customer_Rating IS NOT NULL GROUP BY Vehicle_Type ORDER BY avg_customer_rating DESC;

-- 9. Total booking value of successful rides
SELECT SUM(Booking_Value) AS total_booking_value FROM rides WHERE Booking_Status = 'Success';

-- 10. Incomplete rides with reason
SELECT Booking_ID, Customer_ID, Vehicle_Type, Incomplete_Rides_Reason
FROM rides WHERE Incomplete_Rides = 'Yes';
