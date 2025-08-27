"""

Description
------------

This module calculates the error histogram of observations over a period, for example:
  

    .. image:: ../../../docs/source/_static/histogram.png
      :alt: Clasic time serie
  
    .. image:: ../../../docs/source/_static/histogram2.png
      :alt: Clasic time serie




""" 
#!/usr/bin/python3
import sqlite3
import pikobs
import re
import os
from  dask.distributed import Client
import numpy as np
import sqlite3
import os
import re
import sqlite3
from  datetime import datetime, timedelta
import glob
import sqlite3
import pikobs  # Assuming this is a custom module for region processing

def create_and_insert_flag_observations(input_file, output_file, region,pathwork):
    # Connect to the input SQLite file
    conn_input = sqlite3.connect(input_file)
    basename = os.path.basename(input_file)
    cursor_input = conn_input.cursor()

    # Get region criteria
    LAT1, LAT2, LON1, LON2 = pikobs.regions(region)
    LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)

    # Connect to the output SQLite file with optimizations
    conn_output = sqlite3.connect(f'{pathwork}/{output_file}', uri=True, isolation_level=None, timeout=999)
    conn_output.execute('PRAGMA synchronous = OFF')  # Turn off synchronous mode for faster writes
    conn_output.execute('PRAGMA journal_mode = MEMORY')  # Use memory journal mode for faster writes
    cursor_output = conn_output.cursor()

    # Create a table in the output database if it does not exist
    cursor_output.execute('''
        CREATE TABLE IF NOT EXISTS flag_observations (
            date TEXT,
            flag INTEGER,
            num_data_entries INTEGER,
            id_stn INTEGER,
            varno interger,
            vcoord integer
        )
    ''')

    # Query to get the required data
    query = f'''
        SELECT 
    {basename[0:10]},
    d.flag, 
    COUNT(*) AS num_data_entries, 
    h.id_stn, 
    d.varno,
    d.vcoord
    
FROM 
    data d
JOIN 
    header h ON d.id_obs = h.id_obs
    -- where {LATLONCRIT}
GROUP BY 
    h.date, 
    d.varno,
    d.flag, 
    h.id_stn,
    d.vcoord;
    '''

    # Execute the query and fetch results
    cursor_input.execute(query)
    results = cursor_input.fetchall()

    # Insert results into the output database in batches
    cursor_output.executemany('''
        INSERT INTO flag_observations (date, flag, num_data_entries, id_stn, varno, vcoord)
        VALUES (?, ?, ?, ?, ?,?)
    ''', results)

    # Commit and close the connections
    conn_input.close()
    conn_output.commit()
    conn_output.close()


