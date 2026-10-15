import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    HAS_XGBOOST = False
from app.features import extract_features

def load_dataset():
    print("[+] Building dataset samples...")
    benign = [
        "https://www.google.com",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://github.com/torvalds/linux",
        "https://stackoverflow.com/questions/tagged/python",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "https://www.amazon.in/gp/bestsellers",
        "https://docs.python.org/3/library/urllib.parse.html",
        "https://pypi.org/project/scikit-learn/",
        "https://fastapi.tiangolo.com/tutorial/first-steps/",
        "https://vitejs.dev/guide/",
        "https://react.dev/learn",
        "https://news.ycombinator.com/item?id=1"
    ]
    phishing = [
        "http://secure-login.bank-update.verify.com.auth.ru/login.php",
        "http://192.168.1.105/paypal/signin/index.html",
        "http://verification-service.account-recovery.support.co.vu/auth",
        "http://update.wallet-metamask.security-auth.net/sync",
        "http://amazon-prime-refund.verify-payment.top/claim",
        "http://appleid.apple.com.verify-identity.ru/signin",
        "http://netflix-billing-update.com.payment-gateway.cn/auth",
        "http://microsoft-outlook-web-access.security.tk/owa",
        "http://secure.chase-online.banking-update.xyz/login",
        "http://instagram-helpdesk.copyright-infringement.cc/action",
        "http://185.220.101.5/banking/signin.asp",
        "http://crypto-airdrop.claim-tokens.support.ml/connect"
    ]
    records = []
    for u in benign:
        feat = extract_features(u)
        records.append({"url": u, "label": 0, **{f"f_{i}": v for i, v in enumerate(feat["vector"])}})
    for u in phishing:
        feat = extract_features(u)
        records.append({"url": u, "label": 1, **{f"f_{i}": v for i, v in enumerate(feat["vector"])}})
    return pd.DataFrame(records)

def run():
    df = load_dataset()
    f_cols = [c for c in df.columns if c.startswith("f_")]
    X = df[f_cols].values
    y = df["label"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    print(f"[+] Dataset Ready: Train={len(X_train)}, Test={len(X_test)}")
    print("=" * 60)
    # Model 1: Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    rf_probs = rf.predict_proba(X_test)[:, 1]
    rf_preds = rf.predict(X_test)
    rf_auc = roc_auc_score(y_test, rf_probs)
    print(f"[1] Random Forest ROC-AUC: {rf_auc:.4f}")
    print("Classification Report (Random Forest):")
    print(classification_report(y_test, rf_preds, target_names=["Benign", "Phishing"], zero_division=0))
    print("=" * 60)
    # Model 2: XGBoost / Gradient Boosting
    if HAS_XGBOOST:
        gb = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, eval_metric="logloss", random_state=42)
        name = "XGBoost"
    else:
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
        name = "GradientBoosting"
    gb.fit(X_train, y_train)
    gb_probs = gb.predict_proba(X_test)[:, 1]
    gb_preds = gb.predict(X_test)
    gb_auc = roc_auc_score(y_test, gb_probs)
    print(f"[2] {name} ROC-AUC: {gb_auc:.4f}")
    print(f"Classification Report ({name}):")
    print(classification_report(y_test, gb_preds, target_names=["Benign", "Phishing"], zero_division=0))
    print("=" * 60)
    champ = gb if gb_auc > rf_auc else rf
    champ_name = name if gb_auc > rf_auc else "Random Forest"
    print(f"[+] Champion Model Selected: {champ_name}")
    save_path = os.path.join("app", "phishguard_rf.joblib")
    joblib.dump(champ, save_path)
    print(f"[+] Exported to {save_path} successfully!")

if __name__ == "__main__":
    run()
