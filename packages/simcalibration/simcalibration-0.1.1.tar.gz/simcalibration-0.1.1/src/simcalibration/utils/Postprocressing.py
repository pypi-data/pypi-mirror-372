import os
from statistics import variance

import matplotlib.pyplot as plt
import pandas as pd
import scipy
from matplotlib import transforms
from matplotlib.pyplot import scatter
from numpy import mean, int64
from transpose_dict import TD
from scipy.stats import sem, kendalltau, rankdata, stats
import numpy as np
import seaborn as sns
figuredirname = os.sep+"figures"+os.sep

class Postprocessing():
    def __init__(self):
        if os.path.isdir(os.getcwd() + figuredirname) == False:
            os.mkdir(os.getcwd() + figuredirname)
        pass

    def realworld_benchmarks_visualise(self, analysis0_results: pd.DataFrame):
        score_names = analysis0_results.index
        for score_name in score_names:
            y = [np.mean(analysis0_results[alg][score_name]) for alg in analysis0_results.columns]
            y_err = [scipy.stats.sem(analysis0_results[alg][score_name]) for alg
                       in analysis0_results.columns]

            alg_names = analysis0_results.columns
            x_pos = np.arange(len(alg_names))

            fig, ax = plt.subplots()
            ax.bar(x_pos, y, yerr=y_err, align='center', alpha=0.5, ecolor='black', capsize=10)
            ax.set_ylim(0, 1)
            ax.set_ylabel(score_name)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(alg_names, rotation=90)
            # ax.set_title(f'{score_name} of different ML models')
            ax.yaxis.grid(True)

            # Save the figure and show
            plt.tight_layout()
            plt.savefig(os.getcwd()+figuredirname+'realworld_benchmarks_bar_plot_with_error_bars.png')
            plt.show()

    def realworld_benchmarks_bootstrapping_visualise(self, analysis1_results: pd.DataFrame):
        score_names = analysis1_results.index
        for score_name in score_names:
            y = [np.mean(analysis1_results[alg][score_name]) for alg in analysis1_results.columns]

            y_err = [scipy.stats.sem(analysis1_results[alg][score_name]) for alg
                       in analysis1_results.columns]
            alg_names = analysis1_results.columns
            x_pos = np.arange(len(alg_names))

            fig, ax = plt.subplots()
            ax.bar(x_pos, y, yerr=y_err, align='center', alpha=0.5, ecolor='black', capsize=10)
            ax.set_ylim(0, 1)
            ax.set_ylabel(score_name)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(alg_names, rotation=90)
            # ax.set_title(f'{score_name} of different ML models')
            ax.yaxis.grid(True)

            # Save the figure and show
            plt.tight_layout()
            plt.savefig(os.getcwd()+figuredirname+'realworld_benchmarks_bootstrapped_bar_plot_with_error_bars.png')
            plt.show()

    def meta_simulation_visualise(self, results: list):
        list_of_ntrue_accuracies = results[0]
        list_of_npractitioner_accuracies = results[1]
        list_of_nsl_accuracies = results[2]
        n_true_repetitions = results[3]
        n_practitioner_repititions = results[4]
        n_sl_repititions = results[5]
        self.dg_models = results[6]
        self.ml_models = results[7]
        list_of_ntrue_cv_accuracies = results[8]
        list_of_npractitioner_cv_accuracies = results[9]
        list_of_nsl_cv_accuracies = results[10]
        ml_labels = [ml.name for ml in self.ml_models]
        sl_colors = {"hc": 'red', "tabu": 'blue', "rsmax2": 'green', "mmhc": 'yellow', "h2pc": 'orange', "gs": "cyan","pc.stable": "brown", "limited-real": "pink"}
        sl_offset = {"hc": 2, "tabu": 4, "rsmax2": 6, "mmhc": 8, "h2pc": 10, "gs": 12, "pc.stable": 14}
        sns.set_style("darkgrid")
        sns.set_context("notebook")
        # Cross-validation visualisations
        mean_cv_accuracies = {ml_method: mean(accuracies) for ml_method, accuracies in list_of_ntrue_cv_accuracies.items()}

        ranked_cv_ml_methods = sorted(mean_cv_accuracies, key=mean_cv_accuracies.get, reverse=False)
        # Create boxplot for relative performance per pathways across all repetition for all ml methods
        output_pd_cv = pd.DataFrame(
            columns=['est', 'avgml', 'est-to-avgml', 'true', 'est-true', 'ML_method', 'SL', 'repetition'])
        for practitioner_rep in range(n_practitioner_repititions):
            ml_method_cv_performance_list = []

            for ml in self.ml_models:
                ml_method_cv_performance_list.append(list_of_npractitioner_cv_accuracies[ml.name][practitioner_rep])
            avg_ml_cv_rep_performance = mean(ml_method_cv_performance_list)

            for ml in self.ml_models:
                true_cv_performance = mean(list_of_ntrue_cv_accuracies[ml.name])
                practitioner_cv_performance = list_of_npractitioner_cv_accuracies[ml.name][practitioner_rep]
                output_pd_cv = output_pd_cv.append({'est': practitioner_cv_performance, 'avgml': avg_ml_cv_rep_performance,
                                            'est-to-avgml': practitioner_cv_performance - avg_ml_cv_rep_performance,
                                            'true': true_cv_performance,
                                            'est-true': practitioner_cv_performance - true_cv_performance,
                                            'ML_method': ml.name, 'SL': 'limited-real', 'repetition': practitioner_rep},
                                           ignore_index=True)
        for sl in self.dg_models:
            for practitioner_rep in range(n_practitioner_repititions):
                ml_method_cv_performance_list = []

                for ml in self.ml_models:
                    ml_method_cv_performance_list.append(list_of_nsl_cv_accuracies[sl.SLClass][ml.name][practitioner_rep])
                avg_ml_cv_rep_performance = mean(ml_method_cv_performance_list)

                for ml in self.ml_models:
                    sl_cv_performance = list_of_nsl_cv_accuracies[sl.SLClass][ml.name][practitioner_rep]
                    true_cv_performance = mean(list_of_ntrue_cv_accuracies[ml.name])
                    output_pd_cv = output_pd_cv.append({'est': sl_cv_performance, 'avgml': avg_ml_cv_rep_performance,
                                            'est-to-avgml': sl_cv_performance - avg_ml_cv_rep_performance,
                                            'true': true_cv_performance,
                                            'est-true': sl_cv_performance - true_cv_performance, 'ML_method': ml.name,
                                            'SL': sl.SLClass, 'repetition': practitioner_rep}, ignore_index=True)
        output_pd_cv.to_csv("meta_simulation_cv_performance_per_repetition.csv")
        output_pd_cv['ML_method'] = pd.Categorical(output_pd_cv['ML_method'], categories=ranked_cv_ml_methods, ordered=True)

        performance_diff_avgmean_table = output_pd_cv.pivot_table(index='SL', columns='ML_method', values='est-to-avgml',aggfunc='mean')
        performance_diff_avgmean_table.to_csv("meta_simulation_cv_performance_difference_avgmean_table.csv")

        performance_diff_true_table = output_pd_cv.pivot_table(index='SL', columns='ML_method', values='est-true',aggfunc='mean')
        performance_diff_true_table.to_csv("meta_simulation_cv_performance_difference_true_table.csv")


        plt.figure(figsize=(10, 10), dpi=300)
        sns.boxplot(x=output_pd_cv['ML_method'], y=output_pd_cv['est-true'], hue=output_pd_cv['SL'], palette=sl_colors,showfliers=True,showmeans=True,meanprops={"marker":"o","markerfacecolor":"black", "markeredgecolor":"grey","markersize":"5"},order=ranked_cv_ml_methods)
        plt.title('Boxplot of CV difference to true by ML method for strategies')
        plt.ylabel('Difference to True (CV)')
        plt.xlabel('ML Method (least performing to best)')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_cv_diff_to_true_xaxis_ordered.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        sns.boxplot(x=output_pd_cv['ML_method'], y=output_pd_cv['est-to-avgml'], hue=output_pd_cv['SL'], palette=sl_colors,showfliers=True,showmeans=True,meanprops={"marker": "o", "markerfacecolor": "black", "markeredgecolor": "grey", "markersize": "5"},order=ranked_cv_ml_methods)
        plt.title('Boxplot of CV difference to avg ml performances by ML method for strategies')
        plt.ylabel('Difference to Avg ML performance')
        plt.xlabel('ML Method (least performing to best)')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_cv_diff_to_avg_ml_performance.png')
        plt.show()

        # Scatterplot for cv
        scatter_cv_data = []
        list_of_xy_pairs_cv = []
        dict_of_xy_pairs_sl_cv = {learner.SLClass: [] for learner in self.dg_models}

        for practitioner_rep in range(n_practitioner_repititions):
            for ml in self.ml_models:
                list_of_xy_pairs_cv.append((mean(list_of_ntrue_cv_accuracies[ml.name]),list_of_npractitioner_cv_accuracies[ml.name][practitioner_rep]))
                for sl in dict_of_xy_pairs_sl_cv.keys():
                    dict_of_xy_pairs_sl_cv[sl].append((mean(list_of_ntrue_cv_accuracies[ml.name]),list_of_nsl_cv_accuracies[sl][ml.name][practitioner_rep]))


        fig = plt.figure(figsize=(10, 10), dpi=300)
        # Plot the scatter points for each SL model with offset
        for sl in dict_of_xy_pairs_sl_cv.keys():
            offset = lambda p: transforms.ScaledTranslation(p / 72., 0, plt.gcf().dpi_scale_trans)
            trans = plt.gca().transData
            x_cv_true, y_sl_cv = zip(*dict_of_xy_pairs_sl_cv[sl])
            corr, _ = kendalltau(x_cv_true, y_sl_cv)
            plt.scatter(x=x_cv_true, y=y_sl_cv, c=sl_colors[sl], s=8, label=sl, alpha=0.7,transform=trans + offset(sl_offset[sl]))
            scatter_cv_data.extend([x,y,sl] for x, y in zip(x_cv_true, y_sl_cv))

        # Add diagonal reference line
        plt.plot([0, 1], [0, 1], ls="--", c="grey", alpha=0.4)

        # Plot the main black points for cv accuracies with x-axis adjustment
        x_cv, y_cv = zip(*list_of_xy_pairs_cv)
        plt.scatter(x=x_cv, y=y_cv, color='black', label='limited-real', s=15, marker='x', alpha=1)
        scatter_cv_data.extend([x,y, 'limited-real'] for x, y in zip(x_cv, y_cv))

        for ml_index, ml_name in enumerate(ranked_cv_ml_methods):
            plt.axvline(x=mean_cv_accuracies[ml_name], ls='--', c='lightgrey', alpha=0.7)
        # Set limits and labels
        plt.xlim(0.45, 1)
        plt.ylim(0.45, 1)
        plt.title("Scatterplot of x-y pairs between true and CV-estimated performances")
        plt.xlabel("Accuracy (True CV Reference)")
        plt.ylabel("Accuracy (Estimated CV Performance)")
        plt.legend(loc='upper right')

        for ml_index, ml_name in enumerate(ranked_cv_ml_methods):
            plt.text(x=mean_cv_accuracies[ml_name], y=0.95, s=ml_name, fontsize=7, rotation='vertical', rotation_mode='anchor', horizontalalignment='center', verticalalignment='bottom', alpha=0.8)
        # Save and show the plot
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_scatterplot_every_practitioner_repetition_cv_accuracies_all_methods.png')
        plt.show()

        scatter_cv_df = pd.DataFrame(scatter_cv_data, columns=['True_CV_Accuracy', 'Estimated_CV_Accuracy', 'Strategy'])
        scatter_cv_df.to_csv(os.getcwd() + figuredirname + 'interworld_benchmarks_scatterplot_cv_true_est_accuracies_all_methods_table.csv', index=False)

        sl_differences_var_cv = pd.DataFrame(columns=['est-var', 'ML_method', 'SL'])
        for ml in self.ml_models:
            sl_differences_var_cv = sl_differences_var_cv.append({'est-var': np.var(list_of_npractitioner_cv_accuracies[ml.name]), 'ML_method': ml.name,'SL': 'limited-real'}, ignore_index=True)
        for ml in self.ml_models:
            for sl in self.dg_models:
                sl_differences_var_cv = sl_differences_var_cv.append({'est-var': np.var(list_of_nsl_cv_accuracies[sl.SLClass][ml.name]), 'ML_method': ml.name, 'SL': sl.SLClass},ignore_index=True)

        sl_differences_var_cv.to_csv("meta_simulation_cv_variance_per_ml_method.csv")

        variance_table = sl_differences_var_cv.pivot(index='SL', columns='ML_method', values='est-var')
        variance_table.to_csv("meta_simulation_cv_variance_table.csv")

        plt.figure(figsize=(10, 10), dpi=300)
        sns.barplot(x=sl_differences_var_cv['ML_method'], y=sl_differences_var_cv['est-var'],hue=sl_differences_var_cv['SL'], data=sl_differences_var_cv)
        plt.title('Grouped bar plot of variance across all CV repetitions for ML method performances between learners')
        plt.ylabel('Variance (CV) across datasets for ML method performance')
        plt.xlabel('ML Method')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_barplot_all_ml_methods_learner_cv_variance.png')
        plt.show()

        pairwise_variance_test_results = []
        ci_results_var_diff = []
        for ml in self.ml_models:
            practitioner_data = list_of_npractitioner_cv_accuracies[ml.name]
            practitioner_var = np.var(practitioner_data)

            for sl in self.dg_models:
                sl_data = list_of_nsl_cv_accuracies[sl.SLClass][ml.name]
                sl_var = np.var(sl_data)

                # F-test between SL and practitioner
                f_stat, p_value = stats.f_oneway(practitioner_data, sl_data)

                # Bootstrapped confidence intervals for variance differences
                boot_practitioner_var = np.random.choice(practitioner_data, size=(1000, len(practitioner_data)),replace=True).var(axis=1)
                boot_sl_var = np.random.choice(sl_data, size=(1000, len(sl_data)), replace=True).var(axis=1)
                boot_var_diff = boot_sl_var - boot_practitioner_var
                ci_lower, ci_upper = np.percentile(boot_var_diff, [2.5, 97.5])

                # Collect results
                pairwise_variance_test_results.append({
                    'ML_method': ml.name,
                    'SL': sl.SLClass,
                    'Practitioner_var': practitioner_var,
                    'SL_var': sl_var,
                    'F_stat': f_stat,
                    'p_value': p_value
                })

                ci_results_var_diff.append({
                    'ML_method': ml.name,
                    'SL': sl.SLClass,
                    'CI_var_diff_lower': ci_lower,
                    'CI_var_diff_upper': ci_upper
                })

        # Exporting Results
        pd.DataFrame(pairwise_variance_test_results).to_csv("meta_simulation_cv_pairwise_variance_test_results.csv", index=False)
        pd.DataFrame(ci_results_var_diff).to_csv("meta_simulation_cv_ci_results_variance.csv", index=False)

        # Regular visualisations
        output_pd = pd.DataFrame(columns=['est','avgml','est-to-avgml','true','est-true', 'ML_method', 'SL','repetition'])
        for practitioner_rep in range(0, n_practitioner_repititions):
            ml_method_performance_list = []
            #practitioner_rep_ml_methods = list_of_npractitioner_accuracies[practitioner_rep]
            for ml in self.ml_models:
                ml_method_performance_list.append(list_of_npractitioner_accuracies[ml.name][practitioner_rep])
            avg_ml_rep_performance = mean(ml_method_performance_list)
            for ml in self.ml_models:
                true_rep_ml_performance = mean(list_of_ntrue_accuracies[ml.name])
                practitioner_rep_ml_performance = list_of_npractitioner_accuracies[ml.name][practitioner_rep]
                output_pd = output_pd.append({'est': (practitioner_rep_ml_performance),'avgml': avg_ml_rep_performance,
                                                    'est-to-avgml': (practitioner_rep_ml_performance - avg_ml_rep_performance),
                                              'true': true_rep_ml_performance, 'est-true': (practitioner_rep_ml_performance - true_rep_ml_performance),
                                                    'ML_method': ml.name, 'SL': 'limited-real','repetition': practitioner_rep}, ignore_index=True)

        for sl in self.dg_models:
            for practitioner_rep in range(0, n_practitioner_repititions):
                ml_method_performance_list = []
                for ml in self.ml_models:
                    ml_method_performance_list.append(list_of_nsl_accuracies[sl.SLClass][ml.name][practitioner_rep])
                avg_ml_rep_performance = mean(ml_method_performance_list)
                for ml in self.ml_models:
                    sl_rep_ml_performance = list_of_nsl_accuracies[sl.SLClass][ml.name][practitioner_rep]
                    true_rep_ml_performance = mean(list_of_ntrue_accuracies[ml.name])
                    output_pd = output_pd.append({'est': sl_rep_ml_performance,'avgml': avg_ml_rep_performance, 'est-to-avgml': (sl_rep_ml_performance - avg_ml_rep_performance),'true': true_rep_ml_performance, 'est-true': (sl_rep_ml_performance - true_rep_ml_performance),'ML_method': ml.name, 'SL': sl.SLClass, 'repetition': practitioner_rep}, ignore_index=True)
        output_pd.to_csv("meta_simulation_performance_per_repetition.csv")

        # Create absolute match proportion bar graph between pathway's top ml method and true ml method
        matches_from_practitioner_limited_world = 0
        sl_match_counts = {learner.SLClass: 0 for learner in self.dg_models}
        for repetition in range(0, n_practitioner_repititions):
            list_of_comparable_ranks_in_one_repitition = {method.name: 0 for method in self.ml_models}
            list_of_comparable_ranks_in_one_repitition_b = {method.name: 0 for method in self.ml_models}
            for ml in self.ml_models:
                list_of_comparable_ranks_in_one_repitition[ml.name] = mean(list_of_ntrue_accuracies[ml.name])#[repetition]
                list_of_comparable_ranks_in_one_repitition_b[ml.name] = list_of_npractitioner_accuracies[ml.name][repetition]
            if max(list_of_comparable_ranks_in_one_repitition_b,key=list_of_comparable_ranks_in_one_repitition_b.get) == max(list_of_comparable_ranks_in_one_repitition, key=list_of_comparable_ranks_in_one_repitition.get):
                matches_from_practitioner_limited_world += 1
        for sl in sl_match_counts.keys():
            sl_match_count = 0
            for repetition in range(0, n_practitioner_repititions):
                list_of_comparable_ranks_in_one_repitition = {method.name: 0 for method in self.ml_models}
                list_of_comparable_ranks_in_one_repitition_b = {method.name: 0 for method in self.ml_models}
                for ml in self.ml_models:
                    list_of_comparable_ranks_in_one_repitition[ml.name] = mean(list_of_ntrue_accuracies[ml.name])#[repetition]
                    list_of_comparable_ranks_in_one_repitition_b[ml.name] = list_of_nsl_accuracies[sl][ml.name][repetition]
                if max(list_of_comparable_ranks_in_one_repitition_b,key=list_of_comparable_ranks_in_one_repitition_b.get) == max(list_of_comparable_ranks_in_one_repitition, key=list_of_comparable_ranks_in_one_repitition.get):
                    sl_match_count += 1
            sl_match_counts[sl] = sl_match_count / n_practitioner_repititions
        sl_match_counts["limited-real"] = matches_from_practitioner_limited_world / n_practitioner_repititions
        fig = plt.figure(figsize=(10, 10), dpi=300)
        plt.bar(list(sl_match_counts.keys()), list(sl_match_counts.values()), color='maroon', width=0.4)
        plt.xlabel("Technique")
        plt.ylabel("Percentage of correctly recommended ML methods")
        plt.title("Proportion of matched top ML methods from technique to true top benchmarks")
        plt.style.use("seaborn")
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_barplot_proportion_matches_max_method.png')
        plt.show()

        # Create scatterplot of relative performances for every repetition for all ml methods between alternative pathways
        scatter_data = []

        list_of_xy_pairs_all_methods_limited_world = []
        dict_of_xy_pairs_sl = {learner.SLClass: [] for learner in self.dg_models}

        for repetition in range(0, n_practitioner_repititions):
            for ml_index, ml_method_label in enumerate(self.ml_models):
                list_of_xy_pairs_all_methods_limited_world.append((mean(list_of_ntrue_accuracies[ml_method_label.name]),list_of_npractitioner_accuracies[ml_method_label.name][repetition]))
                for sl in dict_of_xy_pairs_sl.keys():
                    dict_of_xy_pairs_sl[sl].append((mean(list_of_ntrue_accuracies[ml_method_label.name]),list_of_nsl_accuracies[sl][ml_method_label.name][repetition]))
        sl_colors = {"hc": 'red', "tabu": 'blue', "rsmax2": 'green', "mmhc": 'yellow', "h2pc": 'orange', "gs": "cyan","pc.stable": "brown", "limited-real": "pink"}
        sl_offset = {"hc": 2, "tabu": 4, "rsmax2": 6, "mmhc": 8, "h2pc": 10, "gs": 12, "pc.stable": 14}
        fig = plt.figure(figsize=(10, 10), dpi=300)
        for sl in dict_of_xy_pairs_sl.keys():
            offset = lambda p: transforms.ScaledTranslation(p / 72., 0, plt.gcf().dpi_scale_trans)
            trans = plt.gca().transData
            x_true_accuracies, y_sl_accuracies = zip(*dict_of_xy_pairs_sl[sl])
            corr, _ = kendalltau(x_true_accuracies, y_sl_accuracies)
            plt.scatter(x=x_true_accuracies, y=y_sl_accuracies, c=sl_colors[sl], s=8,label=sl, alpha=0.7, transform=trans + offset(sl_offset[sl]))#label=sl + ' (' + str(round(corr, 2)) + ')'
            scatter_data.extend([x,y,sl] for x, y in zip(x_true_accuracies, y_sl_accuracies))
        plt.title("Scatterplot of x-y pairs between true and benchmarked accuracies for every practitioner repetition for all ml methods")
        plt.xlabel("Accuracy (True Reference)")
        plt.ylabel("Accuracy (Estimated Performance)")
        plt.plot([0, 1], [0, 1], ls="--", c="grey", alpha=0.4)
        x_true_accuracies, y_limited_accuracies = zip(*list_of_xy_pairs_all_methods_limited_world)
        corr, _ = kendalltau(x_true_accuracies, y_limited_accuracies)
        plt.scatter(x=x_true_accuracies, y=y_limited_accuracies, c='black',label='limited-real', s=15, marker='x', alpha=1)#label='limited-real (' + str(round(corr, 2)) + ')'
        scatter_data.extend([x,y, 'limited-real'] for x, y in zip(x_true_accuracies, y_limited_accuracies))

        for ml_index, ml_method_label in enumerate(self.ml_models):
            plt.axvline(x=x_true_accuracies[ml_index], ls='--', c='lightgrey', alpha=0.7)
        plt.xlim(0.45, 1)
        plt.ylim(0.45, 1)
        plt.legend(loc='upper right')
        plt.tight_layout()

        rank_methods = {method.name: 0 for method in self.ml_models}
        for idx, item in enumerate(self.ml_models):
            rank_methods[item.name] = list_of_xy_pairs_all_methods_limited_world[idx][0]
        rank_methods = sorted(rank_methods.items(), key=lambda kv: (kv[1], kv[0]))
        ordered_list_of_methods = []
        for item in rank_methods:
            ordered_list_of_methods.append(item[0])  # retrieve the true rank performance, [1] would retrieve limited performance
        for ml_index, ml_method_label in enumerate(self.ml_models):
            plt.text(x=x_true_accuracies[ml_index], y=0.95, s=ml_method_label.name,fontsize=7, rotation='vertical',rotation_mode='anchor',horizontalalignment='center', verticalalignment='bottom', alpha=0.8)#y=y_limited_accuracies[ml_index]
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_scatterplot_every_practitioner_repetition_accuracies_all_methods.png')
        plt.show()

        scatter_df = pd.DataFrame(scatter_data, columns=['True_Accuracy','Estimated_Accuracy', 'Strategy'])
        scatter_df.to_csv(os.getcwd()+figuredirname+ 'interworld_benchmarks_scatterplot_true_est_accuracies_all_methods_table.csv', index=False)

        # Barplot calculation of std
        sl_differences_var = pd.DataFrame(columns=['est-var', 'ML_method', 'SL'])
        sl_differences_std = pd.DataFrame(columns=['est-std', 'ML_method', 'SL'])

        #practitioner_ml_method_performance_list = {method.name: [] for method in self.ml_models}
        for ml in self.ml_models:
            #for practitioner_rep in range(0, n_practitioner_repititions):
            #    practitioner_ml_method_performance_list[ml.name].append(list_of_npractitioner_accuracies[practitioner_rep][ml.name])
            sl_differences_var = sl_differences_var.append({'est-var': np.var(list_of_npractitioner_accuracies[ml.name]),'ML_method': ml.name,'SL': 'limited-real'}, ignore_index=True)
            sl_differences_std = sl_differences_std.append({'est-std': np.std(list_of_npractitioner_accuracies[ml.name]), 'ML_method': ml.name, 'SL': 'limited-real'},ignore_index=True)

        for ml in self.ml_models:
            for sl in self.dg_models:
                #sl_ml_method_performance_list = {method.name: [] for method in self.ml_models}
                #for practitioner_rep in range(0, n_practitioner_repititions):
                #    sl_ml_method_performance_list[ml.name].append(list_of_nsl_accuracies[sl.SLClass][ml.name][practitioner_rep])
                sl_differences_var = sl_differences_var.append({'est-var': np.var(list_of_nsl_accuracies[sl.SLClass][ml.name]),'ML_method': ml.name,'SL': sl.SLClass}, ignore_index=True)
                sl_differences_std = sl_differences_std.append({'est-std': np.std(list_of_nsl_accuracies[sl.SLClass][ml.name]),'ML_method': ml.name, 'SL': sl.SLClass}, ignore_index=True)

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.barplot(x=sl_differences_var['ML_method'], y=sl_differences_var['est-var'],hue=sl_differences_var['SL'], data=sl_differences_var)
        plt.title('Grouped bar plot of variance across all repetitions for ML method performances between learners')
        plt.ylabel('Variance across datasets for ML method performance')
        plt.xlabel('ML Method')
        ax.tick_params(labelrotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_barplot_all_ml_methods_learner_var.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.barplot(x=sl_differences_std['ML_method'], y=sl_differences_std['est-std'],hue=sl_differences_std['SL'], data=sl_differences_std)
        plt.title('Grouped bar plot of standard deviation across all repetitions for ML method performances between learners')
        plt.ylabel('Standard deviation across datasets for ML method performance')
        plt.xlabel('ML Method')
        ax.tick_params(labelrotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_barplot_all_ml_methods_learner_std.png')
        plt.show()

        sl_differences_var.to_csv("meta_simulation_variance_per_ml_method.csv")

        pairwise_variance_test_results = []
        ci_results_var_diff = []

        # Statistical Analysis: Pairwise Variance Testing (Practitioner vs Each SL)
        for ml in self.ml_models:
            practitioner_data = list_of_npractitioner_accuracies[ml.name]
            practitioner_var = np.var(practitioner_data)

            for sl in self.dg_models:
                sl_data = list_of_nsl_accuracies[sl.SLClass][ml.name]
                sl_var = np.var(sl_data)

                # F-test between SL and practitioner
                f_stat, p_value = stats.f_oneway(practitioner_data, sl_data)

                # Bootstrapped confidence intervals for variance differences
                boot_practitioner_var = np.random.choice(practitioner_data, size=(1000, len(practitioner_data)),replace=True).var(axis=1)
                boot_sl_var = np.random.choice(sl_data, size=(1000, len(sl_data)), replace=True).var(axis=1)
                boot_var_diff = boot_sl_var - boot_practitioner_var
                ci_lower, ci_upper = np.percentile(boot_var_diff, [2.5, 97.5])

                # Collect results
                pairwise_variance_test_results.append({
                    'ML_method': ml.name,
                    'SL': sl.SLClass,
                    'Practitioner_var': practitioner_var,
                    'SL_var': sl_var,
                    'F_stat': f_stat,
                    'p_value': p_value
                })

                ci_results_var_diff.append({
                    'ML_method': ml.name,
                    'SL': sl.SLClass,
                    'CI_var_diff_lower': ci_lower,
                    'CI_var_diff_upper': ci_upper
                })

        # Exporting Results
        pd.DataFrame(pairwise_variance_test_results).to_csv("meta_simulation_pairwise_variance_test_results.csv", index=False)
        pd.DataFrame(ci_results_var_diff).to_csv("meta_simulation_ci_results_variance.csv", index=False)

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.boxplot(x=output_pd['ML_method'], y=output_pd['est-true'], hue=output_pd['SL'],palette=sl_colors,showfliers=False, showmeans=True,meanprops={"marker":"o","markerfacecolor":"black", "markeredgecolor":"grey","markersize":"5"})
        plt.title('Boxplot of difference between estimated performances and true by ml method for strategies')
        plt.ylabel('Difference to True estimated performance')
        plt.xlabel('ML Method')
        ax.set_xticklabels(ml_labels, rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_diff_to_true.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.boxplot(x=output_pd['ML_method'], y=output_pd['est-true'], hue=output_pd['SL'],palette=sl_colors,showfliers=False, order=ordered_list_of_methods, showmeans=True,meanprops={"marker":"o","markerfacecolor":"black", "markeredgecolor":"grey","markersize":"5"})
        plt.title('Boxplot of difference between estimated performances and true by ml method for strategies')
        plt.ylabel('Difference to True estimated performance')
        plt.xlabel('ML Method (least performing to best)')
        added_methods = []
        for idx, item in enumerate(rank_methods):
            added_methods.append(rank_methods[idx][0])# + " (True perf: "+ str(round(rank_methods[idx][1],2))+")" )
            ax.get_xticklabels()
        ax.set_xticklabels(added_methods, rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_diff_to_true_xaxis_ordered.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.boxplot(x=output_pd['ML_method'], y=output_pd['est-true'], hue=output_pd['SL'],palette=sl_colors,showfliers=True, order=ordered_list_of_methods, showmeans=True,meanprops={"marker":"o","markerfacecolor":"black", "markeredgecolor":"grey","markersize":"5"})
        plt.title('Boxplot of difference between estimated performances and true by ml method for strategies')
        plt.ylabel('Difference to True estimated performance')
        plt.xlabel('ML Method (least performing to best)')
        added_methods = []
        for idx, item in enumerate(rank_methods):
            added_methods.append(rank_methods[idx][0])# + " (True perf: "+ str(round(rank_methods[idx][1],2))+")" )
            ax.get_xticklabels()
        ax.set_xticklabels(added_methods, rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_diff_to_true_xaxis_ordered_fliers.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.boxplot(x=output_pd['ML_method'], y=output_pd['est-to-avgml'], hue=output_pd['SL'],palette=sl_colors,showfliers=False, showmeans=True,meanprops={"marker":"o","markerfacecolor":"black", "markeredgecolor":"grey","markersize":"5"})
        plt.title('Boxplot of difference between estimated and avg ml performances by ml method for strategies')
        plt.ylabel('Difference to Avg ML performance')
        plt.xlabel('ML Method')
        ax.set_xticklabels(ml_labels, rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_diff_to_avg_ml_performance.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.boxplot(x=output_pd['ML_method'], y=output_pd['est-to-avgml'], hue=output_pd['SL'],palette=sl_colors,showfliers=False, order=ordered_list_of_methods, showmeans=True,meanprops={"marker":"o","markerfacecolor":"black", "markeredgecolor":"grey","markersize":"5"})
        plt.title('Boxplot of difference between estimated and avg ml performances by ml method for strategies')
        plt.ylabel('Difference to Avg ML performance')
        plt.xlabel('ML Method (least performing to best)')
        added_methods = []
        for idx, item in enumerate(rank_methods):
            added_methods.append(rank_methods[idx][0]) #+ " (True perf:"+ str(round(rank_methods[idx][1],2))+")" )
            ax.get_xticklabels()
        ax.set_xticklabels(added_methods, rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_diff_to_avg_ml_performance_xaxis_ordered.png')
        plt.show()

        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.boxplot(x=output_pd['ML_method'], y=output_pd['est-to-avgml'], hue=output_pd['SL'], palette=sl_colors,showfliers=True,order=ordered_list_of_methods, showmeans=True,meanprops={"marker": "o", "markerfacecolor": "black", "markeredgecolor": "grey","markersize": "5"})
        plt.title('Boxplot of difference between estimated and avg ml performances by ml method for strategies')
        plt.ylabel('Difference to Avg ML performance')
        plt.xlabel('ML Method (least performing to best)')
        added_methods = []
        for idx, item in enumerate(rank_methods):
            added_methods.append(rank_methods[idx][0])  # + " (True perf:"+ str(round(rank_methods[idx][1],2))+")" )
            ax.get_xticklabels()
        ax.set_xticklabels(added_methods, rotation=90)
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_boxplot_all_ml_methods_diff_to_avg_ml_performance_xaxis_ordered_fliers.png')
        plt.show()

        for ml in self.ml_models:
            ml_method_filtered_performance = output_pd[output_pd['ML_method'] == ml.name]
            plt.figure(figsize=(10, 10), dpi=300)
            sns.kdeplot(data=ml_method_filtered_performance, x='est', hue='SL',fill=True, common_norm=False, alpha=0.5, legend=True,warn_singular=False)#, clip=(0.0, 1.0))
            plt.title('Distribution of ' + ml.name + ' performances grouped by alternative strategies')
            plt.xlabel("Performance")
            plt.ylabel("Density")
            #plt.legend()#ml_method_filtered_performance['SL'])
            plt.tight_layout()
            plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_kdeplot_performance_'+ml.name+'by_sl.png')
            plt.show()

        violin_header = [method.name for method in self.ml_models]
        violin_header.append("SL")
        # Save csv of performances for every repetition for all ml methods for all alternative pathways
        csv_performances = pd.DataFrame(columns=violin_header)
        ranked_csv_performances = pd.DataFrame(columns=violin_header)
        violinplot_performances = pd.DataFrame({'ML_Method': pd.Series(dtype='str'),'rank': pd.Series(dtype='int'),'SL': pd.Series(dtype='str')})
        for practitioner_rep in range(0, n_practitioner_repititions):
            practitioner_rep_ml_methods = {method.name: list_of_npractitioner_accuracies[method.name][practitioner_rep] for method in self.ml_models}#list_of_npractitioner_accuracies[practitioner_rep]
            csv_performances = csv_performances.append({method.name: practitioner_rep_ml_methods[method.name] for method in self.ml_models}, ignore_index=True)
            ranked_performances = pd.DataFrame.from_dict([dict(zip(practitioner_rep_ml_methods.keys(), rankdata([-i for i in practitioner_rep_ml_methods.values()], method='min')))], dtype=int64)
            ranked_performances["SL"] = "limited-real"
            ranked_csv_performances = ranked_csv_performances.append(ranked_performances)
            for ml in self.ml_models:
                violinplot_performances = violinplot_performances.append({'ML_Method':ml.name, 'rank': ranked_performances[ml.name].loc[0], "SL":'limited-real'}, ignore_index=True)
        for sl in self.dg_models:
            csv_performances = pd.DataFrame(columns=self.ml_models)
            ranked_csv_performances = pd.DataFrame(columns=self.ml_models)
            for sl_rep in range(0, n_practitioner_repititions):
                sl_accuracies = {method.name: 0 for method in self.ml_models}
                for ml in self.ml_models:
                    sl_accuracies[ml.name] = list_of_nsl_accuracies[sl.SLClass][ml.name][sl_rep]
                csv_performances = csv_performances.append({method.name: list_of_nsl_accuracies[sl.SLClass][method.name][sl_rep] for method in self.ml_models}, ignore_index=True)
                ranked_performances = pd.DataFrame.from_dict([dict(zip(sl_accuracies.keys(),rankdata([-i for i in sl_accuracies.values()],method='min')))],dtype=int64)
                ranked_performances["SL"] = sl.SLClass
                ranked_csv_performances = ranked_csv_performances.append(ranked_performances)
                for ml in self.ml_models:
                    violinplot_performances = violinplot_performances.append({'ML_Method': ml.name, 'rank': ranked_performances[ml.name].loc[0], "SL": sl.SLClass}, ignore_index=True)

        # Create violinplot of rank spread by ml method grouped by sl
        plt.figure(figsize=(10, 10), dpi=300)
        ax = sns.violinplot(x=violinplot_performances["ML_Method"], y=violinplot_performances["rank"], hue=violinplot_performances["SL"], inner=None,scale='width', cut=0, order=ordered_list_of_methods)
        plt.legend()
        sns.move_legend(ax, "center left", bbox_to_anchor=(1, 0.5))
        plt.title("Density of ML method ranks by alternative strategies")
        ax.set_xticklabels(ordered_list_of_methods, rotation=90)
        plt.xlabel("ML Methods (least performing to best)")
        plt.tight_layout()
        plt.savefig(os.getcwd() + figuredirname + 'interworld_benchmarks_violinplot_every_repetition_rank_all_methods_composite.png')
        plt.show()

    def dict_to_list(self, score_name, all_results: dict):
        data = []
        ml_algs = list(TD(all_results, 1).keys())
        worlds = list(all_results.keys())
        for alg in ml_algs:
            inner_list = [alg]
            for world in worlds:
                inner_list.append(all_results[world][alg][score_name])
            data.append(inner_list)
        return data

    # not used for now
    def get_true_performance_stats(self, scores: dict):
        # scores: dict of shape {"ml_model_name": {"score_name": list_of_values}}
        score_names = TD(scores, 1).keys()
        stats = {ml_model_name: {score_name: {} for score_name in score_names} for ml_model_name in scores.keys()}
        for ml_model_name in scores.keys():
            for score in score_names:
                stats[ml_model_name][score]["min"] = np.min(scores[ml_model_name][score])
                stats[ml_model_name][score]["max"] = np.max(scores[ml_model_name][score])
                stats[ml_model_name][score]["mean"] = np.mean(scores[ml_model_name][score])
        return stats

    def plot_analysis_coef(self, analysis2_results: dict, pipeline: str = "Real-world"):
        markers = ['x', 'o', '^', '*', '+', 's', 'p']
        c = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
        corr_df = self.corr_dict_to_pd(analysis2_results)
        print(corr_df)
        real_corr = corr_df.loc[corr_df['world'] == pipeline].correlation
        for i, world in enumerate(set(corr_df.world)):
            if world == "PC":
                continue
            world_corr = corr_df.loc[corr_df['world'] == world].correlation

            plt.scatter(real_corr.tolist(), world_corr.tolist(), marker=markers[i], c=c[i], label=world)

        plt.title("pair-wise correlations of learned vs real world")
        plt.xlabel("real world correlations")
        plt.ylabel("learned world correlations")
        plt.legend()
        plt.tight_layout()
        plt.savefig('scatter_plot_of_ccs.png')
        plt.show()

    def dict_to_dataframe_sns(self, scores: dict, score_name: str = 'balanced_accuracy_score') -> pd.DataFrame:
        '''

        :param scores: dict of form {world_name: {ml_model_name: {score_name: list of scores]...}...}...}
        :param score_name:
        :return: dataframe with columns=[world, ml_model, score] and rows corresponding to individual entries
        '''
        score_dict = TD(scores, 2)[score_name]
        raw_scores_df = pd.DataFrame(score_dict)
        list_of_lists = []

        for col in raw_scores_df.columns:
            for row in raw_scores_df.index:
                for i in range(5):
                    list_of_lists.append([col, row, raw_scores_df[col][row][i]])

        return pd.DataFrame(list_of_lists, columns=["world", "ml_model", "score"])

    def corr_dict_to_pd(self, corr_dict):
        corr_pd = pd.concat(corr_dict)
        corr_pd.rename(columns={0: 'correlation'}, inplace=True)
        corr_pd.index = corr_pd.index.set_names(['world', 'pair'])
        corr_pd.reset_index(level=['world', 'pair'], inplace=True)
        corr_pd["pair"] = corr_pd["level_0"] + corr_pd["level_1"]
        corr_pd.drop(columns=["level_0", "level_1"], inplace=True)
        return corr_pd
