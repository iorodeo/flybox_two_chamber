import os
import flybox_params as params
from flybox_two_chamber import FlyBoxTwoChamber
import flybox_mod_params as params

if 0:
    create_proj = False 
    create_stl = False
    create_dxf = True 
    
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
        
    if create_proj:
        box.write_proj_scad()
    if create_stl:
        box.write_assembly_stl(**assembly_options)
    if create_dxf:
        box.write_dxf()

if 1:
    
    tol_list = [0.1*x for x in range(-7,8)]

    for tol in tol_list:
        params.z_tol_door = tol
        box = FlyBoxTwoChamber(params)
        n = int(10*abs(tol))

        if tol < 0:
            symb = 'n'
        else:
            symb = 'p'
        new_name_dxf = 'door_{0}{1}.dxf'.format(symb,n)
        new_name_scad = 'door_{0}{1}.scad'.format(symb,n)
        
        #box.write_proj_scad(part_names=['door'],fake_proj=True)
        #os.rename('door.scad', new_name_scad)
        box.write_dxf(part_names=['door'])
        os.rename('door.dxf', new_name_dxf)
