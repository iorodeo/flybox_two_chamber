import flybox_params as params
from flybox_two_chamber import FlyBoxTwoChamber

create_proj = False 
create_stl = False
create_dxf = False 
vconfig_transtabs = False # Use transparancy in stl visual configuration

import flybox_params as params
box = FlyBoxTwoChamber(params)

if not vconfig_transtabs:
    assembly_options = {
            'explode': (0,0,5),
            'show_top_outer': False,
            'show_top_inner': False, 
            'show_bot_outer': True,
            'show_bot_inner': True,
            'show_door_pos': True,
            'show_door_neg': True,
            'show_side_pos': True,
            'show_side_neg': True,
            'show_divider': True,
            'show_standoff': True,
            'door_open': True,
            'vconfig_only': True,
            }
    box.write_assembly_scad('flybox_assembly.scad', **assembly_options)
else:
    assembly_options = {
            'assembly_method': box.get_transtabs_assembly,
            'vconfig_filename': 'transtabs_vconfig.pkl',
            'explode': (0,0,0),
            'vconfig_only': False,
            }
    box.write_assembly_scad('transtabs_assembly.scad',**assembly_options)
    
if create_stl:
    box.write_assembly_stl(**assembly_options)
if create_proj:
    box.write_proj_scad()
if create_dxf:
    box.write_dxf()


