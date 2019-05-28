# coding: utf-8

from lxml import etree

import xml.sax

import pprint

import inspect

import numpy as np

# data = etree.parse("../models/Opensim_model/arm26.osim")
# for body in data.xpath('/OpenSimDocument/Model/BodySet/objects/Body'):
#     print(body.get("name"))
#     for i in range(len(body.getchildren())):
#         print(body.getchildren()[i].text)

def index_go_to(_root, _tag, _attrib=False, _attribvalue='', index=''):
    #return index to go to _tag which can have condition on its attribute
    i = 0
    for _child in _root:
        if type(_child) == str:
            return ''
        if _attrib != False:
            if _child.tag == _tag and _child.get(_attrib) == _attribvalue:
                return index+'[{}]'.format(i)
            else:
                i += 1
        else:
            if _child.tag == _tag:
                return index+'[{}]'.format(i)
            else:
                i += 1 
    #not found in children, go to grand children
    else:
        j = 0
        if _root is not None:
            for _child in _root:
                a = index_go_to(_child, _tag, _attrib, _attribvalue, index+'[{}]'.format(j))
                if a:
                 return index_go_to(_child, _tag, _attrib, _attribvalue, index+'[{}]'.format(j))
                else:
                    j += 1

def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

def go_to(_root, _tag, _attrib=False, _attribvalue=''):
    #return element corresponding to _tag 
    #which can have condition on its attribute
    _index = index_go_to(_root, _tag, _attrib, _attribvalue)
    if _index == None:
        return 'None'
    else:
        _index = index_go_to(_root, _tag, _attrib, _attribvalue)
        return eval(retrieve_name(_root)+_index)   
    
def coord_sys(axis):
    # define orthonormal coordinate system with given z-axis
    [a, b, c] = axis
    if a == 0:
        if b == 0:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            else:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        else:
            if c == 0:
                return [[0, 0, 1], [1, 0, 0], [0, 1, 0]]
            else:
                y_temp = [0, -c/b, 1]
    else:
        if b == 0:
            if c == 0:
                return [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
            else:
                y_temp = [-c/a, 0, 1]
        else:
            y_temp = [-b/a, 1, 0]
    z_temp = [a, b, c]
    x_temp = np.cross(y_temp, z_temp)
    norm_x_temp = np.linalg.norm(x_temp)
    norm_z_temp = np.linalg.norm(z_temp)
    x = [1/norm_x_temp*x_el for x_el in x_temp]
    z = [1/norm_z_temp*z_el for z_el in z_temp]
    y = [y_el for y_el in np.cross(z, x)]
    return [x, y, z]
                    
class OrthoMatrix:
    def __init__(self, translation, rotation_1=[0, 0, 0], rotation_2=[0, 0, 0], rotation_3=[0, 0, 0]):
        self.trans = np.transpose(np.array([translation]))
        self.axe_1 = rotation_1 #axis of rotation for theta_1
        self.axe_2 = rotation_2 #axis of rotation for theta_2
        self.axe_3 = rotation_3 #axis of rotation for theta_3
        self.rot_1 = np.transpose(np.array(coord_sys(self.axe_1)))#rotation matrix for theta_1
        self.rot_2 = np.transpose(np.array(coord_sys(self.axe_2)))#rotation matrix for theta_2
        self.rot_3 = np.transpose(np.array(coord_sys(self.axe_3)))#rotation matrix for theta_3
        self.rotation_matrix = self.rot_3.dot(self.rot_2.dot(self.rot_1)) #rotation matrix for 
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]),axis=0)
    
    def get_rotation_matrix(self):
        return self.rotation_matrix
    
    def get_translation(self):
        return self.trans
    
    def get_matrix(self):
        return self.matrix
    
    def transpose(self):
        self.rotation_matrix = np.transpose(self.rotation_matrix)
        self.trans = -self.rotation_matrix.dot(self.trans)
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]),axis=0)
        return self.matrix


class ConvertedFromOsim2Biorbd:
    def __init__(self, path, originfile,version=3):

        self.path = path
        self.originfile = originfile
        self.version = str(version)

        self.data_origin = etree.parse(self.originfile)
        self.root = self.data_origin.getroot()

        self.file = open(self.path, 'w')
        self.file.write('version '+self.version+'\n')
        self.file.write('\n// File extracted from '+ self.originfile)
        self.file.write('\n')

        def new_text(element):
            if type(element) == str:
                return element
            else:
                return element.text
            
