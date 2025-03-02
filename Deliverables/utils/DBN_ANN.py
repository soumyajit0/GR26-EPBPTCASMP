import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer  # returns a sparse matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from xgboost import XGBClassifier
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# ... (rest of your code)
# =============================================================================
# --- ANN & DBN Models (PyTorch) ---
# =============================================================================

# ---------- ANN Model ----------
class ANN(nn.Module):
    def __init__(self, input_dim):
        super(ANN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 1)  # Binary classification output
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.sigmoid(self.fc2(x))
        return x

def train_ann_model(X_train, y_train, input_dim, epochs=20, batch_size=64, lr=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ANN(input_dim).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train.reshape(-1, 1)))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch_X, batch_y in loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch_X.size(0)
    return model

# ---------- DBN Model (with RBM Pretraining) ----------
class RBM(nn.Module):
    def __init__(self, n_vis, n_hid):
        super(RBM, self).__init__()
        self.W = nn.Parameter(torch.randn(n_vis, n_hid) * 0.01)
        self.h_bias = nn.Parameter(torch.zeros(n_hid))
        self.v_bias = nn.Parameter(torch.zeros(n_vis))

    def sample_h(self, v):
        prob = torch.sigmoid(torch.matmul(v, self.W) + self.h_bias)
        return prob, torch.bernoulli(prob)

    def sample_v(self, h):
        prob = torch.sigmoid(torch.matmul(h, self.W.t()) + self.v_bias)
        return prob, torch.bernoulli(prob)

class DBN(nn.Module):
    def __init__(self, input_dim, hidden_dims):
        super(DBN, self).__init__()
        self.rbm_layers = nn.ModuleList()
        dims = [input_dim] + hidden_dims
        for i in range(len(dims) - 1):
            self.rbm_layers.append(RBM(dims[i], dims[i+1]))
        # Final supervised layer for binary classification
        self.classifier = nn.Linear(dims[-1], 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        for rbm in self.rbm_layers:
            x = torch.sigmoid(torch.matmul(x, rbm.W) + rbm.h_bias)
        x = self.classifier(x)
        x = self.sigmoid(x)
        return x

def pretrain_rbm(rbm, train_loader, epochs=5, lr=0.01, k=1):
    optimizer = optim.SGD(rbm.parameters(), lr=lr)
    for epoch in range(epochs):
        for batch in train_loader:
            v, _ = batch
            v = v.view(v.size(0), -1)
            prob_h, h_sample = rbm.sample_h(v)
            v_model = v
            for _ in range(k):
                prob_h, h_sample = rbm.sample_h(v_model)
                prob_v, v_model = rbm.sample_v(h_sample)
            loss = torch.mean((v - v_model) ** 2)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

def train_dbn_model(X_train, y_train, input_dim, hidden_dims=[128, 64],
                    pretrain_epochs=5, fine_tune_epochs=20, batch_size=64, lr=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tensor_X = torch.FloatTensor(X_train)
    dataset = TensorDataset(tensor_X, torch.zeros(tensor_X.size(0)))  # Dummy labels for RBM training
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    dbn = DBN(input_dim, hidden_dims).to(device)
    current_input = tensor_X.clone()
    for i, rbm in enumerate(dbn.rbm_layers):
        layer_dataset = TensorDataset(current_input, torch.zeros(current_input.size(0)))
        layer_loader = DataLoader(layer_dataset, batch_size=batch_size, shuffle=True)
        pretrain_rbm(rbm, layer_loader, epochs=pretrain_epochs, lr=lr)
        new_inputs = []
        with torch.no_grad():
            for batch, _ in layer_loader:
                batch = batch.to(device)
                prob_h, _ = rbm.sample_h(batch)
                new_inputs.append(prob_h.cpu())
        current_input = torch.cat(new_inputs, dim=0)

    tensor_y = torch.FloatTensor(y_train.reshape(-1, 1))
    fine_tune_dataset = TensorDataset(torch.FloatTensor(X_train), tensor_y)
    fine_tune_loader = DataLoader(fine_tune_dataset, batch_size=batch_size, shuffle=True)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(dbn.parameters(), lr=lr)

    dbn.train()
    for epoch in range(fine_tune_epochs):
        epoch_loss = 0.0
        for batch_X, batch_y in fine_tune_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = dbn(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch_X.size(0)
    return dbn

# =============================================================================
# --- Prevent Script Execution ---
# =============================================================================
if __name__ == "__main__":
    print("⚠️ This script defines ANN and DBN models and should only be imported, not executed directly.")
