import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test 
from collections import namedtuple
import os

# if all true, as in singScore from R. 
def signature_score(df_expression: pd.DataFrame, gen_set_up: list = None, gen_set_down: list = None, 
                    perc_norm: bool = True, center_to_cero: bool = True) -> pd.DataFrame:
    '''
    df_expression: a pandas dataframe is required, where colums are samples and index is genes. Recomendation: TPM, 
    log2(TPM +1) or any unit normalized between samples.

    gen_set_up = list including the genes from gene signature which are upregulated, in str.
    gen_set_down = list including the genes from the gene signature which are downregulated, in str.

    perc_norm = Boolean option to choose if you want to normalize the scoring following the original singscore method, 
    result will be between -1 and 1. Default = True
    center_to_cero: Bollean option to choose if you want the scoring to be set around 0.

    Return: A pd.DataFrame with 2 columns named 'sample' and 'score' whith the score per sample.

    function to normilize the scoring, folowing mathematical method, original singscore paper.
    '''
    def normalize(score: float, gendir: int, gentot: int):
            smin = (gendir + 1)/2
            smax = (2*gentot - gendir + 1)/2
            return (score - smin)/(smax - smin)
    
    #In case we only have upregulated genes:
    df_score = None
    if gen_set_down == None:
        num_gens = len(df_expression)
        # Only acount genes from gene signature which are found in the expersion matrix
        filtered_genset = [x for x in gen_set_up if x in df_expression.index]

        # Rank the expresion of each gene of the expresion matrix for each sample in ascending (higher expresion will give a bigger number of rank)
        ranked_df = df_expression.rank(axis=0, method='min')
        ranked_df = ranked_df.T
        # We only keep rank of genes in gene signature
        ranked_df = ranked_df[filtered_genset]
        # We do the mean for each sample of the rank of the signature genes
        df_score = ranked_df.mean(axis=1)

    # In case we only have downregulated genes:
    elif gen_set_up == None:
        num_gens = len(df_expression)
        # Only acount genes from gene signature which are found in the expersion matrix
        filtered_genset = [x for x in gen_set_down if x in df_expression.index]
        # Rank the expresion of each gene of the expresion matrix for each sample in descending (lower expresion will give a bigger number of rank)
        ranked_df = df_expression.rank(axis=0, method='min', ascending = False)
        ranked_df = ranked_df.T
        ranked_df = ranked_df[filtered_genset]
    
        df_score = ranked_df.mean(axis=1)

    if df_score != None:
        # Normalizes following the  athematical formula from singscore original paper
        if perc_norm:    
            df_score = df_score.apply(lambda x: normalize(x, len(filtered_genset), num_gens))
        # Sets distributions of scores aorund 0 if before normalized
        if center_to_cero and perc_norm:
            df_score = df_score - 0.5
        # Sets distribution of scores around 0 if before not normalized 
        if center_to_cero and not perc_norm:
            expected_mean = (num_gens + 1) / 2
            df_score = df_score - expected_mean
            df_score = df_score / expected_mean

    # In case we have Down and Up regulated genes:
    if gen_set_up != None and gen_set_down!= None:
        num_gens = len(df_expression)
        # Only acount genes from gene signature which are found in the expersion matrix
        filtered_genset_up = [x for x in gen_set_up if x in df_expression.index]
        filtered_genset_down = [x for x in gen_set_down if x in df_expression.index]

        # Same as other conditions but duplicate (for up and down)
        ranked_df_up = df_expression.rank(axis = 0, method = 'min')
        ranked_df_up = ranked_df_up.T
        ranked_df_up = ranked_df_up[filtered_genset_up]
        ranked_df_down = df_expression.rank(axis = 0, method = 'min', ascending = False) 
        ranked_df_down = ranked_df_down.T
        ranked_df_down = ranked_df_down[filtered_genset_down]

        df_score_up = ranked_df_up.mean(axis = 1)
        df_score_down = ranked_df_down.mean(axis = 1)

        if perc_norm:
            df_score_up = df_score_up.apply(lambda x: normalize(x, len(filtered_genset_up), num_gens))
            df_score_down = df_score_down.apply(lambda x: normalize(x, len(filtered_genset_down), num_gens))

        if center_to_cero and perc_norm:
            df_score_up = df_score_up - 0.5
            df_score_down = df_score_down - 0.5
        
        if center_to_cero and not perc_norm:
            expected_mean = (num_gens + 1) / 2
            df_score_up = df_score_up - expected_mean
            df_score_up = df_score_up / expected_mean
            df_score_down = df_score_down - expected_mean
            df_score_down = df_score_down / expected_mean
        # the up and down scores are added at the and after all normalizations
        df_score = df_score_up + df_score_down
    

    df_score = df_score.reset_index()
    df_score.columns = ['sample', 'score']
    return df_score


SurvCutResult = namedtuple("SurvCutResult", [
    "best_p", "best_stat", "best_tresh", "n_high", "n_low", 'graph'
])


