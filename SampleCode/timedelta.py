from datetime import datetime, timedelta
a = datetime(2025, 5, 24, 14, 30)

b = a + timedelta(hours=2, minutes=15)
print("Updated Datetime:", b)