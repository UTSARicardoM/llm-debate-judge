# src\plot_results.py

import pandas as pd
import matplotlib.pyplot as plt

# ================================
# Create results dataframe
# ================================
data = {
    "method": ["Debate + Judge", "Direct QA", "Self-Consistency"],
    "accuracy": [0.65, 0.44, 0.49],
}

df = pd.DataFrame(data)

# ================================
# Plot bar chart
# ================================
plt.figure()

plt.bar(df["method"], df["accuracy"])

plt.title("Model Performance Comparison")
plt.xlabel("Method")
plt.ylabel("Accuracy")

plt.xticks(rotation=15)

plt.tight_layout()

# Save figure
plt.savefig("results/figures/performance_comparison.png")

# Show plot
plt.show()