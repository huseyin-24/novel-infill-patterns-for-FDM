import numpy as np
import math

# Function called for polygon region
def polygon(side_num, random_density, radius):
    center = (107.5, 107.5)        # Define the center 
    num_points_per_side = 10       # Define the number of equally spaced points you want along each side
    offset_distance = wall_offset  # Adjust the offset distance as needed
    equally_spaced_points = []
    walls_points = []

    # Calculate the coordinates of the octagon's vertices
    angle = np.linspace(0, 2*np.pi, side_num+1)  # Divide the circle into side_number equal angles
    x = center[0] + radius * np.cos(angle)       
    y = center[1] + radius * np.sin(angle)

    # Add vertices to the corresponding list
    for i in range(len(angle)): 
        walls_points.append((x[i],y[i]))

    # Calculate equally spaced points along each side of the octagon
    for i in range(side_num):
        x_start, x_end = x[i], x[i + 1]
        y_start, y_end = y[i], y[i + 1]
        
        x_points = np.linspace(x_start, x_end, num_points_per_side)
        y_points = np.linspace(y_start, y_end, num_points_per_side)
        
        # Combine the x and y coordinates into points and add them to the list
        equally_spaced_points.extend(zip(x_points, y_points))

    # Calculate the first and second offset points towards the center of the octagon  
    dct = {}
    for i in range(2):  # Add offset walls 2 times
        dct['offset_points_%s' % (i+1)] = []
        dct['vertices_inner_%s' % (i+1)] = [] 
        
        if i == 0 : aa = equally_spaced_points
        else : aa = dct['offset_points_1']    
        
        for ind, tple in enumerate(aa):
            x, y = tple
            dx = center[0] - x
            dy = center[1] - y
            offset_x = x + (dx / np.hypot(dx, dy)) * offset_distance
            offset_y = y + (dy / np.hypot(dx, dy)) * offset_distance
            dct['offset_points_%s' % (i+1)].append((offset_x, offset_y))
            
            # Pick and add only vertices into list not equally spaced points
            if ind%num_points_per_side == 0:
                dct['vertices_inner_%s' % (i+1)].append((offset_x, offset_y))    
        
        dct['vertices_inner_%s' % (i+1)].append(dct['vertices_inner_%s' % (i+1)][0]) # add the first element so that the polygon is continuos
        
        # add vertices of offset polygon 
        walls_points = walls_points + dct['vertices_inner_%s' % (i+1)]

    # add random points
    infill_points =[]
    for i in range(random_density):
        index = np.random.randint(0,len(dct['offset_points_2'])-1)   # Pick random index from the last and innermost wall offset points
        infill_points.append(dct['offset_points_2'][index])          # Add corresponding point with random index into infill list 
    
    return (np.array(walls_points), np.array(infill_points))         # Convert the final points to a NumPy array before returning

# Assistant function called for transition region
def polygon_wall(side_num, radius):
    center = (107.5, 107.5)  # Define the center 
    num_points_per_side = 10 # Define the number of equally spaced points you want along each side
    walls_points = []

    # Calculate the coordinates of the octagon's vertices
    angle = np.linspace(0, 2*np.pi, side_num+1)  # Divide the circle into side_number equal angles
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)

     # Calculate equally spaced points along each side of the octagon
    for i in range(side_num):
        x_start, x_end = x[i], x[i + 1]
        y_start, y_end = y[i], y[i + 1]
        
        x_points = np.linspace(x_start, x_end, num_points_per_side)
        y_points = np.linspace(y_start, y_end, num_points_per_side)
        
        # Combine the x and y coordinates into points and add them to the list
        walls_points.extend(zip(x_points, y_points))

    return np.array(walls_points)

