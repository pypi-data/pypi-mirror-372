from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder

def one_hot_encode(X_train, X_val, X_test, categorical_cols):
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return (encoder.fit_transform(X_train[categorical_cols]),
            encoder.transform(X_val[categorical_cols]),
            encoder.transform(X_test[categorical_cols]),
            encoder)

def label_encode(series):
    encoder = LabelEncoder()
    return encoder.fit_transform(series), encoder

def ordinal_encode(X_train, X_val, X_test, categorical_cols, categories="auto"):
    encoder = OrdinalEncoder(categories=categories)
    return (encoder.fit_transform(X_train[categorical_cols]),
            encoder.transform(X_val[categorical_cols]),
            encoder.transform(X_test[categorical_cols]),
            encoder)
