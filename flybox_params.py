"""
Parameters for two chamber flybox. 

Units: mm
"""
style = '3mm'
#style = '1.5mm'

# Inner dimensions of the box
x_inner = 100.0
y_inner = 75.0
z_inner = 10.0

dim_inner = x_inner, y_inner, z_inner 

# Standoffs
diam_standoff = 6.0
diam_standoff_hole = 3.4 
space_standoff = 1.0

# Material thickness 
if style == '3mm':
    thickness_side = 3.0
    thickness_door = 3.0 
    thickness_divider = 3.0
    thickness_top_outer = 3.0 
    thickness_bot_outer = 3.0 
elif style == '1.5mm':
    thickness_side = 1.5
    thickness_door = 1.5 
    thickness_divider = 1.5
    thickness_top_outer = 1.5 
    thickness_bot_outer = 1.5 
else:
    raise ValueError, 'unknown style {0}'.format(style)

thickness_top_inner = 1.5
thickness_bot_inner = 1.5 

thickness_divider_transtabs = 1.5
thickness_divider_transtabs_side = 0.5 

# Radii 
radius_top = 3.0
radius_bot = 3.0 
radius_door = 0.5*(z_inner + thickness_top_inner + thickness_bot_inner)

# Door handle and tolerance 
length_door_handle = 1.5*radius_door
diam_door_handle_hole = radius_door
z_tol_door = 0.0

# Tabs
width_tab_normal = 10.0 
width_tab_div_to_side = z_inner/3.0
tab_pos_div_to_side = (0.5,)
tab_pos_div_to_topbot = (0.25,0.75)
tab_pos_side_to_topbot = (0.1,0.5,0.9)

# rendering fn parameters
projection_fn = 50
stl_fn = 50

# stl veiwer color rgba
vconfig_color_standoff = 0.4, 0.4, 0.4, 1.0
vconfig_color_top_inner = 0.4, 0.4, 1.0, 1.0
vconfig_color_top_outer = vconfig_color_top_inner 
vconfig_color_bot_inner = vconfig_color_top_inner
vconfig_color_bot_outer = vconfig_color_top_inner
vconfig_color_side = 0.9, 0.9, 0.9, 1.0
vconfig_color_divider = vconfig_color_side 
vconfig_color_door = vconfig_color_side 

vconfig_color_divider_transtabs = 0.6, 0.6, 1.0, 0.3
vconfig_color_transtabs_side = 0.9, 0.9, 0.9, 1.0

# stl vconfig backgound color rgb  and size
vconfig_color_background = 0.5, 0.5, 0.6
vconfig_size = 600,600




