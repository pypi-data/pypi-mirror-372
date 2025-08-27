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

# Function to get counts over time for both paths
def get_counts_by_date(path, family, start_date_str, end_date_str):
    # Convert to datetime for filtering
    start_date = pd.to_datetime(start_date_str, format='%Y%m%d%H')
    end_date = pd.to_datetime(end_date_str, format='%Y%m%d%H')
    
    # Get all files that match the pattern
    files = glob(os.path.join(path, f'*{family}*'))
    print (files)
    # Filter files based on start and end date
    filtered_files = []
    for file in files:
        
        file_date = extract_date_from_filename(file, family)
        if start_date <= file_date <= end_date:
            filtered_files.append(file)

    date_counts = {}

    # Iterate over the filtered files
    for file in filtered_files:
        conn = sqlite3.connect(file)
        cursor = conn.cursor()
        
        # Perform the count(*) query
        cursor.execute('SELECT COUNT(*) FROM data')
        count = cursor.fetchone()[0]
        
        # Extract the date from the filename
        file_date = extract_date_from_filename(file, family)
        
        # Sum counts by date
        if file_date not in date_counts:
            date_counts[file_date] = 0
        date_counts[file_date] += count
        
        conn.close()

    return date_counts

# Paths for the two families
name1 = 'postalt'
#name1 = 'evalalt'

#path1 = f'/home/sprj700/data_maestro/ppp6/maestro_archives/G2FC900V2E22/monitoring/banco/{name1}/'
path1 = f'/home/smco500/.suites/psmon/monitoring/g2/hub/ppp5/sqlite/banco/{name1}/'
path1 = f'/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/{name1}/'
name2 = 'evalalt'
#name2 = 'dbase'

#path2 = f'/home/sprj700/data_maestro/ppp6/maestro_archives/G2FC900V2E22/monitoring/banco/{name2}/'
path2 = f'/home/smco500/.suites/psmon/monitoring/g2/hub/ppp5/sqlite/banco/{name2}/'
path2 = f'/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/{name2}/'

family1 = '*cris*'
family2 = '*cris*'
print (path1)
print (path2)
start_date_str = '2024102400'  # Example start date
end_date_str = '2024102800'    # Example end date
if name1=='postalt'and name2=='evalalt':

  color1='tab:blue'
  color2='tab:green'

if name1=='evalalt' and name2=='dbase':

  color1='tab:green'
  color2='tab:orange'


# Get counts for both families
counts_family1 = get_counts_by_date(path1, family1, start_date_str, end_date_str)
counts_family2 = get_counts_by_date(path2, family2, start_date_str, end_date_str)

# Create DataFrame for easy plotting
df_family1 = pd.DataFrame(list(counts_family1.items()), columns=['Date', 'Count_family1'])
df_family2 = pd.DataFrame(list(counts_family2.items()), columns=['Date', 'Count_family2'])

# Merge both DataFrames on Date
df_merged = pd.merge(df_family1, df_family2, on='Date', how='outer').fillna(0)
# Sort the DataFrame by Date to ensure correct order in the plot
df_merged = df_merged.sort_values(by='Date')

# Calculate percentage of family2 compared to family1
print (df_merged['Count_family1'],df_merged['Count_family2'])
df_merged['Percentage'] = (df_merged['Count_family1'] / df_merged['Count_family2']) * 100
# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot percentage on primary y-axis
ax1.plot(df_merged['Date'], df_merged['Percentage'], marker='o', color='tab:red', label=f'Percentage ({name2} / {name1})')
print  (df_merged['Percentage'])
ax1.set_xlabel('Date')
ax1.set_ylabel('Percentage (%)', color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax1.set_ylim(0,100)

# Secondary y-axis to show total counts for both family1 and family2
ax2 = ax1.twinx()
ax2.set_ylim(0,400000000)

ax2.plot(df_merged['Date'], df_merged['Count_family1'], marker='x', color=color1, label=f'Count {name1}')
ax2.plot(df_merged['Date'], df_merged['Count_family2'], marker='x', color=color2, label=f'Count {name2} ')
ax2.set_ylabel('Observations (Count)', color='black')

# Adding legends
ax1.legend(loc='lower left', bbox_to_anchor=(0, 1.15))
ax2.legend(loc='lower right', bbox_to_anchor=(0, 1.15))

# Set grid, rotate x labels and tight layout
plt.grid(True)
plt.xticks(rotation=45)
plt.title(f'Percentage of _{name1} over {name2} Count with Total Observations Over Time( Family:{family1})')
plt.tight_layout()
plt.savefig(f'{family1}_{name2}_{name1}_{start_date_str}_{end_date_str}_comparison_plot2.png', dpi=300)  # You can adjust the dpi for higher quality

plt.show()
