# coding: utf-8

from lxml import etree

import xml.sax

import pprint



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
            for body in self.data_origin.xpath('/OpenSimDocument/Model/BodySet/objects/Body'):
                L.append(body.get("name"))
            return L

        def parent_body(body):
            return self.data_origin.xpath("/OpenSimDocument/Model/BodySet/objects/"
                                          "Body[@name='{}']/CustomJoint/parent_body".format(body))

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
        return self.data_origin.xpath('/OpenSimDocument/Model/credits')[0].text

    def publications(self):
        return self.data_origin.xpath('/OpenSimDocument/Model/publications')[0].text

    def body_list(self):
        L = []
        for body in self.data_origin.xpath('/OpenSimDocument/Model/BodySet/objects/Body'):
            L.append(body.get("name"))
        return L

    def parent_body(self, body):
        return self.data_origin.xpath("/OpenSimDocument/Model/BodySet/objects/"
                                      "Body[@name={}]/CustomJoint/parent_body".format(body))


def main():
    #Segment definition
    pass


if __name__ == "__main__":
    main()


data = ConvertedFromOsim2Biorbd('../models/testconversion0.biomod', "../models/Opensim_model/arm26.osim")
print(data.credits())
print(data.publications())
print(data.body_list())
for body in data.body_list():
    parent = data.parent_body(body)
    print(body)
    print(parent)

print('******')
origin = data.data_origin
root = origin.getroot()
# root = etree.fromstring('data_as_string')
print(root.tag)
print(root.attrib)
print('******')
for child in root:
    print(child.tag, child.attrib)
print('******')
print(root[0][8][0][0][0].text)
print('******')
for body in root.iter('Body'):
    print(body.attrib)
    print(body.tag)
print('******')
for body in root.iter('parent_body'):
    print(body.tag)
    print(body.attrib)
    print(body.getchildren())
    print(body.text)
print('******')
print(root.findall("./parent_body"))
print('******')
print(root[0].tag)

bodyset = root[0][8][0].tag
print(bodyset)
for child in root:
    print(child.tag)
print('******')
def go_to(_root, _tag, index = ''):
    i = 0
    for _child in _root:
        if _child.tag == _tag:
            return index+'[{}]'.format(i)
        else:
            i += 1

    else:
        j = 0
        for _child in _root:
             return go_to(_child, _tag, index+'[{}]'.format(j))


index = go_to(root, 'Body')
print(index)
