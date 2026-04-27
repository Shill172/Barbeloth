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

   df = df.sort_values(["Name", "Patch"]).copy()
   df = df.reset_index(drop=True)

   # Shift Time_since_ran forward by 1 within each chars history to prevent data leak
   df["Time_since_ran"] = df.groupby("Name")["Time_since_ran"].shift(1)

   # Chars first row now has no value for Time_since_ran, so fill it
   df["Time_since_ran"] = df["Time_since_ran"].fillna(999)

   # Same for total_runs 
   df["Total_runs"] = df.groupby("Name")["Total_runs"].shift(1).fillna(0)

   chronicle_names = df_original[df_original["Is_chronicle"] == 1]["Name"].unique()
   df = df[df["Total_runs"] > 0]

   df = df.drop(columns=["Name", "Is_chronicle"])

   df = pd.get_dummies(df, columns=["Element", "Weapon"])

   X = df.drop(columns="Ran")
   y = df["Ran"]

   return X, y, chronicle_names

def show_predictions_for_patch(df_original, model, X, y, chronicle_names, patch):
   # Get the rows for this patch from the original df (which still has Name)
   patch_mask = X["Patch"] == patch
   X_patch = X[patch_mask]
    
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

   results = pd.DataFrame({
     "Name": names.values,
     "Actual": actuals.values,
     "Predicted_prob": probs.round(2),
     "Predicted": (probs >= 0.4).astype(int)
   }).sort_values("Predicted_prob", ascending=False)

   print(f"\nPatch {patch} Predictions")
   print(results.to_string(index=False))


df = read_banner_history()
df_original = df.copy()

X, y, chronicle_names = prepare_features(df)

df_original = df_original.sort_values(["Name", "Patch"]).reset_index(drop=True)

split_patch = 6.3

X_train = X[X["Patch"] < split_patch]
y_train = y[X["Patch"] < split_patch]
X_test = X[X["Patch"] >= split_patch]
y_test = y[X["Patch"] >= split_patch]

print(f"Training rows: {len(X_train)}. Test rows: {len(X_test)}")

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))

show_predictions_for_patch(df_original, model, X, y, chronicle_names, patch=6.4)
