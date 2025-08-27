import cartopy.crs as ccrs
import pylab as plt
import numpy as np
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

def type_projection(Proj):   
   
   """

Projection type
================

 .. image:: ../../../docs/source/_static/proj.png
      :alt: proj Plot


   """

   
   Proj= Proj.lower()
   pc = ccrs.PlateCarree()
   if Proj=='cyl':
    PROJ = ccrs.PlateCarree()
    fig = plt.figure(figsize=(14,7))
    ax = plt.axes(projection=PROJ)
   
    ax.set_extent([-180, 180, -90, 90], crs=PROJ)
    LATPOS=[-90,-60,-30,00,30,60,90]
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)

   elif Proj=='orthon':
    PROJ= ccrs.Orthographic(central_latitude=90.0, central_longitude=-80.0)
    fig = plt.figure(figsize=(14,14))
    ax = plt.axes(projection=PROJ)
   
    ax.set_global()
    ax.coastlines(resolution='110m')
   
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
   elif Proj=='orthos':
    PROJ= ccrs.Orthographic(central_latitude=-90.0, central_longitude=-80.0)
    fig = plt.figure(figsize=(14,14))
    ax = plt.axes(projection=PROJ)
   
    ax.set_global()
    ax.coastlines(resolution='110m')
   
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
    #=================================================================================
   elif Proj=='robinson':
    PROJ = ccrs.Robinson()
    fig = plt.figure(figsize=(15,7))
    ax = plt.subplot(1, 1, 1, projection=PROJ)
   
    ax.set_extent([-180, 180, -90, 90], pc )
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
   # ax.coastlines(resolution='110m')

   elif Proj=='europe':
    PROJ=ccrs.NorthPolarStereo( )#central_longitude=-105.0)
    fig = plt.figure(figsize=[14, 14])
    ax = plt.subplot(1, 1, 1, projection=PROJ)
   
    #ax.set_extent([-50,  53, 42, 90], pc )
    ax.set_extent([-20, 50, 30, 90], crs=ccrs.PlateCarree()) 
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
   
   
   elif Proj=='canada':
  #  PROJ=ccrs.NorthPolarStereo( central_longitude=-105.0)
  #  fig = plt.figure(figsize=[14, 7])
  #  ax = plt.subplot(1, 1, 1, projection=PROJ)
  # 
  #  ax.set_extent([-150,  -53, 42, 90], pc )
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
    PROJ = ccrs.NorthPolarStereo(central_longitude=-105.0)
    fig = plt.figure(figsize=[14, 14])
    ax = plt.subplot(1, 1, 1, projection=PROJ)
   
    # Ajusta el set_extent para la proyección polar
    ax.set_extent([-150, -53, 42, 90], crs=ccrs.PlateCarree())

   elif Proj=='ameriquenord':
    PROJ=ccrs.NorthPolarStereo( central_longitude=-105.0)
    fig = plt.figure(figsize=[14, 7])
    ax = plt.subplot(1, 1, 1, projection=PROJ)
   
    ax.set_extent([-140,  -40, 20, 90], pc )
    ax.set_extent([-170,  -40, 20, 90], pc )
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
   
   elif Proj=='npolar':
    PROJ=ccrs.NorthPolarStereo( central_longitude=-90.5)
    fig = plt.figure(figsize=[13, 7])
    ax = plt.subplot(1, 1, 1, projection=PROJ)
   
    ax.set_extent([-180, 180, 00, 90], pc )
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)
    ax.coastlines(resolution='110m')
   elif Proj=='spolar':
    PROJ=ccrs.SouthPolarStereo( central_longitude=-86)
    fig = plt.figure(figsize=[14, 14])
    ax = plt.subplot(1, 1, 1, projection=PROJ)
   
    ax.set_extent([-180, 180, -90, 00], pc )
    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)

   elif Proj=='hrdps':

    pole_latitude = 35.7
    pole_longitude = 65.5

    PROJ=ccrs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude)
    fig = plt.figure(figsize=[14, 7])
    ax = plt.subplot(1, 1, 1, projection=PROJ)
    lat_0 = 48.8
    delta_lat = 10.
    lon_0 = 266.00
    delta_lon = 40.
    ax.set_extent([lon_0 - delta_lon, lon_0 + delta_lon, lat_0 - delta_lat, lat_0 + delta_lat], pc)


    LATPOS=[-90,-80,-60,-50,-40,-30,00,30,40,50,60,80,90]
    LATPOS=range(-90, 91, 10)




   elif Proj == 'reg':
     Size_mapx=10
     Size_mapy=10
     pole_latitude=31.758
     pole_longitude=178.008 -90.
     llcrnrlat = -7.74911
     llcrnrlon = -128.80635
     urcrnrlat = 57.88194
     urcrnrlon =39.378404
     central_rotated_longitude=-90. -1.991605
     PROJ = ccrs.RotatedPole(pole_longitude=pole_longitude ,  pole_latitude=pole_latitude,
                          central_rotated_longitude=central_rotated_longitude)
     fig=plt.figure(1,figsize=( Size_mapx,Size_mapy))
     ax = fig.add_subplot(1, 1, 1, projection=PROJ)
   
     mapExtent=[llcrnrlon , urcrnrlon,llcrnrlat,urcrnrlat]
     ax.set_extent(mapExtent)
     xs, ys, zs = PROJ.transform_points(pc,
                                    np.array([llcrnrlon, urcrnrlon]),
                                    np.array([llcrnrlat, urcrnrlat])).T
    # print (  ' Xlims=', xs )
   #  print (  ' Ylims=', ys )
   
     ax.set_xlim(xs)
     ax.set_ylim(ys)
     LATPOS=[-60,-30,00,10.,20.,30.,40.,50.,60.,70.,80.,90.]
  
   gl = ax.gridlines(draw_labels=True, linewidth=0.7, color='gray', alpha=0.5, linestyle='--')
   gl.top_labels = False              # Quita etiquetas arriba
   gl.right_labels = False            # Quita etiquetas derecha
   
   # Para dejar los labels bonitos:
   gl.xlabel_style = {'size': 12}
   gl.ylabel_style = {'size': 12}
   gl.xformatter = LongitudeFormatter()
   gl.yformatter = LatitudeFormatter()
   
   # (Opcional) Controlar intervalos:
   gl.xlocator = plt.FixedLocator(np.arange(-180, 181, 30))
   gl.ylocator = plt.FixedLocator(np.arange(-90, 91, 30))
   
   # Si quieres cambiar el texto de los ejes:
   #ax.set_xlabel('Longitud')
   #ax.set_ylabel('Latitud')
   return ax, fig, LATPOS, PROJ, pc
 #  print (  ' HEURE5 Nombre=', datetime.datetime.now().time() )
