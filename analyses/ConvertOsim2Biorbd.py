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

        # Segment definition
        self.write('\n// SEGMENT DEFINITION\n\n')
        for body in body_list(self)[1:]:
            parent = parent_body(body)
            self.write('// Informations about {} segment\n'
                       '    //Segment\n'
                       '    segment {}\n'
                       '        parent {} \n'.format(body, body, parent))

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
    pass


if __name__ == "__main__":
    main()


data = ConvertedFromOsim2Biorbd(
        '../models/testconversion0.biomod', 
        "../models/Opensim_model/arm26.osim")

print('******')
origin = data.data_origin
root = origin.getroot()
print('******')


def index_go_to(_root, _tag, _attrib=False, _attribvalue='', index=''):
    #return index to go to _tag which can have condition on its attribute
    if index == '':
        print('root : '+retrieve_name(_root))
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


index = index_go_to(root, 'Body', 'name', 'r_humerus')
print(index)
print(eval('root'+index).get("name"))
print(go_to(root, 'Body', 'name', 'r_humerus').get("name"))
print(retrieve_name(root))