#        def print_credits():
#            return new_text(go_to(self.root, 'credits'))
#        
#        def print_publications():
#            return new_text(go_to(self.root, 'publications'))

        def body_list(self):
            L = []
            for body in self.data_origin.xpath(
                    '/OpenSimDocument/Model/BodySet/objects/Body'):
                L.append(body.get("name"))
            return L

        def parent_body(body, list_actuated):
            ref = new_text(go_to(go_to(self.root, 'Body', 'name', body), 'parent_body'))
            body_actu = ref
            for _body in list_actuated:
                    if _body.find(ref) != 0:
                        body_actu = _body                        
            return body_actu
        
        def matrix_inertia(body):
            return [new_text(go_to(go_to(self.root, 'Body', 'name', body), 'inertia_xx')),
                    new_text(go_to(go_to(self.root, 'Body', 'name', body), 'inertia_yy')),
                    new_text(go_to(go_to(self.root, 'Body', 'name', body), 'inertia_zz')),
                    new_text(go_to(go_to(self.root, 'Body', 'name', body), 'inertia_xy')),
                    new_text(go_to(go_to(self.root, 'Body', 'name', body), 'inertia_xz')),
                    new_text(go_to(go_to(self.root, 'Body', 'name', body), 'inertia_yz'))]

        def muscle_list(self):
            L = []
            for muscle in self.data_origin.xpath(
                    '/OpenSimDocument/Model/ForceSet/objects/Thelen2003Muscle'):
                L.append(muscle.get("name"))
            return L

        def list_pathpoint_muscle(muscle):
            #return list of viapoint for each muscle
            viapoint = []
            index_pathpoint = index_go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'PathPoint')
            list_index = list(index_pathpoint)
            tronc_list_index = list_index[:len(list_index)-2]
            tronc_index = ''.join(tronc_list_index)
            index_root = index_go_to(self.root, 'Thelen2003Muscle', 'name', muscle)
            index_tronc_total = index_root+tronc_index
            i = 0
            while True:
                try:
                    child = eval('self.root'+index_tronc_total+str(i)+']')
                    viapoint.append(child.get("name"))
                    i += 1
                except Exception as e:
                        #print('Error', e)
                        break  
            return viapoint
        
        def list_transform_body(body):
            #return list of transformation for each body
            transformation = []
            index_transformation = index_go_to(go_to(self.root, 'Body', 'name', body), 'TransformAxis')
            if index_transformation == None:
                return []
            else:
                list_index = list(index_transformation)
                tronc_list_index = list_index[:len(list_index)-2]
                tronc_index = ''.join(tronc_list_index)
                index_root = index_go_to(self.root, 'Body', 'name', body)
                index_tronc_total = index_root+tronc_index
                i = 0
                while True:
                    try:
                        child = eval('self.root'+index_tronc_total+str(i)+']')
                        transformation.append(child.get("name")) if child.get('name') != None else True
                        i += 1
                    except Exception as e:
                        #print('Error', e)
                        break  
                return transformation
        
        def list_markers_body(body):
            #return list of transformation for each body
            markers = []
            index_markers = index_go_to(self.root, 'Marker')
            if index_markers == None:
                return []
            else:
                list_index = list(index_markers)
                tronc_list_index = list_index[:len(list_index)-2]
                tronc_index = ''.join(tronc_list_index)
                i = 0
                while True:
                    try:
                        child = eval('self.root'+tronc_index+str(i)+']').get('name')
                        which_body = new_text(go_to(go_to(self.root, 'Marker', 'name', child), 'body'))
                        if which_body == body:
                            markers.append(child) if child != None else True
                        i += 1
                    except Exception as e:
                        #print('Error', e)
                        break  
                return markers

        def get_body_pathpoint(pathpoint, list_actuated):
            ref = new_text(go_to(go_to(self.root, 'PathPoint', 'name', pathpoint), 'body'))
            body_path = ref
            for _body in list_actuated:
                if _body.find(ref) == 0:
                    body_path = _body
            return body_path
        
        def muscle_group_reference(muscle, ref_group):
            for el in ref_group:
                if muscle == el[0]:
                    return el[1]
            else:
                return 'None'
        
