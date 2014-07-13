from __future__ import print_function
import os
import flybox_params as params
from flybox_two_chamber import FlyBoxTwoChamber
import flybox_mod_params as params
from py2scad import INCH2MM

MM2INCH = 1.0/INCH2MM



if 1:
    create_proj = False 
    create_stl = False
    create_dxf = False 
    
    box = FlyBoxTwoChamber(params)

    print('x_outer (mm): {0}'.format(box.x_outer))
    print('y_outer (mm): {0}'.format(box.y_outer))
    print()
    print('x_outer (in): {0}'.format(box.x_outer*MM2INCH))
    print('y_outer (in): {0}'.format(box.y_outer*MM2INCH))
    
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

# Door tests
# -----------------------------------------------------------------------------
#if 0:
#    
#    tol_list = [0.1*x for x in range(-7,8)]
#
#    for tol in tol_list:
#        params.z_tol_door = tol
#        box = FlyBoxTwoChamber(params)
#        n = int(10*abs(tol))
#
#        if tol < 0:
#            symb = 'n'
#        else:
#            symb = 'p'
#        new_name_dxf = 'door_{0}{1}.dxf'.format(symb,n)
#        new_name_scad = 'door_{0}{1}.scad'.format(symb,n)
#        
#        #box.write_proj_scad(part_names=['door'],fake_proj=True)
#        #os.rename('door.scad', new_name_scad)
#        box.write_dxf(part_names=['door'])
#        os.rename('door.dxf', new_name_dxf)
