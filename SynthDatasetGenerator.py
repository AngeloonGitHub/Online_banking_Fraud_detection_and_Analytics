import pandas as pd
import numpy as np
from faker import Faker

# Initialisation de Faker
fake = Faker()
np.random.seed(42)

# Nombre de transactions à générer
n_samples = 15_000

# Types de transactions
transaction_types = ["CASH_OUT", "PAYMENT", "CASH_IN", "TRANSFER", "DEBIT"]

# Génération des données
transactions = []
usernames = [fake.user_name() for _ in range(n_samples // 2)]  # Liste d'utilisateurs fictifs

for _ in range(n_samples):
    step = np.random.choice(range(1, 8))
    trans_type = np.random.choice(transaction_types, p=[0.3, 0.3, 0.2, 0.15, 0.05])
    amount = round(np.random.uniform(10, 19999), 2)
    oldbalanceOrig = round(np.random.uniform(0, 25560), 2)
    oldbalanceDest = round(np.random.uniform(0, 15000), 2)  # Initialisation ici
    newbalanceDest = oldbalanceDest  # Nouvelle initialisation pour éviter des erreurs

    isFraud = 0
    isAlertedFraud = 0

    user_orig = np.random.choice(usernames)
    user_dest = np.random.choice(usernames)

    # Assurer la cohérence des transactions où expéditeur et destinataire sont identiques
    if trans_type in ["TRANSFER", "DEBIT"]:
        user_dest = user_orig

    # Règles spécifiques aux fraudes
    if isinstance(step, (np.ndarray, pd.Series)):
        if (step > 4).any():  # Vérifie si au moins une valeur dépasse 4
            isAlertedFraud = 1
    else:
        if step > 4:
            isAlertedFraud = 1

    if trans_type in ["CASH_OUT", "TRANSFER", "DEBIT", "CASH_IN", "PAYMENT"] and np.random.rand() < 0.05:
        isFraud = 1  # 5% des transactions sont frauduleuses
    if trans_type in ["CASH_OUT", "TRANSFER"] and amount > 15000:
        isAlertedFraud = 1  # Les fraudes au-dessus de 15000 sont signalées
    if isFraud and user_orig == user_dest:
        isAlertedFraud = 1  # Usager suspect et fraudeur

    if trans_type == "CASH_IN" and oldbalanceDest == newbalanceDest:
        isFraud = 1  # Un dépôt d’argent doit modifier le solde du destinataire
    if trans_type == "PAYMENT" and oldbalanceDest == newbalanceDest and amount > 0:
        isFraud = 1  # Un paiement doit modifier le solde sauf s'il est annulé

    if isFraud:
        newbalanceDest = oldbalanceDest + np.random.uniform(-amount, amount / 2)  # Simule des fonds partiellement détournés
    else:
        newbalanceDest = oldbalanceDest + amount

    # Gestion des soldes après transaction
    newbalanceOrig = oldbalanceOrig - amount if oldbalanceOrig >= amount else oldbalanceOrig  # Gérer les comptes à découvert

    transactions.append([step, trans_type, user_orig, user_dest, amount, oldbalanceOrig, newbalanceOrig, oldbalanceDest, newbalanceDest, isAlertedFraud, isFraud])

# Création du DataFrame
df_synthetic = pd.DataFrame(transactions, columns=["step", "type", "user_orig", "user_dest", "amount", "oldbalanceOrig", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isAlertedFraud", "isFraud"])

# Sauvegarde
df_synthetic.to_csv("synthetic_transactions.csv", index=False)

print("Generated !")
