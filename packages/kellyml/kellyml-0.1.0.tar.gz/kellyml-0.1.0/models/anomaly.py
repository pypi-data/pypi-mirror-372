from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

def isolation_forest_anomaly(X_train, X_test, contamination=0.05):
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(X_train)
    return model, model.predict(X_test)  # -1 = anomaly, 1 = normal

def lof_anomaly(X_train, X_test, n_neighbors=20, contamination=0.05):
    model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination, novelty=True)
    model.fit(X_train)
    return model, model.predict(X_test)

def one_class_svm_anomaly(X_train, X_test, nu=0.05, kernel='rbf'):
    model = OneClassSVM(nu=nu, kernel=kernel)
    model.fit(X_train)
    return model, model.predict(X_test)
