import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle


df = pd.read_csv('transactions.csv')


print("✅ Columns in dataset:", df.columns)


df.drop(columns=['transaction_id_anonymous', 'transaction_date', 'payee_id_anonymous'], inplace=True)


features = [
    'transaction_amount', 'transaction_channel', 'transaction_payment_mode_anonymous',
    'payment_gateway_bank_anonymous', 'payer_browser_anonymous', 'payer_email_anonymous',
    'payee_ip_anonymous', 'payer_mobile_anonymous'
]


missing_features = [col for col in features if col not in df.columns]
if missing_features:
    print(f"❌ Error: Missing columns in dataset: {missing_features}")
    exit()


label_encoders = {}
for col in ['transaction_channel', 'transaction_payment_mode_anonymous', 
            'payment_gateway_bank_anonymous', 'payer_browser_anonymous', 
            'payer_email_anonymous', 'payee_ip_anonymous', 'payer_mobile_anonymous']:
    label_encoders[col] = LabelEncoder()
    df[col] = label_encoders[col].fit_transform(df[col].astype(str))


X = df.drop(columns=['is_fraud'])  
y = df['is_fraud']

print("✅ Checking data types before training:")
print(X.dtypes)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)


with open('fraud_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model trained and saved successfully!")
