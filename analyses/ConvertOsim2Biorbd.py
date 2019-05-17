# coding: utf-8

from lxml import etree

import xml.sax

import pprint

import inspect

# data = etree.parse("../models/Opensim_model/arm26.osim")
# for body in data.xpath('/OpenSimDocument/Model/BodySet/objects/Body'):
#     print(body.get("name"))
#     for i in range(len(body.getchildren())):
#         print(body.getchildren()[i].text)


class ConvertedFromOsim2Biorbd:
    def __init__(self, path, originfile):

        self.path = path
        self.originfile = originfile

        self.data_origin = etree.parse(self.originfile)
        self.root = self.data_origin.getroot()

        self.file = open(self.path, 'w')
        self.file.write('File extracted from '+ self.originfile)
        self.file.write('\n')

        self.file.close()

        def body_list(self):
            L = []
            for body in self.data_origin.xpath(
                    '/OpenSimDocument/Model/BodySet/objects/Body'):
                L.append(body.get("name"))
            return L

        def parent_body(body):
            return go_to(go_to(self.root, 'Body', 'name', body), 'parent_body').text
        
        def mass_body(body):
            return go_to(go_to(self.root, 'Body', 'name', body), 'mass').text
        
        def matrix_inertia(body):
            return [go_to(go_to(self.root, 'Body', 'name', body), 'inertia_xx').text,
                    go_to(go_to(self.root, 'Body', 'name', body), 'inertia_yy').text,
                    go_to(go_to(self.root, 'Body', 'name', body), 'inertia_zz').text,
                    go_to(go_to(self.root, 'Body', 'name', body), 'inertia_xy').text,
                    go_to(go_to(self.root, 'Body', 'name', body), 'inertia_xz').text,
                    go_to(go_to(self.root, 'Body', 'name', body), 'inertia_yz').text]
            
        def center_of_mass(body):
            return go_to(go_to(self.root, 'Body', 'name', body), 'mass_center').text
        
        def extremities(body):
            return [go_to(go_to(self.root, 'Body', 'name', body), 'mass_center').text,
                    go_to(go_to(self.root, 'Body', 'name', body), 'mass_center').text]

        # Segment definition
        self.write('\n// SEGMENT DEFINITION\n')
        for body in body_list(self)[1:]:
            #segment data
            parent = parent_body(body)
            rt_in_matrix = 1
            [r11, r12, r13, r14,
            r21, r22, r23, r24,
            r31, r32, r33, r34,
            r41, r42, r43, r44] = [0, 0, 0, 0,
                              0, 0, 0, 0,
                              0, 0, 0, 0,
                              0, 0, 0, 0]
            [i11, i22, i33, i12, i13, i23] = matrix_inertia(body)
            mass = mass_body(body)
            com = center_of_mass(body)
            mesh = extremities(body)
            #writing data                  
            self.write('\n// Informations about {} segment\n'
                       '    // Segment\n'
                       '    segment {}\n'
                       '        parent {} \n'
                       '        RTinMatrix    {}\n'
                       '        RT\n'.format(body, body, parent, rt_in_matrix))
            self.write(
                       '            {}    {}    {}    {}\n'
                       '            {}    {}    {}    {}\n'
                       '            {}    {}    {}    {}\n'
                       '            {}    {}    {}    {}\n'
                       .format(r11, r12, r13, r14,
                               r21, r22, r23, r24,
                               r31, r32, r33, r34,
                               r41, r42, r43, r44))
            self.write('        //translations xyz\n')
            self.write('        //rotations xyz\n')
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
            self.write('        mesh    {}\n'.format(mesh[0]))#center of mass
            self.write('        mesh    {}\n'.format(mesh[1]))#center of mass
            self.write('    endsegment\n')
            
            

    def __getattr__(self, attr):
        print('Error : {} is not an attribute of this class'.format(attr))

    # def __setattr__(self, name_attr, val_attr):
    #     object.__setattr__(self, name_attr, val_attr)
    #     self.enregistrer()

    # def get_name(self):
    #     return self.name

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


def index_go_to(_root, _tag, _attrib=False, _attribvalue='', index=''):
    #return index to go to _tag which can have condition on its attribute
    i = 0
    for _child in _root:
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
    
    return eval(retrieve_name(_root)+_index)
