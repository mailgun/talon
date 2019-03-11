# -*- coding: utf-8 -*-

"""The module's functions could init, train, save and load a classifier.
The classifier could be used to detect if a certain line of the message
body belongs to the signature.
"""

from __future__ import absolute_import

from numpy import genfromtxt
from sklearn.externals import joblib
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.model_selection import RandomizedSearchCV, RepeatedStratifiedKFold, cross_val_score
from scipy.stats import expon
import matplotlib.pyplot as plt
import numpy as np
    


def init():
    """Inits classifier with optimal options."""
    return LinearSVC(C=10.0)


def train(classifier, train_data_filename, save_classifier_filename=None):
    """Trains and saves classifier so that it could be easily loaded later."""
    file_data = genfromtxt(train_data_filename, delimiter=",")
    train_data, labels = file_data[:, :-1], file_data[:, -1]
    classifier.fit(train_data, labels)

    if save_classifier_filename:
        joblib.dump(classifier, save_classifier_filename)
    return classifier


def load(saved_classifier_filename, train_data_filename):
    """Loads saved classifier. """
    try:
        return joblib.load(saved_classifier_filename)
    except Exception:
        import sys
        if sys.version_info > (3, 0):
            return load_compat(saved_classifier_filename)

        raise


def load_compat(saved_classifier_filename):
    import os
    import pickle
    import tempfile

    # we need to switch to the data path to properly load the related _xx.npy files
    cwd = os.getcwd()
    os.chdir(os.path.dirname(saved_classifier_filename))

    # convert encoding using pick.load and write to temp file which we'll tell joblib to use
    pickle_file = open(saved_classifier_filename, 'rb')
    classifier = pickle.load(pickle_file, encoding='latin1')

    try:
        # save our conversion if permissions allow
        joblib.dump(classifier, saved_classifier_filename)
    except Exception:
        # can't write to classifier, use a temp file
        tmp = tempfile.SpooledTemporaryFile()
        joblib.dump(classifier, tmp)
        saved_classifier_filename = tmp

    # important, use joblib.load before switching back to original cwd
    jb_classifier = joblib.load(saved_classifier_filename)
    os.chdir(cwd)

    return jb_classifier

def gather_params_for_classifier_training(classifier_choice, test_type):
    n_params_sampled = 20
    outer_cv_n_repeats = 2
    inner_cv_n_repeats = 2
    param_dist = {'C': expon(scale=10), 'kernel': ['linear'], 'class_weight':['balanced']}
    clf = SVC()
    print("Training setup")
    print()
    if(classifier_choice=="linear svm"):
        param_dist = {'C': expon(scale=10), 'kernel': ['linear'], 'class_weight':['balanced']}
        clf = SVC()
        param_plot = ['C']
        print("Classifier: Linear SVM")
    if classifier_choice=="rbf svm":
        param_dist = {'C': expon(scale=10), 'gamma': expon(scale=.1), 'kernel': ['rbf'], 'class_weight':['balanced']}
        clf = SVC()
        param_plot = ['C', 'gamma']
        print("Classifier: RBF kernel SVM")
    if classifier_choice=="poly svm":
        param_dist = {'C': expon(scale=10), 'gamma': expon(scale=.1), 'kernel': ['poly'], 'degree':[2,3,4,5,6,7,8,9], 'class_weight':['balanced']}
        clf = SVC()
        param_plot = ['C', 'degree', 'gamma']
        print("Classifier: Poly kernel SVM")
    if classifier_choice=="original":
        param_dist = {}
        clf = init()
        param_plot = []
        print("Classifier: Linear SVM")
        print("C: 10")
    if(test_type=='legit'):
        n_params_sampled = 100
        inner_cv_n_repeats = 5
        outer_cv_n_repeats = 5
    if(test_type=='test'):
        n_params_sampled = 20
        inner_cv_n_repeats = 2
        outer_cv_n_repeats = 2
    print("#Params sampled: ")
    print(n_params_sampled)
    print("Inner CV #repeats: ")
    print(inner_cv_n_repeats)
    print("Outer CV #repeats: ")
    print(outer_cv_n_repeats)
    print("--")

    return {'param_dist':param_dist, 'clf':clf, 'n_params_sampled':n_params_sampled, 'param_plot':param_plot, 'inner_cv_n_repeats':inner_cv_n_repeats, 'outer_cv_n_repeats':outer_cv_n_repeats}
    


