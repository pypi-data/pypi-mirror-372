import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob

# Extraer fecha del nombre de archivo
def extract_date_from_filename(filename, family):
    basename = os.path.basename(filename)
    date_str = basename.split(family)[0][:10]  # 'yyyymmddhh'
    return pd.to_datetime(date_str, format='%Y%m%d%H')

# Obtener conteos por fecha
def get_counts_by_date(path, family, start_date_str, end_date_str):
    start_date = pd.to_datetime(start_date_str, format='%Y%m%d%H')
    end_date = pd.to_datetime(end_date_str, format='%Y%m%d%H')
    
    # Filtrar archivos en el rango de fechas especificado
    files = [file for file in glob(os.path.join(path, f'*{family}*'))
             if start_date <= extract_date_from_filename(file, family) <= end_date]
    
    date_counts = {}
    for file in files:
        print (file)
        conn = sqlite3.connect(file)
        cursor = conn.cursor()
        
        # Obtener el conteo de observaciones en cada archivo
        cursor.execute('SELECT COUNT(*) FROM data;')
        count = cursor.fetchone()[0]
        
        file_date = extract_date_from_filename(file, family)
        date_counts[file_date] = date_counts.get(file_date, 0) + count
        
        conn.close()

    return date_counts

# Definir rutas para las diferentes familias
families = {
    'postalt': '/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/postalt/',
    'evalat': '/home/smco500/.suites/gdps/g2/hub/ppp6/monitoring/banco/evalalt/',
    'dbase': '/home/smco500/.suites/psmon/monitoring/g2/hub/ppp5/sqlite/banco/dbase/'
}

# Fechas y patrón de familia
family_pattern = '*cris*'
start_date_str = '2024102412'
end_date_str = '2024102912'

# Almacenar todos los conteos por familia
all_counts = {family: get_counts_by_date(path, family_pattern, start_date_str, end_date_str)
              for family, path in families.items()}

# Crear un DataFrame consolidado para conteos por fecha
df_counts = pd.DataFrame({family: pd.Series(counts) for family, counts in all_counts.items()}).reset_index()
df_counts.rename(columns={'index': 'Date'}, inplace=True)
df_counts.fillna(0, inplace=True)  # Rellenar valores faltantes con 0

# Calcular porcentajes entre las familias
df_counts['Percentage_postalt_evalat'] = (df_counts['postalt'] / (df_counts['evalat']/2)) * 100
df_counts['Percentage_evalat_dbase'] = (df_counts['evalat'] / df_counts['dbase']) * 100

# Calcular promedios de los porcentajes
average_percentage_postalt_evalat = df_counts['Percentage_postalt_evalat'].mean()
average_percentage_evalat_dbase = df_counts['Percentage_evalat_dbase'].mean()

# Graficar resultados
fig, ax1 = plt.subplots(figsize=(10, 6))

# Gráfico de porcentajes
ax1.set_ylabel('Percentage (%)', color='tab:red')
ax1.set_xlabel('Date')
ax1.plot(df_counts['Date'], df_counts['Percentage_evalat_dbase'], marker='*', markersize=12, linestyle='-', linewidth=4,  color='tab:red', label=f'Average Percentage evalalt/dbase = {average_percentage_evalat_dbase:.2f}%')
ax1.plot(df_counts['Date'], df_counts['Percentage_postalt_evalat'], marker='o', markersize=12, linestyle='-', linewidth=4, color='tab:red', label=f'Average Percentage postalt/evalalt = {average_percentage_postalt_evalat:.2f}%')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax1.set_ylim(0, 105)

# Crear segundo eje para conteo de observaciones
ax2 = ax1.twinx()
ax2.set_ylabel('Observations (Count)', color='black')
ax2.plot(df_counts['Date'], df_counts['dbase']/2, marker='x', linewidth=2, color='tab:orange', label=f'Average Count dbase = {int(df_counts["dbase"].mean()/2)}')
ax2.plot(df_counts['Date'], df_counts['evalat']/2, marker='x', linewidth=2, color='tab:green', label=f'Average Count evalalt = {int(df_counts["evalat"].mean())}')
ax2.plot(df_counts['Date'], df_counts['postalt'], marker='x', linewidth=2, color='tab:blue', label=f'Average   Count postalt = {int(df_counts["postalt"].mean())}')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_ylim(0, 200000000)

# Añadir leyendas y título
ax1.legend(loc='center left')
ax2.legend(loc='center right')
plt.title(f'Observations count and Percentages evalalt/dbase # postalt/evalalt Over Time - Family: {family_pattern}')
     #     f'Average Percentage postalt/evalat: {average_percentage_postalt_evalat:.2f}% '
     #     f'Average Percentage evalat/dbase: {average_percentage_evalat_dbase:.2f}%')
plt.xticks(rotation=45)
plt.grid(True)
plt.savefig('_plot4.png', dpi=300)
plt.savefig(f'{family_pattern}_{start_date_str}_{end_date_str}_comparison_plot.png', dpi=300) 
plt.show()

# Imprimir resultados para verificar
print("Conteos y porcentajes por fecha:")
print(df_counts[['Date', 'postalt', 'evalat', 'dbase', 'Percentage_postalt_evalat', 'Percentage_evalat_dbase']])

