import sqlite3
import glob
import os

import sqlite3

def create_and_insert_flag_observations(input_file, output_file):
    # Connect to the input SQLite file
    conn_input = sqlite3.connect(input_file)
    cursor_input = conn_input.cursor()
    print (input_file)
    # Connect to the output SQLite file
    conn_output = sqlite3.connect(output_file)
    cursor_output = conn_output.cursor()

    # Create a table in the output database if it does not exist
    cursor_output.execute('''
        CREATE TABLE IF NOT EXISTS flag_observations (
            date TEXT,
            time TEXT,
            flag INTEGER,
            num_data_entries INTEGER,
            id_stn INTEGER
        )
    ''')

    # Query to get the required data
    query = '''
        SELECT 
            h.date, 
            h.time, 
            d.flag, 
            COUNT(*) AS num_data_entries, 
            h.id_stn
        FROM 
            data d
        JOIN 
            header h ON d.id_obs = h.id_obs
        GROUP BY 
            h.date, 
            h.time, 
            d.flag, 
            h.id_stn
        ORDER BY 
            h.date, 
            h.time, 
            h.id_stn, 
            d.flag;
    '''
    
    # Execute the query
    cursor_input.execute(query)
    results = cursor_input.fetchall()

    # Insert results into the output database
    for date, time, flag, num_data_entries, id_stn in results:
        cursor_output.execute('''
            INSERT INTO flag_observations (date, time, flag, num_data_entries, id_stn)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, time, flag, num_data_entries, id_stn))

    # Close the connections
    conn_input.close()
    conn_output.commit()
    conn_output.close()

# Usage of the script

# Specify the directory path
directory = '/home/sprj700/data_maestro/ppp6/maestro_archives/G2FC900V2E22/monitoring/banco/postalt/'

# Use glob to get the list of files in the directory
print (directory)
file_list = glob.glob(os.path.join(directory, '20220812*amsua_allsky'))
output_file="output_file.db"
for filein in file_list:
   create_and_insert_flag_observations(filein, output_file)