#        # Credits
#        self.write('\n// CREDITS')
#        _credits = print_credits()
#        self.write('\n'+_credits+'\n')
#        
#         # Publications
#        self.write('\n// PUBLICATIONS\n')
#        _publications = print_publications()
#        self.write('\n'+_publications+'\n')

        # Segment definition
        body_list_actuated =  []
        self.write('\n// SEGMENT DEFINITION\n')
        
        for body in body_list(self):
            self.write('\n// Information about {} segment\n'.format(body))
            parent = parent_body(body, body_list_actuated)
            list_transform = list_transform_body(body)
            # segment data
            if list_transform == []:
                list_transform = ['']
            for transformation in list_transform:
                if transformation == '':    
                    rotomatrix = OrthoMatrix([0, 0, 0])
                    body_child = body
                else:
                    body_child = body+'_'+transformation
                    axis_str = new_text(go_to(go_to(go_to(self.root, 'Body', 'name', body), 'TransformAxis', 'name', transformation), 'axis'))
                    axis = [float(s) for s in axis_str.split(' ')]
                    if transformation.find('rotation') != 0:
                        rotomatrix = OrthoMatrix([0, 0, 0], axis)
                    elif transformation.find('translation') != 0:
                        rotomatrix = OrthoMatrix(axis)
                rt_in_matrix = 1
                [[r11, r12, r13, r14],
                [r21, r22, r23, r24],
                [r31, r32, r33, r34],
                [r41, r42, r43, r44]] = rotomatrix.get_matrix().tolist()
                [i11, i22, i33, i12, i13, i23] = matrix_inertia(body)
                mass = new_text(go_to(go_to(self.root, 'Body', 'name', body), 'mass'))
                com = new_text(go_to(go_to(self.root, 'Body', 'name', body), 'mass_center'))
                #TO DO add mesh files
                # writing data                  
                self.write('    // Segment\n')
                self.write('    segment {}\n'.format(body_child)) if body_child != 'None' else self.write('')
                self.write('        parent {} \n'.format(parent)) if parent != 'None' else self.write('')
                self.write('        RTinMatrix    {}\n'.format(rt_in_matrix)) if rt_in_matrix != 'None' else self.write('')
                self.write('        RT\n')
                self.write(
                           '            {}    {}    {}    {}\n'
                           '            {}    {}    {}    {}\n'
                           '            {}    {}    {}    {}\n'
                           '            {}    {}    {}    {}\n'
                           .format(r11, r12, r13, r14,
                                   r21, r22, r23, r24,
                                   r31, r32, r33, r34,
                                   r41, r42, r43, r44))
                self.write('        //translations {}{}{}\n'.format('x','y','z'))
                self.write('        //rotations {}\n'.format('z'))
                self.write('        mass {}\n'.format(mass))
                self.write('        inertia\n')
                self.write(
                           '            {}    {}    {}\n'
                           '            {}    {}    {}\n'
                           '            {}    {}    {}\n'
                           .format(i11, i12, i13,
                                   i12, i22, i23,
                                   i13, i23, i33))
                self.write('        com    {}\n'.format(com))#center of mass
                self.write('    endsegment\n')
                parent = body_child
            body_list_actuated.append(body_child)
            # Markers
            _list_markers = list_markers_body(body)
            if _list_markers != []:
                self.write('\n    // Markers')
                for marker in _list_markers:
                    position = new_text(go_to(go_to(self.root, 'Marker', 'name', marker), 'location'))
                    parent_marker = parent
                    self.write('\n    marker    {}'.format(marker))
                    self.write('\n        parent    {}'.format(parent_marker))
                    self.write('\n        position    {}'.format(position))
                    self.write('\n    endmarker\n')
            
        # Muscle definition
        self.write('\n// MUSCLE DEFINIION\n')
        sort_muscle = []
        muscle_ref_group = []
        for muscle in muscle_list(self):
            viapoint = list_pathpoint_muscle(muscle)
            bodies_viapoint = []
            for pathpoint in viapoint:
                bodies_viapoint.append(get_body_pathpoint(pathpoint, body_list_actuated))
            # it is supposed that viapoints are organized in order 
            # from the parent body to the child body
            body_start = bodies_viapoint[0]
            body_end = bodies_viapoint[len(bodies_viapoint)-1]
            sort_muscle.append([body_start, body_end])
            muscle_ref_group.append([muscle, body_start+'_to_'+body_end])
        # selecting muscle group
        group_muscle = []
        for ext_muscle in sort_muscle:
            if ext_muscle not in group_muscle:
                group_muscle.append(ext_muscle)        
        # print muscle group
        for muscle_group in group_muscle:
            self.write('\n// {} > {}\n'.format(muscle_group[0], muscle_group[1]))
            self.write('musclegroup {}\n'.format(muscle_group[0]+'_to_'+muscle_group[1]))
            self.write('    OriginParent        {}\n'.format(muscle_group[0]))
            self.write('    InsertionParent        {}\n'.format(muscle_group[1]))
            self.write('endmusclegroup\n')
            # muscle
            for muscle in muscle_list(self):
                # muscle data
                m_ref = muscle_group_reference(muscle, muscle_ref_group)
                if m_ref == muscle_group[0]+'_to_'+muscle_group[1]:
                    muscle_type = 'hillthelen'
                    state_type = 'buchanan'
                    start_point = list_pathpoint_muscle(muscle)[0]
                    end_point = list_pathpoint_muscle(muscle)[len(list_pathpoint_muscle(muscle))-1]
                    start_pos = new_text(go_to(go_to(self.root, 'PathPoint', 'name', start_point), 'location'))
                    insert_pos = new_text(go_to(go_to(self.root, 'PathPoint', 'name', end_point), 'location'))
                    opt_length = new_text(go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'optimal_fiber_length'))
                    max_force = new_text(go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'max_isometric_force'))
                    tendon_slack_length = new_text(go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'tendon_slack_length'))
                    pennation_angle = new_text(go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'pennation_angle_at_optimal'))
                    pcsa = new_text(go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'pcsa'))
                    max_velocity = new_text(go_to(go_to(self.root, 'Thelen2003Muscle', 'name', muscle), 'max_contraction_velocity'))
                    
                # print muscle data
                    self.write('\n    muscle    {}'.format(muscle))
                    self.write('\n        Type    {}'.format(muscle_type)) if muscle_type != 'None' else self.write('')
                    self.write('\n        statetype    {}'.format(state_type)) if state_type!= 'None' else self.write('')
                    self.write('\n        musclegroup    {}'.format(m_ref)) if m_ref != 'None' else self.write('')
                    self.write('\n        OriginPosition    {}'.format(start_pos)) if start_pos != 'None' else self.write('')
                    self.write('\n        InsertionPosition    {}'.format(insert_pos)) if insert_pos != 'None' else self.write('')
                    self.write('\n        optimalLength    {}'.format(opt_length)) if  opt_length != 'None' else self.write('')
                    self.write('\n        maximalForce    {}'.format(max_force)) if max_force != 'None' else self.write('')
                    self.write('\n        tendonSlackLength    {}'.format(tendon_slack_length)) if tendon_slack_length != 'None' else self.write('')
                    self.write('\n        pennationAngle    {}'.format(pennation_angle)) if pennation_angle != 'None' else self.write('')
                    self.write('\n        PCSA    {}'.format(pcsa)) if pcsa != 'None' else self.write('')
                    self.write('\n        maxVelocity    {}'.format(max_velocity)) if max_velocity != 'None' else self.write('')
                    self.write('\n    endmuscle\n')
                    # viapoint
                    for viapoint in list_pathpoint_muscle(muscle):
                        # viapoint data
                        parent_viapoint = get_body_pathpoint(viapoint,  body_list_actuated)
                        viapoint_pos = new_text(go_to(go_to(self.root, 'PathPoint', 'name', viapoint), 'location'))
                        # print viapoint data
                        self.write('\n        viapoint    {}'.format(viapoint))
                        self.write('\n            parent    {}'.format(parent_viapoint)) if parent_viapoint != 'None' else self.write('')
                        self.write('\n            muscle    {}'.format(muscle))
                        self.write('\n            musclegroup    {}'.format(m_ref)) if m_ref != 'None' else self.write('')
                        self.write('\n            position    {}'.format(viapoint_pos)) if viapoint_pos != 'None' else self.write('')
                        self.write('\n        endviapoint')
                    self.write('\n')
                    
        self.file.close()

    def __getattr__(self, attr):
        print('Error : {} is not an attribute of this class'.format(attr))

    def get_path(self):
        return self.path

    def write(self, string):
        self.file = open(self.path, 'a')
        self.file.write(string)
        self.file.close()

    def get_origin_file(self):
        return self.originfile

    def credits(self):
        return self.data_origin.xpath(
                '/OpenSimDocument/Model/credits')[0].text

    def publications(self):
        return self.data_origin.xpath(
                '/OpenSimDocument/Model/publications')[0].text

    def body_list(self):
        L = []
        for body in self.data_origin.xpath(
                '/OpenSimDocument/Model/BodySet/objects/Body'):
            L.append(body.get("name"))
        return L


def main():
    #Segment definition
    data = ConvertedFromOsim2Biorbd(
        '../models/testconversion0.biomod', 
        "../models/Opensim_model/arm26.osim")

    origin = data.data_origin
    root = origin.getroot()

if __name__ == "__main__":
    main()
