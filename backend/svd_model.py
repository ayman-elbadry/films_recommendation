"""
SVD Model class using Stochastic Gradient Descent (pure NumPy).
Shared module so pickle can find the class from any import context.
"""

import numpy as np


class SVDModel:
    """
    SVD model using Stochastic Gradient Descent (SGD).
    Learns user and item latent factor matrices from a ratings dataset.
    """

    def __init__(self, n_factors=50, n_epochs=20, lr=0.005, reg=0.02):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.reg = reg
        self.global_mean = 0.0
        self.user_bias = None
        self.item_bias = None
        self.user_factors = None
        self.item_factors = None
        self.user_map = {}
        self.item_map = {}

    def fit(self, user_ids, item_ids, ratings):
        """Train the SVD model on the given ratings."""
        unique_users = np.unique(user_ids)
        unique_items = np.unique(item_ids)
        self.user_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.item_map = {iid: idx for idx, iid in enumerate(unique_items)}

        n_users = len(unique_users)
        n_items = len(unique_items)

        print(f"  Training SVD: {n_users} users, {n_items} items, {len(ratings)} ratings")
        print(f"  Factors={self.n_factors}, Epochs={self.n_epochs}, LR={self.lr}, Reg={self.reg}")

        self.global_mean = np.mean(ratings)
        self.user_bias = np.zeros(n_users)
        self.item_bias = np.zeros(n_items)
        rng = np.random.default_rng(42)
        self.user_factors = rng.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = rng.normal(0, 0.1, (n_items, self.n_factors))

        u_indices = np.array([self.user_map[u] for u in user_ids])
        i_indices = np.array([self.item_map[i] for i in item_ids])

        for epoch in range(self.n_epochs):
            indices = np.arange(len(ratings))
            rng.shuffle(indices)

            total_error = 0.0
            for idx in indices:
                u = u_indices[idx]
                i = i_indices[idx]
                r = ratings[idx]

                pred = (
                    self.global_mean
                    + self.user_bias[u]
                    + self.item_bias[i]
                    + np.dot(self.user_factors[u], self.item_factors[i])
                )
                err = r - pred
                total_error += err ** 2

                self.user_bias[u] += self.lr * (err - self.reg * self.user_bias[u])
                self.item_bias[i] += self.lr * (err - self.reg * self.item_bias[i])

                uf = self.user_factors[u].copy()
                self.user_factors[u] += self.lr * (
                    err * self.item_factors[i] - self.reg * self.user_factors[u]
                )
                self.item_factors[i] += self.lr * (
                    err * uf - self.reg * self.item_factors[i]
                )

            rmse = np.sqrt(total_error / len(ratings))
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f"    Epoch {epoch + 1}/{self.n_epochs}, RMSE: {rmse:.4f}")

    def predict(self, user_id, item_id):
        """Predict the rating a user would give to an item."""
        if user_id not in self.user_map or item_id not in self.item_map:
            return self.global_mean

        u = self.user_map[user_id]
        i = self.item_map[item_id]

        pred = (
            self.global_mean
            + self.user_bias[u]
            + self.item_bias[i]
            + np.dot(self.user_factors[u], self.item_factors[i])
        )
        return float(np.clip(pred, 0.5, 5.0))
