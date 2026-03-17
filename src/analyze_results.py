# src/analyze_results.py

import pandas as pd  

# Load metrics file
df = pd.read_csv("results/metrics.csv")  

print("\n=== FINAL RESULTS ===\n")  
print(df)  # Show all results

print("\nBest Method:")  
# Select row with highest accuracy
print(df.loc[df["accuracy"].idxmax()])  