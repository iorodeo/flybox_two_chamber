from __future__ import print_function
import os
import pickle
import subprocess
from py2scad import *


class FlyBoxTwoChamber(object):

    def __init__(self, params):
        self.params = params
        self.make_top_and_bot()
        self.make_doors()
        self.make_sides()
        self.make_divider()
        self.make_divider_transtabs()
        self.make_vconfig_color_dict()

    def make_top_and_bot(self):
        """
        Create inner and outer layers of the top and bottom.
        """
        # Outer dimesions for box
        x = self.params.x_inner  
        x += 2*self.params.thickness_door  
        x += 2*self.params.diam_standoff + 4*self.params.space_standoff
        y = self.params.y_inner
        y += 2*self.params.thickness_side 
        y += 2*self.params.diam_standoff + 4*self.params.space_standoff
        self.x_outer, self.y_outer = x, y

        # Get list of slots for tabs
        slot_list = []
        slot_pos_list = self.get_slot_pos_list('side_to_topbot')
        size_slot = self.params.width_tab_normal, self.params.thickness_side
        for pos in slot_pos_list: 
            slot_list.append((pos,size_slot))

        slot_pos_list = self.get_slot_pos_list('div_to_topbot')
        size_slot = self.params.thickness_divider, self.params.width_tab_normal
        for pos in slot_pos_list:
            slot_list.append((pos, size_slot))

        # Create top and bottom parts - both inner and outer layers
        for pos in ('top', 'bot'):
            for layer in ('inner', 'outer'):
                z = getattr(self.params,'thickness_{0}_{1}'.format(pos,layer))
                r = getattr(self.params,'radius_{0}'.format(pos))
                plate_params = { 'size': (x,y,z), 'radius': r, 'slots': slot_list}
                part = Plate_W_Slots(plate_params).make()
                setattr(self,'{0}_{1}'.format(pos,layer),part)

        # Cut inner top and bottom to make slots for sliding doors
        x_door_cut = self.params.thickness_door
        y_door_cut = y
        z_door_cut = 2.0*max([
            self.params.thickness_top_inner, 
            self.params.thickness_bot_inner,
            ])
        size_door_cut = x_door_cut, y_door_cut, z_door_cut
        cube_door_cut = Cube(size=size_door_cut)

        vx = 0.5*self.params.x_inner + 0.5*x_door_cut
        vy = 2*self.params.space_standoff + self.params.diam_standoff
        self.cube_door_cut_pos = Translate(cube_door_cut, v=( vx,vy,0))
        self.cube_door_cut_neg = Translate(cube_door_cut, v=(-vx,vy,0))

        self.top_inner = Difference([
            self.top_inner,
            self.cube_door_cut_pos,
            self.cube_door_cut_neg,
            ])

        self.bot_inner = Difference([
            self.bot_inner,
            self.cube_door_cut_pos,
            self.cube_door_cut_neg,
            ])

        # Create standoff holes and standoffs
        self.hole_list_standoff = []
        for i in (-1,0,1):
            for j in (-1,1):
                for pos in ('top', 'bot'):
                    for layer in ('outer', 'inner'):

                        x_hole = 0.5*x - self.params.space_standoff  
                        x_hole -= 0.5*self.params.diam_standoff
                        x_hole = i*x_hole

                        y_hole = 0.5*y - self.params.space_standoff 
                        y_hole -= 0.5*self.params.diam_standoff
                        y_hole = j*y_hole

                        hole = {
                                'panel' : '{0}_{1}'.format(pos,layer),
                                'type'  : 'round',
                                'location' : (x_hole, y_hole),
                                'size' : self.params.diam_standoff_hole,
                                }
                self.hole_list_standoff.append(hole)

        self.add_holes(self.hole_list_standoff)

        # Create standoff
        self.standoff = Cylinder(
                r1 = 0.5*self.params.diam_standoff,
                r2 = 0.5*self.params.diam_standoff,
                h = self.params.z_inner,
                )


    def make_doors(self):
        """
        Create the sliding doors.
        """
        x_door = self.params.z_inner 
        x_door += self.params.thickness_top_inner 
        x_door += self.params.thickness_bot_inner
        x_door - self.params.z_tol_door

        y_door = self.y_outer
        y_door -= 2*self.params.space_standoff + self.params.diam_standoff
        y_door += self.params.length_door_handle
        self.x_door, self.y_door = x_door, y_door

        part0 = rounded_box(
                x_door, 
                y_door, 
                self.params.thickness_door,
                self.params.radius_door,
                round_z = False,
                )

        part1 = Cube(size=(
            x_door, 
            (y_door-self.params.length_door_handle), 
            self.params.thickness_door
            ))

        part1 = Translate(part1,v=(0,-0.5*self.params.length_door_handle,0))
        self.door = Union([part0,part1])

        # Add handle hole to door
        hole = {
                'panel': 'door',
                'type': 'round',
                'location': (0,0.5*y_door - self.params.radius_door),
                'size': self.params.diam_door_handle_hole,
                }
        self.add_holes([hole])


    def make_sides(self):
        """
        Creates the side walls
        """
        x_side = self.params.x_inner
        y_side = self.params.z_inner
        z_side = self.params.thickness_side

        tab_data_xz_pos = []
        for pos in self.params.tab_pos_side_to_topbot:
            tab_data_xz_pos.append((
                pos, 
                self.params.width_tab_normal,
                self.params.thickness_top_inner + self.params.thickness_top_outer,
                '+'
                ))
        tab_data_xz_neg = []
        for pos in self.params.tab_pos_side_to_topbot:
            tab_data_xz_neg.append((
                pos,
                self.params.width_tab_normal,
                self.params.thickness_bot_inner + self.params.thickness_bot_outer,
                '+'
                ))

        plate_params = {
                'size': (x_side, y_side, z_side),
                'xz+': tab_data_xz_pos,
                'xz-': tab_data_xz_neg,
                'yz+': [],
                'yz-': [],
                }
        self.side = Plate_W_Tabs(plate_params).make()

        # Add hole for divider tab
        slot_list = []
        slot_pos_list = self.get_slot_pos_list('div_to_side')
        for pos in slot_pos_list:
            slot_size = (
                    self.params.thickness_divider,
                    self.params.width_tab_div_to_side
                    )
            slot_hole = {
                    'panel': 'side',
                    'type': 'square',
                    'location': pos,
                    'size': slot_size,
                    }
            slot_list.append(slot_hole)
        self.add_holes(slot_list)


    def make_divider(self):
        x_div = self.params.z_inner
        y_div = self.params.y_inner
        z_div = self.params.thickness_divider

        tab_data_xz_pos = []
        tab_data_xz_neg = []
        width_tab = self.params.width_tab_div_to_side
        depth_tab = self.params.thickness_side
        for val in self.params.tab_pos_div_to_side:
            tab_data = (val, width_tab, depth_tab, '+')
            tab_data_xz_pos.append(tab_data)
            tab_data_xz_neg.append(tab_data)

        tab_data_yz_pos = []
        tab_data_yz_neg = []
        width_tab = self.params.width_tab_normal
        depth_tab_pos = self.params.thickness_top_inner + self.params.thickness_top_outer
        depth_tab_neg = self.params.thickness_bot_inner + self.params.thickness_bot_outer
        for val in self.params.tab_pos_div_to_topbot:
            tab_data_pos = (val, width_tab, depth_tab_pos, '+')
            tab_data_neg = (val, width_tab, depth_tab_neg, '+')
            tab_data_yz_pos.append(tab_data_pos)
            tab_data_yz_neg.append(tab_data_neg)

        params = {
                'size': (x_div, y_div, z_div),
                'xz+': tab_data_xz_pos,
                'xz-': tab_data_xz_neg,
                'yz+': tab_data_yz_pos,
                'yz-': tab_data_yz_neg,
                }
        self.divider = Plate_W_Tabs(params).make()

    def make_divider_transtabs(self):
        x_div = self.params.z_inner
        y_div = self.params.y_inner
        z_div = self.params.thickness_divider_transtabs

        tab_data_xz_pos = []
        tab_data_xz_neg = []
        width_tab = self.params.width_tab_div_to_side
        depth_tab = self.params.thickness_side
        for val in self.params.tab_pos_div_to_side:
            tab_data = (val, width_tab, depth_tab, '+')
            tab_data_xz_pos.append(tab_data)
            tab_data_xz_neg.append(tab_data)

        tab_data_yz_pos = []
        tab_data_yz_neg = []
        width_tab = self.params.width_tab_normal
        depth_tab_pos = self.params.thickness_top_inner + self.params.thickness_top_outer
        depth_tab_neg = self.params.thickness_bot_inner + self.params.thickness_bot_outer
        for val in self.params.tab_pos_div_to_topbot:
            tab_data_pos = (val, width_tab, depth_tab_pos, '+')
            tab_data_neg = (val, width_tab, depth_tab_neg, '+')
            tab_data_yz_pos.append(tab_data_pos)
            tab_data_yz_neg.append(tab_data_neg)

        params = {
                'size': (x_div, y_div, z_div),
                'xz+': tab_data_xz_pos,
                'xz-': tab_data_xz_neg,
                'yz+': tab_data_yz_pos,
                'yz-': tab_data_yz_neg,
                }
        self.divider_transtabs = Plate_W_Tabs(params).make()
        side_size = (x_div, y_div, self.params.thickness_divider_transtabs_side)
        self.divider_transtabs_side = Cube(size=side_size)


    def add_holes(self, hole_list, cut_depth = None):
        """
        Add holes to given panel of the enclosure.
        """
        if not cut_depth:
            thickness_list = []
            for name in dir(self.params):
                if 'thickness' in name:
                    value = getattr(self.params,name)
                    thickness_list.append(value)
            cut_depth = 2*max(thickness_list)

        for hole in hole_list:
            # Create differencing cylinder for hole based on hole type.
            if hole['type'] == 'round':
                radius = 0.5*hole['size']
                hole_cyl = Cylinder(r1=radius, r2=radius, h=cut_depth)
            elif hole['type'] == 'square':
                sz_x, sz_y = hole['size']
                sz_z = cut_depth 
                hole_cyl = Cube(size = (sz_x,sz_y,sz_z))
            elif hole['type'] == 'rounded_square':
                sz_x, sz_y, radius = hole['size']
                sz_z = cut_depth 
                hole_cyl = rounded_box(sz_x, sz_y, sz_z, radius, round_z=False)
            else:
                raise ValueError, 'unkown hole type {0}'.format(hole['type'])

            # Translate cylinder into position
            x,y = hole['location']
            hole_cyl = Translate(hole_cyl, v = (x,y,0.0))

            # Get panel in which to make hole
            panel = getattr(self, hole['panel'])

            # Cut hole
            panel = Difference([panel, hole_cyl])
            setattr(self, hole['panel'], panel)


    def get_slot_pos_list(self,name):
        """
        Get lists of x,y position for tabs given their names. Note, coordinates
        are for the unrotated parts - not the assembled parts.
        """
        slot_pos_list = []
        if name == 'side_to_topbot':
            for val in self.params.tab_pos_side_to_topbot:
                for j in (-1,1):
                    x_slot = (0.5 - val)*self.params.x_inner
                    y_slot = j*(0.5*self.params.y_inner + 0.5*self.params.thickness_side)
                    slot_pos_list.append((x_slot,y_slot))
        elif name == 'div_to_topbot':
            for val in self.params.tab_pos_div_to_topbot:
                x_slot = 0.0
                y_slot = (0.5 - val)*self.params.y_inner
                slot_pos_list.append((x_slot,y_slot))
        elif name == 'div_to_side':
            for val in self.params.tab_pos_div_to_side:
                x_slot = 0.0
                y_slot = (0.5 - val)*self.params.z_inner
                slot_pos_list.append((x_slot,y_slot))
        else:
            raise ValueError, 'unknown tab type {0}'.format(name)
        return slot_pos_list
        

    def get_assembly(self,**kwargs):
        part_dict = {} 
        options = {}
        try:
            explode = kwargs['explode']
        except KeyError:
            explode = 0,0,0
        try:
            output_type = kwargs['output_type']
        except KeyError:
            output_type = 'list'
        assert output_type in ('list','dict')

        x_explode, y_explode, z_explode = explode

        # Add top and bottoms (inner and outer)
        vz = 0.5*self.params.z_inner + 0.5*self.params.thickness_top_inner
        vz += z_explode
        top_inner = Translate(self.top_inner,v=(0,0,vz))
        part_dict['top_inner'] = top_inner
        options['show_top_inner'] = True

        vz = 0.5*self.params.z_inner + self.params.thickness_top_inner
        vz += 0.5*self.params.thickness_top_outer
        vz += 2.0*z_explode
        top_outer = Translate(self.top_outer,v=(0,0,vz))
        part_dict['top_outer'] = top_outer
        options['show_top_outer'] = True
        
        vz = -(0.5*self.params.z_inner + 0.5*self.params.thickness_bot_inner)
        vz -= z_explode
        bot_inner = Translate(self.bot_inner,v=(0,0,vz))
        part_dict['bot_inner'] = bot_inner
        options['show_bot_inner'] = True

        vz = -(0.5*self.params.z_inner + self.params.thickness_bot_inner)
        vz -= 0.5*self.params.thickness_bot_outer
        vz -= 2.0*z_explode

        bot_outer = Translate(self.bot_outer,v=(0,0,vz))
        part_dict['bot_outer'] = bot_outer
        options['show_bot_outer'] = True

        # Add standoffs
        standoff_list = []
        for hole in self.hole_list_standoff:
            x_standoff, y_standoff = hole['location']
            x_standoff += 2*sign(x_standoff)*x_explode
            y_standoff += 2*sign(y_standoff)*y_explode
            standoff = Translate(self.standoff,v=(x_standoff, y_standoff, 0))
            standoff_list.append(standoff)
        part_dict['standoff'] = standoff_list
        options['show_standoff'] = True

        # Add doors
        try:
            door_open = kwargs['door_open']
        except KeyError:
            door_open = False 
        door = Rotate(self.door,a=90, v=(0,1,0))
        vx = 0.5*self.params.x_inner + 0.5*self.params.thickness_door
        vx += x_explode
        vy = 0.5*self.y_door - 0.5*self.y_outer
        vy += 2*self.params.space_standoff + self.params.diam_standoff

        if door_open:
            vy += self.y_door

        door_pos = Translate(door,v=(vx,vy,0))
        door_neg = Translate(door,v=(-vx,vy,0))
        part_dict['door_pos'] = door_pos
        part_dict['door_neg'] = door_neg
        options['show_door_pos'] = True
        options['show_door_neg'] = True

        # Add sides
        side = Rotate(self.side,a=90,v=(1,0,0))
        vy = 0.5*self.params.y_inner + 0.5*self.params.thickness_side
        vy += y_explode
        side_pos = Translate(side,v=(0,vy,0))
        side_neg = Translate(side,v=(0,-vy,0))
        part_dict['side_pos'] = side_pos
        part_dict['side_neg'] = side_neg
        options['show_side_pos'] = True
        options['show_side_neg'] = True

        # Add divider
        divider = Rotate(self.divider,a=90,v=(0,1,0))
        part_dict['divider'] = divider
        options['show_divider'] = True

        # Generate output list
        output_list = []
        output_dict = {}
        options.update(kwargs)
        for name, part in part_dict.iteritems():
            if options['show_{0}'.format(name)]:
                if type(part) is list:
                    output_list.extend(part)
                else:
                    output_list.append(part)
                output_dict[name] = part
        if output_type == 'list':
            return output_list 
        else:
            return output_dict

    def get_transtabs_assembly(self, **kwargs):
        part_dict = {} 
        options = {}
        try:
            explode = kwargs['explode']
        except KeyError:
            explode = 0,0,0
        try:
            output_type = kwargs['output_type']
        except KeyError:
            output_type = 'list'
        assert output_type in ('list','dict')

        x_explode, y_explode, z_explode = explode
        # Add divider
        divider_transtabs = Rotate(self.divider_transtabs,a=90,v=(0,1,0))
        part_dict['divider_transtabs'] = divider_transtabs
        options['show_divider_transtabs'] = True

        # Add divider sides
        divider_transtabs_side = Rotate(self.divider_transtabs_side,a=90,v=(0,1,0))
        vx = 0.5*self.params.thickness_divider_transtabs
        vx += 0.5*self.params.thickness_divider_transtabs_side
        vx += x_explode
        divider_transtabs_side_pos = Translate(divider_transtabs_side,v=(vx,0,0))
        divider_transtabs_side_neg = Translate(divider_transtabs_side,v=(-vx,0,0))
        part_dict['transtabs_side_pos'] = divider_transtabs_side_pos
        part_dict['transtabs_side_neg'] = divider_transtabs_side_neg
        options['show_transtabs_side_pos'] = True
        options['show_transtabs_side_neg'] = True

        # Generate output list
        output_list = []
        output_dict = {}
        options.update(kwargs)
        for name, part in part_dict.iteritems():
            if options['show_{0}'.format(name)]:
                if type(part) is list:
                    output_list.extend(part)
                else:
                    output_list.append(part)
                output_dict[name] = part
        if output_type == 'list':
            return output_list 
        else:
            return output_dict

    def write_proj_scad(self):
        """
        Write the project scad files
        """
        part_names = [
                'top_outer',
                'top_inner',
                'bot_outer',
                'bot_inner',
                'door', 
                'side',
                'divider',
                ]
        scad_file_list = []
        for name in part_names:
            scad_name = '{0}.{1}'.format(name,'scad')
            part = getattr(self,name)
            part_proj = Projection(part)
            prog = SCAD_Prog()
            prog.fn = self.params.projection_fn
            prog.add(part_proj)
            prog.write(scad_name)
            scad_file_list.append(scad_name)
        return scad_file_list

    def write_dxf(self,erase_scad=True):
        scad_file_list = self.write_proj_scad()
        for scad_name in scad_file_list:
            base_name, ext = os.path.splitext(scad_name)
            dxf_name = '{0}.{1}'.format(base_name,'dxf')
            print('writing: {0}'.format(dxf_name))
            subprocess.call(['openscad','-x',dxf_name,scad_name])
            if erase_scad:
                os.remove(scad_name)

    def write_assembly_scad(self,filename,**kwargs):
        try:
            assembly_method = kwargs['assembly_method']
        except KeyError:
            assembly_method = self.get_assembly
        box_assembly = assembly_method(**kwargs)
        prog_assembly = SCAD_Prog()
        prog_assembly.fn = 50
        prog_assembly.add(box_assembly)
        prog_assembly.write(filename)


    def write_assembly_stl(self,**kwargs):
        kwargs['output_type'] = 'dict'
        try:
            erase_scad = kwargs['erase_scad']
        except KeyError:
            erase_scad = True
        try:
            vconfig_only = kwargs['vconfig_only']
        except KeyError:
            vconfig_only = False
        try:
            assembly_method = kwargs['assembly_method']
            vconfig_filename = kwargs['vconfig_filename']
        except KeyError:
            assembly_method = self.get_assembly
            vconfig_filename = 'flybox_assembly_vconfig.pkl'
        part_dict = assembly_method(**kwargs)
        vconfig_dict = {}
        vconfig_dict['background'] = self.params.vconfig_color_background
        vconfig_dict['size'] = self.params.vconfig_size
        vconfig_part_list = []
        for name, part in part_dict.iteritems():
            if type(part) is list:
                for i, subpart in enumerate(part):
                    subname = '{0}_{1}'.format(name,i)
                    vconfig_part = self.write_stl(
                            subname, 
                            subpart, 
                            erase_scad=erase_scad, 
                            vconfig_only=vconfig_only,
                            )
                    vconfig_part_list.append(vconfig_part)
            else:
                vconfig_part = self.write_stl(
                        name, 
                        part, 
                        erase_scad=erase_scad,
                        vconfig_only=vconfig_only,
                        )
                vconfig_part_list.append(vconfig_part)
        vconfig_dict['objects'] = vconfig_part_list
        with open(vconfig_filename,'w') as f:
            pickle.dump(vconfig_dict, f)


    def write_stl(self, name, part, erase_scad=True, vconfig_only=False):
        scad_filename = '{0}.scad'.format(name)
        stl_filename = '{0}.stl'.format(name)
        print('{0} --> {1}'.format(scad_filename, stl_filename))
        prog = SCAD_Prog()
        prog.fn = self.params.stl_fn
        prog.add(part)
        prog.write(scad_filename)
        if not vconfig_only:
            subprocess.call(['openscad', '-s', stl_filename, scad_filename])
        if erase_scad==True:
            os.remove(scad_filename)
        rgba_color = self.get_vconfig_color(name)
        vconfig = self.get_part_vconfig(stl_filename,rgba_color)
        return vconfig

 
    def get_part_vconfig(self, filename, rgba_color):
        color = rgba_color[:3]
        opacity = rgba_color[3]
        parameters = {
                'specular_power' : 0.8,
                'specular'       : 0.7,
                'diffuse'        : 0.7, 
                'color'          : color,
                'opacity'        : opacity, 
                } 
        vconfig = {'filename' : filename, 'parameters' : parameters}
        return vconfig 

    def get_vconfig_color(self,name):
        for color_name in self.vconfig_color_dict:
            if color_name in name:
                print(color_name, name)
                return self.vconfig_color_dict[color_name]

    def make_vconfig_color_dict(self):
        self.vconfig_color_dict = {}
        for name in dir(self.params):
            if 'vconfig_color' in name:
                color_name = name[len('vconfig_color_'):]
                self.vconfig_color_dict[color_name] = getattr(self.params,name) 



def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # Testing and development

    import flybox_params as params
    box = FlyBoxTwoChamber(params)

    if 0:
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
        box.write_assembly_stl(**assembly_options)

    # Show transparent tabs
    if 0:
        assembly_options = {
                'assembly_method': box.get_transtabs_assembly,
                'vconfig_filename': 'transtabs_vconfig.pkl',
                'explode': (0,0,0),
                'vconfig_only': False,
                }
        box.write_assembly_scad('transtabs_assembly.scad',**assembly_options)
        box.write_assembly_stl(**assembly_options)

    #box.write_proj_scad()
    #box.write_dxf()


