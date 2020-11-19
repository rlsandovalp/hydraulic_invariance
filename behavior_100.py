import arcpy
from arcpy import env

# Variables of the files and folders
split2 = arcpy.env.workspace+"\\Invarianza\\mappe\\split2.shp"
symbology100 = arcpy.env.workspace+"\\Lecco\\layers\\symbology100.lyr"

# Load the shapefile
mxd = arcpy.mapping.MapDocument("CURRENT")  
df = arcpy.mapping.ListDataFrames(mxd)[0]  
arcpy.MakeFeatureLayer_management(split2, "split2")  

# Apply the symbology and show the shapefile in the canvas
arcpy.ApplySymbologyFromLayer_management(in_layer="split2", in_symbology_layer=symbology100)
addLayer = arcpy.mapping.Layer("split2") 
arcpy.mapping.AddLayer(df,addLayer) 