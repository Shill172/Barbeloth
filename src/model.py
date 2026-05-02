import pandas as pd # Basically excel for python 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np 
from dataprocessing import get_num_rerun_slots_per_patch, get_banner_runs

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

def get_rerun_slots_for_patch(patch):
   rerun_slots = get_num_rerun_slots_per_patch()

   match = rerun_slots[rerun_slots["Patch"] == patch]

   return int(match.iloc[0]["Rerun_slots"])

# Will update in the future to get the no of reruns that a patch ha
def longest_time_is_rerun(): 
   df = read_banner_history() 

   chronicle_entries = df[df["Is_chronicle"] == 1]
   first_chronicle_patch = chronicle_entries.groupby("Name")["Patch"].min()
   df["Cutoff_Patch"] = df["Name"].map(first_chronicle_patch).fillna(float("inf"))
   df = df[df["Patch"] < df["Cutoff_Patch"]].copy()

   rerun_slots = get_num_rerun_slots_per_patch()
   
   all_patches = sorted(df["Patch"].unique())
   
   results = []

   for _, row in rerun_slots.iterrows(): 
      current_patch = row["Patch"]
      n = int(row["Rerun_slots"])

      if n == 0:
         continue

      # Find the index of the current patch so we can tell how time they have waited
      # When they actually run
      try:
         current_idx = all_patches.index(current_patch)
         if current_idx == 0: continue 
         previous_patch = all_patches[current_idx - 1]
      except ValueError:
         continue

      prediction_pool = df[df["Patch"] == previous_patch].copy()

      # Dont want debuts 
      prediction_pool = prediction_pool[prediction_pool["Total_runs"] >= 1]

      # Pick n (num of rerun slots for that patch) top wait times
      top = prediction_pool.nlargest(n, "Time_since_ran").copy()
      top["Patch"] = current_patch 
      
      results.append(top[["Patch", "Name", "Time_since_ran"]])

   if not results:
      return pd.DataFrame()

   final = pd.concat(results).reset_index(drop=True)
   
   final.to_csv("resources/longest_waiting_time_will_run_predictions.csv", index=False)
   
   return final

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


def predict_n_patches(df_original, X, y, chronicle_names, start_patch):
   all_patches = sorted(X["Patch"].unique())

   patches_to_predict = []

   for p in all_patches:
      if p >= start_patch:
         patches_to_predict.append(p)

   results = []

   for patch in patches_to_predict: 
      train_mask = X["Patch"] < patch 
      test_mask = X["Patch"] == patch

      if train_mask.sum() == 0 or test_mask.sum() == 0:
         continue

      X_train = X[train_mask].drop(columns=["Patch"])
      y_train = y[train_mask]

      X_patch = X[test_mask]
      y_patch = y[test_mask]

      model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")

      model.fit(X_train, y_train)

      predicted = show_predictions_for_patch(
         df_original,
         model, 
         X_patch, 
         y_patch,
         chronicle_names,
         patch
      )

      results.append(predicted)

   final = pd.concat(results).reset_index(drop=True)

   final.to_csv("resources/model_predictions.csv", index=False)

   return final


def calculate_prediction_accuracy(predicted_df, actual_df, min_patch):
   # Data types must match
   predicted_df["Patch"] = predicted_df["Patch"].astype(float)
   actual_df["Patch"] = actual_df["Patch"].astype(float)

   filtered_predictions = predicted_df[predicted_df["Patch"] >= min_patch].copy()

   if filtered_predictions.empty:
      print(f"No predictions found after patch {min_patch}.")
      return 0.0

   # Intersection to find where columns match (correct prediction)
   correct_predictions = pd.merge(
      filtered_predictions, 
      actual_df[["Name", "Patch"]], 
      on=["Name", "Patch"], 
      how="inner"
   )

   if not correct_predictions.empty:
      print(f"Correct predictions for patch: {min_patch}+:")
      print(correct_predictions.sort_values("Patch").to_string(index=False))
   else:
      print(f"No correct predictions found after patch {min_patch}")

   accuracy = (len(correct_predictions) / len(filtered_predictions)) * 100
   
   print(f"\nTotal Predicted: {len(filtered_predictions)}")
   print(f"Correct Hits: {len(correct_predictions)}")
   print(f"Accuracy: {accuracy:.2f}%")
   
   return accuracy

# predicted_df = longest_time_is_rerun()
# actual_df = get_banner_runs()
# calculate_prediction_accuracy(predicted_df, actual_df, min_patch=6.0)


df = read_banner_history()
df_original = df.copy()

X, y, chronicle_names = prepare_features(df)

df_original = df_original.sort_values(["Name", "Patch"]).reset_index(drop=True)

predicted_df = predict_n_patches(
   df_original,
   X,
   y,
   chronicle_names,
   start_patch=5.8
)

actual_df = get_banner_runs()
calculate_prediction_accuracy(predicted_df, actual_df, min_patch=5.8)


print(predicted_df[predicted_df["Patch"] == 6.0].to_string(index=False))

# split_patch = 6.0

# X_train = X[X["Patch"] < split_patch].drop(columns=["Patch"])
# y_train = y[X["Patch"] < split_patch]
# X_test = X[X["Patch"] >= split_patch].drop(columns=["Patch"])
# y_test = y[X["Patch"] >= split_patch]

# print(f"Training rows: {len(X_train)}. Test rows: {len(X_test)}")

# model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
# model.fit(X_train, y_train)

# y_pred = model.predict(X_test)

# print(classification_report(y_test, y_pred))

# show_predictions_for_patch(df_original, model, X, y, chronicle_names, patch=6.5)