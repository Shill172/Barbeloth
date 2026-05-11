import pandas as pd # Basically excel for python 
import numpy as np 
from dataprocessing import get_rerun_slots_for_patch
from config import LAST_REGULAR_RERUN_FILE


def load_last_regular_rerun_map():
   """
   Returns {Name: last_regular_patch} for characters who are chronicle
   """

   df = pd.read_csv(LAST_REGULAR_RERUN_FILE)
   return dict(zip(df["Name"], df["Patch"].astype(float)))


def is_chronicle_excluded(name, patch, last_regular_map):
   """
   Returns True if the characters next appearence is chronicle
   """
   if name not in last_regular_map:
      return False 
   return patch > last_regular_map[name]


def prepare_features(df):
   """
   Builds features X and target (ran) y from banner history DataFrame

   - Shifts Time_since_ran and Total_runs forward to avoid data leakage 
   (model can only see what happens before each patch)
   - drops debut rows (total runs == 0 after shift)
   - One hot encode elements and weapons 

   returns X, y, chronicle_names
   """

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

   return X, y

def show_predictions_for_patch(df_original, model, X, y, patch):
   """
   Uses a trained model to predict which characters run in a known patch then
   prints a comparison with the actuals. 

   Returns a DataFrame of (Patch, Name, Predicted_prob)
   """
   last_regular_map = load_last_regular_rerun_map()

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

   # Exclude chronicle characters whose last regular rerun has already passed
   for i, name in enumerate(names.values):
      if is_chronicle_excluded(name, patch, last_regular_map):
         probs[i] = 0.0

   n = get_rerun_slots_for_patch(patch)

   top_indices = probs.argsort()[-n:][::-1]
   predicted = np.zeros(len(probs), dtype=int)
   predicted[top_indices] = 1

   results = pd.DataFrame({
     "Name": names.values,
     "Actual": actuals.values,
     "Predicted_prob": probs.round(2),
     "Predicted": predicted
   }).sort_values("Predicted_prob", ascending=False)

   print(f"\nPatch {patch} Predictions")
   print(results.to_string(index=False))

   predicted = results[results["Predicted"] == 1].copy()
   predicted["Patch"] = patch 

   return predicted[["Patch", "Name", "Predicted_prob"]]


def predict_next_patch(df_original, model, next_patch):
   """
   Predicts a patch that hasn't happened yet. 
   Builds features from most recent data for characters, then scores them with the 
   provided model. 

   Characters are manually taken off if: 
   - Been off banner for 3 or less patches (too soon to rerun)
   - Their next banner is chronicle (no chance for a regular rerun)
   """
   last_regular_map = load_last_regular_rerun_map()

   this_patch = df_original.sort_values("Patch").groupby("Name").last().reset_index()

   this_patch = this_patch[
      ~this_patch["Name"].apply(lambda name: is_chronicle_excluded(name, next_patch, last_regular_map))
   ]

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

   # characters don"t run before being off banner for 3 versions (6 cycles)
   for i in range(len(future)): 
      if future.iloc[i]["Time_since_ran"] <= 3: 
         probs[i] = 0.0 

   n = get_rerun_slots_for_patch(next_patch)

   top_indices = probs.argsort()[-n:][::-1]
   predicted = np.zeros(len(probs), dtype=int)
   predicted[top_indices] = 1

   results = pd.DataFrame({
      "Name": names,
      "Predicted_prob": probs.round(2),
      "Predicted": predicted
   }).sort_values("Predicted_prob", ascending=False)

   print(f"\nPredictions for Patch {next_patch}")
   print(results.to_string(index=False))