def create_serie_histogram(family, 
                        new_db_filename, 
                        existing_db_filename,
                        region_seleccionada,
                        selected_flags, 
                        id_stn,
                        channel, 
                        varno):
    """

    Create a new SQLite database with a 'moyenne' table and populate it with data from an existing database.

    Args:

      new_db_filename (str): Filename of the new database to be created.
  
      existing_db_filename (str): Filename of the existing database to be attached.
  
      region_seleccionada (str): Region selection criteria.
   
      selected_flags (str): Selected flags criteria.
   
      FONCTION (float): Value for sum_fonction column.

    
    Returns:
    
      None
    
    """

 
    pattern = r'(\d{10})'
    match = re.search(pattern, existing_db_filename)

    if match:
        date = match.group(1)
       
    else:
        print("No 10 digits found in the string.")
    
    # Connect to the new database
    if id_stn[0]=='all':
      criteria_id_stn = '    '
    else:
       # Paso 1: Añadir comillas simples alrededor de cada elemento
       elementos_con_comillas = [f"'{elemento}'" for elemento in id_stn]

       # Paso 2: Unir los elementos con comas
       resultado = f"({','.join(elementos_con_comillas)})"
       criteria_id_stn = f'and id_stn in {resultado}'
    if channel[0]=='all':
      criteria_vcoord = '    '
    else:
       resultado = f"({','.join(channel)})"
       criteria_vcoord = f'and vcoord in {resultado}    '

      
    new_db_conn = sqlite3.connect(new_db_filename, uri=True, isolation_level=None, timeout=999)
    new_db_cursor = new_db_conn.cursor()

    FAM, VCOORD, VCOCRIT, STATB, VCOORD, VCOTYP = pikobs.family(family)
    LAT1, LAT2, LON1, LON2 = pikobs.regions(region_seleccionada)
    LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)
    flag_criteria = pikobs.flag_criteria(selected_flags)

    # Attach the existing database
    new_db_cursor.execute(f"ATTACH DATABASE '{existing_db_filename}' AS db;")
    # load extension CMC 
    new_db_conn.enable_load_extension(True)
    extension_dir = f'{os.path.dirname(pikobs.__file__)}/extension/libudfsqlite-shared.so'
    new_db_conn.execute(f"SELECT load_extension('{extension_dir}')")
    # Create the 'moyenne' table in the new database if it doesn't exist
    new_db_cursor.execute("""
           CREATE TABLE IF NOT EXISTS serie_cardio ( 
            DATE INTEGER,
            Chan INTEGER,
            Nrej INTEGER,
            Nacc INTIGER,
            AvgOMP FLOAT, 
            AvgOMA FLOAT,
            StdOMP FLOAT,
            StdOMA FLOAT,
            NDATA  INTEGER,
            Nprofile INTEGER,
            AvgBCOR FLOAT,
            AvgOBS FLOAT,
            Ntot INTEGER,
            varno INTEGER,
            id_stn  TEXT
        );
    """)
    query=f"""INSERT INTO serie_cardio (

            DATE,
            Chan,
            Nrej,
            Nacc,
            AvgOMP, 
            AvgOMA,
            StdOMP,
            StdOMA,
            NDATA,
            Nprofile,
            AvgBCOR,
            AvgOBS,
            Ntot,
            varno,
            id_stn
        )
    
    
             SELECT 
                 isodatetime({date}) AS DATE,  
                 VCOORD As Chan, 
                 SUM(flag & 512=512) AS Nrej,
                 SUM(flag & 4096=4096) AS Nacc,
                 ROUND(AVG(OMP), 4) AS AvgOMP,
                 ROUND(AVG(OMA), 4) AS AvgOMA,
                 ROUND(STDDEV(OMP), 4) AS StdOMP,
                 ROUND(STDDEV(OMA), 4) AS StdOMA,
                 SUM(OMP IS NOT NULL) AS NDATA,
                 COUNT(DISTINCT id_obs) AS Nprofils,
                 ROUND(AVG(BIAS_CORR), 4) AS AvgBCOR,
                 ROUND(AVG(OBSVALUE), 4) AS AvgOBS,
                 (SELECT COUNT(*) FROM header h2 WHERE h2.ID_STN = header.ID_STN) AS Ntot,
                 varno AS varno,
                 id_stn AS id_stn
                 
            FROM 
                 header
             NATURAL JOIN 
                 data
             WHERE 
                 VARNO = {int(varno)}
                 {criteria_id_stn}
                 {criteria_vcoord}
                 {flag_criteria}
                 {LATLONCRIT}
                 {VCOCRIT}
             GROUP BY 
                 VCOORD, ID_STN
             HAVING 
                 SUM(OMP IS NOT NULL) >= 50;"""

    new_db_cursor.execute(query)
    # Commit changes and detach the existing database
    new_db_conn.commit()

    # Commit changes and detach the existing database
    new_db_cursor.execute("DETACH DATABASE db;")

    # Close the connections
    new_db_conn.close()