def train_withcv(train_data_filename, save_classifier_filename=None, classifier_choice="linear svm", test_type='test'):
    """Nested cross validates, finds optimum parameters, trains and saves classifier so that it could be easily loaded later."""
    file_data = genfromtxt(train_data_filename, delimiter=",")
    train_data, labels = file_data[:, :-1], file_data[:, -1]
    scoring = {'accuracy':'accuracy'}#, 'f1':'f1', 'precision':'precision', 'recall':'recall'}
    training_params_dict = gather_params_for_classifier_training(classifier_choice, test_type)

    # Estimate generalized performance of model
    clf = training_params_dict.get('clf')
    param_distributions = training_params_dict.get('param_dist')
    n_params_sampled = training_params_dict.get('n_params_sampled')
    
    inner_cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=training_params_dict.get('inner_cv_n_repeats'))
    random_search = RandomizedSearchCV(estimator=clf, param_distributions=param_distributions, n_iter=n_params_sampled, cv=inner_cv, scoring=scoring, refit='accuracy')
    outer_cv = RepeatedStratifiedKFold(n_splits=6, n_repeats=training_params_dict.get('outer_cv_n_repeats'))
    nested_score = cross_val_score(random_search, X=train_data, y=labels, cv=outer_cv)

    # Fit model with best params 
    random_search.fit(X=train_data, y=labels)
    classifier = random_search.best_estimator_
    
    print("Final model trained on full dataset with repeated stratified kfold cv")
    print("Best params: "+str(random_search.best_params_))
    print("Best accuracy score: "+str(random_search.best_score_))
    print()
    print("Expected performance on test data measured used nestedcv")
    print(nested_score.mean())

    #Plot validation curves
    param_list_to_plot = training_params_dict.get('param_plot')
    plot_validation_curve(param_list_to_plot, list(scoring.keys())[0], random_search.cv_results_)

    if save_classifier_filename:
        joblib.dump(classifier, save_classifier_filename)
    return classifier


def plot_validation_curve(param_list_to_plot, score_name, cv_results):
    for param in param_list_to_plot:
        param_string = "param_" + param
        plt.title("Validation Curve with SVM")
        plt.xlabel(param_string)
        plt.ylabel("Score")
        lw = 2
        param_x_vals = np.asarray(cv_results.get(param_string))
        try:
            param_x_vals = np.asfarray(param_x_vals)
        except:
            print(param+" is a non numeric parameter")
        #Sort the param values
        arg_sort_idx = np.argsort(param_x_vals)
        param_x_vals = np.sort(param_x_vals)
        train_scores_mean = cv_results.get("mean_train_"+score_name)[arg_sort_idx]
        train_scores_std = cv_results.get("std_train_"+score_name)[arg_sort_idx]
        test_scores_mean = cv_results.get("mean_test_"+score_name)[arg_sort_idx]
        test_scores_std = cv_results.get("std_test_"+score_name)[arg_sort_idx]
        ylim_min = min(min(train_scores_mean-train_scores_std), min(test_scores_mean-test_scores_std))*0.95
        plt.ylim(ylim_min, 1)

        plt.plot(param_x_vals, train_scores_mean, label="Training score", color="darkorange", linewidth=lw)
        plt.fill_between(param_x_vals, train_scores_mean - train_scores_std, train_scores_mean + train_scores_std, alpha=0.2, color="darkorange", linewidth=lw)
        plt.plot(param_x_vals, test_scores_mean, label="Cross-validation score", color="navy", linewidth=lw)
        plt.fill_between(param_x_vals, test_scores_mean - test_scores_std, test_scores_mean + test_scores_std, alpha=0.2, color="navy", lw=lw)
        plt.legend(loc="best")
        plt.show()


