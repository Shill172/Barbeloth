import pandas as pd # Basically excel for python 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

luna_version_map = {
    "Luna I": 6.0,
    "Luna II": 6.1,
    "Luna III": 6.2,
    "Luna IV": 6.3,
    "Luna V": 6.4, 
    "Luna VI": 6.5,
    "Luna VII": 6.6, 
    "Luna VIII": 6.7 
}

def read_banner_history():

   df = pd.read_csv("resources/banner_history_long.csv")

   df["Patch"] = df["Patch"].map(luna_version_map).fillna(df["Patch"])

    # Convert patches to floats "1.0" = 1.0
   df["Patch"] = df["Patch"].astype(float)

   return df 

def prepare_features(df):
   # Name is an identifier, so don't need it 
   df = df.drop(columns=["Name"])

   # One hot encode string columns
   # pd.get_dummies() automatically finds strin columns and expands 
   df = pd.get_dummies(df, columns=["Element", "Weapon"])

   # Seperate features (X) from target (y)
   # X = things model looks at
   # y = answer to predict
   X = df.drop(columns="Ran")
   y = df["Ran"]

   return X, y 


df = read_banner_history()

X, y = prepare_features(df)

print(X.shape)        # should have more columns now due to one-hot encoding
print(X.columns.tolist())  # see all the feature names
print(y.value_counts())    # how many 1s vs 0s? (ran vs didn't run)