def create_data_list_cardio(datestart1, 
                            dateend1,
                            family,
                            pathin, 
                            pathwork,
                            flag_criteria,
                            id_stn,
                            channel,
                            region_seleccionada):
    
    data_list_cardio = []

    # Convert datestart and dateend to datetime objects
    datestart = datetime.strptime(datestart1, '%Y%m%d%H')
    dateend = datetime.strptime(dateend1, '%Y%m%d%H')

    # Initialize the current_date to datestart
    current_date = datestart

    # Define a timedelta of 6 hours
    delta = timedelta(hours=6)
    FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)

    element_array = np.array([float(x) for x in element.split(',')])
    for varno in element_array:
   #  print ("VCOORD", vcoord, element, type(element))
     # Iterate through the date range in 6-hour intervals
     while current_date <= dateend:
        # Format the current date as a string
        formatted_date = current_date.strftime('%Y%m%d%H')

        # Build the file name using the date and family
        filename = f'{formatted_date}_{family}'

        file_path_name = f'{pathin}/{filename}'
        conn = sqlite3.connect(file_path_name)
        # Create a cursor to execute SQL queries
        cursor = conn.cursor()

        #  Create a new dictionary and append it to the list
        data_dict = {'family': family,
                     'filein': f'{pathin}/{filename}',
                     'db_new': f'{pathwork}/cardio_{datestart1}_{dateend1}_{flag_criteria}_{family}.db',
                     'region': region_seleccionada,
                     'flag_criteria': flag_criteria,
                     'varno':  varno,
                     'vcoord': channel,
                     'id_stn': id_stn}
        data_list_cardio.append(data_dict)
        conn.close()

        # Update the current_date in the loop by adding 6 hours
        current_date += delta

    return data_list_cardio


def get_station_ids(cursor, id_stn):
    if id_stn[0] == 'all':
        cursor.execute("SELECT DISTINCT id_stn FROM data natural join header;")
        return [item[0] for item in cursor.fetchall()]
    else:
        
        return np.array(id_stn)

def fetch_channels_and_varno(cursor, idstn, channel):
    criter = f'WHERE id_stn = "{idstn}"'
    if channel[0] == 'all':
        query = f"SELECT DISTINCT vcoord, varno FROM data natural join header {criter} ORDER BY vcoord ASC;"
        cursor.execute(query)
        return cursor.fetchall()
    if channel[0] == 'join':
        return channel, idstn

def create_data_list_plot2(datestart1, dateend1, family, pathwork, region, id_stn, channel):
    data_list_plot = []
    import glob
    filedb = f'{pathwork}/output_file{region}.db'
    try:
        with sqlite3.connect(filedb) as conn:
            cursor = conn.cursor()
            id_stns = get_station_ids(cursor, id_stn)

            for idstn in id_stns:
                channels_varno = fetch_channels_and_varno(cursor, idstn, channel)
                for chan, varno in channels_varno:
                    data_dict_plot = {
                        'id_stn': idstn,
                        'vcoord': chan,
                        'varno': varno
                    }
                    data_list_plot.append(data_dict_plot)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return data_list_plot

