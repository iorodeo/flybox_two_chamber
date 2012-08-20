import flybox_params as params
from flybox_two_chamber import FlyBoxTwoChamber

box = FlyBoxTwoChamber(params)

assembly_options = {
        'explode': (0,0,0),
        'show_top_outer': True,
        'show_top_inner': True, 
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
if params.create_scad_proj:
    box.write_proj_scad()
if params.create_stl:
    box.write_assembly_stl(**assembly_options)
if params.create_dxf:
    box.write_dxf()

