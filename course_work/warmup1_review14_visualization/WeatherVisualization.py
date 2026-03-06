#Lesson Date: 09/02

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
titanic_file_path = os.path.join(BASE_DIR, "titanic_dataset.csv")
temp_file_path = os.path.join(BASE_DIR, "weatherHistory_df.csv")

titanic_df = pd.read_csv(titanic_file_path)

DATE_COLUMN = "Formatted Date"
TEMPERATURE_COLUMN = "Temperature (C)"
weather_df = pd.read_csv(temp_file_path).sort_values(DATE_COLUMN).head(1000)
weather_df[DATE_COLUMN] = pd.to_datetime(weather_df[DATE_COLUMN], errors="coerce", utc=True)

weather_df_interpolated = weather_df.set_index(DATE_COLUMN).interpolate(method="time")


fig, axes = plt.subplots(2,2, figsize=(12,8))



def format_daily_axis(ax, day_interval: int = 6) -> None:
    locator = mdates.DayLocator(interval=day_interval)
    formatter = mdates.ConciseDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)




sns.set_theme(style="whitegrid")

sns.lineplot(
    data=weather_df.dropna(),
    x = DATE_COLUMN,
    y= TEMPERATURE_COLUMN,
    ax=axes[0][0]
)

axes[0][0].set_title("Line: Dropped NaN")
axes[0][0].set_xlabel("Date")
axes[0][0].set_ylabel("Temp")
format_daily_axis(axes[0][0], day_interval=1)

sns.lineplot(
    data=weather_df.interpolate(),
    x = DATE_COLUMN,
    y= TEMPERATURE_COLUMN,
    ax=axes[0][1]
)

axes[0][1].set_title("Line: Linear Interpolation")
axes[0][1].set_xlabel("Date")
axes[0][1].set_ylabel("Temp")
format_daily_axis(axes[0][1], day_interval=1)


sns.histplot(
    data=weather_df.dropna(),
    x=TEMPERATURE_COLUMN,
    bins=20,
    ax = axes[1][0]
)
axes[1][0].set_title("Hist: Dropped Nan")
axes[1][0].set_xlabel("Frequency")
axes[1][0].set_ylabel("Temp")


sns.histplot(
    data=weather_df_interpolated,
    x=TEMPERATURE_COLUMN,
    bins=20,
    ax = axes[1][1]
)
axes[1][1].set_title("Hist: Linear Interpolation")
axes[1][1].set_xlabel("Frequency")
axes[1][1].set_ylabel("Temp")



    
        


plt.tight_layout()
plt.show()