def create_data_list_plot(family, pathwork, region, id_stn, vcoord):
    filedb = f'{pathwork}/output_file{region}.db'
    
    conn = sqlite3.connect(filedb)  # Conectar a la base de datos
    cursor = conn.cursor()

    data_dict_plot = []

    # Paso 1: Obtener todos los valores distintos de 'varno'
    cursor.execute("SELECT DISTINCT varno FROM flag_observations")
    varnos = cursor.fetchall()

    for varno_tuple in varnos:
        varno = varno_tuple[0]

        if vcoord[0] == 'join':
            if id_stn[0] == 'join':
                # Si 'id_stn' y 'vcoord' son 'join', solo se necesita un registro por 'varno'
                data_dict_plot.append({
                    'id_stn': 'join',
                    'vcoord': 'join',
                    'varno': varno
                })

            elif id_stn[0] == 'all':
                # Obtener 'id_stn' para cada 'varno' y 'vcoord' es 'join'
                query_id_stn = """
                    SELECT DISTINCT id_stn
                    FROM flag_observations
                    WHERE varno = ?
                """
                cursor.execute(query_id_stn, (varno,))
                id_stns = cursor.fetchall()

                for id_stn_tuple in id_stns:
                    id_stn_value = id_stn_tuple[0]
                    data_dict_plot.append({
                        'id_stn': id_stn_value,
                        'vcoord': 'join',
                        'varno': varno
                    })

        elif vcoord[0] == 'all':
            if id_stn[0] == 'join':
                # Obtener 'id_stn' para cada 'varno' y 'vcoord' es 'all'
                    
                    # Obtener 'vcoord' para cada 'id_stn'
                    query_vcoord = """
                        SELECT DISTINCT vcoord
                        FROM flag_observations
                        WHERE varno = ? 
                    """
                    cursor.execute(query_vcoord, (varno,))
                    vcoords = cursor.fetchall()

                    for vcoord_tuple in vcoords:
                        vcoord_value = vcoord_tuple[0]
                        data_dict_plot.append({
                            'id_stn': 'join',
                            'vcoord': vcoord_value,
                            'varno': varno
                        })

            elif id_stn[0] == 'all':
                # Obtener 'id_stn' y 'vcoord' para cada 'varno'
                query_id_stn = """
                    SELECT DISTINCT id_stn
                    FROM flag_observations
                    WHERE varno = ?
                """
                cursor.execute(query_id_stn, (varno,))
                id_stns = cursor.fetchall()

                for id_stn_tuple in id_stns:
                    id_stn_value = id_stn_tuple[0]
                    
                    # Obtener 'vcoord' para cada 'id_stn'
                    query_vcoord = """
                        SELECT DISTINCT vcoord
                        FROM flag_observations
                        WHERE varno = ? AND id_stn = ?
                    """
                    cursor.execute(query_vcoord, (varno, id_stn_value))
                    vcoords = cursor.fetchall()

                    for vcoord_tuple in vcoords:
                        vcoord_value = vcoord_tuple[0]
                        data_dict_plot.append({
                            'id_stn': id_stn_value,
                            'vcoord': vcoord_value,
                            'varno': varno
                        })

    conn.close()
    return data_dict_plot


def filter_files_by_date(path_experience_files, family, date1, date2):
    # Lista todos los archivos que coinciden con el patrón
    file_list = glob.glob(os.path.join(path_experience_files, f'*{family}'))

    # Convertir las fechas de los archivos y el rango a objetos datetime
    date_format = "%Y%m%d%H"
    date1_dt = datetime.strptime(date1, date_format)
    date2_dt = datetime.strptime(date2, date_format)

    filtered_files = []

    for file in file_list:
        # Extraer la parte de la fecha del nombre del archivo
        basename = os.path.basename(file)
        date_str = basename.split('_')[0]  # Esto asume que la fecha está al principio y seguida de '_'
        
        try:
            file_date = datetime.strptime(date_str, date_format)
        except ValueError:
            # Si no se puede convertir la fecha, ignorar el archivo
            continue
        
        # Verificar si la fecha del archivo está dentro del rango
        if date1_dt <= file_date <= date2_dt:
            filtered_files.append(file)
    
    return filtered_files  

