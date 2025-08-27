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
    # Convert to datetime for filtering
    start_date = pd.to_datetime(start_date_str, format='%Y%m%d%H')
    end_date = pd.to_datetime(end_date_str, format='%Y%m%d%H')
    
    # Get all files that match the pattern
    files = glob(os.path.join(path, f'*{family}*'))
    filtered_files = []
    for file in files:
        file_date = extract_date_from_filename(file, family)
        if start_date <= file_date <= end_date:
            filtered_files.append(file)

    date_counts = {}

    for file in filtered_files:
        print (file)
        conn = sqlite3.connect(file)
        cursor = conn.cursor()
     #   cursor.execute('CREATE INDEX idx_id_stn ON header (id_stn);')
        # Query to count relevant rows
        cursor.execute('SELECT COUNT(*) FROM data;')#JOIN header ON data.id_obs = header.id_obs WHERE header.id_stn LIKE "NOA%";')
        count = cursor.fetchone()[0]
        
        file_date = extract_date_from_filename(file, family)
        
        if file_date not in date_counts:
            date_counts[file_date] = 0
        date_counts[file_date] += count
        
        conn.close()

    return date_counts

# Paths for the families
families = {
    'postalt': '/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/postalt/',
    'evalat': '/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/evalalt/',
    'dbase': '/home/smco500/.suites/psmon/monitoring/g2/hub/ppp5/sqlite/banco/dbase/'
}

# Dates and pattern for the query
family_pattern = '*cris*'
start_date_str = '2024102400'
end_date_str = '2024102418'

# Dictionary to store counts by date
all_counts = {}

# Loop through each family to get counts
for family, path in families.items():
    counts = get_counts_by_date(path, family_pattern, start_date_str, end_date_str)
    all_counts[family] = counts

# Create DataFrame from counts
df_counts = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in all_counts.items()])).reset_index()
df_counts.rename(columns={'index': 'Date'}, inplace=True)

# Fill missing values with 0
df_counts.fillna(0, inplace=True)

# Calculate percentages
df_counts['Percentage_postalt_evalat'] = (df_counts['postalt'] / df_counts['evalat']) * 100
df_counts['Percentage_evalat_dbase'] = (df_counts['evalat'] / df_counts['dbase']) * 100

# Calculate average percentages
average_percentage_postalt_evalalt = df_counts['Percentage_postalt_evalat'].mean()
average_percentage_evalat_dbase = df_counts['Percentage_evalat_dbase'].mean()
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.set_ylabel('Percentage (%)', color='tab:red')
ax1.set_xlabel('Date')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax1.set_ylim(0, 105)

ax1.plot(df_counts['Date'], df_counts['Percentage_postalt_evalat'], marker='o', color='tab:red', label=f'Percentage postalt/evalat') 
ax1.plot(df_counts['Date'], df_counts['Percentage_evalat_dbase'], marker='*', color='tab:red', label=f'Percentage evalalt/dbase')

plt.title(f'Count with Total Observations Over Time. Family: {family_pattern};\n'
             f'Average Percentage postalt/evalat : {average_percentage_postalt_evalalt:.2f}% Average Percentage evalalt/dbase : {average_percentage_evalat_dbase:.2f}% ')
   

ax2 = ax1.twinx()
ax2.set_ylabel('Observations (Count)', color='black')
ax2.set_ylim(0, 200000000)
ax2.plot(df_counts['Date'], df_counts['postalt'], marker='x', color='tab:blue' ,label=f'Count postalt')
ax2.plot(df_counts['Date'], df_counts['evalat'], marker='x',  color='tab:green' , label=f'Count evalat')
ax2.plot(df_counts['Date'], df_counts['dbase'], marker='x', color='tab:yellow' ,  label=f'Count dbase')
ax2.set_ylabel('Observations (Count)', color='black')

ax1.legend(loc='lower left', bbox_to_anchor=(0, 1.15))
ax2.legend(loc='lower right', bbox_to_anchor=(0, 1.15))

plt.savefig(f'_plot4.png', dpi=300) 
plt.grid(True)
plt.xticks(rotation=45)

plt.show()


# Print results for debugging
print("Conteos y porcentajes por fecha:")
print(df_counts[['Date', 'postalt', 'evalat', 'dbase', 'Percentage_postalt_evalat', 'Percentage_evalat_dbase']])

