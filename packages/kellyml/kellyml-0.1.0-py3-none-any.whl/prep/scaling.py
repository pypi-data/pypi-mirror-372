from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler, Normalizer

def standard_scale(X_train, X_val, X_test):
    scaler = StandardScaler()
    return scaler.fit_transform(X_train), scaler.transform(X_val), scaler.transform(X_test)

def minmax_scale(X_train, X_val, X_test):
    scaler = MinMaxScaler()
    return scaler.fit_transform(X_train), scaler.transform(X_val), scaler.transform(X_test)

def robust_scale(X_train, X_val, X_test):
    scaler = RobustScaler()
    return scaler.fit_transform(X_train), scaler.transform(X_val), scaler.transform(X_test)

def maxabs_scale(X_train, X_val, X_test):
    scaler = MaxAbsScaler()
    return scaler.fit_transform(X_train), scaler.transform(X_val), scaler.transform(X_test)

def normalize(X_train, X_val, X_test, norm='l2'):
    scaler = Normalizer(norm=norm)
    return scaler.fit_transform(X_train), scaler.transform(X_val), scaler.transform(X_test)
