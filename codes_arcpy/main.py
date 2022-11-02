import arcpy
import pandas as pd
from arcpy import env
import numpy as np
import math

arcpy.ImportToolbox(arcpy.env.workspace+"\\Lecco\\Tools\\ExcelTools\\Excel and CSV Conversion Tools")

#Variables
max_capaci = (arcpy.GetParameter(0)/100)
duration = (arcpy.GetParameter(4)/60)

# max_capaci = 0.7
# duration = 1

#DEM, losses file and rain file of Lecco
DEM = arcpy.env.workspace+"\\..\\Lecco\\rasters\\lecco_dem.img"
losses_file = arcpy.env.workspace+"\\Lecco\\Shapes\\infiltr.shp"
rain_file = arcpy.env.workspace+"\\Lecco\\Shapes\\lspp_lecco.shp"

# Input Files (Network, town limits)
nodes = arcpy.GetParameter(1)
segments = arcpy.GetParameter(2)
limiti = arcpy.GetParameter(3)

# nodes = arcpy.env.workspace+"\mappe\\nodes.shp"
# segments = arcpy.env.workspace+"\\mappe\\segments.shp"
# limiti = arcpy.env.workspace+"\\mappe\\limiti3.shp"

# Processing files (sewers, areas)
segment2 = arcpy.env.workspace+"\\Invarianza\\mappe\\segment2.shp"
fogne2 = arcpy.env.workspace+"\\Invarianza\\mappe\\fogne2.shp"
fogne3 = arcpy.env.workspace+"\\Invarianza\\mappe\\fogne3.shp"
split2 = arcpy.env.workspace+"\\Invarianza\\mappe\\split2.shp"
thiessen = arcpy.env.workspace+"\\Invarianza\\mappe\\thiessen.shp"
clip_thiessen = arcpy.env.workspace+"\\Invarianza\\mappe\\clip_thiessen.shp"
# Files with the infiltration and rain information
losses = arcpy.env.workspace+"\\Invarianza\\mappe\\losses.shp"
losses_dissolve = arcpy.env.workspace+"\\Invarianza\\mappe\\losses_Dissolve.shp"
complete = arcpy.env.workspace+"\\Invarianza\\mappe\\complete.shp"
complete_dissolve = arcpy.env.workspace+"\\Invarianza\\mappe\\complete_Dissolve.shp"
# Files used in the accumulation of the flow
nodes_csv = arcpy.env.workspace+"\\Invarianza\\mappe\\nodes.csv"
fogne3_csv = arcpy.env.workspace+"\\Invarianza\\mappe\\fogne3.csv"
segments_csv = arcpy.env.workspace+"\\Invarianza\\mappe\\segments.csv"
up_nodes = arcpy.env.workspace+"\\Invarianza\\mappe\\upnodes.csv"
table_csv = arcpy.env.workspace+"\\Invarianza\\mappe\\upnodes_CSVToTable.dbf"

# Delete conflict files
arcpy.AddMessage("Deleting old files ...")
arcpy.Delete_management(fogne2)
arcpy.Delete_management(fogne3)
arcpy.Delete_management(segment2)
arcpy.Delete_management(split2)
arcpy.Delete_management(thiessen)
arcpy.Delete_management(clip_thiessen)
arcpy.Delete_management(losses)
arcpy.Delete_management(losses_dissolve)
arcpy.Delete_management(complete)
arcpy.Delete_management(complete_dissolve)
arcpy.Delete_management(nodes_csv)
arcpy.Delete_management(segments_csv)
arcpy.Delete_management(up_nodes)
arcpy.Delete_management(table_csv)

# Test if the network has been correctly drawn
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
arcpy.Delete_management(segments_csv)
arcpy.Delete_management(nodes_csv)
if len(trouble_pipes)>0:
   arcpy.AddWarning("The Following pipes have geometry troubles. Please correct the elevations in the 'nodes' shapefile or redraw the network in the 'NET' shapefile. Then run the Script2")
   arcpy.AddWarning(trouble_pipes)

arcpy.Copy_management(arcpy.Describe(segments).catalogPath, segment2)

# Create the areas and cut the areas to those of interest for the project
arcpy.AddMessage("Creating areas ...")
arcpy.CreateThiessenPolygons_analysis(nodes, thiessen, "ALL")
arcpy.Clip_analysis(thiessen, limiti, clip_thiessen)

