import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob

# Function to extract date from filename
def extract_date_from_filename(filename, family):
    basename = os.path.basename(filename)
    date_str = basename.split(family)[0][:10]  # 'yyyymmddhh'
    return pd.to_datetime(date_str, format='%Y%m%d%H')

def get_counts_by_date(path, family, start_date_str, end_date_str):
    start_date = pd.to_datetime(start_date_str, format='%Y%m%d%H')
    end_date = pd.to_datetime(end_date_str, format='%Y%m%d%H')
    
    files = glob(os.path.join(path, f'*{family}*'))
    filtered_files = []
    for file in files:
        file_date = extract_date_from_filename(file, family)
        if start_date <= file_date <= end_date:
            filtered_files.append(file)

    date_counts = {}

    for file in filtered_files:
        conn = sqlite3.connect(file)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM data JOIN header ON data.id_obs = header.id_obs WHERE header.id_stn LIKE "NOA%";')
        count = cursor.fetchone()[0]
        
        file_date = extract_date_from_filename(file, family)
        date_counts[file_date] = date_counts.get(file_date, 0) + count
        
        conn.close()

    return date_counts

# Paths for the families
families = [
    ('postalt', '/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/'),
    ('evalat', '/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/'),
    ('dbase', '/home/smco500/.suites/psmon/monitoring/g2/hub/ppp5/sqlite/banco/'),
    ('evalalt', '/home/smco500/.suites/psmon/monitoring/g2/hub/ppp5/sqlite/banco/')
]

family_patterns = ['*cris*', '*cris*']
start_date_str = '2024102500'
end_date_str = '2024102800'

# Get counts for both families
counts = {}
for name, path in families:
    counts[name] = get_counts_by_date(path, family_patterns[0], start_date_str, end_date_str)

# Create DataFrame for easy plotting
df_list = []
for name in counts:
    df = pd.DataFrame(list(counts[name].items()), columns=['Date', f'Count_{name}'])
    df_list.append(df)

# Merge all DataFrames
df_merged = df_list[0]
for df in df_list[1:]:
    df_merged = pd.merge(df_merged, df, on='Date', how='outer')

df_merged.fillna(0, inplace=True)
df_merged.sort_values(by='Date', inplace=True)

# Calculate percentages
df_merged['Percentage_evalalt'] = (df_merged['Count_evalalt'] / df_merged['Count_dbase'].replace(0, pd.NA)) * 100
df_merged['Percentage_postalt'] = (df_merged['Count_postalt'] / df_merged['Count_evalat'].replace(0, pd.NA)) * 100

# Calculate average percentages
average_percentage_evalalt = df_merged['Percentage_evalalt'].mean()
average_percentage_postalt = df_merged['Percentage_postalt'].mean()

# Plotting
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot percentages on primary y-axis
ax1.plot(df_merged['Date'], df_merged['Percentage_evalalt'], marker='o', color='tab:red', label='Percentage (evalalt / dbase)')
ax1.plot(df_merged['Date'], df_merged['Percentage_postalt'], marker='o', color='tab:orange', label='Percentage (postalt / evalat)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Percentage (%)', color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax1.set_ylim(0, 105)

# Annotate each point with its percentage
for i, (date, percentage_evalalt, percentage_postalt) in enumerate(zip(df_merged['Date'], df_merged[['Percentage_evalalt', 'Percentage_postalt']].values)):
    ax1.text(date, percentage_evalalt, f'{percentage_evalalt:.2f}%', ha='center', va='bottom', fontsize=8, color='tab:red')
    ax1.text(date, percentage_postalt, f'{percentage_postalt:.2f}%', ha='center', va='bottom', fontsize=8, color='tab:orange')

# Secondary y-axis to show total counts for both families
ax2 = ax1.twinx()
ax2.set_ylim(0, df_merged[['Count_evalalt', 'Count_dbase', 'Count_postalt', 'Count_evalat']].max().max() * 1.1)
ax2.plot(df_merged['Date'], df_merged['Count_evalalt'], marker='x', color='tab:blue', label='Count evalalt')
ax2.plot(df_merged['Date'], df_merged['Count_dbase'], marker='x', color='tab:green', label='Count dbase')
ax2.plot(df_merged['Date'], df_merged['Count_postalt'], marker='x', color='tab:purple', label='Count postalt')
ax2.plot(df_merged['Date'], df_merged['Count_evalat'], marker='x', color='tab:brown', label='Count evalat')
ax2.set_ylabel('Observations (Count)', color='black')

# Adding legends
ax1.legend(loc='upper left', bbox_to_anchor=(0, 1.15))
ax2.legend(loc='upper right', bbox_to_anchor=(1, 1.15))

# Display average percentages on the plot
plt.title(f'Percentage Comparison; Average Percentages: evalalt: {average_percentage_evalalt:.2f}%, postalt: {average_percentage_postalt:.2f}%')

# Set grid, rotate x labels, and tight layout
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'comparison_plot_all_families_{start_date_str}_{end_date_str}.png', dpi=300)

plt.show()

