import pandas as pd
from gene_signature_survival import signature_surv

#inputs
#gene signatures
Pos = ['MMP1', 'QSOX1', 'OXTR', ]
Neg = ['MSX1', 'ELN', 'PMP22']

dir = r'tests\outputs'
df_expression = pd.read_csv(r'tests\data\TCGA_BRCA_ALL_CODING_TPM.csv', sep = ',', index_col = 0)
df_clinical = pd.read_csv(r'tests\data\brca_tcga_pan_can_atlas_2018_clinical_data.tsv', sep = '\t')
event = 'event'
time = 'time'
time_units = 'Months'
score_name = 'test'

#convert event to 1 or 0
df_clinical['event'] = df_clinical['Disease Free Status'].apply(lambda x: 1 if 'Recurred/Progressed' in str(x) else 0)

# Convert time to float
df_clinical['time'] = pd.to_numeric(df_clinical['Disease Free (Months)'], errors='coerce')


signature_surv(df_expression, df_clinical, time, time_units, event, dir, score_name, Pos, Neg)