def surv_cutpoint(df_scores: pd.DataFrame, df_clinical: pd.DataFrame, time: str, event: str, min_group: int = 20):
    '''
    df_scores: A pd.DataFrame with 2 columns, one named 'sample' and other named 'score'.
    df_clinical: A pd.DataFrame with a column named 'sample'and another column with the events 0 or 1 and one with time to event or censure.
    time: string stating the name of the column in the df_clinical where the time untill event is found
    event: string stating the name of the column in the df_clinical where the event is found
    min_group: minimum percentage of samples that should be in each group after group split. Default = 20%
    '''
    # creates a merged df with the scores and the clinical data 
    df_merge = df_scores.merge(df_clinical[['sample', time, event]], left_on = 'sample', right_on='sample', how = 'left')
    df_merge = df_merge.dropna(subset=[time, event])

    # Creates a list of all possible score thresholds. Each threshold is a point before each sample score, so all possible sample splits are tested.
    # to_cut takes out the first and last min_group percentage. Default = %
    tresholds = sorted(list(df_merge['score']))
    tresholds = [x-0.0000000000000001 for x in tresholds]
    to_cut = (min_group * 1/100) * len(tresholds)
    to_cut = int(to_cut)
    tresholds = tresholds[to_cut:-(to_cut)]
    

    stats = []
    treshes = []
    best_p = 1
    best_stat = 0
    best_tresh = None
    n_high = None
    n_low  = None

    # For each possible threshold
    for tresh in tresholds:
        # Divides samples in 2 groups, score higher than threshold and lower than.
        high = df_merge[df_merge['score'] > tresh]
        low = df_merge[df_merge['score'] <= tresh]

        # Calculates Log-rank test for that specific sample separation
        result = logrank_test(
            high[time], low[time],
            event_observed_A = high[event],
            event_observed_B = low[event]
        )

        # Will keep track of all statistics and thresholds used
        stats.append(result.test_statistic)
        treshes.append(tresh)

        # if the p-value of this tested threshold (sample separation) is better than the others already tested,
        # this threshold is the best for the moment
        if result.p_value < best_p:
            best_stat = result.test_statistic
            best_p = result.p_value
            best_tresh = tresh
            n_high = len(high)
            n_low = len(low)

    
    print(f"🔹 Mejor punto de corte: {best_tresh}")
    print(f"🔹 Mejor estadistico Log-Rank: {best_stat}")
    print(f"🔹 p-valor log-rank: {best_p}")
    print(f'🔹 N+ = {n_high}, N- = {n_low}')
    '''
    The returns:
    stats and treshes: is the list tracking all the tested tracking and its results.
    best: is the best statistic and the best treshold
    n: is the number of samples for high scoring samples and low scoring sampels
    '''
    graph = (stats, treshes, best_tresh)
    return SurvCutResult(best_p, best_stat, best_tresh, n_high, n_low, graph)


def plot_cutpoint(graph: tuple, dir: str, score_name: str):
    '''
    graph: is the tuple returned by surv_cutpoint with the same name. Contains in [0]: Track of the statistic, [1]: track of thresholds tested,
    [2]: the finally best threshold selected

    dir: Directory were you want to save the figure
    score_name: Name of the score (i.e. if the score comes from a gene signature, the gene signature name)
    '''
    # takes data from graph tuple
    treshes = np.array(graph[1])
    stats = np.array(graph[0])
    best_tresh = graph[2]
    # separates the track of thresholds in 2 masks, before and after the best threshold
    mask1 = treshes <= best_tresh
    mask2 = treshes > best_tresh


    print(f'len stats:{len(stats)}, len tresh:{len(treshes)}')
    plt.figure(figsize=(12,4))
    plt.scatter(x = treshes[mask1], y = stats[mask1], s = 2, color = "#6ABBD8", label = 'High')
    plt.scatter(x = treshes[mask2], y = stats[mask2], s = 2, color = "#F2857D", label = 'Low')
    plt.axvline(x=best_tresh, color='grey', linestyle='--', linewidth=1.5)
    plt.text(best_tresh + 0.001, max(stats)*0.1, f'Treshold: {best_tresh:.5f}', color='grey', fontsize=10, rotation = 90)
    plt.xlabel('Score')
    plt.ylabel('Log-rank Statistic')
    plt.title(f'Maximally selected treshold Log-Rank for {score_name}')
    plt.legend()
    plt.savefig(os.path.join(dir, f'{score_name}_treshold.png'), dpi = 600)
    plt.show()



kaplan_meierResult = namedtuple("kaplan_meierResult", [
    'statistic', 'p_value', 'threshold', 'n_pos', 'n_neg'
])

