# Scikit-learn Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Classification](#classification)
4. [Regression](#regression)
5. [Clustering](#clustering)
6. [Dimensionality Reduction](#dimensionality-reduction)
7. [Model Selection & Validation](#model-selection--validation)
8. [Preprocessing](#preprocessing)
9. [Feature Engineering](#feature-engineering)
10. [Ensemble Methods](#ensemble-methods)
11. [Neural Networks](#neural-networks)
12. [Semi-Supervised Learning](#semi-supervised-learning)
13. [Outlier Detection](#outlier-detection)
14. [Multiclass & Multioutput](#multiclass--multioutput)
15. [Calibration](#calibration)
16. [Pipelines](#pipelines)
17. [Metrics](#metrics)
18. [Cross-Validation](#cross-validation)
19. [Datasets](#datasets)
20. [Best Practices](#best-practices)

## Introduction

Scikit-learn is a powerful machine learning library for Python that provides simple and efficient tools for data analysis and modeling. It features various classification, regression, and clustering algorithms, and is designed to interoperate with NumPy and pandas.

### Core Principles
- **Consistent API**: All estimators share a consistent interface
- **Composition**: Complex pipelines from simple building blocks
- **Sensible defaults**: Good default values for all parameters
- **Inspection**: All parameter values are exposed as public attributes
- **Documentation**: Comprehensive documentation and examples

## Installation

### Basic Installation
```bash
# Using pip
pip install scikit-learn

# Using conda
conda install scikit-learn

# Install with all optional dependencies
pip install scikit-learn[all]

# Development version
pip install --pre scikit-learn
```

### Verify Installation
```python
import sklearn
print(sklearn.__version__)

# Check available estimators
from sklearn.utils import all_estimators
estimators = all_estimators()
print(f"Total estimators: {len(estimators)}")
```

## Classification

### Logistic Regression
```python
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train classifier
clf = LogisticRegression(
    penalty='l2',           # Regularization type
    C=1.0,                  # Inverse regularization strength
    solver='lbfgs',         # Optimization algorithm
    max_iter=100,           # Maximum iterations
    multi_class='auto',     # Multiclass strategy
    random_state=42
)
clf.fit(X_train, y_train)

# Predict
y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f}")
print(classification_report(y_test, y_pred))
```

### Support Vector Machines
```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Create pipeline with scaling
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(
        kernel='rbf',           # Kernel type
        C=1.0,                  # Regularization parameter
        gamma='scale',          # Kernel coefficient
        probability=True,       # Enable probability estimates
        random_state=42
    ))
])

# Train and predict
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

# Decision function and support vectors
decision_values = pipe.named_steps['svm'].decision_function(X_test)
n_support = pipe.named_steps['svm'].n_support_
print(f"Support vectors per class: {n_support}")
```

### Random Forest Classifier
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, roc_auc_score
import numpy as np

# Create and train classifier
rf_clf = RandomForestClassifier(
    n_estimators=100,           # Number of trees
    max_depth=None,             # Maximum tree depth
    min_samples_split=2,        # Min samples to split node
    min_samples_leaf=1,         # Min samples in leaf
    max_features='sqrt',        # Features to consider for split
    bootstrap=True,             # Bootstrap samples
    oob_score=True,             # Out-of-bag score
    n_jobs=-1,                  # Parallel jobs
    random_state=42
)
rf_clf.fit(X_train, y_train)

# Feature importance
importances = rf_clf.feature_importances_
indices = np.argsort(importances)[::-1]
print("Feature ranking:")
for i in range(X.shape[1]):
    print(f"{i+1}. Feature {indices[i]}: {importances[indices[i]]:.3f}")

# OOB Score
if rf_clf.oob_score:
    print(f"OOB Score: {rf_clf.oob_score_:.3f}")
```

### Gradient Boosting Classifier
```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

# Create classifier
gb_clf = GradientBoostingClassifier(
    n_estimators=100,           # Number of boosting stages
    learning_rate=0.1,          # Shrinks contribution of each tree
    max_depth=3,                # Maximum tree depth
    subsample=1.0,              # Fraction of samples for training
    criterion='friedman_mse',   # Split quality measure
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42
)

# Train with early stopping
from sklearn.model_selection import validation_curve

# Get validation scores for different n_estimators
param_range = [10, 50, 100, 200, 500]
train_scores, val_scores = validation_curve(
    gb_clf, X_train, y_train, 
    param_name="n_estimators", 
    param_range=param_range,
    cv=5, scoring="accuracy"
)

# Feature importance by gain
gb_clf.fit(X_train, y_train)
feature_importance = gb_clf.feature_importances_

# Staged predictions for understanding boosting
staged_accuracy = []
for pred in gb_clf.staged_predict(X_test):
    staged_accuracy.append(accuracy_score(y_test, pred))
```

### K-Nearest Neighbors
```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV

# Create KNN classifier
knn = KNeighborsClassifier(
    n_neighbors=5,              # Number of neighbors
    weights='uniform',          # Weight function ('uniform' or 'distance')
    algorithm='auto',           # Algorithm for neighbor search
    metric='minkowski',         # Distance metric
    p=2                        # Power parameter for Minkowski
)

# Grid search for optimal parameters
param_grid = {
    'n_neighbors': [3, 5, 7, 9],
    'weights': ['uniform', 'distance'],
    'metric': ['euclidean', 'manhattan', 'minkowski']
}

grid_search = GridSearchCV(
    knn, param_grid, 
    cv=5, 
    scoring='accuracy',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")
```

## Regression

### Linear Regression
```python
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.metrics import mean_squared_error, r2_score

# Generate regression data
X, y = make_regression(n_samples=100, n_features=10, noise=0.1, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train model
lr = LinearRegression(
    fit_intercept=True,         # Calculate intercept
    copy_X=True,               # Copy X in fit
    n_jobs=None                # Number of jobs for parallelism
)
lr.fit(X_train, y_train)

# Predictions
y_pred = lr.predict(X_test)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"MSE: {mse:.3f}")
print(f"R²: {r2:.3f}")

# Coefficients
print(f"Coefficients: {lr.coef_}")
print(f"Intercept: {lr.intercept_}")
```

### Ridge Regression
```python
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import PolynomialFeatures

# Ridge regression with cross-validation
alphas = np.logspace(-4, 4, 50)
ridge_cv = RidgeCV(
    alphas=alphas,              # Array of alpha values
    fit_intercept=True,
    scoring=None,               # Use efficient Leave-One-Out CV
    cv=None,                    # Use efficient Leave-One-Out CV
    store_cv_values=True
)
ridge_cv.fit(X_train, y_train)
print(f"Best alpha: {ridge_cv.alpha_}")

# Polynomial features with Ridge
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

ridge_poly = Ridge(alpha=ridge_cv.alpha_)
ridge_poly.fit(X_poly, y_train)
y_pred_poly = ridge_poly.predict(X_test_poly)
```

### Lasso Regression
```python
from sklearn.linear_model import Lasso, LassoCV
from sklearn.linear_model import ElasticNet

# Lasso with cross-validation
lasso_cv = LassoCV(
    alphas=None,                # Auto-generate alphas
    cv=5,                       # Cross-validation folds
    max_iter=1000,
    random_state=42
)
lasso_cv.fit(X_train, y_train)

# Check sparsity (zero coefficients)
n_zeros = np.sum(lasso_cv.coef_ == 0)
print(f"Number of zero coefficients: {n_zeros}/{len(lasso_cv.coef_)}")

# Elastic Net (combines L1 and L2)
elastic_net = ElasticNet(
    alpha=1.0,                  # Constant that multiplies penalty
    l1_ratio=0.5,              # L1 vs L2 balance (0=Ridge, 1=Lasso)
    max_iter=1000,
    random_state=42
)
elastic_net.fit(X_train, y_train)
```

### Support Vector Regression
```python
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

# Scale features (important for SVR)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create SVR models
svr_rbf = SVR(kernel='rbf', C=100, gamma='scale', epsilon=0.1)
svr_linear = SVR(kernel='linear', C=100)
svr_poly = SVR(kernel='poly', C=100, degree=3, gamma='scale')

# Train and compare
models = {'RBF': svr_rbf, 'Linear': svr_linear, 'Poly': svr_poly}
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    score = model.score(X_test_scaled, y_test)
    print(f"{name} SVR R²: {score:.3f}")
```

### Random Forest Regressor
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Create regressor
rf_reg = RandomForestRegressor(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features=1.0,           # Can be int, float, 'sqrt', 'log2'
    bootstrap=True,
    oob_score=True,
    n_jobs=-1,
    random_state=42
)

# Train
rf_reg.fit(X_train, y_train)

# Predictions with uncertainty estimation
y_pred = rf_reg.predict(X_test)

# Get predictions from each tree for uncertainty
predictions = np.array([tree.predict(X_test) for tree in rf_reg.estimators_])
mean_pred = predictions.mean(axis=0)
std_pred = predictions.std(axis=0)

print(f"Mean absolute error: {mean_absolute_error(y_test, y_pred):.3f}")
print(f"Average prediction std: {std_pred.mean():.3f}")
```

## Clustering

### K-Means Clustering
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler

# Generate clustering data
from sklearn.datasets import make_blobs
X, y_true = make_blobs(n_samples=300, centers=4, n_features=2, random_state=42)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means clustering
kmeans = KMeans(
    n_clusters=4,               # Number of clusters
    init='k-means++',           # Initialization method
    n_init=10,                  # Number of different initializations
    max_iter=300,               # Maximum iterations
    tol=1e-4,                   # Convergence tolerance
    algorithm='lloyd',          # Algorithm variant
    random_state=42
)
kmeans.fit(X_scaled)

# Evaluation metrics
labels = kmeans.labels_
silhouette = silhouette_score(X_scaled, labels)
calinski = calinski_harabasz_score(X_scaled, labels)

print(f"Silhouette Score: {silhouette:.3f}")
print(f"Calinski-Harabasz Score: {calinski:.3f}")
print(f"Inertia: {kmeans.inertia_:.3f}")

# Elbow method for optimal k
inertias = []
silhouettes = []
K_range = range(2, 10)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, km.labels_))
```

### DBSCAN Clustering
```python
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import numpy as np

# Determine optimal epsilon using k-distance graph
neighbors = NearestNeighbors(n_neighbors=4)
neighbors_fit = neighbors.fit(X_scaled)
distances, indices = neighbors_fit.kneighbors(X_scaled)
distances = np.sort(distances[:, 3], axis=0)

# DBSCAN clustering
dbscan = DBSCAN(
    eps=0.3,                    # Maximum distance between samples
    min_samples=5,              # Minimum samples in neighborhood
    metric='euclidean',         # Distance metric
    algorithm='auto',           # Algorithm for nearest neighbors
    leaf_size=30,              # Leaf size for tree algorithms
    n_jobs=-1
)
clusters = dbscan.fit_predict(X_scaled)

# Analyze results
n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
n_noise = list(clusters).count(-1)

print(f"Number of clusters: {n_clusters}")
print(f"Number of noise points: {n_noise}")
```

### Hierarchical Clustering
```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# Agglomerative clustering
agg_clustering = AgglomerativeClustering(
    n_clusters=None,            # Number of clusters
    distance_threshold=10,      # Threshold to stop merging
    metric='euclidean',         # Distance metric
    linkage='ward',            # Linkage criterion
    compute_full_tree=True
)
clusters = agg_clustering.fit_predict(X_scaled)

# Create dendrogram
linkage_matrix = linkage(X_scaled, method='ward')
dendrogram(linkage_matrix, truncate_mode='level', p=3)
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Sample index')
plt.ylabel('Distance')
```

### Gaussian Mixture Models
```python
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV

# Gaussian Mixture Model
gmm = GaussianMixture(
    n_components=4,             # Number of components
    covariance_type='full',     # Type of covariance matrix
    tol=1e-3,                  # Convergence threshold
    max_iter=100,              # Maximum iterations
    n_init=1,                  # Number of initializations
    init_params='kmeans',       # Initialization method
    random_state=42
)
gmm.fit(X_scaled)

# Predict probabilities
proba = gmm.predict_proba(X_scaled)
labels = gmm.predict(X_scaled)

# Model selection using BIC
n_components_range = range(1, 10)
bic_scores = []
aic_scores = []

for n in n_components_range:
    gmm_temp = GaussianMixture(n_components=n, random_state=42)
    gmm_temp.fit(X_scaled)
    bic_scores.append(gmm_temp.bic(X_scaled))
    aic_scores.append(gmm_temp.aic(X_scaled))

optimal_n = n_components_range[np.argmin(bic_scores)]
print(f"Optimal number of components (BIC): {optimal_n}")
```

## Dimensionality Reduction

### Principal Component Analysis (PCA)
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA
pca = PCA(
    n_components=None,          # Number of components (None keeps all)
    whiten=False,              # Whiten components
    svd_solver='auto',         # SVD solver
    random_state=42
)
pca.fit(X_scaled)

# Explained variance
explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance_ratio)

# Find number of components for 95% variance
n_components_95 = np.argmax(cumulative_variance >= 0.95) + 1
print(f"Components for 95% variance: {n_components_95}")

# Transform data
pca_95 = PCA(n_components=n_components_95)
X_pca = pca_95.fit_transform(X_scaled)

# Inverse transform (reconstruction)
X_reconstructed = pca_95.inverse_transform(X_pca)
reconstruction_error = np.mean((X_scaled - X_reconstructed) ** 2)
print(f"Reconstruction error: {reconstruction_error:.6f}")
```

### Truncated SVD
```python
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

# For text data (LSA - Latent Semantic Analysis)
documents = [
    "Machine learning is great",
    "Natural language processing is fun",
    "Deep learning requires data"
]

# Create TF-IDF matrix
vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(documents)

# Apply Truncated SVD
svd = TruncatedSVD(
    n_components=2,            # Number of components
    algorithm='randomized',    # Algorithm ('arpack' or 'randomized')
    n_iter=5,                 # Number of iterations for randomized
    n_oversamples=10,         # Oversampling for randomized
    random_state=42
)
X_lsa = svd.fit_transform(X_tfidf)

# Explained variance
print(f"Explained variance ratio: {svd.explained_variance_ratio_}")
```

### t-SNE
```python
from sklearn.manifold import TSNE

# t-SNE for visualization
tsne = TSNE(
    n_components=2,            # Output dimensions
    perplexity=30.0,          # Balance between local and global
    early_exaggeration=12.0,   # Controls cluster spacing
    learning_rate='auto',      # Learning rate
    n_iter=1000,              # Maximum iterations
    metric='euclidean',        # Distance metric
    init='pca',               # Initialization method
    method='barnes_hut',       # Algorithm ('barnes_hut' or 'exact')
    random_state=42
)

# Fit and transform
X_tsne = tsne.fit_transform(X_scaled)

# Note: t-SNE has no transform method, only fit_transform
# For new data, you need to refit entirely
```

### Isomap
```python
from sklearn.manifold import Isomap

# Isomap for non-linear dimensionality reduction
isomap = Isomap(
    n_neighbors=5,             # Number of neighbors
    n_components=2,            # Output dimensions
    eigen_solver='auto',       # Eigenvalue solver
    tol=0,                    # Convergence tolerance
    max_iter=None,            # Maximum iterations
    path_method='auto',        # Path finding algorithm
    neighbors_algorithm='auto', # Nearest neighbors algorithm
    metric='minkowski',        # Distance metric
    n_jobs=-1
)

# Fit and transform
X_isomap = isomap.fit_transform(X_scaled)

# Reconstruction error
reconstruction_error = isomap.reconstruction_error()
print(f"Reconstruction error: {reconstruction_error:.3f}")
```

### Locally Linear Embedding (LLE)
```python
from sklearn.manifold import LocallyLinearEmbedding

# Standard LLE
lle = LocallyLinearEmbedding(
    n_neighbors=10,            # Number of neighbors
    n_components=2,            # Output dimensions
    reg=1e-3,                 # Regularization constant
    eigen_solver='auto',       # Eigenvalue solver
    tol=1e-6,                 # Tolerance for solver
    max_iter=100,             # Maximum iterations
    method='standard',         # LLE variant
    hessian_tol=1e-4,         # For HLLE method
    modified_tol=1e-12,       # For MLLE method
    random_state=42,
    n_jobs=-1
)

X_lle = lle.fit_transform(X_scaled)

# Modified LLE (more stable)
mlle = LocallyLinearEmbedding(
    n_neighbors=12,            # Must be > n_components
    n_components=2,
    method='modified',
    random_state=42
)
X_mlle = mlle.fit_transform(X_scaled)
```

### Kernel PCA
```python
from sklearn.decomposition import KernelPCA

# Kernel PCA for non-linear reduction
kernel_pca = KernelPCA(
    n_components=2,            # Number of components
    kernel='rbf',              # Kernel type
    gamma=10,                  # Kernel coefficient
    degree=3,                  # Degree for poly kernel
    coef0=1,                   # Independent term
    fit_inverse_transform=True, # Learn inverse transform
    eigen_solver='auto',       # Eigenvalue solver
    alpha=1.0,                # Hyperparameter for ridge
    random_state=42,
    n_jobs=-1
)

# Fit and transform
X_kpca = kernel_pca.fit_transform(X_scaled)

# Inverse transform (approximation)
X_back = kernel_pca.inverse_transform(X_kpca)
```

## Model Selection & Validation

### Cross-Validation
```python
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.model_selection import KFold, StratifiedKFold, TimeSeriesSplit

# Basic cross-validation
model = LogisticRegression(random_state=42)
scores = cross_val_score(
    model, X, y,
    cv=5,                      # Number of folds
    scoring='accuracy',        # Scoring metric
    n_jobs=-1
)
print(f"CV Accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")

# Multiple metrics
scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
scores = cross_validate(
    model, X, y,
    cv=5,
    scoring=scoring,
    return_train_score=True,
    return_estimator=False,
    n_jobs=-1
)

for metric in scoring:
    test_score = scores[f'test_{metric}'].mean()
    train_score = scores[f'train_{metric}'].mean()
    print(f"{metric}: Train={train_score:.3f}, Test={test_score:.3f}")

# Custom CV splitters
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
stratified_kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
ts_split = TimeSeriesSplit(n_splits=5)

# Cross-validation with custom splitter
for train_idx, val_idx in stratified_kfold.split(X, y):
    X_train_cv, X_val_cv = X[train_idx], X[val_idx]
    y_train_cv, y_val_cv = y[train_idx], y[val_idx]
    # Train and validate model
```

### Grid Search
```python
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

# Define parameter grid
param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': ['scale', 'auto', 0.001, 0.01],
    'kernel': ['rbf', 'poly', 'sigmoid']
}

# Grid search
grid_search = GridSearchCV(
    estimator=SVC(),
    param_grid=param_grid,
    scoring='accuracy',        # Scoring metric
    n_jobs=-1,                # Parallel jobs
    cv=5,                     # Cross-validation folds
    verbose=1,                # Verbosity level
    refit=True,               # Refit on best params
    return_train_score=True
)

grid_search.fit(X_train, y_train)

# Best parameters and score
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV score: {grid_search.best_score_:.3f}")
print(f"Test score: {grid_search.score(X_test, y_test):.3f}")

# Access results
results = grid_search.cv_results_
best_index = grid_search.best_index_
```

### Random Search
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

# Define parameter distributions
param_dist = {
    'C': uniform(0.1, 100),           # Continuous distribution
    'gamma': uniform(0.001, 0.1),
    'kernel': ['rbf', 'poly'],
    'degree': randint(2, 5)           # Discrete distribution
}

# Random search
random_search = RandomizedSearchCV(
    estimator=SVC(),
    param_distributions=param_dist,
    n_iter=100,               # Number of parameter settings sampled
    scoring='accuracy',
    cv=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

random_search.fit(X_train, y_train)
print(f"Best parameters: {random_search.best_params_}")
```

### Bayesian Optimization
```python
# Using scikit-optimize (install: pip install scikit-optimize)
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer

# Define search space
search_spaces = {
    'C': Real(0.1, 100, prior='log-uniform'),
    'gamma': Real(0.001, 0.1, prior='log-uniform'),
    'degree': Integer(2, 5),
    'kernel': Categorical(['rbf', 'poly'])
}

# Bayesian optimization
bayes_search = BayesSearchCV(
    estimator=SVC(),
    search_spaces=search_spaces,
    n_iter=50,
    cv=5,
    n_jobs=-1,
    random_state=42
)

bayes_search.fit(X_train, y_train)
```

### Learning Curves
```python
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt

# Generate learning curves
train_sizes, train_scores, val_scores = learning_curve(
    estimator=LogisticRegression(),
    X=X, y=y,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    shuffle=True,
    random_state=42
)

# Plot learning curves
train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
val_mean = np.mean(val_scores, axis=1)
val_std = np.std(val_scores, axis=1)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, label='Training score')
plt.plot(train_sizes, val_mean, label='Validation score')
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1)
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1)
plt.xlabel('Training Set Size')
plt.ylabel('Accuracy Score')
plt.legend()
plt.title('Learning Curves')
```

### Validation Curves
```python
from sklearn.model_selection import validation_curve

# Generate validation curves
param_range = np.logspace(-3, 3, 7)
train_scores, val_scores = validation_curve(
    estimator=SVC(),
    X=X, y=y,
    param_name='C',
    param_range=param_range,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

# Plot validation curves
train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
val_mean = np.mean(val_scores, axis=1)
val_std = np.std(val_scores, axis=1)

plt.figure(figsize=(10, 6))
plt.semilogx(param_range, train_mean, label='Training score')
plt.semilogx(param_range, val_mean, label='Validation score')
plt.fill_between(param_range, train_mean - train_std, train_mean + train_std, alpha=0.1)
plt.fill_between(param_range, val_mean - val_std, val_mean + val_std, alpha=0.1)
plt.xlabel('Parameter C')
plt.ylabel('Accuracy Score')
plt.legend()
plt.title('Validation Curves')
```

## Preprocessing

### Scaling and Normalization
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import Normalizer, MaxAbsScaler

# Standard Scaling (z-score normalization)
scaler = StandardScaler(
    with_mean=True,            # Center to mean
    with_std=True              # Scale to unit variance
)
X_standard = scaler.fit_transform(X)

# Min-Max Scaling
minmax = MinMaxScaler(
    feature_range=(0, 1)       # Output range
)
X_minmax = minmax.fit_transform(X)

# Robust Scaling (using median and IQR)
robust = RobustScaler(
    quantile_range=(25.0, 75.0), # IQR range
    with_centering=True,
    with_scaling=True
)
X_robust = robust.fit_transform(X)

# L2 Normalization (unit norm)
normalizer = Normalizer(
    norm='l2'                  # 'l1', 'l2', or 'max'
)
X_normalized = normalizer.fit_transform(X)

# Max Abs Scaling (preserves sparsity)
maxabs = MaxAbsScaler()
X_maxabs = maxabs.fit_transform(X)
```

### Encoding Categorical Variables
```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder
from sklearn.preprocessing import LabelBinarizer
import pandas as pd

# Sample data
data = pd.DataFrame({
    'color': ['red', 'blue', 'green', 'red'],
    'size': ['S', 'M', 'L', 'M'],
    'quality': ['good', 'bad', 'good', 'excellent']
})

# Label Encoding (for target variable)
le = LabelEncoder()
y_encoded = le.fit_transform(data['color'])
print(f"Classes: {le.classes_}")
y_decoded = le.inverse_transform(y_encoded)

# One-Hot Encoding
onehot = OneHotEncoder(
    drop='first',              # Drop first column to avoid multicollinearity
    sparse_output=False,       # Return dense array
    handle_unknown='ignore'    # Handle unknown categories
)
X_onehot = onehot.fit_transform(data[['color', 'size']])
feature_names = onehot.get_feature_names_out(['color', 'size'])

# Ordinal Encoding (for ordered categories)
ordinal = OrdinalEncoder(
    categories=[['bad', 'good', 'excellent']], # Order matters
    handle_unknown='use_encoded_value',
    unknown_value=-1
)
quality_encoded = ordinal.fit_transform(data[['quality']])

# Label Binarizer (for multi-class to binary)
lb = LabelBinarizer()
y_binary = lb.fit_transform(data['color'])
```

### Handling Missing Values
```python
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer
from sklearn.experimental import enable_iterative_imputer
import numpy as np

# Create data with missing values
X_missing = X.copy()
missing_mask = np.random.random(X_missing.shape) < 0.1
X_missing[missing_mask] = np.nan

# Simple Imputation
simple_imputer = SimpleImputer(
    strategy='mean',           # 'mean', 'median', 'most_frequent', 'constant'
    fill_value=0,             # For strategy='constant'
    keep_empty_features=False
)
X_simple = simple_imputer.fit_transform(X_missing)

# KNN Imputation
knn_imputer = KNNImputer(
    n_neighbors=5,
    weights='uniform',         # 'uniform' or 'distance'
    metric='nan_euclidean'
)
X_knn = knn_imputer.fit_transform(X_missing)

# Iterative Imputation (MICE)
iterative_imputer = IterativeImputer(
    estimator=None,            # Default uses BayesianRidge
    max_iter=10,
    random_state=42
)
X_iterative = iterative_imputer.fit_transform(X_missing)

# Indicator for missingness
from sklearn.impute import MissingIndicator
indicator = MissingIndicator(
    features='all',            # 'missing-only' or 'all'
    sparse=False
)
missing_mask = indicator.fit_transform(X_missing)
```

### Feature Transformation
```python
from sklearn.preprocessing import PowerTransformer, QuantileTransformer
from sklearn.preprocessing import FunctionTransformer

# Power Transform (Yeo-Johnson or Box-Cox)
power = PowerTransformer(
    method='yeo-johnson',      # 'yeo-johnson' or 'box-cox'
    standardize=True          # Apply zero-mean, unit-variance
)
X_power = power.fit_transform(X)

# Quantile Transform (uniform or normal output)
quantile = QuantileTransformer(
    n_quantiles=1000,
    output_distribution='uniform', # 'uniform' or 'normal'
    subsample=100000,
    random_state=42
)
X_quantile = quantile.fit_transform(X)

# Custom Function Transform
def log_transform(X):
    return np.log1p(np.abs(X))

custom = FunctionTransformer(
    func=log_transform,
    inverse_func=np.expm1,
    validate=True
)
X_custom = custom.fit_transform(X)

# Polynomial Features
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(
    degree=2,                  # Polynomial degree
    interaction_only=False,    # Only interaction features
    include_bias=True         # Include bias column
)
X_poly = poly.fit_transform(X)
```

### Discretization
```python
from sklearn.preprocessing import KBinsDiscretizer, Binarizer

# K-Bins Discretization
discretizer = KBinsDiscretizer(
    n_bins=5,                  # Number of bins
    encode='onehot',          # 'onehot', 'ordinal', or 'onehot-dense'
    strategy='quantile',       # 'uniform', 'quantile', or 'kmeans'
    subsample=None
)
X_discrete = discretizer.fit_transform(X)

# Binarization
binarizer = Binarizer(
    threshold=0.0             # Threshold for binarization
)
X_binary = binarizer.fit_transform(X)
```

## Feature Engineering

### Feature Selection
```python
from sklearn.feature_selection import SelectKBest, SelectPercentile
from sklearn.feature_selection import chi2, f_classif, mutual_info_classif
from sklearn.feature_selection import RFE, RFECV
from sklearn.feature_selection import SelectFromModel

# Univariate Feature Selection
selector = SelectKBest(
    score_func=f_classif,      # Scoring function
    k=10                       # Number of features to select
)
X_selected = selector.fit_transform(X, y)
scores = selector.scores_
selected_features = selector.get_support(indices=True)

# Recursive Feature Elimination
from sklearn.linear_model import LogisticRegression
estimator = LogisticRegression()
rfe = RFE(
    estimator=estimator,
    n_features_to_select=5,    # Number of features
    step=1                     # Features to remove at each iteration
)
X_rfe = rfe.fit_transform(X, y)
ranking = rfe.ranking_

# RFE with Cross-Validation
rfecv = RFECV(
    estimator=estimator,
    step=1,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
X_rfecv = rfecv.fit_transform(X, y)
optimal_features = rfecv.n_features_

# Select from Model (L1-based)
from sklearn.linear_model import LassoCV
lasso = LassoCV(cv=5)
selector_model = SelectFromModel(
    estimator=lasso,
    threshold='median'         # Threshold for selection
)
selector_model.fit(X, y)
X_model = selector_model.transform(X)
```

### Feature Extraction
```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer, FeatureHasher

# Text Feature Extraction - Count Vectorizer
count_vec = CountVectorizer(
    max_features=1000,         # Maximum features
    ngram_range=(1, 2),       # N-gram range
    stop_words='english',      # Stop words
    min_df=2,                 # Minimum document frequency
    max_df=0.95,              # Maximum document frequency
    binary=False              # Binary features
)
documents = ["Text processing example", "Another text document"]
X_counts = count_vec.fit_transform(documents)

# TF-IDF Vectorizer
tfidf_vec = TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 3),
    sublinear_tf=True,        # Sublinear TF scaling
    use_idf=True,             # Use IDF
    smooth_idf=True,          # Smooth IDF weights
    norm='l2'                 # Normalize vectors
)
X_tfidf = tfidf_vec.fit_transform(documents)

# Dict Vectorizer (for dict features)
dict_data = [
    {'feature1': 1, 'feature2': 2},
    {'feature1': 3, 'feature3': 1}
]
dict_vec = DictVectorizer(sparse=False)
X_dict = dict_vec.fit_transform(dict_data)

# Feature Hasher (for high-dimensional sparse data)
hasher = FeatureHasher(
    n_features=1024,          # Number of features
    input_type='string',      # Input type
    alternate_sign=True       # Alternate sign to preserve expectation
)
X_hashed = hasher.transform(documents)
```

### Feature Union
```python
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Combine multiple feature extraction methods
combined_features = FeatureUnion([
    ('pca', PCA(n_components=2)),
    ('univ_select', SelectKBest(k=1))
])

# Fit and transform
X_combined = combined_features.fit_transform(X, y)

# With preprocessing
from sklearn.pipeline import Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('features', combined_features),
    ('classifier', LogisticRegression())
])
pipe.fit(X, y)
```

## Ensemble Methods

### Voting Classifier
```python
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# Create individual classifiers
clf1 = LogisticRegression(random_state=42)
clf2 = SVC(probability=True, random_state=42)
clf3 = GaussianNB()

# Voting Classifier
voting_clf = VotingClassifier(
    estimators=[('lr', clf1), ('svc', clf2), ('nb', clf3)],
    voting='soft',             # 'hard' or 'soft'
    weights=[2, 1, 1]         # Optional weights for each classifier
)

voting_clf.fit(X_train, y_train)
y_pred = voting_clf.predict(X_test)

# Access individual classifiers
for name, clf in voting_clf.named_estimators_.items():
    score = clf.score(X_test, y_test)
    print(f"{name}: {score:.3f}")
```

### Bagging
```python
from sklearn.ensemble import BaggingClassifier, BaggingRegressor
from sklearn.tree import DecisionTreeClassifier

# Bagging Classifier
bagging = BaggingClassifier(
    estimator=DecisionTreeClassifier(),
    n_estimators=100,          # Number of base estimators
    max_samples=1.0,          # Fraction of samples
    max_features=1.0,         # Fraction of features
    bootstrap=True,           # Bootstrap samples
    bootstrap_features=False, # Bootstrap features
    oob_score=True,           # Out-of-bag score
    n_jobs=-1,
    random_state=42
)

bagging.fit(X_train, y_train)
print(f"OOB Score: {bagging.oob_score_:.3f}")

# Feature importance (if base estimator has it)
if hasattr(bagging.estimators_[0], 'feature_importances_'):
    importances = np.mean([
        tree.feature_importances_ for tree in bagging.estimators_
    ], axis=0)
```

### AdaBoost
```python
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier

# AdaBoost Classifier
ada_boost = AdaBoostClassifier(
    estimator=DecisionTreeClassifier(max_depth=1),
    n_estimators=100,          # Number of boosting rounds
    learning_rate=1.0,         # Shrinks contribution
    algorithm='SAMME',         # 'SAMME' or 'SAMME.R'
    random_state=42
)

ada_boost.fit(X_train, y_train)

# Staged predictions (see performance at each boosting iteration)
staged_scores = []
for pred in ada_boost.staged_predict(X_test):
    staged_scores.append(accuracy_score(y_test, pred))

# Feature importance
feature_importance = ada_boost.feature_importances_
```

### Extra Trees
```python
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor

# Extra Trees (Extremely Randomized Trees)
extra_trees = ExtraTreesClassifier(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',       # Random subset of features
    bootstrap=False,           # No bootstrap (uses all samples)
    oob_score=False,          # No OOB (no bootstrap)
    n_jobs=-1,
    random_state=42
)

extra_trees.fit(X_train, y_train)

# Feature importance
importances = extra_trees.feature_importances_
std = np.std([tree.feature_importances_ for tree in extra_trees.estimators_], axis=0)
```

### Stacking
```python
from sklearn.ensemble import StackingClassifier, StackingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

# Base models
base_models = [
    ('svc', SVC(probability=True, random_state=42)),
    ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
]

# Meta-model
meta_model = LogisticRegression(random_state=42)

# Stacking Classifier
stacking = StackingClassifier(
    estimators=base_models,
    final_estimator=meta_model,
    cv=5,                      # Cross-validation for training meta-model
    stack_method='auto',       # Method to call on base estimators
    n_jobs=-1,
    passthrough=False          # Add original features to meta-model
)

stacking.fit(X_train, y_train)
y_pred = stacking.predict(X_test)

# Access base model predictions
X_meta = stacking.transform(X_test)  # Base model predictions
```

## Neural Networks

### Multi-layer Perceptron Classifier
```python
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

# Scale features (important for neural networks)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# MLP Classifier
mlp = MLPClassifier(
    hidden_layer_sizes=(100, 50),  # Architecture: 2 hidden layers
    activation='relu',              # 'relu', 'tanh', 'logistic'
    solver='adam',                  # 'adam', 'sgd', 'lbfgs'
    alpha=0.0001,                  # L2 regularization
    batch_size='auto',             # Batch size for SGD/Adam
    learning_rate='constant',      # 'constant', 'invscaling', 'adaptive'
    learning_rate_init=0.001,
    max_iter=200,
    shuffle=True,
    random_state=42,
    early_stopping=True,           # Early stopping
    validation_fraction=0.1,       # Fraction for validation
    n_iter_no_change=10,          # Iterations without improvement
    verbose=True
)

mlp.fit(X_scaled, y_train)

# Training history
print(f"Loss curve: {mlp.loss_curve_}")
print(f"Best validation score: {mlp.best_validation_score_}")
print(f"Number of iterations: {mlp.n_iter_}")
```

### Multi-layer Perceptron Regressor
```python
from sklearn.neural_network import MLPRegressor

# MLP Regressor
mlp_reg = MLPRegressor(
    hidden_layer_sizes=(100, 100, 50),  # 3 hidden layers
    activation='relu',
    solver='adam',
    alpha=0.001,                        # Stronger regularization
    learning_rate='adaptive',           # Adaptive learning rate
    max_iter=1000,
    early_stopping=True,
    validation_fraction=0.15,
    random_state=42
)

# Training with scaled features
mlp_reg.fit(X_scaled, y_train)

# Predictions
y_pred = mlp_reg.predict(scaler.transform(X_test))

# Partial dependence
from sklearn.inspection import partial_dependence
pdp, axes = partial_dependence(mlp_reg, X_scaled, features=[0, 1])
```

## Semi-Supervised Learning

### Label Propagation
```python
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
import numpy as np

# Create semi-supervised dataset (some labels are -1)
rng = np.random.RandomState(42)
unlabeled_points = rng.rand(len(y)) < 0.7  # 70% unlabeled
y_semi = y.copy()
y_semi[unlabeled_points] = -1

# Label Propagation
label_prop = LabelPropagation(
    kernel='rbf',              # Kernel for similarity matrix
    gamma=20,                  # Kernel parameter
    n_neighbors=7,             # For knn kernel
    max_iter=1000,
    tol=1e-3
)
label_prop.fit(X, y_semi)

# Predict on unlabeled data
predicted_labels = label_prop.transduction_[unlabeled_points]

# Label Spreading (more robust to noise)
label_spread = LabelSpreading(
    kernel='rbf',
    gamma=20,
    n_neighbors=7,
    alpha=0.2,                # Clamping factor [0, 1]
    max_iter=30
)
label_spread.fit(X, y_semi)
```

### Self-Training
```python
from sklearn.semi_supervised import SelfTrainingClassifier
from sklearn.svm import SVC

# Base classifier
base_classifier = SVC(probability=True, random_state=42)

# Self-training classifier
self_training = SelfTrainingClassifier(
    base_estimator=base_classifier,
    threshold=0.75,            # Confidence threshold
    criterion='threshold',     # 'threshold' or 'k_best'
    k_best=10,                # For 'k_best' criterion
    max_iter=10,              # Maximum iterations
    verbose=True
)

# Fit with partially labeled data
self_training.fit(X, y_semi)

# Check which samples were labeled
labeled_indices = self_training.labeled_iter_ == 0
print(f"Initially labeled: {labeled_indices.sum()}")
print(f"Total labeled: {(self_training.labeled_iter_ >= 0).sum()}")
```

## Outlier Detection

### Isolation Forest
```python
from sklearn.ensemble import IsolationForest

# Isolation Forest
iso_forest = IsolationForest(
    n_estimators=100,
    max_samples='auto',        # Samples to draw
    contamination='auto',      # Expected proportion of outliers
    max_features=1.0,         # Features to draw
    bootstrap=False,
    random_state=42
)

# Fit and predict (-1 for outliers, 1 for inliers)
outliers = iso_forest.fit_predict(X)
scores = iso_forest.score_samples(X)  # Anomaly scores

# Decision function (negative for outliers)
decision = iso_forest.decision_function(X)
```

### Local Outlier Factor
```python
from sklearn.neighbors import LocalOutlierFactor

# LOF for outlier detection
lof = LocalOutlierFactor(
    n_neighbors=20,            # Number of neighbors
    algorithm='auto',          # Algorithm for NN search
    metric='minkowski',        # Distance metric
    contamination='auto',      # Expected proportion of outliers
    novelty=False             # False for outlier detection, True for novelty
)

# Fit and predict
outliers = lof.fit_predict(X)
scores = lof.negative_outlier_factor_  # LOF scores

# For novelty detection (predict on new data)
lof_novelty = LocalOutlierFactor(novelty=True, contamination=0.1)
lof_novelty.fit(X_train)
new_outliers = lof_novelty.predict(X_test)
```

### One-Class SVM
```python
from sklearn.svm import OneClassSVM

# One-Class SVM
oc_svm = OneClassSVM(
    kernel='rbf',
    gamma='scale',
    nu=0.1,                   # Upper bound on fraction of outliers
    shrinking=True,
    cache_size=200,
    verbose=False
)

# Fit and predict
oc_svm.fit(X_train)
outliers = oc_svm.predict(X_test)
scores = oc_svm.score_samples(X_test)
decision = oc_svm.decision_function(X_test)
```

### Elliptic Envelope
```python
from sklearn.covariance import EllipticEnvelope

# Elliptic Envelope (assumes Gaussian distribution)
envelope = EllipticEnvelope(
    store_precision=True,
    assume_centered=False,
    support_fraction=None,     # Fraction of support points
    contamination=0.1,        # Contamination parameter
    random_state=42
)

# Fit and predict
envelope.fit(X_train)
outliers = envelope.predict(X_test)
scores = envelope.score_samples(X_test)
mahalanobis = envelope.mahalanobis(X_test)  # Mahalanobis distances
```

## Multiclass & Multioutput

### Multiclass Classification
```python
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.multiclass import OutputCodeClassifier
from sklearn.svm import LinearSVC

# One-vs-Rest (OvR)
ovr = OneVsRestClassifier(
    LinearSVC(random_state=42),
    n_jobs=-1
)
ovr.fit(X_train, y_train)

# One-vs-One (OvO)
ovo = OneVsOneClassifier(
    LinearSVC(random_state=42),
    n_jobs=-1
)
ovo.fit(X_train, y_train)

# Error-Correcting Output Codes
ecoc = OutputCodeClassifier(
    LinearSVC(random_state=42),
    code_size=2,              # Size of error-correcting code
    random_state=42,
    n_jobs=-1
)
ecoc.fit(X_train, y_train)
```

### Multilabel Classification
```python
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np

# Create multilabel target
y_multilabel = np.array([
    [1, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 0, 0],
    [1, 1, 0, 1]
])

# MultiOutput Classifier
multi_clf = MultiOutputClassifier(
    RandomForestClassifier(n_estimators=100, random_state=42),
    n_jobs=-1
)
multi_clf.fit(X_train[:4], y_multilabel)
y_pred = multi_clf.predict(X_test[:4])
```

### Multioutput Regression
```python
from sklearn.multioutput import MultiOutputRegressor, RegressorChain
from sklearn.datasets import make_regression

# Create multioutput regression data
X_multi, y_multi = make_regression(
    n_samples=100, n_features=10, n_targets=3, random_state=42
)

# MultiOutput Regressor (independent targets)
multi_reg = MultiOutputRegressor(
    GradientBoostingRegressor(random_state=42),
    n_jobs=-1
)
multi_reg.fit(X_multi[:80], y_multi[:80])

# Regressor Chain (considers correlations)
chain_reg = RegressorChain(
    GradientBoostingRegressor(random_state=42),
    order='random',           # Order of chain
    random_state=42
)
chain_reg.fit(X_multi[:80], y_multi[:80])
```

### Multiclass-Multioutput Classification
```python
from sklearn.datasets import make_classification
from sklearn.multioutput import ClassifierChain

# Create multiclass-multioutput data
X, y1 = make_classification(n_samples=100, n_features=100,
                           n_informative=30, n_classes=3,
                           random_state=1)
y2 = np.random.choice([0, 1, 2], 100)
y3 = np.random.choice([0, 1, 2], 100)
Y = np.vstack((y1, y2, y3)).T

# Classifier Chain
chain_clf = ClassifierChain(
    RandomForestClassifier(n_estimators=100, random_state=42),
    order='random',
    random_state=42
)
chain_clf.fit(X[:80], Y[:80])
y_pred = chain_clf.predict(X[80:])
```

## Calibration

### Calibrated Classifier
```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.calibration import calibration_curve

# Train uncalibrated classifier
svm = LinearSVC(random_state=42)
svm.fit(X_train, y_train)

# Calibrate classifier
calibrated_clf = CalibratedClassifierCV(
    estimator=svm,
    method='sigmoid',          # 'sigmoid' or 'isotonic'
    cv=3,                     # Cross-validation folds
    ensemble=True             # Ensemble of calibrated classifiers
)
calibrated_clf.fit(X_train, y_train)

# Compare probabilities
prob_uncalibrated = svm.decision_function(X_test)
prob_calibrated = calibrated_clf.predict_proba(X_test)

# Calibration plot
from sklearn.calibration import CalibrationDisplay
CalibrationDisplay.from_estimator(
    calibrated_clf, X_test, y_test,
    n_bins=10,
    name='Calibrated SVM'
)
```

### Probability Calibration Methods
```python
# Isotonic Regression (non-parametric)
isotonic_calibrated = CalibratedClassifierCV(
    estimator=svm,
    method='isotonic',
    cv='prefit'               # Use pre-fitted classifier
)
isotonic_calibrated.fit(X_val, y_val)

# Platt Scaling (sigmoid)
sigmoid_calibrated = CalibratedClassifierCV(
    estimator=svm,
    method='sigmoid',
    cv='prefit'
)
sigmoid_calibrated.fit(X_val, y_val)

# Evaluate calibration
from sklearn.metrics import brier_score_loss
brier_isotonic = brier_score_loss(y_test, 
                                 isotonic_calibrated.predict_proba(X_test)[:, 1])
brier_sigmoid = brier_score_loss(y_test,
                                sigmoid_calibrated.predict_proba(X_test)[:, 1])
```

## Pipelines

### Basic Pipeline
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC

# Create pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=2)),
    ('svm', SVC(random_state=42))
])

# Fit and predict
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

# Access pipeline steps
pca_step = pipe.named_steps['pca']
print(f"PCA explained variance: {pca_step.explained_variance_ratio_}")

# Set parameters
pipe.set_params(svm__C=10, pca__n_components=3)
```

### Column Transformer
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import pandas as pd

# Sample dataframe with mixed types
df = pd.DataFrame({
    'numeric1': [1, 2, 3, 4],
    'numeric2': [5, 6, 7, 8],
    'category': ['a', 'b', 'a', 'c']
})

# Define transformations for different columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['numeric1', 'numeric2']),
        ('cat', OneHotEncoder(drop='first'), ['category'])
    ],
    remainder='passthrough',   # 'drop' or 'passthrough'
    sparse_threshold=0.3,      # Threshold for sparse matrix
    n_jobs=-1
)

# Use in pipeline
pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression())
])
```

### Pipeline with Grid Search
```python
from sklearn.model_selection import GridSearchCV

# Pipeline with multiple steps
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('selector', SelectKBest()),
    ('classifier', SVC())
])

# Parameter grid with pipeline notation
param_grid = {
    'selector__k': [5, 10, 20],
    'selector__score_func': [f_classif, mutual_info_classif],
    'classifier__C': [0.1, 1, 10],
    'classifier__kernel': ['linear', 'rbf']
}

# Grid search on pipeline
grid = GridSearchCV(
    pipe,
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
grid.fit(X_train, y_train)

print(f"Best params: {grid.best_params_}")
```

### Make Pipeline Helper
```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

# Simplified pipeline creation
pipe = make_pipeline(
    StandardScaler(),
    PCA(n_components=2),
    LogisticRegression()
)

# Steps are named automatically
print(pipe.named_steps.keys())  # 'standardscaler', 'pca', 'logisticregression'
```

## Metrics

### Classification Metrics
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import f1_score, confusion_matrix, classification_report
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve
from sklearn.metrics import cohen_kappa_score, matthews_corrcoef

# Basic metrics
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average='weighted')
recall = recall_score(y_true, y_pred, average='weighted')
f1 = f1_score(y_true, y_pred, average='weighted')

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)
print(f"Confusion Matrix:\n{cm}")

# Classification report
report = classification_report(y_true, y_pred, 
                             target_names=['Class 0', 'Class 1', 'Class 2'])
print(report)

# ROC AUC (for binary classification)
if len(np.unique(y_true)) == 2:
    auc = roc_auc_score(y_true, y_proba[:, 1])
    fpr, tpr, thresholds = roc_curve(y_true, y_proba[:, 1])

# Additional metrics
kappa = cohen_kappa_score(y_true, y_pred)
mcc = matthews_corrcoef(y_true, y_pred)
```

### Regression Metrics
```python
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score, explained_variance_score
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import median_absolute_error, max_error

# Common regression metrics
mse = mean_squared_error(y_true, y_pred)
rmse = mean_squared_error(y_true, y_pred, squared=False)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)
evs = explained_variance_score(y_true, y_pred)

# Percentage and robust metrics
mape = mean_absolute_percentage_error(y_true, y_pred)
medae = median_absolute_error(y_true, y_pred)
max_err = max_error(y_true, y_pred)

print(f"MSE: {mse:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"MAE: {mae:.3f}")
print(f"R²: {r2:.3f}")
print(f"MAPE: {mape:.3f}")
```

### Clustering Metrics
```python
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics import davies_bouldin_score, adjusted_rand_score
from sklearn.metrics import normalized_mutual_info_score, homogeneity_score
from sklearn.metrics import completeness_score, v_measure_score

# Internal metrics (no ground truth needed)
silhouette = silhouette_score(X, labels)
calinski = calinski_harabasz_score(X, labels)
davies_bouldin = davies_bouldin_score(X, labels)

# External metrics (need ground truth)
ari = adjusted_rand_score(y_true, labels)
nmi = normalized_mutual_info_score(y_true, labels)
homogeneity = homogeneity_score(y_true, labels)
completeness = completeness_score(y_true, labels)
v_measure = v_measure_score(y_true, labels)
```

### Custom Scoring Functions
```python
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_val_score

# Define custom metric
def custom_metric(y_true, y_pred):
    # Custom logic
    return np.mean(y_true == y_pred) * 100

# Create scorer
custom_scorer = make_scorer(
    custom_metric,
    greater_is_better=True,    # Direction of optimization
    needs_proba=False,         # Needs probability predictions
    needs_threshold=False      # Needs decision threshold
)

# Use in cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring=custom_scorer)

# Multiple metrics
from sklearn.metrics import get_scorer_names
available_scorers = get_scorer_names()  # List all available scorers
```

## Cross-Validation

### K-Fold Cross-Validation
```python
from sklearn.model_selection import KFold, StratifiedKFold, RepeatedKFold
from sklearn.model_selection import RepeatedStratifiedKFold

# Standard K-Fold
kfold = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

for fold, (train_idx, val_idx) in enumerate(kfold.split(X)):
    X_train_fold = X[train_idx]
    X_val_fold = X[val_idx]
    print(f"Fold {fold}: Train={len(train_idx)}, Val={len(val_idx)}")

# Stratified K-Fold (preserves class distribution)
skfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Repeated K-Fold
rkfold = RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)
rskfold = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
```

### Leave-One-Out and Leave-P-Out
```python
from sklearn.model_selection import LeaveOneOut, LeavePOut

# Leave-One-Out (LOO)
loo = LeaveOneOut()
for train_idx, test_idx in loo.split(X):
    X_train_loo = X[train_idx]
    X_test_loo = X[test_idx]  # Single sample

# Leave-P-Out
lpo = LeavePOut(p=2)  # Leave 2 samples out
n_splits = lpo.get_n_splits(X)
print(f"Number of splits: {n_splits}")
```

### Time Series Split
```python
from sklearn.model_selection import TimeSeriesSplit

# Time Series Cross-Validation
tscv = TimeSeriesSplit(
    n_splits=5,
    max_train_size=None,       # Maximum training set size
    test_size=None,           # Fixed test set size
    gap=0                     # Gap between train and test
)

for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
    print(f"Fold {fold}:")
    print(f"  Train: indices {train_idx[0]} to {train_idx[-1]}")
    print(f"  Test:  indices {test_idx[0]} to {test_idx[-1]}")
```

### Group-based Splitting
```python
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.model_selection import LeaveOneGroupOut, LeavePGroupsOut

# Define groups (e.g., patient IDs, user IDs)
groups = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4])

# Group K-Fold (groups don't overlap between train/test)
group_kfold = GroupKFold(n_splits=3)
for train_idx, test_idx in group_kfold.split(X, y, groups):
    train_groups = groups[train_idx]
    test_groups = groups[test_idx]
    
# Leave One Group Out
logo = LeaveOneGroupOut()
for train_idx, test_idx in logo.split(X, y, groups):
    pass

# Group Shuffle Split
gss = GroupShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
```

### Nested Cross-Validation
```python
from sklearn.model_selection import cross_val_score, GridSearchCV

# Inner CV for hyperparameter tuning
param_grid = {'C': [0.1, 1, 10]}
inner_cv = KFold(n_splits=3, shuffle=True, random_state=42)

# Outer CV for model evaluation
outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)

# Nested CV scores
nested_scores = []
for train_idx, test_idx in outer_cv.split(X, y):
    X_train_outer, X_test_outer = X[train_idx], X[test_idx]
    y_train_outer, y_test_outer = y[train_idx], y[test_idx]
    
    # Inner grid search
    grid = GridSearchCV(SVC(), param_grid, cv=inner_cv)
    grid.fit(X_train_outer, y_train_outer)
    
    # Evaluate on outer test set
    score = grid.score(X_test_outer, y_test_outer)
    nested_scores.append(score)

print(f"Nested CV Score: {np.mean(nested_scores):.3f} (+/- {np.std(nested_scores):.3f})")
```

## Datasets

### Built-in Datasets
```python
from sklearn import datasets

# Classification datasets
iris = datasets.load_iris()
digits = datasets.load_digits()
wine = datasets.load_wine()
breast_cancer = datasets.load_breast_cancer()

# Regression datasets
diabetes = datasets.load_diabetes()
boston = datasets.load_boston()  # Deprecated
california_housing = datasets.fetch_california_housing()

# Access data
X, y = iris.data, iris.target
feature_names = iris.feature_names
target_names = iris.target_names
description = iris.DESCR
```

### Synthetic Data Generation
```python
from sklearn.datasets import make_classification, make_regression
from sklearn.datasets import make_blobs, make_circles, make_moons
from sklearn.datasets import make_multilabel_classification

# Classification data
X_class, y_class = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=15,          # Informative features
    n_redundant=5,             # Redundant features
    n_classes=3,               # Number of classes
    n_clusters_per_class=2,    # Clusters per class
    weights=[0.5, 0.3, 0.2],   # Class weights
    flip_y=0.01,               # Label noise
    random_state=42
)

# Regression data
X_reg, y_reg = make_regression(
    n_samples=1000,
    n_features=20,
    n_informative=15,
    n_targets=1,               # Number of targets
    noise=0.1,                 # Gaussian noise
    random_state=42
)

# Clustering data
X_blobs, y_blobs = make_blobs(
    n_samples=1000,
    n_features=2,
    centers=4,
    cluster_std=1.0,
    random_state=42
)

# Non-linear patterns
X_moons, y_moons = make_moons(n_samples=1000, noise=0.1, random_state=42)
X_circles, y_circles = make_circles(n_samples=1000, noise=0.1, factor=0.5, random_state=42)

# Multilabel classification
X_multi, y_multi = make_multilabel_classification(
    n_samples=1000,
    n_features=20,
    n_classes=5,
    n_labels=2,                # Average labels per sample
    random_state=42
)
```

### Sample Generators
```python
from sklearn.datasets import make_sparse_spd_matrix, make_low_rank_matrix
from sklearn.datasets import make_s_curve, make_swiss_roll

# Sparse SPD matrix
spd_matrix = make_sparse_spd_matrix(
    n_dim=100,
    alpha=0.95,                # Sparsity level
    norm_diag=False,
    smallest_coef=0.1,
    largest_coef=0.9,
    random_state=42
)

# Low-rank matrix
low_rank = make_low_rank_matrix(
    n_samples=100,
    n_features=50,
    effective_rank=10,
    tail_strength=0.5,
    random_state=42
)

# 3D manifolds
X_scurve, color = make_s_curve(n_samples=1000, noise=0.1, random_state=42)
X_swiss, color = make_swiss_roll(n_samples=1000, noise=0.1, random_state=42)
```

## Best Practices

### Model Persistence
```python
import joblib
import pickle

# Save model with joblib (recommended)
joblib.dump(model, 'model.pkl')
loaded_model = joblib.load('model.pkl')

# Save with pickle
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# Save pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
joblib.dump(pipeline, 'pipeline.pkl')
```

### Handling Imbalanced Data
```python
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE  # pip install imbalanced-learn
from imblearn.under_sampling import RandomUnderSampler

# Class weights
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y),
    y=y
)
class_weight_dict = dict(zip(np.unique(y), class_weights))

# Use in classifier
clf = LogisticRegression(class_weight='balanced')
# or
clf = LogisticRegression(class_weight=class_weight_dict)

# SMOTE oversampling
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Undersampling
under_sampler = RandomUnderSampler(random_state=42)
X_under, y_under = under_sampler.fit_resample(X_train, y_train)
```

### Feature Scaling Considerations
```python
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split

# IMPORTANT: Fit scaler only on training data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Correct approach
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit and transform
X_test_scaled = scaler.transform(X_test)        # Only transform

# For cross-validation, use Pipeline
from sklearn.pipeline import Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', SVC())
])
# Pipeline ensures proper scaling in CV
```

### Memory Optimization
```python
from sklearn.datasets import load_svmlight_file
from scipy import sparse

# Use sparse matrices when appropriate
X_sparse = sparse.csr_matrix(X)

# Memory-efficient data loading
X, y = load_svmlight_file('data.svmlight')

# Partial fit for large datasets
from sklearn.linear_model import SGDClassifier
sgd = SGDClassifier()
for chunk in data_chunks:
    sgd.partial_fit(chunk[0], chunk[1], classes=all_classes)

# Use generators for large datasets
def data_generator(file_path, chunk_size=1000):
    while True:
        chunk = pd.read_csv(file_path, chunksize=chunk_size)
        for data in chunk:
            X = data.drop('target', axis=1)
            y = data['target']
            yield X, y
```

### Reproducibility
```python
import numpy as np
import random
from sklearn.model_selection import train_test_split

# Set random seeds
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)

# Use random_state in all functions
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

model = RandomForestClassifier(random_state=RANDOM_STATE)
cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
```

### Performance Optimization
```python
# Use n_jobs for parallelization
model = RandomForestClassifier(n_jobs=-1)  # Use all cores

# Cache repeated computations
from sklearn.pipeline import Pipeline
from sklearn.kernel_approximation import Nystroem

pipe = Pipeline([
    ('nystroem', Nystroem(random_state=42)),
    ('svm', SVC())
], memory='cache_directory')  # Cache transformations

# Use warm_start for iterative algorithms
model = SGDClassifier(warm_start=True)
for epoch in range(n_epochs):
    model.partial_fit(X_train, y_train, classes=np.unique(y))

# Efficient hyperparameter search
from sklearn.model_selection import HalvingGridSearchCV
halving_search = HalvingGridSearchCV(
    estimator, param_grid,
    resource='n_samples',
    factor=3,
    cv=5
)
```

### Model Interpretation
```python
from sklearn.inspection import permutation_importance
from sklearn.inspection import partial_dependence, PartialDependenceDisplay

# Feature importance
if hasattr(model, 'feature_importances_'):
    importances = model.feature_importances_

# Permutation importance (model-agnostic)
perm_importance = permutation_importance(
    model, X_test, y_test,
    n_repeats=10,
    random_state=42
)

# Partial dependence plots
features = [0, 1, (0, 1)]  # Individual and interaction
display = PartialDependenceDisplay.from_estimator(
    model, X_train, features,
    kind='average'  # 'average' or 'individual'
)
```

## Conclusion

Scikit-learn provides a comprehensive suite of machine learning tools with a consistent API. Key takeaways:

1. **Consistent Interface**: All estimators follow fit/predict pattern
2. **Preprocessing**: Always scale features for distance-based algorithms
3. **Validation**: Use proper cross-validation to avoid overfitting
4. **Pipelines**: Combine preprocessing and modeling steps
5. **Model Selection**: Use GridSearch or RandomSearch for hyperparameter tuning
6. **Metrics**: Choose appropriate metrics for your problem
7. **Best Practices**: Always split data before preprocessing, set random states for reproducibility

For more information, visit the [official documentation](https://scikit-learn.org/).