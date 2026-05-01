import pandas as pd # Basically excel for python 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np 

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

# Will update in the future to get the no of reruns that a patch ha
def longest_time_is_rerun(): 
   
   df = read_banner_history() 

   chronicle_names = df[df["Is_chronicle"] == 1]["Name"].unique()

   df = df[~df['Name'].isin(chronicle_names)]

   result = df.groupby("Patch").apply(lambda x : x.nlargest(4, "Time_since_ran")).reset_index()

   print(result[["Patch", "Name", "Time_since_ran"]])


def prepare_features(df):

   chronicle_names = df[df["Is_chronicle"] == 1]["Name"].unique()

   df = df.sort_values(["Name", "Patch"]).copy()
   df = df.reset_index(drop=True)

   # Shift Time_since_ran forward by 1 within each chars history to prevent data leak
   df["Time_since_ran"] = df.groupby("Name")["Time_since_ran"].shift(1)

   # Chars first row now has no value for Time_since_ran, so fill it
   df["Time_since_ran"] = df["Time_since_ran"].fillna(999)

   # Same for total_runs 
   df["Total_runs"] = df.groupby("Name")["Total_runs"].shift(1).fillna(0)

   df = df[df["Total_runs"] > 0]

   df = df.drop(columns=["Name", "Is_chronicle"])

   df = pd.get_dummies(df, columns=["Element", "Weapon"])

   X = df.drop(columns="Ran")
   y = df["Ran"]

   return X, y, chronicle_names

def show_predictions_for_patch(df_original, model, X, y, chronicle_names, patch):
   # Get the rows for this patch from the original df (which still has Name)
   patch_mask = X["Patch"] == patch
   X_patch = X[patch_mask].drop(columns=["Patch"])
    
   # Get the corresponding names from the original df using the same index
   if "Name" in df_original.columns:
      names = df_original.loc[X_patch.index, "Name"]
   else:
      names = X_patch.index

   probs = model.predict_proba(X_patch)[:, 1]  # probability of Ran=1
   actuals = y[patch_mask]

   # Chronicle characters do not rerun
   is_chronicle = names.isin(chronicle_names).values
   probs[is_chronicle] = 0.0

   top4_indices = probs.argsort()[-4:][::-1]
   predicted = np.zeros(len(probs), dtype=int)
   predicted[top4_indices] = 1

   results = pd.DataFrame({
     "Name": names.values,
     "Actual": actuals.values,
     "Predicted_prob": probs.round(2),
     "Predicted": predicted
   }).sort_values("Predicted_prob", ascending=False)

   print(f"\nPatch {patch} Predictions")
   print(results.to_string(index=False))

def predict_next_patch(df_original, model, chronicle_names, next_patch):
   this_patch = df_original.sort_values("Patch").groupby("Name").last().reset_index()

   is_chronicle = this_patch["Name"].isin(chronicle_names)
   this_patch = this_patch[is_chronicle == False]


   # Since theres no data for the next patch, we must build the features for it
   future = this_patch.copy()
   future["Patch"] = next_patch

   for i in future.index: 
      if future.loc[i, "Ran"] == 1: 
         future.loc[i, "Time_since_ran"] = 0
      else: 
         future.loc[i, "Time_since_ran"] = future.loc[i, "Time_since_ran"] + 1

   future = future.drop(columns=["Name", "Is_chronicle", "Ran"]) 
   future = pd.get_dummies(future, columns=["Element", "Weapon"])

   # Aligns the columns to match training data 
   future = future.reindex(columns=model.feature_names_in_, fill_value=0)

   names = this_patch["Name"].values
   probs = model.predict_proba(future)[:, 1]

   # characters don't run before being off banner for 3 versions (6 cycles)
   for i in range(len(future)): 
      if future.iloc[i]["Time_since_ran"] <= 3: 
         probs[i] = 0.0 

   top4_indices = probs.argsort()[-4:][::-1]
   predicted = np.zeros(len(probs), dtype=int)
   predicted[top4_indices] = 1

   results = pd.DataFrame({
      "Name": names,
      "Predicted_prob": probs.round(2),
      "Predicted": predicted
   }).sort_values("Predicted_prob", ascending=False)

   print(f"\nPredictions for Patch {next_patch}")
   print(results.to_string(index=False))


longest_time_is_rerun() 

"""
df = read_banner_history()
df_original = df.copy()

X, y, chronicle_names = prepare_features(df)

df_original = df_original.sort_values(["Name", "Patch"]).reset_index(drop=True)

split_patch = 6.0

X_train = X[X["Patch"] < split_patch].drop(columns=["Patch"])
y_train = y[X["Patch"] < split_patch]
X_test = X[X["Patch"] >= split_patch].drop(columns=["Patch"])
y_test = y[X["Patch"] >= split_patch]

print(f"Training rows: {len(X_train)}. Test rows: {len(X_test)}")

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))

show_predictions_for_patch(df_original, model, X, y, chronicle_names, patch=6.4)

"""