def kaplan_meier(df_scores: pd.DataFrame, df_clinical: pd.DataFrame, time: str, time_unit: str, event:str, score_name: str, threshold: float, dir: str):
    '''
    This function will finally apply the Log-rank test to the groups of splited samples by the best threshold found with surv_cutpoint,
    as well as the Kaplan meier model fit.

    df_scores: A pd.DataFrame with 2 columns, one named 'sample' and other named 'score'.
    df_clinical: A pd.DataFrame with a column named 'sample'and another column with the events 0 or 1 and one with time to event or censure.
    time: string stating the name of the column in the df_clinical where the time untill event is found
    event: string stating the name of the column in the df_clinical where the event is found
    score_name: Name of the score (i.e. if the score comes from a gene signature, the gene signature name)
    threshold: a float number, is the score threshold which will split the samples in high score or low score,
    normally determined from surv_cutpoint function.
    dir: Directory were you want to save the result file and the kaplan meier grafic.
    '''
    # we separe groups by score treshold
    positive_samples = df_scores[df_scores['score'] > threshold]['sample'].tolist()
    negative_samples = df_scores[df_scores['score'] <= threshold]['sample'].tolist()

    # Eliminar filas con valores faltantes
    df_clinical = df_clinical.dropna(subset=[event, time])

    df_clinical_pos = df_clinical[df_clinical['sample'].isin(positive_samples)]
    df_clinical_neg = df_clinical[df_clinical['sample'].isin(negative_samples)]

    T_pos = df_clinical_pos[time]
    E_pos = df_clinical_pos[event]
    T_neg = df_clinical_neg[time]
    E_neg = df_clinical_neg[event]

    #log_rank statisticall test
    test_result = logrank_test(T_pos, T_neg, E_pos, E_neg)
    print(test_result)
    #fit the model and graphic
    kmf = KaplanMeierFitter()
    kmf.fit(T_pos, E_pos, label = f'positive_{score_name}')
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.figure(figsize=(8,6))
    ax = kmf.plot_survival_function(ci_show = True, show_censors=True, color = "#D62728")
    kmf.fit(T_neg, E_neg, label = f'negative_{score_name}')
    ax = kmf.plot_survival_function(ax=ax, ci_show = True, show_censors=True, color = "#1F77B4")
    ax.legend(loc='upper right')
    plt.title(f'Kaplan meier model fit for {score_name}')
    plt.xlabel(f'Time ({time_unit})')
    plt.ylabel('Survival probabilities')
    plt.text(0.05, 0.12, f'p-value Log-Rank test = {test_result.p_value:.4f}', transform = ax.transAxes)
    plt.text(0.05, 0.07, f'n_pos = {len(df_clinical_pos)}', transform = ax.transAxes)
    plt.text(0.05, 0.02, f'n_neg = {len(df_clinical_neg)}', transform = ax.transAxes)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(dir, f'{score_name}_survival.png'), dpi = 600)
    plt.show()

    with open(os.path.join(dir, f'{score_name}_log_rank_test.txt'), mode = 'w') as file:
        file.write(str(test_result.summary))
        file.write('\n')
        file.write(f'Treshold used for separating groups: {threshold}')
        file.write('\n')
        file.write(f'n positive: {len(df_clinical_pos)}')
        file.write('\n')
        file.write(f'n negative: {len(df_clinical_neg)}')
    
    return kaplan_meierResult(test_result.test_statistic, test_result.p_value, threshold, len(df_clinical_pos), len(df_clinical_neg))




def signature_surv(df_expression: pd.DataFrame, 
                   df_clinical: pd.DataFrame, 
                   time: str, 
                   time_unit: str, 
                   event: str,
                   dir: str, 
                   score_name: str, 
                   gen_set_up: list = None, 
                   gen_set_down: list = None, 
                   perc_norm = True, 
                   center_to_cero = True, 
                   min_group: int = 20
                   ):
    
    '''
    df_expression: a pandas dataframe is required, where colums are samples and index is genes. Recomendation: TPM, 
    log2(TPM +1) or any unit normalized between samples.
    df_clinical: A pd.DataFrame with a column named 'sample'and another column with the events 0 or 1 and one with time to event or censure.
    time: string stating the name of the column in the df_clinical where the time untill event is found
    time_unit: a str stating if the time is dyas, months... Just for graph.
    event: string stating the name of the column in the df_clinical where the event is found
    dir: string of path for directory were result files want to be stored
    score_name: Name of the score (i.e. if the score comes from a gene signature, the gene signature name)
    gen_set_up = list including the genes from gene signature which are upregulated, in str.
    gen_set_down = list including the genes from the gene signature which are downregulated, in str.
    perc_norm = Boolean option to choose if you want to normalize the scoring following the original singscore method, 
    result will be between -1 and 1. Default = True
    center_to_cero: Bollean option to choose if you want the scoring to be set around 0.
    min_group: minimum percentage of samples that should be in each group after group split. Default = 20%
    '''

    df_scoring = signature_score(df_expression, gen_set_up, gen_set_down, perc_norm, center_to_cero)
    cut_result = surv_cutpoint(df_scoring, df_clinical, time, event, min_group)
    plot_cutpoint(cut_result.graph, dir, score_name)
    kaplan_meier(df_scoring, df_clinical, time, time_unit, event, score_name, cut_result.best_tresh, dir)



