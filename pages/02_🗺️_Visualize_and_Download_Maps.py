import streamlit as st
import folium
import geopandas as gpd
import pyproj
from streamlit_folium import folium_static
from branca.colormap import linear
import tempfile
from zipfile import ZipFile

def my_color_function(feature):
    """Maps low values to green and high values to red."""
    if unemployment_dict[feature["id"]] > 6.5:
        return "#ff0000"
    else:
        return "#008000"

st.set_page_config(
    page_title="Download Maps",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

def save_shapefile_with_bytesio(dataframe, directory, my_municipality, my_parameter):
    dataframe.to_file(f"{directory}/"+my_municipality+"_"+my_parameter+".shp",  driver='ESRI Shapefile')
    zipObj = ZipFile(f"{directory}/"+my_municipality+"_"+my_parameter+"_zip.zip", 'w')
    zipObj.write(f"{directory}/"+my_municipality+"_"+my_parameter+".shp",arcname = my_municipality+'_'+my_parameter+'.shp')
    zipObj.write(f"{directory}/"+my_municipality+"_"+my_parameter+".cpg",arcname = my_municipality+'_'+my_parameter+'.cpg')
    zipObj.write(f"{directory}/"+my_municipality+"_"+my_parameter+".dbf",arcname = my_municipality+'_'+my_parameter+'.dbf')
    zipObj.write(f"{directory}/"+my_municipality+"_"+my_parameter+".prj",arcname = my_municipality+'_'+my_parameter+'.prj')
    zipObj.write(f"{directory}/"+my_municipality+"_"+my_parameter+".shx",arcname = my_municipality+'_'+my_parameter+'.shx')
    zipObj.close()


st.header('Visualize and Download Maps')

maps_and_filename = {'Soil Use': 'Data/Shapes_example/dusaf.shp', 
                     'LSPP': 'Data/Shapes_example/lspp_lecco.shp',
                     'Infiltration': 'Data/Shapes_example/infiltr.shp',
                     'Plan for hydrogeological management - Disasters': 'Data/Shapes_example/PAI_dissesti.shp',
                     'Plan for hydrogeological management - Feasibility': 'Data/Shapes_example/PAI_fattib.shp',
                     'Plan for hydrogeological management - High Risk': 'Data/Shapes_example/PAI_RME.shp',
                     'Plan for hydrogeological management - Seismic': 'Data/Shapes_example/PAI_sismi.shp',
                     'Pedology 250k': 'Data/Shapes_example/ped_250.shp',
                     'Pedology 50k': 'Data/Shapes_example/ped_50.shp',
                     'Permeability': 'Data/Shapes_example/permea_lecco.shp',}

number_variables = {'Soil Use': ['LIV_1', 'LIV_2', 'LIV_3', 'LIV_4'],
                    'LSPP': ['a1', 'n', 'alpha', 'epsilon', 'kappa', 'w1', 'w2', 'w3', 'h1_10', 'h1_50', 'h1_100'],
                    'Infiltration': ['CN', 'fo_Horton', 'fc_Horton', 'k_Horton'],
                    'Pedology 250k': ['CO_1M', 'PROF_UTILE', 'PH_1M']
                    }

fieldless_parameters = ['None',
                        'Plan for hydrogeological management - Disasters',
                        'Plan for hydrogeological management - Feasibility',
                        'Plan for hydrogeological management - High Risk',
                        'Plan for hydrogeological management - Seismic',
                        'Pedology 50k',
                        'Permeability']

col1, col2 = st.columns([1,2])
with col1:
    # Read shapefile with geometries of all municipalities
    all_municipalities = gpd.read_file("Data/Shapes_example/Comuni.shp")
    all_municipalities.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # Create list of names of municipalities
    names_municipalities = all_municipalities['NOME_COM'].unique().tolist()
    names_municipalities.sort()
    # Create list of names of maps
    names_maps = list(maps_and_filename.keys())
    names_maps.append('None')

    # Request user to select a municipality and a map
    my_municipality = st.selectbox('Select the municipality', names_municipalities)
    my_parameter = st.selectbox('Select the map', names_maps, index = len(names_maps)-1)

    if my_parameter not in fieldless_parameters:
        parameter_file = gpd.read_file(maps_and_filename[my_parameter]) 
        columns = number_variables[my_parameter]
        variable = st.selectbox('Select a variable to color the map', columns)

with col2:
    # Define the area to plot the results
    if my_municipality != 'None':
        area_to_show = all_municipalities[all_municipalities['NOME_COM'] == my_municipality]
    else:
        area_to_show = all_municipalities

    if my_parameter == 'None':
    # Create the map object
        m = folium.Map(location=[area_to_show['geometry'].centroid.y.mean(), area_to_show['geometry'].centroid.x.mean()], 
                    tiles = 'CartoDB Positron', zoom_start=13)
        
        # Add the clipped map to the map object
        folium.GeoJson(area_to_show, name="Municipalities", popup = folium.features.GeoJsonPopup(fields = ['NOME_COM'])).add_to(m)

        # folium.LayerControl().add_to(m)
        folium_static(m, width = 600, height = 600)
    else:
        # Load the selected map, clip it to the selected area and create a list of columns to show in the popup
        parameter_file = gpd.read_file(maps_and_filename[my_parameter])
        parameter_file.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        clipped = gpd.clip(parameter_file, area_to_show)

        if clipped.empty:
            st.write('The selected map does not have data for the selected municipality.')
            st.stop()

        columns = clipped.columns.tolist()
        columns.pop()
        # Create the map object
        m = folium.Map(location=[area_to_show['geometry'].centroid.y.mean(), area_to_show['geometry'].centroid.x.mean()], 
                    tiles = 'CartoDB Positron', zoom_start=13)

        if my_parameter in fieldless_parameters:
            folium.GeoJson(clipped, name = my_parameter, popup = folium.features.GeoJsonPopup(fields = columns)
                           ).add_to(m)
            # folium.LayerControl().add_to(m)
            folium_static(m, width = 600, height = 600)
        else:
        # Create the colormap to be used in the map
            clipped[variable] = clipped[variable].astype(float).round(2)
            colormap = linear.YlGn_09.scale(clipped[variable].min(), clipped[variable].max())
            colormap.caption = variable
            colormap.add_to(m)

            # Add the clipped map to the map object
            folium.GeoJson(clipped, 
                        name = my_parameter, 
                        popup = folium.features.GeoJsonPopup(fields = columns),
                        style_function = lambda feature : {"fillColor": colormap(feature["properties"][variable]),
                        "color": "black",
                        "weight": 0.2,
                        "fillOpacity": 0.9}
            ).add_to(m)

            # folium.LayerControl().add_to(m)
            folium_static(m, width = 600, height = 600)

with col1:
    st.header('Download the map')
    st.write('Click the button below to download the map.')
    filename = my_municipality + '_' + my_parameter + '.shp'
    clipped.to_file(filename)

    with tempfile.TemporaryDirectory() as tmp:
        #create the shape files in the temporary directory
        save_shapefile_with_bytesio(clipped, tmp, my_municipality, my_parameter)
        with open(f"{tmp}/"+my_municipality+"_"+my_parameter+"_zip.zip", "rb") as file:
            st.download_button(
                label="Download data",
                data=file,
                file_name=my_municipality+'_'+my_parameter+'.zip',
                mime='application/zip',
            )