# COMPUTING THE INFILTRATION INFORMATION
# Intersect losses with the areas
arcpy.AddMessage("Computing the infiltration capacity ...")
arcpy.Intersect_analysis("'"+losses_file+"' #;'"+clip_thiessen+"' #", losses, join_attributes="ALL", cluster_tolerance="-1 Unknown", output_type="INPUT")
# Create fields in the table of losses
[arcpy.AddField_management(losses,field_name,"DOUBLE") for field_name in ['area', 'cn1']]
# Compute each one of the fields created in the previous line
arcpy.CalculateField_management(losses,'AREA','!shape.area!','PYTHON')
arcpy.CalculateField_management(losses, "cn1", "[CN] * [area]")

# Dissolve the losses file
arcpy.Dissolve_management(losses, losses_dissolve, "Input_FID", "cn1 SUM", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
# Create fields in the table of losses dissolve
[arcpy.AddField_management(losses_dissolve,field_name,"DOUBLE") for field_name in ['area', 'CN']]
# Compute each one of the fields created in the previous line
arcpy.CalculateField_management(losses_dissolve,'AREA','!shape.area!','PYTHON')
arcpy.CalculateField_management(losses_dissolve, "CN", "[SUM_cn1] / [area]")
# Delete useless fields in the losses dissolve file
arcpy.DeleteField_management(losses_dissolve, ["SUM_CN1"])


# COMPUTING THE RAIN INFORMATION
# Intersect rain with the areas
arcpy.AddMessage("Computing the rain properties ...")
arcpy.Intersect_analysis("'"+rain_file+"' #;'"+losses_dissolve+"' #", complete, join_attributes="ALL", cluster_tolerance="-1 Unknown", output_type="INPUT")
# Create fields in the table of rain
[arcpy.AddField_management(complete,field_name,"DOUBLE") for field_name in ['area', 'a1', 'n1', 'alpha', 'epsilon', 'kappa']]
# Compute the fields created in the previous line
arcpy.CalculateField_management(complete,'area','!shape.area!','PYTHON')
arcpy.CalculateField_management(complete, "a1", "[a1point_gr] * [area]")
arcpy.CalculateField_management(complete, "n1", "[ennepoint1] * [area]")
arcpy.CalculateField_management(complete, "alpha", "[alphpoint_] * [area]")
arcpy.CalculateField_management(complete, "epsilon", "[epsipoint_] * [area]")
arcpy.CalculateField_management(complete, "kappa", "[kappapoi_1] * [area]")
# Dissolve the rain file
arcpy.Dissolve_management(complete, complete_dissolve, dissolve_field="INPUT_FID", statistics_fields="CN MEAN;a1 SUM;n1 SUM;alpha SUM;epsilon SUM;kappa SUM", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
# Create fields in the table of rain
[arcpy.AddField_management(complete_dissolve,field_name,"DOUBLE") for field_name in ['duration', 'area', 'a1', 'n1', 'alpha', 'epsilon', 'kappa', 'w_10', 'a_10', 'pe_10', 'h_10','w_30', 'a_30', 'pe_30', 'h_30','w_50', 'a_50', 'pe_50', 'h_50', 'w_100', 'a_100', 'pe_100', 'h_100', 'CN','S','i_10','i_50']]
# Compute the fields created in the previous line
arcpy.CalculateField_management(complete_dissolve,'duration',str(duration))
arcpy.CalculateField_management(complete_dissolve,'area','!shape.area!','PYTHON')
arcpy.CalculateField_management(complete_dissolve, "a1", "[SUM_a1] / [area]")
if duration<1:
   arcpy.CalculateField_management(complete_dissolve, "n1", 0.5)
else:
   arcpy.CalculateField_management(complete_dissolve, "n1", "[SUM_n1] / [area]")
arcpy.CalculateField_management(complete_dissolve, "alpha", "[SUM_alpha] / [area]")
arcpy.CalculateField_management(complete_dissolve, "epsilon", "[SUM_epsilo] / [area]")
arcpy.CalculateField_management(complete_dissolve, "kappa", "[SUM_kappa] / [area]")
arcpy.CalculateField_management(complete_dissolve, "CN", "[MEAN_CN] ")
arcpy.CalculateField_management(complete_dissolve, "S", " 25.4*(1000/[CN]-10) ")
arcpy.CalculateField_management(complete_dissolve, "w_10", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 10/(10-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_10", "[w_10] * [a1] * [duration]^[n1]")
arcpy.CalculateField_management(complete_dissolve, "pe_10", "(([a_10]-0.2*[S])^2)/([a_10]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_10", "[pe_10]*[area] / (1000*[duration]*60*60)")
arcpy.CalculateField_management(complete_dissolve, "w_30", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 30/(30-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_30", "[w_30] * [a1] * [duration]^[n1]")
arcpy.CalculateField_management(complete_dissolve, "pe_30", "(([a_30]-0.2*[S])^2)/([a_30]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_30", "[pe_30]*[area] / (1000*[duration]*60*60)")
arcpy.CalculateField_management(complete_dissolve, "w_50", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 50/(50-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_50", "[w_50] * [a1] * [duration]^[n1]")
arcpy.CalculateField_management(complete_dissolve, "pe_50", "(([a_50]-0.2*[S])^2)/([a_50]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_50", "[pe_50]*[area] / (1000*[duration]*60*60)")
arcpy.CalculateField_management(complete_dissolve, "w_100", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 100/(100-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_100", "[w_100] * [a1] * [duration]^[n1]")
arcpy.CalculateField_management(complete_dissolve, "pe_100", "(([a_100]-0.2*[S])^2)/([a_100]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_100", "[pe_100]*[area] / (1000*[duration]*60*60)")
arcpy.CalculateField_management(complete_dissolve, "i_10", "[a_10]*[duration]^([n1]-1)")
arcpy.CalculateField_management(complete_dissolve, "i_50", "[a_50]*[duration]^([n1]-1)")

# Delete useless fields
arcpy.DeleteField_management(complete_dissolve, ["SUM_a1", "SUM_n1", "SUM_alpha", "SUM_epsilo", "SUM_kappa","MEAN_CN"])


# Move the information of the areas to the sewers
arcpy.AddMessage("Transfering areas information to the sewers ...")
field_map = 'Node "Input_FID" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',Input_FID,-1,-1;X "POINT_X" true true false 19 Double 0 0 ,First,#,'+str(nodes)+',POINT_X,-1,-1;Y "POINT_Y" true true false 19 Double 0 0 ,First,#,'+str(nodes)+',POINT_Y,-1,-1;Z "Z" true true false 19 Double 0 0 ,First,#,'+str(nodes)+',Z,-1,-1;h_10 "h_10" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_10,-1,-1;h_30 "h_30" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_30,-1,-1;h_50 "h_50" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_50,-1,-1;h_100 "h_100" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_100,-1,-1'
arcpy.SpatialJoin_analysis(nodes, complete_dissolve, fogne2, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping=field_map, match_option="INTERSECT", search_radius="", distance_field_name="")
arcpy.DeleteField_management(fogne2, ["Join_Count", "TARGET_FID"])


# Delete overlay nodes to have only one node per spatial location
arcpy.Dissolve_management(fogne2, fogne3, dissolve_field="Node", statistics_fields="X MEAN; Y MEAN; Z MEAN;h_10 MEAN;h_30 MEAN;h_50 MEAN;h_100 MEAN", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
[arcpy.AddField_management(fogne3,field_name,"DOUBLE") for field_name in ['Acum10', 'Acum30', 'Acum50', 'Acum100']]

# Compute maximum capacity of the pipes adding Z information
arcpy.AddMessage("Computing capacity of the pipes ...")
# Add required fields
[arcpy.AddField_management(segment2,field_name,"DOUBLE") for field_name in ['z_start','z_end', 'length', 'slope', 'max_capaci', 'd', 'theta', 'A', 'Rh', 'ks', 'Q', 'Qr_Q']]
arcpy.JoinField_management(segment2, "node_up", fogne2, "FID", fields="Z")
arcpy.JoinField_management(segment2, "node_dw", fogne2, "FID", fields="Z")
arcpy.CalculateField_management(segment2,'z_start',"[Z]")
arcpy.CalculateField_management(segment2,'z_end',"[Z_1]")
arcpy.CalculateField_management(segment2,'length','!shape.length!','PYTHON')
cd_blk = """def pendiente(zs, ze, length):\n   pen=(zs-ze)/length\n   if pen<0.005:\n      hola = 0.005\n   else:\n      hola = pen\n   return hola"""
arcpy.CalculateField_management(segment2, "slope", "pendiente( !z_start!, !z_end!, !length!)", "PYTHON_9.3", cd_blk)
arcpy.CalculateField_management(segment2,'max_capaci',str(max_capaci))
arcpy.CalculateField_management(segment2,'d',"[Diameter_m]*[max_capaci]")
arcpy.CalculateField_management(segment2,"theta","2*math.acos(1 - 2*(!Diameter_m!*(1-!max_capaci!))/!Diameter_m!)",'PYTHON')
arcpy.CalculateField_management(segment2,"A","math.pi*(!Diameter_m!**2)/4-((!Diameter_m!)**2)*(!theta!-math.sin(!theta!))/8",'PYTHON')
arcpy.CalculateField_management(segment2,"Rh","!A!/(math.pi*!Diameter_m!-!Diameter_m!*!theta!/2)",'PYTHON')
arcpy.CalculateField_management(segment2,"ks","75")
arcpy.CalculateField_management(segment2,"Q","!A!*!ks!*!Rh!**(2./3)*math.sqrt(!slope!)",'PYTHON')
arcpy.CalculateField_management(segment2,"Qr_Q","1./(!ks!*math.sqrt(!slope!)*(!Diameter_m!**(8./3)))",'PYTHON')

# Update nodes names
arcpy.JoinField_management(segment2, "node_up", fogne2, "FID", fields="Node")
arcpy.JoinField_management(segment2, "node_dw", fogne2, "FID", fields="Node")
arcpy.CalculateField_management(segment2,'node_up',"[Node]")
arcpy.CalculateField_management(segment2,'node_dw',"[Node_1]")

# Delete useless fields
arcpy.DeleteField_management(segment2, ["Z", "Z_1", "Node", "Node_1"])

# Accumulate the flow in the network
arcpy.AddMessage("Accumulating the flow ...")
arcpy.TableToCSV_tableconversion(fogne3, nodes_csv, "COMMA")
arcpy.TableToCSV_tableconversion(segment2, segments_csv, "COMMA")
df_nodes = pd.read_csv(nodes_csv)
df_pipes = pd.read_csv(segments_csv)
df_nodes = df_nodes.sort_values(by=['MEAN_Z'], ascending=False)

for i in range(len(df_pipes)):
   ni = df_pipes.iloc[i,2]
   nf = df_pipes.iloc[i,3]
   zi = (df_nodes[df_nodes['Node']==ni]['MEAN_Z']).iloc[0]
   zf = (df_nodes[df_nodes['Node']==nf]['MEAN_Z']).iloc[0]
   if zf>zi:
      df_nodes.loc[int(df_nodes[df_nodes['Node']==ni].iloc[0,0]),'MEAN_Z'] = zf+0.01

df_nodes = df_nodes.sort_values(by=['MEAN_Z'], ascending=False)

for i in range(len(df_nodes)):
   acum10 = df_nodes.iloc[i,5]
   acum30 = df_nodes.iloc[i,6]
   acum50 = df_nodes.iloc[i,7]
   acum100 = df_nodes.iloc[i,8]
   inputs_df = df_pipes[df_pipes['node_dw'] == df_nodes.iloc[i,1]]['node_up']
   algo10 = 0
   algo30 = 0
   algo50 = 0
   algo100 = 0
   flow_input10 = 0
   flow_input30 = 0
   flow_input50 = 0
   flow_input100 = 0
   if len(inputs_df) == 0:
      df_nodes.iloc[i,9] = acum10
      df_nodes.iloc[i,10] = acum30
      df_nodes.iloc[i,11] = acum50
      df_nodes.iloc[i,12] = acum100
   else:
      for j in range(len(inputs_df)):
         flow_input10 = (df_nodes[df_nodes['Node']==inputs_df.iloc[j]]['Acum10']).iloc[0]
         flow_input30 = (df_nodes[df_nodes['Node']==inputs_df.iloc[j]]['Acum30']).iloc[0]
         flow_input50 = (df_nodes[df_nodes['Node']==inputs_df.iloc[j]]['Acum50']).iloc[0]
         flow_input100 = (df_nodes[df_nodes['Node']==inputs_df.iloc[j]]['Acum100']).iloc[0]
         algo10 = algo10 + flow_input10
         algo30 = algo30 + flow_input30
         algo50 = algo50 + flow_input50
         algo100 = algo100 + flow_input100
      df_nodes.iloc[i,9] = acum10 + algo10
      df_nodes.iloc[i,10] = acum30 + algo30
      df_nodes.iloc[i,11] = acum50 + algo50
      df_nodes.iloc[i,12] = acum100 + algo100
df_nodes.to_csv(up_nodes)
#arcpy.Delete_management(nodes_csv)
#arcpy.Delete_management(segments_csv)

# Load the information of the CSV file into the table of contents
arcpy.CSVToTable_tableconversion(up_nodes, table_csv, "COMMA")
spRef = arcpy.Describe(segments).spatialReference
arcpy.MakeXYEventLayer_management(table_csv, "mean_x", "mean_y", "Fogne4", spRef, "mean_z")

mxd = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataFrames(mxd)[0]
addLayer = arcpy.mapping.Layer("Fogne4")
arcpy.mapping.AddLayer(df,addLayer)
addLayer = arcpy.mapping.Layer(segment2)
arcpy.mapping.AddLayer(df,addLayer)

# Add the information of the acumulated flow to the pipes and compare those values
arcpy.AddMessage("Comparing the flow capacity of the pipes with the flow accumulated in the system ...")
arcpy.SpatialJoin_analysis(target_features=segment2, join_features="Fogne4", out_feature_class=split2, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping='Q "Q" true true false 19 Double 0 0 ,First,#,segment2,Q,-1,-1;Qr_Q "Qr_Q" true true false 19 Double 0 0 ,First,#,segment2,Qr_Q,-1,-1;length "length" true true false 19 Double 0 0 ,First,#,segment2,length,-1,-1;z_start "z_start" true true false 19 Double 0 0 ,First,#,segment2,z_start,-1,-1;z_end "z_end" true true false 19 Double 0 0 ,First,#,segment2,z_end,-1,-1;Diameter_m "Diameter_m" true true false 19 Double 0 0 ,First,#,segment2,Diameter_m,-1,-1;slope "slope" true true false 19 Double 0 0 ,First,#,segment2,slope,-1,-1;acum10 "acum10" true true false 19 Double 0 0 ,Min,#,Fogne4,acum10,-1,-1;acum30 "acum30" true true false 19 Double 0 0 ,Min,#,Fogne4,acum30,-1,-1;acum50 "acum50" true true false 19 Double 0 0 ,Min,#,Fogne4,acum50,-1,-1;acum100 "acum100" true true false 19 Double 0 0 ,Min,#,Fogne4,acum100,-1,-1', match_option="INTERSECT", search_radius="", distance_field_name="")
[arcpy.AddField_management(split2,field_name,"DOUBLE") for field_name in ['behav_10','behav_30','behav_50', 'behav_100', 'h_10', 'h_30', 'h_50', 'h_100']]
arcpy.CalculateField_management(split2,"behav_10","[Q]-[acum10]")
arcpy.CalculateField_management(split2,"behav_30","[Q]-[acum30]")
arcpy.CalculateField_management(split2,"behav_50","[Q]-[acum50]")
arcpy.CalculateField_management(split2,"behav_100","[Q]-[acum100]")
cd_blk = """def altura(Q_r, diametro, flujo):\n   Qr=Q_r*flujo\n   if Qr>0.320529:\n      hola = diametro\n   else:\n      hola = diametro*0.926*math.sqrt(1-math.sqrt(1-3.110*Qr))\n   return hola"""
arcpy.CalculateField_management(split2, "h_10", "altura( !Qr_Q!, !Diameter_m!, !acum10!)", "PYTHON_9.3", cd_blk)
arcpy.CalculateField_management(split2, "h_30", "altura( !Qr_Q!, !Diameter_m!, !acum30!)", "PYTHON_9.3", cd_blk)
arcpy.CalculateField_management(split2, "h_50", "altura( !Qr_Q!, !Diameter_m!, !acum50!)", "PYTHON_9.3", cd_blk)
arcpy.CalculateField_management(split2, "h_100", "altura( !Qr_Q!, !Diameter_m!, !acum100!)", "PYTHON_9.3", cd_blk)
arcpy.DeleteField_management(split2, ["Qr_Q"])

# Turn off non relevant layers 
turn_off = ["Fogne4","fogne2_Dissolve","fogne2","nodes","segments","segment2","fogne3","NET","complete_Dissolve","complete","losses_Dissolve","losses","clip_thiessen","thiessen"]
turn_on = ["split2","picture1.jpg","Fiumi"]
mxd = arcpy.mapping.MapDocument("current")
layers = arcpy.mapping.ListLayers(mxd)
for layer in layers:
  if layer.name in turn_off:
    layer.visible = False  
  elif layer.name in turn_on:
    layer.visible = True

for df in arcpy.mapping.ListDataFrames(mxd):
    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
        if lyr.name in turn_off:
            arcpy.mapping.RemoveLayer(df, lyr)

arcpy.RefreshTOC()
arcpy.RefreshActiveView()