import arcpy
from arcpy import env

# DEM, nodes and segments
nodes = arcpy.env.workspace+"\\shapes\\nodes.shp"
segments = arcpy.env.workspace+"\\shapes\\segments.shp"
nodes_csv = arcpy.env.workspace+"\\nodes.csv"
segments_csv = arcpy.env.workspace+"\\segments.csv"
segment2 = arcpy.env.workspace+"\\shapes\\segment2.shp"
fogne2 = arcpy.env.workspace+"\\shapes\\fogne2.shp"
fogne3 = arcpy.env.workspace+"\\shapes\\fogne3.shp"
split2 = arcpy.env.workspace+"\\shapes\\split2.shp"
thiessen = arcpy.env.workspace+"\\shapes\\thiessen.shp"
clip_thiessen = arcpy.env.workspace+"\\shapes\\clip_thiessen.shp"
losses = arcpy.env.workspace+"\\shapes\\losses.shp"
losses_dissolve = arcpy.env.workspace+"\\shapes\\losses_Dissolve.shp"
complete = arcpy.env.workspace+"\\shapes\\complete.shp"
complete_dissolve = arcpy.env.workspace+"\\shapes\\complete_Dissolve.shp"
up_nodes = arcpy.env.workspace+"\\upnodes.csv"
table_csv = arcpy.env.workspace+"\\upnodes_CSVToTable.dbf"

# Delete old files
arcpy.AddMessage("Deleting old files ...")
arcpy.Delete_management(nodes)
arcpy.Delete_management(segments)
arcpy.Delete_management(nodes_csv)
arcpy.Delete_management(segments_csv)
arcpy.Delete_management(segment2)
arcpy.Delete_management(fogne2)
arcpy.Delete_management(fogne3)
arcpy.Delete_management(split2)
arcpy.Delete_management(thiessen)
arcpy.Delete_management(clip_thiessen)
arcpy.Delete_management(losses)
arcpy.Delete_management(losses_dissolve)
arcpy.Delete_management(complete)
arcpy.Delete_management(complete_dissolve)
arcpy.Delete_management(up_nodes)
arcpy.Delete_management(table_csv)


# Turn off non relevant layers 
turn_off = ["nodes","segments","nodes_csv","segments_csv","segment2","fogne2","fogne3","split2","thiessen","clip_thiessen","losses_Dissolve","losses","complete","complete_dissolve"]
mxd = arcpy.mapping.MapDocument("current")
layers = arcpy.mapping.ListLayers(mxd)
for layer in layers:
  if layer.name in turn_off:
    layer.visible = False  

for df in arcpy.mapping.ListDataFrames(mxd):
    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
        if lyr.name in turn_off:
            arcpy.mapping.RemoveLayer(df, lyr)

arcpy.RefreshTOC()
arcpy.RefreshActiveView()