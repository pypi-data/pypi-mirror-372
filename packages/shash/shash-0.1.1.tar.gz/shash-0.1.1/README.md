# Shash Package

A custom Python package for data analysis, preparation, and model evaluation.

## Features

- **Data preparation & EDA**
  - `datacheck`: Checks for missing/null values and duplicate rows in a DataFrame.
  - `dataeda`: Provides basic exploration of a DataFrame, including `head`, `shape`, `info`, and descriptive statistics (`describe`).

- **Model evaluation**
  - `evaluate_model`: Computes key evaluation metrics for classification models, including accuracy, precision, recall, F1-score, confusion matrix, Classification report and ROC AUC score.


## Installation

Install from PyPI:

```bash
pip install shash


## Usage

```python
from shash.dataprep import datacheck, dataeda
from shash.evaluation import evaluate_model

# Example usage
datacheck(df)        # Check for missing values and duplicates
dataeda(df)          # Explore the dataset: head, shape, info, describe
evaluate_model(y_val, y_pred_val, y_proba_val, dataset_name="Validation Set")  # Evaluate model performance: accuracy, precision, recall, F1-score, confusion matrix
