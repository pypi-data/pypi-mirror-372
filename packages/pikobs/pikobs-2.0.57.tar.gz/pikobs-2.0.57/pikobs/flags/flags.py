"""
Generating Flags Info
=========================================================

This module calculates the type of flag associated with each observation for different families of observations. For example, the following representations:

 .. image:: ../../../docs/source/_static/flagatms_allsky.png
      :alt: atms allsky flag Plot

 .. image:: ../../../docs/source/_static/flagcris.png
      :alt: cris  flag Plot

 .. image:: ../../../docs/source/_static/flagiasi.png
      :alt: iasi flag Plot

Parameters Explanation
^^^^^^^^^^^^^^^^^^^^^^
- **path_experience:** Path to the directory where the experience data is stored.
- **experience_name:** Name of the specific experience.
- **pathwork:** Directory path indicating the working directory for the script.
- **datestart:** Start date and time of the assimilation process (format: YYYYMMDDHH).
- **dateend:** End date and time of the assimilation process (format: YYYYMMDDHH).
- **region:** Geographic region or area of interest for the assimilation analysis. (e.g., Monde, PoleNord, PoleSud, AmeriqueduNord, OuestAmeriqueduNord, AmeriqueDuNordPlus, ExtratropiquesNord, HemisphereNord, HemisphereSud, Asie, Europe, Mexique, Canada, BaieDhudson, Arctiquecanadien, EtatsUnis, Tropiques30, Tropiques, Australie, Pacifique and Atlantique)
- **family:** Family of data assimilated (e.g., mwhs2, mwhs2_qc, to_amsua_qc, to_amsua, to_amsua_allsky, to_amsua_allsky_qc, to_amsub_qc, to_amsub, ssmis_qc, ssmis, iasi, iasi_qc, crisfsr1_qc, crisfsr2_qc, cris, atms_allsky, atms_qc and csr, csr_qc)
- **id_stn:** all or satellite IDs for which assimilation results are analyzed (e.g., METOP-1, METOP-3). Modify as needed to specify particular satellites.
- **channel:** all or specific channels to analyze. Use 'all' to analyze all available channels. Modify as needed to specify particular channels of interest.
- **plot_title:** Title for the generated cardiogram.
- **n_cpu:** Number of CPU cores to be used for parallel processing. Adjust according to your system capabilities.

Additional Note
^^^^^^^^^^^^^^^
- Modify **--channel** and **--id_stn** parameters as needed to specify particular satellites and channels of interest.
- Ensure paths (**path_experience, pathwork**) are correctly set to point to your data directories.
- The script leverages parallel processing (**--n_cpu**) to optimize performance, adjust according to your system capabilities.
- The generated cardiograms provide comprehensive visual insights into the assimilation performance metrics across selected satellites, channels, and criteria.
- Adjust the parameters (**--channel, --id_stn, etc.**) according to your specific requirements and data.


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

def create_and_insert_flag_observations(input_file, output_file, region,pathwork,family):
    # Connect to the input SQLite file
    print (input_file)
    conn_input = sqlite3.connect(input_file)
    basename = os.path.basename(input_file)
    cursor_input = conn_input.cursor()

    # Get region criteria
    LAT1, LAT2, LON1, LON2 = pikobs.regions(region)
    LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)

    # Connect to the output SQLite file with optimizations
    conn_output = sqlite3.connect(f'{pathwork}/{family}/{output_file}', uri=True, isolation_level=None, timeout=99999)
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
    flag, 
    COUNT(*) AS num_data_entries, 
    id_stn, 
    varno,
    vcoord
    
FROM 
    data 
natural join  
    header 
    -- where {LATLONCRIT}
GROUP BY 
    date, 
    varno,
    flag, 
    id_stn,
    vcoord;
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
    filedb = f'{pathwork}/{family}/output_file{region}.db'
    
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
    print (path_experience_files, family)
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
   
   #pikobs.delete_create_folder(pathwork, family)

   for family in familys:
     for region in regions:
       pikobs.delete_create_folder(pathwork, family)

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
             create_and_insert_flag_observations(input_file, output_file, region, pathwork,family)
       else:

          print (f'Number of files in paralle = {len(file_list)}')
          with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                           n_workers=n_cpu, 
                                           silence_logs=40) as client:
            delayed_funcs = [dask.delayed(create_and_insert_flag_observations)(
                               input_file, output_file, region, pathwork,family)for input_file in file_list]

            results = dask.compute(*delayed_funcs)
       tn= time.time() 
       print ('Total time for plotting:',tn-t0 )  
       data_list_plot = create_data_list_plot(family, pathwork, region, id_stn, channel)
      # os.makedirs(f'{pathwork}/plots_{family}')
       t0 = time.time()
       if len(data_list_plot)==0:
          raise ValueError('You must specify best selectoion od id_stn and channel plot==0')
       n_cpu=1
      # print (data_list_plot)
       if n_cpu==1: 
          print (f'in Serie plots = {len(data_list_plot)}')
          print (data_list_plot)
          for  data_ in data_list_plot: 
              print ( data_['vcoord'],data_['id_stn'],   data_['varno'])


              pikobs.flags_plotv2(pathwork,
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
            delayed_funcs = [dask.delayed(pikobs.flags_plotv2)(
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

