import numpy as np
import matplotlib.pyplot as plt
from dtaidistance import dtw

# Create signals
signal_2 = np.sin(np.linspace(0, 10, 80))  # Shorter sine wave
signal_3 = np.sin(np.linspace(0, 10, 100))  # Longer sine wave

# Convert to NumPy arrays
a = np.array(signal_3)  # 100 points
b = np.array(signal_2)  # 80 points

# Initialize cost matrix (DTW uses a (len(a) x len(b)) grid)
cost_matrix = np.full((len(a), len(b)), np.inf)  # Fill with large values

# Function to evaluate DTW cost and store in matrix
def EvaluatePathCost(t, j, a, b):
    if t < len(a) and j < len(b):  # Ensure indices are valid
        cost = dtw.distance(a[:t+1], b[:j+1])  # Compute DTW distance up to (t, j)
        cost_matrix[t, j] = cost  # Store in matrix
        return cost
    return np.inf  # Return high cost for out-of-bounds cases

# Run DTW and populate cost matrix
for t in range(len(a)):
    for j in range(len(b)):
        EvaluatePathCost(t, j, a, b)

# Print the final cost matrix
print("DTW Cost Matrix:")
print(cost_matrix)

# Visualize the cost matrix
plt.figure(figsize=(10, 6))
plt.imshow(cost_matrix, aspect='auto', cmap='viridis', origin='lower')
plt.colorbar(label="DTW Cost")
plt.xlabel("Index of Signal 2 (80 points)")
plt.ylabel("Index of Signal 3 (100 points)")
plt.title("DTW Cost Matrix")
plt.show()
