import pandas as pd
from typing import List, Callable

from numpy import mean, int64
from sklearn.model_selection import KFold

from src.simcalibration.dg_models.DGModel import DGModel
from ml_models.MachineLearner import MachineLearner
from src.simcalibration.utils.Data import Data
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

pandas2ri.activate()

########################################################################################################################
# This class provides the functionality to evaluate Machine Learning benchmarking tasks
########################################################################################################################
class Evaluator:
    def __init__(self, ml_models: List[MachineLearner], dg_models: List[DGModel], real_models: List[DGModel],
                 scores: List[Callable], outcome_name: str = "Y"):
        self.scores = scores
        self.real_models = real_models
        self.ml_models = ml_models
        self.dg_models = dg_models
        self.outcome_name = outcome_name

    def realworld_benchmark(self, dg_model_real: DGModel, n_repetitions, n_samples: int, tr_frac: float):
        """
        :param dg_model_real: a real-world DagSim model
        :param n_repetitions: number of times to repeat training-testing
        :param n_samples: number of samples to generate for training + testing
        :param tr_frac: fraction of data for training
        :return: results: benchmarks in the shape {model_name: {score_name: list_of_score_values], ...}, ...}
        """
        results = pd.DataFrame(data=[[[] for _ in range(len(self.ml_models))] for __ in range(len(self.scores))],
                                      index=[sc.__name__ for sc in self.scores],
                                      columns=[md.name for md in self.ml_models])
        for _ in range(n_repetitions):
            orig_train_data, test_data = self._get_train_and_test_from_dg(dg_model_real, n_samples, tr_frac)
            assert len(orig_train_data) + len(test_data) == n_samples
            for ml_model in self.ml_models:
                result_per_repetition_per_model = self._develop_ml_model(ml_model, orig_train_data, test_data)
                for score_name in results.index.values.tolist():
                    results[ml_model.name][score_name].append(result_per_repetition_per_model[score_name])
        return results

    def realworld_benchmark_bootstrapping(self, dg_model_real: DGModel, n_samples: int, tr_frac: float, n_btstrps: int):
        """
        :param dg_model_real: a real-world DagSim model
        :param n_samples: number of samples to generate for training + testing
        :param tr_frac: fraction of data for training
        :param n_btstrps: number of times to perform bootstrapping
        :return: results: benchmarks in the shape {model_name: {score_name: list_of_score_values], ...}, ...}
        """
        orig_train_data, test_data = self._get_train_and_test_from_dg(dg_model_real, n_samples, tr_frac)

        assert len(orig_train_data) + len(test_data) == n_samples

        btstrp_results = pd.DataFrame(data=[[[] for _ in range(len(self.ml_models))] for __ in range(len(self.scores))],
                                      index=[sc.__name__ for sc in self.scores],
                                      columns=[md.name for md in self.ml_models])
        for _ in range(n_btstrps):
            btstr_tr = orig_train_data.bootstrap()
            for ml_model in self.ml_models:
                result_per_btsrtp_per_model = self._develop_ml_model(ml_model, btstr_tr, test_data)
                for score_name in btstrp_results.index.values.tolist():
                    btstrp_results[ml_model.name][score_name].append(result_per_btsrtp_per_model[score_name])
        return btstrp_results

    def meta_simulate(self, dg_model_real: DGModel, n_learning: int, n_train: int,n_test: int, n_true_repetitions: int, n_practitioner_repititions: int, n_sl_repititions: int, kfolds: int):
        """
        :param dg_model_real: a real-world DagSim model
        :param n_learning: number of samples to draw from n_train to use in learners
        :param n_train: number of samples to generate for training
        :param n_test: number of samples to generate for testing
        :param n_true_repetitions: number of times to repeat benchmarking in the true real-world
        :param n_practitioner_repititions: number of times to repeat benchmarking in a limited real-world
        :param n_sl_repititions: number of times to repeat benchmarking in the learner
        :param kfolds: number of k folds to perform in cross-validation
        :return: results: benchmarks in the shape {model_name: {learner: {score_name: list_of_score_values], ...}, ...}, ...}
        """
        list_of_ntrue_accuracies = {method.name: [] for method in self.ml_models}
        list_of_ntrue_cv_accuracies = {method.name: [] for method in self.ml_models}
        list_of_npractitioner_accuracies = {method.name: [] for method in self.ml_models}
        list_of_npractitioner_cv_accuracies = {method.name: [] for method in self.ml_models}
        list_of_nsl_accuracies = {learner.SLClass: {method.name: [] for method in self.ml_models} for learner in self.dg_models}
        list_of_nsl_cv_accuracies = {learner.SLClass: {method.name: [] for method in self.ml_models} for learner in self.dg_models}
        # Obtain true and practitioner accuracies
        dg_metrics, _, _, list_of_ntrue_cv_accuracies = self._get_performance_by_repetition_return_data(dg_model_real, n_train + n_test,0.5, n_true_repetitions, kfolds=kfolds)
        limited_dg_metrics, train_data_list, test_data_list, list_of_npractitioner_cv_accuracies = self._get_performance_by_repetition_return_data(dg_model_real, n_train + n_test,0.5, n_practitioner_repititions, kfolds=kfolds)

        # Store accuracies for true and practitioner models
        for ml in dg_metrics:
            list_of_ntrue_accuracies[ml] = dg_metrics[ml]['balanced_accuracy_score']
            list_of_npractitioner_accuracies[ml] = limited_dg_metrics[ml]['balanced_accuracy_score']

        # Begin practitioner repetitions
        for practitioner_rep in range(0, n_practitioner_repititions):
            print("Practitioner repetition: ", practitioner_rep)


            for dg_model in self.dg_models:
                print("Learner: ", dg_model.SLClass)
                repetition_results = pd.DataFrame(
                    data=[[[] for _ in range(len(self.ml_models))] for __ in range(len(self.scores))],
                    index=[sc.__name__ for sc in self.scores], columns=[md.name for md in self.ml_models])

                sl_temp_scores = {ml.name: [] for ml in self.ml_models}

                # Perform SL repetitions and capture metrics
                for sl_rep in range(0, n_sl_repititions):
                    sl_dg_metrics, sl_train_data, sl_test_data, current_cv_metrics = self._evaluate_bnlearn_dg_model(dg_model=dg_model,learning_data_real=train_data_list[practitioner_rep],n_learning=n_learning,n_train=n_train,n_test=n_test,SLClass=dg_model.SLClass, kfolds=kfolds)
                    for ml in self.ml_models:
                        sl_temp_scores[ml.name].append(current_cv_metrics[dg_model.SLClass][ml.name]['balanced_accuracy_score'])
                    for score_name in repetition_results.index:
                        for ml in self.ml_models:
                            repetition_results[ml.name][score_name].append(sl_dg_metrics[dg_model.SLClass][ml.name][score_name])
                for ml in self.ml_models:
                    for score_name in repetition_results.index:
                        repetition_results[ml.name][score_name] = mean(repetition_results[ml.name][score_name])
                        list_of_nsl_accuracies[dg_model.SLClass][ml.name].append(repetition_results[ml.name][score_name])
                    list_of_nsl_cv_accuracies[dg_model.SLClass][ml.name].append(mean(sl_temp_scores[ml.name]))
        print("----- Output of analysis -----")
        print("True real-world scenario all accuracies for all ml methods: ")
        print(list_of_ntrue_accuracies)
        print("True real-world scenario all avg cross-validation accuracies for all ml methods: ")
        print(list_of_ntrue_cv_accuracies)
        print("Limited real-world scenario all accuracies for all ml methods: ")
        print(list_of_npractitioner_accuracies)
        print("Limited real-world scenario all avg cross-validation accuracies for all ml methods: ")
        print(list_of_npractitioner_cv_accuracies)
        print("Learned worlds scenario all accuracies for all ml methods: ")
        print(list_of_nsl_accuracies)
        print("Learned worlds scenario all avg cross-validation accuracies for all ml methods: ")
        print(list_of_nsl_cv_accuracies)
        print("----- End of Analysis Output -----")
        pd.DataFrame(list_of_ntrue_accuracies).to_csv("ntrue_accuracies.csv")
        pd.DataFrame(list_of_ntrue_cv_accuracies).to_csv("ntrue_cv_accuracies.csv")
        pd.DataFrame(list_of_npractitioner_accuracies).to_csv("npractitioner_accuracies.csv")
        pd.DataFrame(list_of_npractitioner_cv_accuracies).to_csv("npractitioner_cv_accuracies.csv")
        pd.DataFrame(list_of_nsl_accuracies).to_csv("nsl_accuracies.csv")
        pd.DataFrame(list_of_nsl_cv_accuracies).to_csv("nsl_cv_accuracies.csv")
        return [list_of_ntrue_accuracies, list_of_npractitioner_accuracies, list_of_nsl_accuracies, n_true_repetitions, n_practitioner_repititions, n_sl_repititions, self.dg_models, self.ml_models, list_of_ntrue_cv_accuracies, list_of_npractitioner_cv_accuracies, list_of_nsl_cv_accuracies]

    def _evaluate_ml_model(self, ml_model: MachineLearner, test_data: Data):
        """
        Given a **trained** ml model, evaluate its performance using all the defined metrics on the test set.
        :param ml_model: the ml model to evaluate
        :param test_data: the test data to use to evaluate the ml model
        :return: metrics: benchmarks in the shape {model_name: {score_name: list_of_score_values], ...}, ...}
        """
        y_pred = ml_model.predict(test_data)
        metrics = {}
        for score in self.scores:
            metrics.update({score.__name__: score(y_pred=y_pred, y_true=test_data.y)})
        return metrics

    def _develop_all_ml_models(self, train_data: Data, test_data: Data):
        """
        Evaluate a training and test set on all ml models.
        :param train_data: the training set
        :param test_data: the test data
        :return: metrics: benchmarks in the shape {model_name: {score_name: list_of_score_values], ...}, ...}
        """
        metrics = {}
        for ml_model in self.ml_models:
            metrics[f'{ml_model.name}'] = self._develop_ml_model(ml_model=ml_model, train_data=train_data,test_data=test_data)
        return metrics

    def _evaluate_bnlearn_dg_model(self, dg_model: DGModel, learning_data_real, n_learning: int, n_train: int, n_test: int, SLClass: str, kfolds: int):
        """
        Evaluate a limited dataset using a learner, perform ml evaluation and return benchmarks using the learner.
        :param dg_model: a learner model
        :param learning_data_real: the training set to be given to the learner algorithm
        :param n_learning: the number of samples to be spliced from a dataset specifically for the learner (keep at 0)
        :param n_train: the number of samples for the training set
        :param n_test: the number of samples for the test set
        :param SLClass: the label for the learner
        :return: results: the benchmarks from learner, the training dataset and the test dataset
        """
        learning_data_real = learning_data_real.all

        if SLClass == "hc":
            robjects.r('''
                        if(!require(bnlearn)) install.packages('bnlearn')
                        if(!require(plyr)) install.packages('plyr')
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)         
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- hc(learning_data_real)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "tabu":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)         
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- tabu(learning_data_real)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "rsmax2":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)    
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- rsmax2(learning_data_real)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "mmhc":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)     
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- mmhc(learning_data_real)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "h2pc":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)        
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- h2pc(learning_data_real)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "gs":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)           
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- cextend(gs(learning_data_real), strict=FALSE)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "iamb":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)          
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- cextend(iamb(learning_data_real), strict=FALSE)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "fast.iamb":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)        
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- cextend(fast.iamb(learning_data_real), strict=FALSE)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')
        elif SLClass == "iamb.fdr":
            robjects.r('''
                        library(bnlearn)
                        library(plyr)
                        bn_learn <- function(learning_data_real, n_train, n_test, verbose=FALSE) {     
                        learning_data_real <- data.frame(lapply(learning_data_real,as.factor), stringsAsFactors=TRUE)             
                        check_and_modify_levels <- function(column){
                        num_levels <- length(levels(column))
                        if(num_levels==1){
                        new_levels <- c("0","1")
                        column <- factor(column, levels = new_levels)
                        }
                        return(column)
                        }
                        learning_data_real <- data.frame(lapply(learning_data_real,check_and_modify_levels))
                        my_bn <- cextend(iamb.fdr(learning_data_real), strict=FALSE)
                        fit = bn.fit(my_bn, learning_data_real)
                        training_output = rbn(fit, n_train, keep.fitted = TRUE)
                        testing_output = rbn(fit, n_test, keep.fitted = TRUE)
                        list_output <- list(na.omit(training_output), na.omit(testing_output))
                        }
                        ''')

        bn_hc = robjects.r['bn_learn']
        bn_train_output = bn_hc(learning_data_real, n_train, n_test)

        train_data = np.array(bn_train_output[0], dtype=int64)
        test_data = np.array(bn_train_output[1], dtype=int64)
        X = pd.DataFrame(train_data[:, :-1])
        y = pd.Series(train_data[:, -1], name="Y")
        train_data = Data(name="train", X=X, y=y)
        X = pd.DataFrame(test_data[:, :-1])
        y = pd.Series(test_data[:, -1], name="Y")
        test_data = Data(name="test", X=X, y=y)

        kf = KFold(n_splits=kfolds, shuffle=True, random_state=42)
        cv_metrics = {}

        for ml_model in self.ml_models:
            model_name = ml_model.name
            model_fold_metrics = []

            for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

                fold_train_data = Data(name="train_fold", X=X_train, y=y_train)
                fold_val_data = Data(name="val_fold", X=X_val, y=y_val)

                ml_model.learn(fold_train_data)
                fold_scores = self._evaluate_ml_model(ml_model, fold_val_data)
                model_fold_metrics.append(fold_scores)
            avg_model_metrics = {
                metric: np.mean([fold[metric] for fold in model_fold_metrics])
                for metric in model_fold_metrics[0]
            }
            if SLClass not in cv_metrics:
                cv_metrics[SLClass] = {}
            cv_metrics[SLClass][model_name] = avg_model_metrics

        metrics = self._develop_all_ml_models(train_data, test_data)
        metrics = {f'{dg_model.name}': metrics}
        learning_data = train_data[0:n_learning:1] if n_learning > 0 else None
        return metrics, learning_data, test_data, cv_metrics

    def _get_performance_by_repetition(self, dg_model: DGModel, n_samples_real: int, tr_frac: float, n_reps: int,test_data=None):
        """
        Evaluate a data-generating model by a specified number of samples, train/test split and number of repetitions.
        :param dg_model: the data-generating model
        :param n_samples_real: the number of samples to use in the training and test sets
        :param tr_frac: the training-test split to divide samples by
        :param n_reps: the number of repetitions to repeat benchmarks
        :return: results: benchmarks by repetition, the training dataset and the test dataset
        """
        all_scores = {ml_model.name: {score.__name__: [] for score in self.scores} for ml_model in self.ml_models}
        train_data = None
        for rep in range(n_reps):
            train_data = dg_model.generate(int(n_samples_real * tr_frac), self.outcome_name)
            test_data = dg_model.generate(int(n_samples_real * (1 - tr_frac)), self.outcome_name)
            for ml_model in self.ml_models:
                scores = self._develop_ml_model(ml_model, train_data, test_data)
                for score_name in scores.keys():
                    all_scores[ml_model.name][score_name].append(scores[score_name])
        return all_scores, train_data, test_data

    def _get_performance_by_repetition_return_data(self, dg_model: DGModel, n_samples_real: int, tr_frac: float, n_reps: int,kfolds: int, test_data=None):
        """
        Evaluate a data-generating model by a specified number of samples, train/test split and number of repetitions. Return the training datasets per repetition.
        :param dg_model: the data-generating model
        :param n_samples_real: the number of samples to use in the training and test sets
        :param tr_frac: the training-test split to divide samples by
        :param n_reps: the number of repetitions to repeat benchmarks
        :return: results: benchmarks by repetition, the training datasets and the test datasets
        """
        all_scores = {ml_model.name: {score.__name__: [] for score in self.scores} for ml_model in self.ml_models}
        cv_scores = {ml_model.name: [] for ml_model in self.ml_models}
        train_data = None
        train_data_list = []
        test_data_list = []
        for rep in range(n_reps):
            train_data = dg_model.generate(int(n_samples_real * tr_frac), self.outcome_name)
            train_data_list.append(train_data)
            test_data = dg_model.generate(int(n_samples_real * (1 - tr_frac)), self.outcome_name)
            test_data_list.append(test_data)
            for ml_model in self.ml_models:
                scores = self._develop_ml_model(ml_model, train_data, test_data)
                for score_name in scores.keys():
                    all_scores[ml_model.name][score_name].append(scores[score_name])

            # Perform cross-validation on training data
            fold_scores = {ml_model.name: [] for ml_model in self.ml_models}
            # Split train_data into kfolds and perform cross-validation
            kf = KFold(n_splits=kfolds)
            for train_idx, val_idx in kf.split(train_data):
                fold_train_data = train_data[train_idx]
                fold_val_data = train_data[val_idx]

                for ml_model in self.ml_models:
                    fold_score = self._develop_ml_model(ml_model, fold_train_data, fold_val_data)['balanced_accuracy_score']
                    fold_scores[ml_model.name].append(fold_score)
            # Calculate mean score across folds and store in cv_scores
            for ml_name, scores in fold_scores.items():
                mean_cv_score = sum(scores) / kfolds
                cv_scores[ml_name].append(mean_cv_score)

        return all_scores, train_data_list, test_data_list, cv_scores


    def _develop_ml_model(self, ml_model: MachineLearner, train_data: Data, test_data: Data):
        '''
        For a given ml model, train it on the provided training set and evaluate it on the test set.
        '''
        ml_model.learn(train_data)
        scores = self._evaluate_ml_model(ml_model, test_data)
        return scores

    def _get_train_and_test_from_dg(self, dg_model_real, n_samples, tr_frac):
        '''
        For a given data-generating model, generate both a training and test set.
        '''
        train_data = dg_model_real.generate(int(n_samples * tr_frac), self.outcome_name)
        test_data = dg_model_real.generate(int(n_samples * (1 - tr_frac)), self.outcome_name)
        return train_data, test_data