# Function called for transition region
def distorted_polygon(reduction, radius, random_density):
    center = (107.5, 107.5)         # Define the center 
    offset_distance = wall_offset   # Define the offset amount 
    walls_points = []
    
    poly = polygon_wall(8, radius)     # Generate points describing polygon 
    location_vector =  poly - center   # Translate points from center to (0, 0) for the ease of calculations
                                       # Each point represents a vector from (0, 0) to the point 
    length_array = np.linalg.norm(location_vector, axis=1)                    # Calculate length of each vector 
    length_vector = np.array([length_array, length_array]).T                  # Arrange length vector dims for further calculation 
    unit_vector = location_vector / length_vector                             # Unit vector represents direction of each point
    gap_vector = length_vector - 12.5                                         # Represents gap vector from inner polygon to distorted polygon 
    gap_vector *= reduction                                                   # Scale gap vector w.r.t layer height
    new_vector = location_vector - (unit_vector * gap_vector) + center        # Calculate distorted point by subtracting scaled unit vector from location vector 
    walls_points = new_vector.tolist()
    walls_points = list(tuple(sub) for sub in walls_points)
    
    offset_points_1 = []
    for ind, tple in enumerate(walls_points):
        x, y = tple   
        dx = center[0] - x
        dy = center[1] - y
        offset_x = x + (dx / np.hypot(dx, dy)) * offset_distance
        offset_y = y + (dy / np.hypot(dx, dy)) * offset_distance
        offset_points_1.append((offset_x, offset_y))
    walls_points = walls_points + offset_points_1 # add offset points to walls points

    offset_points_2 = []
    for ind, tple in enumerate(offset_points_1):
        x, y = tple
        dx = center[0] - x
        dy = center[1] - y
        offset_x = x + (dx / np.hypot(dx, dy)) * offset_distance
        offset_y = y + (dy / np.hypot(dx, dy)) * offset_distance
        offset_points_2.append((offset_x, offset_y))
    walls_points = walls_points + offset_points_2 # add offset points to walls points
    
    # add random points
    infill_points =[]
    for i in range(random_density):
        index = np.random.randint(0,len(offset_points_2)-1)     # Pick random index from the last and innermost wall offset points
        infill_points.append(offset_points_2[index])            # Add corresponding point with random index into infill list 

    return (np.array(walls_points), np.array(infill_points))    # Convert the final points to a NumPy array before returning

# Function called for middle region
def circle_random(radius, random_density):
    center = (107.5, 107.5)        # Define the center 
    num_points = 76                # Point number describing the circle, taken from Cura
    offset_distance = wall_offset  # Adjust the offset distance as needed
    walls_points = []
    
    # Outer wall
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points  # Calculate angle in radians
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        walls_points.append((x, y))
    walls_points.append(walls_points[0])
    
    # The First offset wall
    offset_points1 =[]
    for i in range(num_points):
        angle = 2 * math.pi * i / (num_points*0.9)  # Calculate angle in radians
        offset_x = center[0] + (radius-offset_distance) * math.cos(angle)
        offset_y = center[1] + (radius-offset_distance) * math.sin(angle)
        offset_points1.append((offset_x, offset_y))
    offset_points1.append(offset_points1[0])
    walls_points = walls_points + offset_points1

    # The Second offset wall
    offset_points2 =[]
    for i in range(num_points):
        angle = 2 * math.pi * i / (num_points*0.8)  # Calculate angle in radians
        offset_x = center[0] + (radius-2*offset_distance) * math.cos(angle)
        offset_y = center[1] + (radius-2*offset_distance) * math.sin(angle)
        offset_points2.append((offset_x, offset_y))
    offset_points2.append(offset_points2[0])
    walls_points = walls_points + offset_points2
    
    # add random points
    infill_points =[]
    for i in range(random_density):
        index = np.random.randint(0,len(offset_points2)-1)
        infill_points.append(offset_points2[index])

    return (np.array(walls_points), np.array(infill_points))

