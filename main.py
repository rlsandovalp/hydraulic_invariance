import arcpy
import pandas as pd
from arcpy import env

arcpy.ImportToolbox(arcpy.env.workspace+"\\..\\ExcelTools\\Excel and CSV Conversion Tools")

#Variables
max_capaci = (arcpy.GetParameter(0)/100)

#DEM, losses file and rain file of Lecco
DEM = arcpy.env.workspace+"\\..\\Lombardy\\Lecco\\rasters\\dem\\DTM5_LC.img"
losses_file = arcpy.env.workspace+"\\..\\Lombardy\\Lecco\\Shapes\\losses.shp"
rain_file = arcpy.env.workspace+"\\..\\Lombardy\\Lecco\\Shapes\\lspp_lecco.shp"

# Input Files (Network, town limits)
nodes = arcpy.GetParameter(1)
segments = arcpy.GetParameter(2)
limiti = arcpy.GetParameter(3)

# Processing files (sewers, areas)
segment2 = arcpy.env.workspace+"\\shapes\\segment2.shp"
fogne2 = arcpy.env.workspace+"\\shapes\\fogne2.shp"
fogne3 = arcpy.env.workspace+"\\shapes\\fogne3.shp"
split2 = arcpy.env.workspace+"\\shapes\\split2.shp"
thiessen = arcpy.env.workspace+"\\shapes\\thiessen.shp"
clip_thiessen = arcpy.env.workspace+"\\shapes\\clip_thiessen.shp"
# Files with the infiltration and rain information
losses = arcpy.env.workspace+"\\shapes\\losses.shp"
losses_dissolve = arcpy.env.workspace+"\\shapes\\losses_Dissolve.shp"
complete = arcpy.env.workspace+"\\shapes\\complete.shp"
complete_dissolve = arcpy.env.workspace+"\\shapes\\complete_Dissolve.shp"
# Files used in the accumulation of the flow
nodes_csv = arcpy.env.workspace+"\\shapes\\nodes.csv"
segments_csv = arcpy.env.workspace+"\\shapes\\segments.csv"
up_nodes = arcpy.env.workspace+"\\shapes\\upnodes.csv"
table_csv = arcpy.env.workspace+"\\shapes\\upnodes_CSVToTable.dbf"

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
if len(trouble_pipes)>0:
   arcpy.AddError("The Following pipes have geometry troubles. Please correct the elevations in the 'nodes' shapefile or redraw the network in the 'NET' shapefile. Then run the Script2")
   arcpy.AddError(trouble_pipes)
   quit()

arcpy.Copy_management(arcpy.Describe(segments).catalogPath, segment2)

# Create the areas and cut the areas to those of interest for the project
arcpy.AddMessage("Creating areas ...")
arcpy.CreateThiessenPolygons_analysis(nodes, thiessen, "ALL")
arcpy.Clip_analysis (thiessen, limiti, clip_thiessen)

