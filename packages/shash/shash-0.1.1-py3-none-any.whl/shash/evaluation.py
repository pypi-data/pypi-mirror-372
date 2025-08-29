import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix,
    ConfusionMatrixDisplay
)

def evaluate_model(y_true, y_pred_labels, y_pred_proba=None, dataset_name="Dataset"):
    """
    Evaluate classification model and print metrics, confusion matrix, and classification report.
    
    Parameters:
    ----------
    y_true : array-like
        True labels.
    y_pred_labels : array-like
        Predicted labels (0/1).
    y_pred_proba : array-like, optional
        Predicted probabilities for the positive class (used for ROC AUC).
    dataset_name : str, default="Dataset"
        Name of dataset for display.
    """
    print(f"\n--- {dataset_name} Evaluation ---")

    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred_labels)
    precision = precision_score(y_true, y_pred_labels, zero_division=0)
    recall = recall_score(y_true, y_pred_labels, zero_division=0)
    f1 = f1_score(y_true, y_pred_labels, zero_division=0)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    # ROC AUC if probabilities are provided
    if y_pred_proba is not None:
        roc_auc = roc_auc_score(y_true, y_pred_proba)
        print(f"ROC AUC  : {roc_auc:.4f}")

    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred_labels, zero_division=0))

    # Confusion matrix
    print("Confusion Matrix (Raw Counts):")
    cm = confusion_matrix(y_true, y_pred_labels)
    print(cm)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="Blues")
    plt.title(f"Confusion Matrix - {dataset_name}")
    plt.show()