f = open(r"path.gcode", "w")                            # Create the gcode file at given path 
fan = ['', 'M106 S85\n','M106 S170\n','M106 S255\n']    # List used for turning on fan 
infill_speed = 4200                                     # For infill F4200 = 70 mm/s
wall_speed = 3300                                       # For walls F3300 = 55mm/s
Z = 0.2                                                 # Inital Layer height
E = 1                                                   # Inital extrusion value 
E_constant = 0.01254                                    # Extrusion constant when calculating Exxx values in gcode
wall_offset = 0.37                                      # Wall offset distance 

# Text files at the end and beginning of gcode so that the machine works. Copied from any gcode generated by cura
start = ''';START_OF_HEADER
;HEADER_VERSION:0.1
;FLAVOR:Griffin
;GENERATOR.NAME:Cura_SteamEngine
;GENERATOR.VERSION:main
;GENERATOR.BUILD_DATE:2022-09-13
;TARGET_MACHINE.NAME:Ultimaker 3 Extended
;EXTRUDER_TRAIN.0.INITIAL_TEMPERATURE:210
;EXTRUDER_TRAIN.0.MATERIAL.VOLUME_USED:40658
;EXTRUDER_TRAIN.0.MATERIAL.GUID:506c9f0d-e3aa-4bd4-b2d2-23e2425b1aa9
;EXTRUDER_TRAIN.0.NOZZLE.DIAMETER:0.4
;EXTRUDER_TRAIN.0.NOZZLE.NAME:AA 0.4
;BUILD_PLATE.TYPE:glass
;BUILD_PLATE.INITIAL_TEMPERATURE:60
;PRINT.TIME:111600
;PRINT.GROUPS:1
;PRINT.SIZE.MIN.X:9
;PRINT.SIZE.MIN.Y:6
;PRINT.SIZE.MIN.Z:0.27
;PRINT.SIZE.MAX.X:135.995
;PRINT.SIZE.MAX.Y:126.919
;PRINT.SIZE.MAX.Z:129.07
;END_OF_HEADER
;Generated with Cura_SteamEngine main
T0
M82 ;absolute extrusion mode

G92 E0
M109 S205 ;nozzle temperature
G0 F15000 X9 Y6 Z2
G280
G1 F1500 E-6.5
M107 ;fan off
M204 S1000 
M205 X20 Y20
G1 F600 Z2.27
G0 F4285.7 X101.945 Y94.703 Z2.27
G1 F600 Z0.27
G1 F2400 X{X} Y{Y} \n'''
end = ''';TIME_ELAPSED: 111600
G1 F1500 
M204 S3000
M107
G91 ;Relative movement
G0 F15000 X8.0 Z0.5 E-4.5 ;Wiping+material retraction
G0 F10000 Z1.5 E4.5 ;Compensation for the retraction
G90 ;Disable relative movement
M82 ;absolute extrusion mode
M104 S0
M104 T1 S0
;End of Gcode
;SETTING_3 {"global_quality": "[general]\\nversion = 4\\nname = Fast #2\\ndefini
;SETTING_3 tion = ultimaker3\\n\\n[metadata]\\ntype = quality_changes\\nquality_
;SETTING_3 type = draft\\nsetting_version = 20\\n\\n[values]\\n\\n", "extruder_q
;SETTING_3 uality": ["[general]\\nversion = 4\\nname = Fast #2\\ndefinition = ul
;SETTING_3 timaker3_extended\\n\\n[metadata]\\ntype = quality_changes\\nquality_
;SETTING_3 type = draft\\nsetting_version = 20\\nposition = 0\\n\\n[values]\\nin
;SETTING_3 fill_pattern = concentric\\ninfill_sparse_density = 60.0\\n\\n", "[ge
;SETTING_3 neral]\\nversion = 4\\nname = Fast #2\\ndefinition = ultimaker3_exten
;SETTING_3 ded\\n\\n[metadata]\\ntype = quality_changes\\nquality_type = draft\\
;SETTING_3 nsetting_version = 20\\nposition = 1\\n\\n[values]\\ninfill_sparse_de
;SETTING_3 nsity = 80\\n\\n"]}
'''

# Write GCODE
f.write(start.format(X=125, Y=107.5)) # Write end text file into gcode so that the machine works