# COMPUTING THE INFILTRATION INFORMATION
# Intersect losses with the areas
arcpy.AddMessage("Computing the infiltration capacity ...")
arcpy.Intersect_analysis("'"+losses_file+"' #;'"+clip_thiessen+"' #", losses, join_attributes="ALL", cluster_tolerance="-1 Unknown", output_type="INPUT")
# Create fields in the table of losses
[arcpy.AddField_management(losses,field_name,"DOUBLE") for field_name in ['area', 'CN', 'fo', 'fc', 'hor_exp', 'runoff_c', 'ko1', 'ks1', 'ws1', 'suc1']]
# Compute each one of the fields created in the previous line
arcpy.CalculateField_management(losses,'AREA','!shape.area!','PYTHON')
arcpy.CalculateField_management(losses, "CN", "[lecco_cn_3] * [area]")
arcpy.CalculateField_management(losses, "fo", "[lecco_cn_4] * [area]")
arcpy.CalculateField_management(losses, "fc", "[lecco_cn_5] * [area]")
arcpy.CalculateField_management(losses, "hor_exp", "[lecco_cn_6] * [area]")
arcpy.CalculateField_management(losses, "runoff_c", "[lecco_cn_7] * [area]")
arcpy.CalculateField_management(losses, "ks1", "[ks] * [area]")
arcpy.CalculateField_management(losses, "ws1", "[wc_sat] * [area]")
arcpy.CalculateField_management(losses, "suc1", "[suction] * [area]")
# Dissolve the losses file
arcpy.Dissolve_management(losses, losses_dissolve, "FID_clip_t", "CN SUM;fo SUM;fc SUM;hor_exp SUM;runoff_c SUM;ks1 SUM;ws1 SUM;suc1 SUM", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
# Create fields in the table of losses
[arcpy.AddField_management(losses_dissolve,field_name,"DOUBLE") for field_name in ['area', 'CN', 'fo', 'fc', 'hor_exp', 'runoff_c', 'ks', 'ws', 'suc']]
# Compute each one of the fields created in the previous line
arcpy.CalculateField_management(losses_dissolve,'AREA','!shape.area!','PYTHON')
arcpy.CalculateField_management(losses_dissolve, "CN", "[SUM_CN] / [area]")
arcpy.CalculateField_management(losses_dissolve, "fo", "[SUM_fo] / [area]")
arcpy.CalculateField_management(losses_dissolve, "fc", "[SUM_fc] / [area]")
arcpy.CalculateField_management(losses_dissolve, "hor_exp", "[SUM_hor_ex] / [area]")
arcpy.CalculateField_management(losses_dissolve, "runoff_c", "[SUM_runoff] / [area]")
arcpy.CalculateField_management(losses_dissolve, "ks", "[SUM_ks1] / [area]")
arcpy.CalculateField_management(losses_dissolve, "ws", "[SUM_ws1] / [area]")
arcpy.CalculateField_management(losses_dissolve, "suc", "[SUM_suc1] / [area]")
# Delete useless fields in the losses dissolve file
arcpy.DeleteField_management(losses_dissolve, ["SUM_CN", "SUM_fo", "SUM_fc", "SUM_hor_ex", "SUM_runoff", "SUM_ks1", "SUM_ws1", "SUM_suc1"])

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
arcpy.Dissolve_management(complete, complete_dissolve, dissolve_field="FID_losses", statistics_fields="CN MEAN;fo MEAN;fc MEAN;hor_exp MEAN;runoff_c MEAN;ks MEAN;ws MEAN;suc MEAN;a1 SUM;n1 SUM;alpha SUM;epsilon SUM;kappa SUM", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
# Create fields in the table of rain
[arcpy.AddField_management(complete_dissolve,field_name,"DOUBLE") for field_name in ['area', 'a1', 'n1', 'alpha', 'epsilon', 'kappa', 'w_10', 'a_10', 'pe_10', 'h_10','w_30', 'a_30', 'pe_30', 'h_30','w_50', 'a_50', 'pe_50', 'h_50', 'w_100', 'a_100', 'pe_100', 'h_100', 'CN', 'fo', 'fc', 'hor_exp', 'runoff_c', 'ks', 'ws', 'suc', 'S']]
# Compute the fields created in the previous line
arcpy.CalculateField_management(complete_dissolve,'area','!shape.area!','PYTHON')
arcpy.CalculateField_management(complete_dissolve, "a1", "[SUM_a1] / [area]")
arcpy.CalculateField_management(complete_dissolve, "n1", "[SUM_n1] / [area]")
arcpy.CalculateField_management(complete_dissolve, "alpha", "[SUM_alpha] / [area]")
arcpy.CalculateField_management(complete_dissolve, "epsilon", "[SUM_epsilo] / [area]")
arcpy.CalculateField_management(complete_dissolve, "kappa", "[SUM_kappa] / [area]")
arcpy.CalculateField_management(complete_dissolve, "CN", "[MEAN_CN] ")
arcpy.CalculateField_management(complete_dissolve, "fo", "[MEAN_fo] ")
arcpy.CalculateField_management(complete_dissolve, "fc", "[MEAN_fc] ")
arcpy.CalculateField_management(complete_dissolve, "hor_exp", "[MEAN_hor_e] ")
arcpy.CalculateField_management(complete_dissolve, "runoff_c", "[MEAN_runof] ")
arcpy.CalculateField_management(complete_dissolve, "ks", "[MEAN_ks] ")
arcpy.CalculateField_management(complete_dissolve, "ws", "[MEAN_ws] ")
arcpy.CalculateField_management(complete_dissolve, "suc", "[MEAN_suc] ")
arcpy.CalculateField_management(complete_dissolve, "S", " 25.4*(1000/[CN]-10) ")
arcpy.CalculateField_management(complete_dissolve, "w_10", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 10/(10-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_10", "[w_10] * [a1]")
arcpy.CalculateField_management(complete_dissolve, "pe_10", "(([a_10]-0.2*[S])^2)/([a_10]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_10", "[pe_10]*[area] / 3600000")
arcpy.CalculateField_management(complete_dissolve, "w_30", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 30/(30-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_30", "[w_30] * [a1]")
arcpy.CalculateField_management(complete_dissolve, "pe_30", "(([a_30]-0.2*[S])^2)/([a_30]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_30", "[pe_30]*[area] / 3600000")
arcpy.CalculateField_management(complete_dissolve, "w_50", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 50/(50-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_50", "[w_50] * [a1]")
arcpy.CalculateField_management(complete_dissolve, "pe_50", "(([a_50]-0.2*[S])^2)/([a_50]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_50", "[pe_50]*[area] / 3600000")
arcpy.CalculateField_management(complete_dissolve, "w_100", "[epsilon]+( [alpha] / [kappa] )*(1-(Log ( 100/(100-1) ))^ [kappa] )")
arcpy.CalculateField_management(complete_dissolve, "a_100", "[w_100] * [a1]")
arcpy.CalculateField_management(complete_dissolve, "pe_100", "(([a_100]-0.2*[S])^2)/([a_100]+0.8*[S])")
arcpy.CalculateField_management(complete_dissolve, "h_100", "[pe_100]*[area] / 3600000")
# Delete useless fields
arcpy.DeleteField_management(complete_dissolve, ["SUM_a1", "SUM_n1", "SUM_alpha", "SUM_epsilo", "SUM_kappa", "FID_losses", "MEAN_CN", "MEAN_fo", "MEAN_fc", "MEAN_hor_e", "MEAN_runof", "MEAN_ks", "MEAN_ws", "MEAN_suc"])


# Move the information of the areas to the sewers
arcpy.AddMessage("Transfering areas information to the sewers ...")
field_map = 'POINT_Y "POINT_Y" true true false 19 Double 0 0 ,First,#,'+str(nodes)+',POINT_Y,-1,-1;POINT_X "POINT_X" true true false 19 Double 0 0 ,First,#,'+str(nodes)+',POINT_X,-1,-1;Z "Z" true true false 19 Double 0 0 ,First,#,'+str(nodes)+',Z,-1,-1;h_10 "h_10" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_10,-1,-1;h_30 "h_30" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_30,-1,-1;h_50 "h_50" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_50,-1,-1;h_100 "h_100" true true false 19 Double 0 0 ,First,#,'+complete_dissolve+',h_100,-1,-1'
arcpy.SpatialJoin_analysis(nodes, complete_dissolve, fogne2, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping=field_map, match_option="INTERSECT", search_radius="", distance_field_name="")

#Delete overlay nodes to have only one node per spatial location
arcpy.Dissolve_management(fogne2, fogne3, dissolve_field="POINT_Y;POINT_X", statistics_fields="Z MEAN;h_10 MEAN;h_30 MEAN;h_50 MEAN;h_100 MEAN", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
[arcpy.AddField_management(fogne3,field_name,"DOUBLE") for field_name in ['Node', 'Acum10', 'Acum30', 'Acum50', 'Acum100']]
arcpy.CalculateField_management(fogne3, "Node", "[POINT_X]+[POINT_Y]")

# Compute maximum capacity of the pipes adding Z information
arcpy.AddMessage("Computing capacity of the pipes ...")
# Add required fields
[arcpy.AddField_management(segment2,field_name,"DOUBLE") for field_name in ['slope', 'length', 'max_capaci', 'd', 'h', 'theta', 'K', 's', 'A', 'Pw', 'Rh', 'RS', 'C', 'Q']]
# Compute the fields created in the previous line
arcpy.UpdateFeatureZ_3d(segment2, DEM, method="BILINEAR", status_field="")
arcpy.AddZInformation_3d(segment2, out_property="Z_MIN", noise_filtering="NO_FILTER")
arcpy.AddZInformation_3d(segment2, out_property="Z_MAX", noise_filtering="NO_FILTER")
arcpy.AddZInformation_3d(segment2, out_property="Z_MEAN", noise_filtering="NO_FILTER")
arcpy.CalculateField_management(segment2,'length','!shape.length!','PYTHON')
arcpy.CalculateField_management(segment2, "slope", expression="([Z_max]-[Z_min])/[length]")
arcpy.CalculateField_management(segment2,'max_capaci',str(max_capaci))
arcpy.CalculateField_management(segment2,'d',"[Diameter_m]*[max_capaci]")
arcpy.CalculateField_management(segment2,"h","[Diameter_m]-[d]")
arcpy.CalculateField_management(segment2,"theta","2*math.acos( (!Diameter_m!/2- !h!)/ (!Diameter_m!/2) )",'PYTHON')
arcpy.CalculateField_management(segment2,"K","0.5*((!Diameter_m!/2)**2)*(!theta!-math.sin(!theta!))",'PYTHON')
arcpy.CalculateField_management(segment2,"s","[theta]*[Diameter_m]/2")
arcpy.CalculateField_management(segment2,"A","math.pi*((!Diameter_m!/2)**2)-!K!",'PYTHON')
arcpy.CalculateField_management(segment2,"Pw","2*math.pi*(!Diameter_m!/2)-!s!",'PYTHON')
arcpy.CalculateField_management(segment2,"Rh","[A]/[Pw]")
arcpy.CalculateField_management(segment2,"RS","[Rh]*[slope]")
arcpy.CalculateField_management(segment2,"C","87/(1+0.06/math.sqrt(!Rh!))",'PYTHON')
arcpy.CalculateField_management(segment2,"Q","!C!*math.sqrt(!RS!)*math.pi*((!Diameter_m!/2)**2)",'PYTHON')


# Accumulate the flow in the network
arcpy.AddMessage("Accumulating the flow ...")
arcpy.TableToCSV_tableconversion(fogne3, nodes_csv, "COMMA")
arcpy.TableToCSV_tableconversion(segment2, segments_csv, "COMMA")
df_nodes = pd.read_csv(nodes_csv)
df_pipes = pd.read_csv(segments_csv)
df_nodes = df_nodes.sort_values(by=['MEAN_Z'], ascending=False)

for i in range (len(df_nodes)):
   df_nodes.iloc[i,8] = round(df_nodes.iloc[i,8],1)

for i in range (len(df_pipes)):
   df_pipes.iloc[i,2] = round(df_pipes.iloc[i,2],1)
   df_pipes.iloc[i,3] = round(df_pipes.iloc[i,3],1)


for i in range(len(df_nodes)):
   acum10 = df_nodes.iloc[i,4]
   acum30 = df_nodes.iloc[i,5]
   acum50 = df_nodes.iloc[i,6]
   acum100 = df_nodes.iloc[i,7]
   inputs_df = df_pipes[df_pipes['end'] == df_nodes.iloc[i,8]]['start']
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
arcpy.Delete_management(nodes_csv)
arcpy.Delete_management(segments_csv)

# Load the information of the CSV file into the table of contents
arcpy.CSVToTable_tableconversion(up_nodes, table_csv, "COMMA")
spRef = arcpy.Describe(segments).spatialReference
arcpy.MakeXYEventLayer_management(table_csv, "point_x", "point_y", "Fogne4", spRef, "mean_z")

mxd = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataFrames(mxd)[0]
addLayer = arcpy.mapping.Layer("Fogne4")
arcpy.mapping.AddLayer(df,addLayer)
addLayer = arcpy.mapping.Layer(segment2)
arcpy.mapping.AddLayer(df,addLayer)

# Add the information of the acumulated flow to the pipes and compare those values
arcpy.AddMessage("Comparing the flow capacity of the pipes with the flow accumulated in the system ...")
arcpy.SpatialJoin_analysis(target_features=segment2, join_features="Fogne4", out_feature_class=split2, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping='Q "Q" true true false 19 Double 0 0 ,First,#,segment2,Q,-1,-1;acum10 "acum10" true true false 19 Double 0 0 ,Min,#,Fogne4,acum10,-1,-1;acum30 "acum30" true true false 19 Double 0 0 ,Min,#,Fogne4,acum30,-1,-1;acum50 "acum50" true true false 19 Double 0 0 ,Min,#,Fogne4,acum50,-1,-1;acum100 "acum100" true true false 19 Double 0 0 ,Min,#,Fogne4,acum100,-1,-1', match_option="INTERSECT", search_radius="", distance_field_name="")
arcpy.AddField_management(split2, "behav_10", "double")
arcpy.CalculateField_management(split2,"behav_10","[Q]-[acum10]")
arcpy.AddField_management(split2, "behav_30", "double")
arcpy.CalculateField_management(split2,"behav_30","[Q]-[acum30]")
arcpy.AddField_management(split2, "behav_50", "double")
arcpy.CalculateField_management(split2,"behav_50","[Q]-[acum50]")
arcpy.AddField_management(split2, "behav_100", "double")
arcpy.CalculateField_management(split2,"behav_100","[Q]-[acum100]")

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