def make_flags(path_experience_files,
                experience_names,      
                pathwork, 
                datestart,
                dateend,
                regions, 
                familys, 
             #   flag_criteria, 
                id_stn,
                channel,
            #    plot_type,
                plot_title,
                n_cpu):
   pikobs.delete_create_folder(pathwork)

   for family in familys:
     for region in regions:
       import time
       import dask


       file_list = filter_files_by_date(path_experience_files, family, datestart, dateend)
       output_file=f"output_file{region}.db"
       try:
           os.remove(output_file)
           print(f"File {output_file} has been deleted.")
       except FileNotFoundError:
           print(f"File {output_file} not found.")
       t0= time.time()

       if n_cpu==1: 
          print (f'Number of files in serie = {len(file_list)}')

          for input_file in file_list:
             create_and_insert_flag_observations(input_file, output_file, region, pathwork)
       else:

          print (f'Number of files in paralle = {len(file_list)}')
          with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                           n_workers=n_cpu, 
                                           silence_logs=40) as client:
            delayed_funcs = [dask.delayed(create_and_insert_flag_observations)(
                               input_file, output_file, region, pathwork)for input_file in file_list]

            results = dask.compute(*delayed_funcs)
       tn= time.time() 
       print ('Total time for plotting:',tn-t0 )  
       data_list_plot = create_data_list_plot(family, pathwork, region, id_stn, channel)
      # os.makedirs(f'{pathwork}/plots_{family}')
       t0 = time.time()
       if len(data_list_plot)==0:
          raise ValueError('You must specify best selectoion od id_stn and channel plot==0')
       n_cpu=1
       if n_cpu==1: 
          print (f'in Serie plots = {len(data_list_plot)}')
          print (data_list_plot)
          for  data_ in data_list_plot[0:1]: 
              print ( data_['vcoord'],data_['id_stn'],   data_['varno'])


              pikobs.flags_plot(pathwork,
                                 datestart,
                                 dateend,
                                 family,
                                 plot_title,
                                 data_['vcoord'],
                                 data_['id_stn'], 
                                 data_['varno'],
                                 region)
       else:
          print (f'Number of plot in paralle = {len(data_list_plot)}')
          with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                           n_workers=n_cpu, 
                                           silence_logs=40) as client:
            delayed_funcs = [dask.delayed(pikobs.flags_plot)(
                                 pathwork,
                                 datestart,
                                 dateend,
                                 family,
                                 plot_title,
                                 data_['vcoord'],
                                 data_['id_stn'], 
                                 data_['varno'],
                                 region)for data_ in data_list_plot]

            results = dask.compute(*delayed_funcs)
       tn= time.time()
       print ('Total time for plotting:',tn-t0 )  


def arg_call():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--path_experience_files', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--experience_name', default='undefined', type=str, help="experience's name")
    parser.add_argument('--pathwork', default='undefined', type=str, help="Working directory")
    parser.add_argument('--datestart', default='undefined', type=str, help="Start date")
    parser.add_argument('--dateend', default='undefined', type=str, help="End date")
    parser.add_argument('--region', nargs="+", default='undefined', type=str, help="Region")
    parser.add_argument('--family', nargs="+", default='undefined', type=str, help="Family")
  #  parser.add_argument('--flags_criteria', default='undefined', type=str, help="Flags criteria")
    parser.add_argument('--id_stn',nargs="+", default='all', type=str, help="id_stn") 
    parser.add_argument('--channel',nargs="+",  default='all', type=str, help="channel") 
  #  parser.add_argument('--plot_type', default='wide', type=str, help="channel")
    parser.add_argument('--plot_title', default='plot', type=str, help="channel")
    parser.add_argument('--n_cpus', default=1, type=int, help="Number of cpus")

    args = parser.parse_args()
    print ( "Inputs in cardiogram calculation")
    print ("----------------------------------------")

    for arg in vars(args):
      
       print (f'--{arg} {getattr(args, arg)}')
    print ("----------------------------------------")
    # check if each argument is 'undefined'
    if args.path_experience_files == 'undefined':
        raise ValueError('You must specify --path_experience_files')
    if args.experience_name == 'undefined':      
        raise ValueError('You must specify -experience_name')
    if args.pathwork  == 'undefined':
        raise ValueError('You must specify --pathwork')
    if args.datestart == 'undefined':
        raise ValueError('You must specify --datestart')
    if args.dateend == 'undefined':
        raise ValueError('You must specify --dateend')
    if args.region == 'undefined':
        raise ValueError('You must specify --region')
    if args.family == 'undefined':
        raise ValueError('You must specify --family')
 #   if args.flags_criteria == 'undefined':
 #       raise ValueError('You must specify --flags_criteria')
   # if args.fonction == 'undefined':
   #     raise ValueError('You must specify --fonction')

    #Call your function with the arguments
    sys.exit(make_flags(args.path_experience_files,
                        args.experience_name,
                        args.pathwork,
                        args.datestart,
                        args.dateend,
                        args.region,
                        args.family,
                        args.id_stn,
                        args.channel,
                        args.plot_title,
                        args.n_cpus))

