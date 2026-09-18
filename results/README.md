# Results

The selected Decision Tree uses `max_depth=10` and `min_samples_leaf=10` for the held-out train/test experiment.

Recorded results from the final ML workspace:

- Held-out test accuracy: approximately **98.13%**
- 5-fold cross-validation mean accuracy: approximately **97.16%**
- Cross-validation standard deviation: approximately **0.70%**
- Tree depth: **10**
- Tree nodes: **193**
- Tree leaves: **97**

The most influential features in this experiment were `lin_acc_avg`, `lin_acc_var`, and `gyro_avg`.

The figures in `figures/` contain the confusion matrix and feature-importance visualization generated during the project.

## Important limitation

Offline accuracy was substantially better than some real-time behavior. Live validation exposed overlap between controlled motion classes and motivated deployment-side stabilization, including a stationary safeguard, majority voting, and state-change confirmation. This distinction is important when interpreting the results.
