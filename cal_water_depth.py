import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

file_atm_name = "baro.csv"
file_device_name = "rbrd.csv"

# Define column names based on the file's structure
initial_col_names = [
    "year", "month", "day", "hour", "minute", "second", "ms", "pressure_mbar"
]

# 1. Read the CSV file, skipping the header comment row (#)
# skiprows=1 skips the comment line.
# header=None is used because we are supplying the names manually.
df = pd.read_csv(
    file_atm_name,
    skiprows=1,
    header=None,
    names=initial_col_names
)

# 2. Combine date/time columns into a single datetime column.
# to_datetime can take a dictionary or DataFrame of components (year, month, day, etc.)
# It automatically handles the msec by putting it into the fractional seconds part.
df['timestamp'] = pd.to_datetime(
    df[["year", "month", "day", "hour", "minute", "second","ms"]]
)

# 3. Rename and convert pressure
# Convert pressure from millibar to microbar (*1000)
df['pressure_microbar'] = df['pressure_mbar'] * 1000.0

initial_col_names = [
    "year", "month", "day", "hour", "minute", "second", "ms", "pressure_microbar"
]
df_device = pd.read_csv(
    file_device_name,
    skiprows=1,
    header=None,
    names=initial_col_names
)

df_device['timestamp'] = pd.to_datetime(
    df_device[["year", "month", "day", "hour", "minute", "second","ms"]]
)

df_device['seaSurfacePressure'] = np.interp(df_device['timestamp'],df['timestamp'],df['pressure_microbar'])
df_device['depth'] = (df_device['seaSurfacePressure']-df_device['pressure_microbar'])/10/9.81/1023

# 4. Create the final DataFrame with only the desired fields
df_final = df_device[['timestamp', 'depth']].copy()


# Display the first few rows and column information
print("--- Final DataFrame (First 5 Rows) ---")
print(df_final.head())
print("\n--- DataFrame Information ---")
print(df_final.info())
df_final.to_csv('water_depth.csv',index=False)

# --- NEW: FILTERING THE DATA ---
filter_date = pd.to_datetime('2025-08-13')
# Create a new DataFrame containing only records after the specified date
df_filtered = df_device[df_device['timestamp'] > filter_date].copy()


# --- PLOTTING THE FILTERED WATER LEVEL ---

if df_filtered.empty:
    print(f"No data found after {filter_date}. Plotting skipped.")
else:
    plt.figure(figsize=(12, 6))

    # Plot depth vs. timestamp using the filtered data
    plt.plot(df_filtered['timestamp'], df_filtered['depth'], 
             marker='.', linestyle='-', markersize=2, label='Water Depth (m)')

    # Formatting the plot for time-series data
    plt.xlabel("Timestamp")
    plt.ylabel("Water Depth (m)")
    plt.title(f"Long-Term Water Level (Data Filtered After {filter_date.date()})")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Improve x-axis date formatting for better readability
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')

    # Add legend and ensure plot elements fit
    plt.legend()
    plt.tight_layout()
    plt.show()
    # Save the plot to a file
    #plt.savefig('water_depth_filtered_plot.png')
    #plt.close()

    print("Filtered water depth plot successfully generated and saved as 'water_depth_filtered_plot.png'")