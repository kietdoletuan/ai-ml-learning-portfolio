#Lesson Date: 09/02

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
titanic_data_path = os.path.join(BASE_DIR, "data/titanic_dataset.csv")

titanic_df = pd.read_csv(titanic_data_path)
titanic_df.drop(columns=["Cabin"])

pattern = re.compile(r",\s(\w+)\.")

titanic_df = (
    titanic_df
    .assign(
        Age = lambda df: df["Age"].fillna(df["Age"].median()),
        Fare = lambda df: df["Fare"].fillna(
            df.groupby("Pclass")["Fare"].transform("median")
        ),
        Log_Fare = lambda df: np.log1p(df["Fare"]),
        Title=lambda df: df["Name"].str.extract(pattern, expand=False).str.strip(),
        Sex_Index = lambda df: (df["Sex"] == "male").astype(int)
    )
    .drop(columns=["Cabin"])

)

fig, axes = plt.subplots(2,2, figsize=(12,8))
fig.suptitle("Titanic Dataset Analysis")

sns.histplot(
    data = titanic_df,
    x = "Age",
    ax = axes[0][0],
    bins = 20,
    kde = True
)

axes[0][0].set_title("Age Distribution")
axes[0][0].set_xlabel("Age")


sns.countplot(
    data = titanic_df,
    x = "Sex",
    hue = "Survived",
    ax = axes[0][1]
)

axes[0][1].set_title("Survival Count By Sex")

sns.histplot(
    data = titanic_df[titanic_df["Survived"] == 1],
    x = "Fare",
    ax = axes[1][0]
)
axes[1][0].set_title("Fare of Survivor Distribution")
axes[1][0].set_xlabel("Fare")


corre = titanic_df[["Survived","Age", "Pclass", "Sex_Index", "SibSp", "Parch", "Fare"]].corr()

sns.heatmap(
    corre,
    annot = True,
    square = True,
    cmap = "coolwarm", 
    cbar = True,
    fmt = "0.2f",
    ax = axes[1][1]
)

axes[1][1].set_title("Heatmap on Correlation For Survival")


plt.tight_layout()
plt.show()