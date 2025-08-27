from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC

def logistic_regression_classifier(X_train, y_train, X_val, penalty='l2', max_iter=1000):
    model = LogisticRegression(penalty=penalty, max_iter=max_iter)
    model.fit(X_train, y_train)
    return model, model.predict(X_val), model.predict_proba(X_val)[:,1]

def knn_classifier(X_train, y_train, X_val, n_neighbors=5, p=2):
    model = KNeighborsClassifier(n_neighbors=n_neighbors, p=p)
    model.fit(X_train, y_train)
    return model, model.predict(X_val), model.predict_proba(X_val)[:,1]

def decision_tree_classifier(X_train, y_train, X_val, max_depth=None):
    model = DecisionTreeClassifier(max_depth=max_depth)
    model.fit(X_train, y_train)
    return model, model.predict(X_val), model.predict_proba(X_val)[:,1]

def random_forest_classifier(X_train, y_train, X_val, n_estimators=100):
    model = RandomForestClassifier(n_estimators=n_estimators)
    model.fit(X_train, y_train)
    return model, model.predict(X_val), model.predict_proba(X_val)[:,1]

def svm_classifier(X_train, y_train, X_val, kernel='rbf', probability=True):
    model = SVC(kernel=kernel, probability=probability)
    model.fit(X_train, y_train)
    return model, model.predict(X_val), model.predict_proba(X_val)[:,1]
