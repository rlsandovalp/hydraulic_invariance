import arcpy
import pandas as pd
from arcpy import env

arcpy.ImportToolbox(arcpy.env.workspace+"\\Lecco\\Tools\\ExcelTools\\Excel and CSV Conversion Tools")
#arcpy.ImportToolbox("C:/Users/rlsan/Downloads/Software/ExcelTools/Excel and CSV Conversion Tools")

# DEM, nodes and segments
DEM = arcpy.env.workspace+"\\Lecco\\rasters\\lecco_dtm.img"
nodes_csv = arcpy.env.workspace+"\\nodes.csv"
segments_csv = arcpy.env.workspace+"\\segments.csv"

# Input Files [Network, analysis limits]
nodes = arcpy.GetParameter(0)
segments = arcpy.GetParameter(1)

# Check if the network has been correctly drawn
arcpy.AddMessage("Checking the geometry of the sewer system ...")
arcpy.TableToCSV_tableconversion(nodes, nodes_csv, "COMMA")
arcpy.TableToCSV_tableconversion(segments, segments_csv, "COMMA")
df_nodes = pd.read_csv(nodes_csv)
df_pipes = pd.read_csv(segments_csv)

for i in range (len(df_nodes)):
   df_nodes.iloc[i,5] = round(df_nodes.iloc[i,5],1)

for i in range (len(df_pipes)):
   df_pipes.iloc[i,2] = round(df_pipes.iloc[i,2],1)
   df_pipes.iloc[i,3] = round(df_pipes.iloc[i,3],1)

trouble_pipes = []
for i in range (len(df_pipes)):
   zini = (df_nodes[df_nodes['point'] == df_pipes.iloc[i,2]]['Z']).iloc[0]
   zend = (df_nodes[df_nodes['point'] == df_pipes.iloc[i,3]]['Z']).iloc[0]
   if zini<=zend:
      trouble_pipes.append(df_pipes.iloc[i,0])
arcpy.Delete_management(nodes_csv)
arcpy.Delete_management(segments_csv)
if len(trouble_pipes) == 0:
   arcpy.AddMessage("The network has no geometry problems. The Main script can be run now.") 
elif len(trouble_pipes)>0:
   arcpy.AddError("The Following pipes have geometry troubles. Please correct the elevations in the 'nodes' shapefile or redraw the network in the 'NET' shapefile. Then run the Script2")
   arcpy.AddError(trouble_pipes)

arcpy.Delete_management(nodes_csv)
arcpy.Delete_management(segments_csv)