# Importar librerias necesarias
import arcpy
import pandas as pd
from arcpy import env

# Importar Toolbox
arcpy.ImportToolbox(arcpy.env.workspace+"\\..\\Lecco\\Tools\\ExcelTools\\Excel and CSV Conversion Tools")
arcpy.ImportToolbox(arcpy.env.workspace+"\\Lecco\\Tools\\ExcelTools\\Excel and CSV Conversion Tools")

# Dfinit ubicaciones del DEM, nodes, segments, nodes_csv, segments_csv
DEM = arcpy.env.workspace+"\\..\\Lecco\\rasters\\lecco_dtm.img"
nodes = arcpy.env.workspace+"\\mappe\\nodes.shp"
segments = arcpy.env.workspace+"\\mappe\\segments.shp"
nodes_csv = arcpy.env.workspace+"\\nodes.csv"
segments_csv = arcpy.env.workspace+"\\segments.csv"

# Delete conflict files
arcpy.AddMessage("Deleting old files ...")
arcpy.Delete_management(nodes)
arcpy.Delete_management(segments)

# -Read Input Files from those selected in the visual screen [Network, analysis limits]
polyline = arcpy.GetParameter(0)
# polyline = arcpy.env.workspace+"\\Lecco\\Shapes\\NET.shp"


# Create the sewers in the polyline vertices
arcpy.AddMessage("Creating sewers ...")
arcpy.FeatureVerticesToPoints_management(polyline, nodes, "ALL")

# Add X Y Z information to the sewers
arcpy.AddMessage("Adding X, Y , Z information to the sewers ...")
arcpy.AddXY_management(nodes)
arcpy.UpdateFeatureZ_3d(nodes, DEM, method="BILINEAR", status_field="")
arcpy.DeleteField_management(nodes, ["ORIG_FID", "POINT_Z", "POINT_M", "Diameter_m", "Id"])
arcpy.AddZInformation_3d(nodes, out_property="Z", noise_filtering="NO_FILTER")
[arcpy.AddField_management(nodes,field_name,"double") for field_name in ['point','node_up','node_dw']]
arcpy.CalculateField_management(nodes,"point","[POINT_X] + [POINT_Y]")
arcpy.CalculateField_management(nodes,"node_up","[FID]")
arcpy.CalculateField_management(nodes,"node_dw","[FID]")

# Create the pipes using the vertices of the network as the limits of each pipe. Then add initial and final node of each pipe.
arcpy.AddMessage("Creating pipes ...")
arcpy.SplitLine_management(polyline, segments)
arcpy.AddGeometryAttributes_management(segments, Geometry_Properties="LINE_START_MID_END", Length_Unit="", Area_Unit="", Coordinate_System="")
arcpy.AddField_management(segments, "start", "double")
arcpy.CalculateField_management(segments,'start',"[START_X] + [START_Y]")
arcpy.AddField_management(segments, "end", "double")
arcpy.CalculateField_management(segments,'end',"[END_X] + [END_Y]")
arcpy.DeleteField_management(segments, ["Id", "Id_fog", "START_X", "START_Y", "START_Z", "START_M", "MID_X", "MID_Y", "MID_Z", "MID_M", "END_X", "END_Y", "END_Z", "END_M"])

arcpy.JoinField_management(segments, "start", nodes, "point", fields="node_up")
arcpy.JoinField_management(segments, "end", nodes, "point", fields="node_dw")

arcpy.DeleteField_management(segments, ["start", "end"])
arcpy.DeleteField_management(nodes, ["point", "node_up", "node_dw"])


# Check the network
# Test if the network has been correctly drawn (This is done in Python, not in arcgis)
arcpy.AddMessage("Checking the geometry of the sewer system ...")
arcpy.TableToCSV_tableconversion(nodes, nodes_csv, "COMMA")
arcpy.TableToCSV_tableconversion(segments, segments_csv, "COMMA")
df_nodes = pd.read_csv(nodes_csv)
df_pipes = pd.read_csv(segments_csv)

trouble_pipes = []
for i in range (len(df_pipes)):
   zini = (df_nodes[df_nodes['FID'] == df_pipes.iloc[i,2]]['Z']).iloc[0]
   zend = (df_nodes[df_nodes['FID'] == df_pipes.iloc[i,3]]['Z']).iloc[0]
   if zini<=zend:
      trouble_pipes.append(df_pipes.iloc[i,0])
arcpy.Delete_management(nodes_csv)
arcpy.Delete_management(segments_csv)
if len(trouble_pipes) == 0:
   arcpy.AddMessage("The Network was created and has no geometry problems. The Main script can be run now.") 
elif len(trouble_pipes)>0:
   arcpy.AddWarning("The Following pipes have geometry troubles. Please correct the elevations in the 'nodes' shapefile or redraw the network in the 'NET' shapefile. Then run the Script2")
   arcpy.AddWarning(trouble_pipes)

# Add files to the canvas
mxd = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataFrames(mxd)[0]
addLayer = arcpy.mapping.Layer(nodes)
arcpy.mapping.AddLayer(df,addLayer)
addLayer = arcpy.mapping.Layer(segments)
arcpy.mapping.AddLayer(df,addLayer)


