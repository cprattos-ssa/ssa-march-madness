"""Train a PyTorch feedforward neural network for March Madness prediction."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import brier_score_loss

from src.data.prepare import (
    build_cv_splits,
    prepare_for_nn,
    augment_training_data,
    CORE_FEATURES,
)


class MarchMadnessNet(nn.Module):
    """Simple feedforward network for binary prediction."""

    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray = None,
    y_val: np.ndarray = None,
    epochs: int = 200,
    patience: int = 20,
    lr: float = 0.001,
    batch_size: int = 256,
    verbose: bool = False,
):
    """Train the neural network with optional early stopping on validation set.

    Returns:
        Trained model (in eval mode).
    """
    device = torch.device("cpu")
    input_dim = X_train.shape[1]
    model = MarchMadnessNet(input_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()

    # Build data loaders
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    has_val = X_val is not None and y_val is not None
    if has_val:
        X_val_t = torch.tensor(X_val, dtype=torch.float32).to(device)
        y_val_t = torch.tensor(y_val, dtype=torch.float32).to(device)

    best_val_loss = float("inf")
    best_state = None
    wait = 0

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(X_batch)
        epoch_loss /= len(train_dataset)

        # Early stopping on validation loss
        if has_val:
            model.eval()
            with torch.no_grad():
                val_preds = model(X_val_t)
                val_loss = criterion(val_preds, y_val_t).item()

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_state = {k: v.clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
                if wait >= patience:
                    if verbose:
                        print(f"    Early stopping at epoch {epoch+1}")
                    break

            if verbose and (epoch + 1) % 50 == 0:
                print(
                    f"    Epoch {epoch+1}: train_loss={epoch_loss:.4f}, "
                    f"val_loss={val_loss:.4f}"
                )
        else:
            # No validation - just train for all epochs
            if verbose and (epoch + 1) % 50 == 0:
                print(f"    Epoch {epoch+1}: train_loss={epoch_loss:.4f}")

    # Restore best weights if we used early stopping
    if has_val and best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    return model


def predict(model, X: np.ndarray) -> np.ndarray:
    """Get predictions from a trained model."""
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X, dtype=torch.float32)
        preds = model(X_t).numpy()
    return np.clip(preds, 0.001, 0.999)


def run_cv(train_df, use_pca, n_components=16, n_folds=5, augment=True):
    """Run leave-one-tournament-out CV for the neural network."""
    splits = build_cv_splits(train_df, n_recent=n_folds)
    fold_scores = []
    all_preds = []
    all_true = []

    for fold_idx, (train_idx, val_idx) in enumerate(splits):
        train_fold = train_df.iloc[train_idx]
        val_fold = train_df.iloc[val_idx]

        # Prepare features
        X_train, y_train, X_val, transformer, feat_names = prepare_for_nn(
            train_fold, val_fold, use_pca=use_pca, n_components=n_components
        )

        # Augment training data
        if augment:
            X_train, y_train = augment_training_data(X_train, y_train)

        # Train with early stopping on validation
        model = train_model(
            X_train, y_train,
            X_val=X_val, y_val=val_fold["Target"].values,
            epochs=200, patience=20, lr=0.001,
            verbose=False,
        )

        # Predict
        y_pred = predict(model, X_val)
        brier = brier_score_loss(val_fold["Target"].values, y_pred)
        fold_scores.append(brier)
        all_preds.extend(y_pred)
        all_true.extend(val_fold["Target"].values)

        season = val_fold["Season"].iloc[0]
        print(f"  Fold {fold_idx+1} (season {season}): Brier = {brier:.4f}")

    mean_brier = np.mean(fold_scores)
    overall_brier = brier_score_loss(all_true, all_preds)
    print(f"  Mean Brier: {mean_brier:.4f}")
    print(f"  Overall Brier: {overall_brier:.4f}")

    return {
        "fold_scores": fold_scores,
        "mean_brier": mean_brier,
        "overall_brier": overall_brier,
    }


def main():
    torch.manual_seed(42)
    np.random.seed(42)

    train_df = pd.read_parquet("data/processed/training_matchups.parquet")
    pred_df = pd.read_parquet("data/processed/prediction_matchups_2026.parquet")
    print(f"Training data: {train_df.shape}")
    print(f"Prediction data: {pred_df.shape}")

    # --- Config 1: No PCA ---
    print("\n=== Neural Net CV (no PCA) ===")
    results_no_pca = run_cv(train_df, use_pca=False, augment=True)

    # --- Config 2: With PCA ---
    print("\n=== Neural Net CV (PCA, 16 components) ===")
    results_pca = run_cv(train_df, use_pca=True, n_components=16, augment=True)

    # Pick the best config
    if results_pca["mean_brier"] < results_no_pca["mean_brier"]:
        best_config = "PCA"
        best_use_pca = True
        best_brier = results_pca["mean_brier"]
    else:
        best_config = "no PCA"
        best_use_pca = False
        best_brier = results_no_pca["mean_brier"]

    print(f"\n=== Best config: {best_config} (mean Brier = {best_brier:.4f}) ===")

    # --- Train final model on all data ---
    print("\nTraining final model on all data...")
    X_train, y_train, X_pred, transformer, feat_names = prepare_for_nn(
        train_df, pred_df, use_pca=best_use_pca, n_components=16
    )
    X_train_aug, y_train_aug = augment_training_data(X_train, y_train)

    final_model = train_model(
        X_train_aug, y_train_aug,
        epochs=200, patience=20, lr=0.001,
        verbose=True,
    )

    # Predict 2026 matchups
    preds_2026 = predict(final_model, X_pred)
    print(f"\n2026 predictions: mean={preds_2026.mean():.4f}, "
          f"std={preds_2026.std():.4f}, "
          f"min={preds_2026.min():.4f}, max={preds_2026.max():.4f}")

    # Save predictions
    out = pred_df[["Season", "TeamLow", "TeamHigh"]].copy()
    out["Pred"] = preds_2026
    out.to_parquet("data/processed/preds_nn.parquet", index=False)
    print(f"Saved predictions to data/processed/preds_nn.parquet ({len(out)} rows)")


if __name__ == "__main__":
    main()
