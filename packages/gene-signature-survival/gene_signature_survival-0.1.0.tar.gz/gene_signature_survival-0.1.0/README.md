Transcriptomic signature–based survival analysis

This paquet aims to give tools for the analysis of the effects of gene signatures in the survival of a clinical cohort based on transcriptomic data.
Tested on Bulk RNA-Seq data, may also be used with microarrays.

Intended workflow: 

- Starting from the point where a gene signature or various are set. (Maybe from a previous experiment; Difexp, GSEA...)
This gene signatures can have positive or negative genes (Up or down regulated)

- A clinical cohort of interest is also needed with transcriptomic data and survival data like RFS...

- The first step is to give a score to each sample of the clinical cohort based on it's expression similarity to the gene signature.

- To be able to compare the survival of the gene signature, the cohort need to be divided in positive or negative for the gene signature, so a threshold from the sample scoring is needed to set the groups.
This is acomplished by finding the score threshold where the maximum log-Rank test statistic is obtained.

- Once the threshold is determined for that gene signature, the final kaplan meier/ Log-Rank test is performed with the 2 groups to compare the
survival probablilities of the positive group (more similar expression to the gene signature) versus the survival probabilities of the negative group (less similar expression to the gene signature).

Functions: *the main function with the whole pipeline is: signature_surv. But is just a pipeline of the other functions. As it may result usefull to use the other functions by separate for other analysis.
For more details on the inputs read documented functions.

- signature_score:

This function inputs an expression matrix and a gene signature (a list of upregulated genes and/or a list of downregulated genes) and returns
a score for each sample based on how aproximate the expression of the genes of that sample is the the upregulated, downregulated genes of the
gene signature. 

This function uses a ranking method. Basically ranks the expression of all the genes of the expression matrix for each sample. Then makes the average of the ranking of the genes that are in the gene signature and after optional normalizations it returns a final score.
For Upregulated genes the ranking is in ascending mode and in downregulated in descending mode, so direction is taken into acount. 

Even if the method does not score based on any comparison between samples, the expression matrix is prefered in units normalized for intersample comparison, for example TPMs, log2 normalization is recomended. 

This function is based on the method described at: 
Foroutan et al. BMC Bioinformatics (2018) 19:404
https://doi.org/10.1186/s12859-018-2435-4

- surv_cutpoint:

This function inputs de score df (sample and score) and a df with the clinical data (sample, time, event).
A minimum % of samples per group is possible, defect = 20%.

This funtion will iterate through all the possible sample partition of the groups and try a Log-Rank test for each group partition, 
will record the result statistic of that test and the score threshold will be the sample which resulted in the highest statistic.
This function was also an interpretation from the surv_cutpoint function from survminer: https://github.com/kassambara/survminer/blob/master/R/surv_cutpoint.R.

- kaplan_meier

This function inputs the score df (sample and score), a df with the clinical data (sample, time, event) and the score threshold.
The function will separate the clinical df samples in positive and negative groups. Will perform a kaplan-meier, plot it with the log-rank test p-value result and return a file with a summary of the analysis.

- signature_surv:

This function creates the final pipeline that includes all of the above functions. 
This function inputs the expression matrix, the clinical df and the gene signature lists.



Test: Examples for the use of the functions are found in tests folder.
Expression and clinical df are from the public TCGA-BRCA database.
Gen signatures are random selected genes from different hallmarks.

