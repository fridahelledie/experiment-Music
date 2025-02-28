import numpy as np
#import dtw-python as dtw
import matplotlib.pyplot as plt
from dtaidistance import dtw

# Create simple test signals
#signal_1 = np.linspace(0, 10, 100)  # Increasing sequence
signal_2 = np.sin(np.linspace(0, 10, 100))  # Sine wave
signal_3 = np.sin(np.linspace(0, 9, 100))  # Sine wave

# Convert to NumPy arrays (DTW library expects arrays)
a = np.array(signal_3)
b = np.array(signal_2)

#Initialization
t = 1 #step  in a
j = 1 #step in b
previous = None #stores the last movement direction

runCount = 1 #prevent excessive movement in the same direction
MaxRunCount = 1000 # Limit on how many consecutive movements in the same direction are allowed.
c = 10 #Warping constraint, defining the alignment window. (ADJUST)

# Placeholder function for path cost evaluation
def EvaluatePathCost(t, j,a,b):

    return dtw.distance(a[:t], b[:j])  # DTW distance up to current index



def GetInc(t, j,a,b): #determines the next movement direction, row, column or both
    if t < c: #Allows movement in both directions at the start (to find the best alignment).
        return "Both"

    if runCount > MaxRunCount: #If too many consecutive moves in one direction, force a switch.
        return "Column" if previous == "Row" else "Row"

    #Chooses the movement direction based on the minimum path cost. (TODO)
    path_costs = {
        (t, j - 1): EvaluatePathCost(t, j - 1,a,b),
        (t - 1, j): EvaluatePathCost(t - 1, j,a,b)
    }

    (x, y), _ = min(path_costs.items(), key=lambda item: item[1])  # Select minimum cost path

    #Determines whether the lowest-cost movement is in time (Row), column (Column), or both.
    if x < t:
        return "Row"
    elif y < j:
        return "Column"
    else:
        return "Both"


#main loop for real time warping

while True:  # Infinite loop; not sure how to handle this
    if GetInc(t, j,a,b) != "Column":
        t += 1  # Move forward in time
        for k in range(j - c + 1, j + 1):  # Evaluating path costs within constraint window
            if k > 0:
                EvaluatePathCost(t, k,a,b)

    if GetInc(t, j,a,b) != "Row":
        j += 1  # Move forward in sequence
        for k in range(t - c + 1, t + 1):  # Evaluating path costs within constraint window
            if k > 0:
                EvaluatePathCost(k, j,a,b)

    # If movement direction is the same, increase runCount. Otherwise, reset it.
    if GetInc(t, j,a,b) == previous:
        runCount += 1
    else:
        runCount = 1  # Reset run count if direction changes

    # Update previous if direction is not Both
    if GetInc(t, j,a,b) != "Both":
        previous = GetInc(t, j,a,b)

    # Break condition (to avoid infinite loop)
    if t > 10 or j > 10:  # Example stopping condition
        break

    print(f"Step: t={t}, j={j}, Direction: {GetInc(t, j, a, b)}")



# Plot signals
plt.figure(figsize=(10, 5))
plt.plot(signal_3, label="Signal 1 (Linear)")
plt.plot(signal_2, label="Signal 2 (Sine)")
plt.legend()
plt.title("Original Signals")
plt.show()

