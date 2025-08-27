from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR

def linear_regression_model(X_train, y_train, X_val):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model, model.predict(X_val)

def ridge_regression(X_train, y_train, X_val, alpha=1.0):
    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)
    return model, model.predict(X_val)

def lasso_regression(X_train, y_train, X_val, alpha=1.0):
    model = Lasso(alpha=alpha)
    model.fit(X_train, y_train)
    return model, model.predict(X_val)

def decision_tree_regressor(X_train, y_train, X_val, max_depth=None):
    model = DecisionTreeRegressor(max_depth=max_depth)
    model.fit(X_train, y_train)
    return model, model.predict(X_val)

def random_forest_regressor(X_train, y_train, X_val, n_estimators=100):
    model = RandomForestRegressor(n_estimators=n_estimators)
    model.fit(X_train, y_train)
    return model, model.predict(X_val)

def gradient_boosting_regressor(X_train, y_train, X_val, n_estimators=100):
    model = GradientBoostingRegressor(n_estimators=n_estimators)
    model.fit(X_train, y_train)
    return model, model.predict(X_val)

def svr_regressor(X_train, y_train, X_val, kernel='rbf'):
    model = SVR(kernel=kernel)
    model.fit(X_train, y_train)
    return model, model.predict(X_val)
