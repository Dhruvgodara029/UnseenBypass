import pandas as pd

df = pd.read_csv("braess_dataset.csv")
print("Shape:", df.shape)
print("\nClass balance:")
print(df["is_braess_road"].value_counts())

# Do the feature columns actually differ between Braess and non-Braess?
feature_cols = ["mid_length_m", "mid_speed_mps", "fast_length_m",
                "slow_length_m", "slow_speed_mps", "demand",
                "free_flow_mid_time_s", "length_ratio"]
print("\nMean feature values by class (0 = not Braess, 1 = Braess):")
print(df.groupby("is_braess_road")[feature_cols].mean().round(2).T)