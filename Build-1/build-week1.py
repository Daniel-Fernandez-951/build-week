# Data Handling
import pandas as pd
import numpy as np
# Graphing Libraries
import plotly.express as px
# Something to visit later (warning supression!).
# pd.options.mode.chained_assignment = None

# Read data, drop some columns.
data = pd.read_csv("/content/detailed_covid.csv")
data = data.drop(['icu_yn', 'hosp_yn', 'current_status', 'sex', 'cdc_report_dt','pos_spec_dt', 'onset_dt', 'Race and ethnicity (combined)'], axis=1)
# Commented out visual check (optional)
# data.head(20)
data_clean = pd.DataFrame.copy(data)

# Masks to observe unusable data in `death_yn`.
missing_mask = (data['death_yn'] == 'Missing')
unk_mask = (data['death_yn'] == 'Unknown')

# Ouput some stats on the removal process.
rm_percent = ((data.shape[0]) - ((data[missing_mask].shape[0]) + (data[unk_mask].shape[0]))) / data.shape[0]
print(f'Unknown = {data[unk_mask].shape[0]}\nMissing = {data[missing_mask].shape[0]}\n    Sum = {(data[missing_mask].shape[0]) + (data[unk_mask].shape[0])}')
print(f'\nPurged Data = {round(rm_percent*100, 1)}%')


# Make binary, for later counting and NaN for removal.
data_clean['death_01'] = data['death_yn'].map({'Yes': 1, 'No': 0, 'Missing': np.NaN, 'Unknown': np.NaN})

# Refrence binary column for NaN removal.
data_clean = data_clean.dropna(how='any', subset=['death_01'])
# Check the difference for a mismatch.
print(f'Cleaning Complete? {(data.shape[0] - data_clean.shape[0]) == (data[missing_mask].shape[0]) + (data[unk_mask].shape[0])}')

# Combine `Unknown` and `NaN` to `Unknown Age`
data_clean['age_grp'] = data_clean['age_group'].replace(regex=['Unknown', np.nan], value='Unknown Age')
# data_clean['age_grp'].value_counts(dropna=False)

# If information is missing; safe to assume unknown.
data_clean['medcond_clean'] = data_clean['medcond_yn'].replace(regex='Missing', value='Unknown' )
# data_clean['medcond_clean'] = data_clean['medcond_yn'].map({'Missing': 'Unknown'})
# 960418
# (data_clean['medcond_clean'] == 'Unknown').value_counts()

# Multiaxis pivot table, Mortality and Comorbidity
table = data_clean.pivot_table(columns='age_grp', index=['death_yn', 'medcond_clean'], values='death_01', aggfunc='count' )
# table
data_clean = pd.DataFrame(data_clean)

table2 = data_clean.pivot_table(index='age_grp', columns=['death_yn'], values='death_01', aggfunc='count' )
table2
# data_clean
# table2[0]

data_clean['medcond_clean_01'] = data_clean['medcond_clean'].map({'Yes': 1, 'No': 0, 'Unknown': 2})
table3 = data_clean.pivot_table(index='age_grp', columns=['medcond_clean'], values='medcond_clean_01', aggfunc='count' )
# table3

fig = px.line(table3)
fig.update_traces(mode="markers+lines")
fig.update_layout(
    hovermode="x unified",
    font=dict(size=16, family="Courier New, monospace", color='black'),
    title={
        'text': "Disclosed Comorbidities By Age",
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top'
        },
    legend_title="Comorbidity",
    xaxis_title="Age Range",
    yaxis_title="Count",
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)'
      )
fig.update_traces(hovertemplate='%{y}')
fig.show()