for layer in range(1050):             # Iterate over 1050 layers
    # text lines written in gcode for information (not seen by machine). INFO LINE
    f.write(';LAYER:{lyr}\n'.format(lyr=layer))
    f.write(';E:{e} in layer {lyr} head.\n'.format(e=E, lyr=layer))
    
    # polygon parts
    if  layer < 150 or 900 <= layer : 
        wall_points, infill_points = polygon(8, 35, 17.5)    # Retrieve points to write gcode 
        wall_points = wall_points.tolist()
        infill_points = infill_points.tolist()

        # Go to first point of the layer without extrusion
        f.write('G0 X{x}, Y{y}, Z{z}\n'.format(x=wall_points[0][0], y=wall_points[0][1], z=Z))
        
        # Go to wall points one by one
        for index, point in enumerate(wall_points): 
            X = point[0]     # Get coordinates of the points
            Y = point[1]   
            if index == 0:   # If the point is the first point of the layer then go there without extrusion
                f.write('G0 X{X} Y{Y} F{F}\n'.format(X=X, Y=Y, F=wall_speed))
                continue
            dist = math.dist((X,Y),(wall_points[index-1][0], wall_points[index-1][1]))      # Calculate distance btw 2 consecutive points
            E += dist * E_constant                                                          # Calculate extrusion amount btw 2 consecutive points
            f.write('G1 X{X} Y{Y} E{E}\n'.format(X=X, Y=Y, E=E))                            # Write corresponding line into gcode file


        # Go to infill points one by one
        for index, point in enumerate(infill_points): 
            X = point[0]    # Get coordinates of the points
            Y = point[1]
            if index == 0:  # If the point is the first point of the layer then go there with extrusion from last point of the wall points
                dist = math.dist((X,Y),(wall_points[-1][0], wall_points[-1][1]))
                E += dist * E_constant
                f.write('G1 X{X} Y{Y} E{E} F{F}\n'.format(X=X, Y=Y, E=E, F=infill_speed))
                continue
            dist = math.dist((X,Y),(infill_points[index-1][0], infill_points[index-1][1]))  # Calculate distance btw 2 consecutive points
            E += dist * E_constant                                                          # Calculate extrusion amount btw 2 consecutive points
            f.write('G1 X{X} Y{Y} E{E}\n'.format(X=X, Y=Y, E=E))                            # Write corresponding line into gcode file

    # transition parts
    elif (150 <= layer < 225) or (825 <= layer < 900):  
        # Determine if the layer is in bottom or upper transition part
        if (150 <= layer < 225):                     
            reduction = (layer - 150) / 75                     # Map layer number into (0, 1) range 
            radius = np.linspace(17.5, 12.5, 75)[layer-150]    # Calculate radius of distorted polygon depending on layer number 
        elif  (825 <= layer < 900):  
            reduction = 1- ((layer - 825) / 75)                # Map layer number into (0, 1) range 
            radius = np.linspace(12.5, 17.5, 75)[layer-825]    # Calculate radius of distorted polygon depending on layer number 
        
        wall_points, infill_points = distorted_polygon(reduction, radius, 35)    # Retrieve points to write gcode 
        wall_points = wall_points.tolist()
        infill_points = infill_points.tolist()

        # Go to first point of the layer without extrusion
        f.write('G0 X{x}, Y{y}, Z{z}\n'.format(x=wall_points[0][0], y=wall_points[0][1], z=Z))

        # Go to wall points one by one
        for index, point in enumerate(wall_points): 
            X = point[0]     # Get coordinates of the points
            Y = point[1]
            if index == 0:   # If the point is the first point of the layer then go there without extrusion
                f.write('G0 X{X} Y{Y} F{F}\n'.format(X=X, Y=Y, F=wall_speed))
                continue
            dist = math.dist((X,Y),(wall_points[index-1][0], wall_points[index-1][1]))     # Calculate distance btw 2 consecutive points
            E += dist * E_constant                                                         # Calculate extrusion amount btw 2 consecutive points
            if dist != 0 :                                                                 # If the distance btw 2 consecutive points is not zero
                f.write('G1 X{X} Y{Y} E{E}\n'.format(X=X, Y=Y, E=E))                       # Write corresponding line into gcode file

        # Go to infill points one by one
        for index, point in enumerate(infill_points): 
            X = point[0]     # Get coordinates of the points
            Y = point[1]
            if index == 0:   # If the point is the first point of the layer then go there with extrusion from the last point of the wall points
                dist = math.dist((X,Y),(wall_points[-1][0], wall_points[-1][1]))
                E += dist * E_constant
                f.write('G1 X{X} Y{Y} E{E} F{F}\n'.format(X=X, Y=Y, E=E, F=infill_speed))
                continue
            dist = math.dist((X,Y),(infill_points[index-1][0], infill_points[index-1][1]))  # Calculate distance btw 2 consecutive points
            E += dist * E_constant                                                          # Calculate extrusion amount btw 2 consecutive points
            f.write('G1 X{X} Y{Y} E{E}\n'.format(X=X, Y=Y, E=E))                            # Write corresponding line into gcode file
  
    # middle part
    elif 225 <= layer < 825: 
        wall_points, infill_points = circle_random(12.5, 32)  # Retrieve points to write gcode 
        wall_points = wall_points.tolist()
        infill_points = infill_points.tolist()
    
        # Go to first point of the layer without extrusion
        f.write('G0 X{x}, Y{y}, Z{z}\n'.format(x=wall_points[0][0], y=wall_points[0][1], z=Z))

        # Go to wall points one by one  
        for index, point in enumerate(wall_points): 
            X = point[0]      # Get coordinates of the points
            Y = point[1]            
            if index == 0:    # If the point is the first point of the layer then go there without extrusion
                f.write('G0 X{X} Y{Y} F{F}\n'.format(X=X, Y=Y, F=wall_speed))
                continue
            dist = math.dist((X,Y),(wall_points[index-1][0], wall_points[index-1][1]))     # Calculate distance btw 2 consecutive points
            E += dist * E_constant                                                         # Calculate extrusion amount btw 2 consecutive points
            f.write('G1 X{X} Y{Y} E{E}\n'.format(X=X, Y=Y, E=E))                           # Write corresponding line into gcode file

        # Go to infill points one by one  
        for index, point in enumerate(infill_points): 
            X = point[0]      # Get coordinates of the points
            Y = point[1]           
            if index == 0:    # If the point is the first point of the layer then go there with extrusion from the last point of the wall points
                dist = math.dist((X,Y),(wall_points[-1][0], wall_points[-1][1]))
                E += dist * E_constant
                f.write('G1 X{X} Y{Y} E{E} F{F}\n'.format(X=X, Y=Y, E=E, F=infill_speed))
                continue 
            dist = math.dist((X,Y),(infill_points[index-1][0], infill_points[index-1][1]))  # Calculate distance btw 2 consecutive points
            E += dist * E_constant                                                          # Calculate extrusion amount btw 2 consecutive points
            f.write('G1 X{X} Y{Y} E{E}\n'.format(X=X, Y=Y, E=E))                            # Write corresponding line into gcode file
    
    Z += 0.2                                                         # Increase height of nozzle by layer thickness
    f.write(';E:{e} in layer {lyr} tail.\n'.format(e=E, lyr=layer))  # INFO LINE
    try: f.write(fan[layer])                                         # Tuning of fan
    except:None 
    if layer == 275 : actual_E_init = E                              # Variables so that material extruded can be kept tracked
    elif layer == 775 : actual_E_term = E                            # in middle region

f.write(end)  # Write end text file into gcode so that the machine works
f.close()     # Close gcode file
###############################

print('''Finished
Total E: {total_E}
E in gage length(100mm): {actual_E} '''.format(total_E=E, actual_E=actual_E_term-actual_E_init))