# coding: utf-8

from lxml import etree

data = etree.parse("../models/Opensim_model/arm26.osim")
for body in data.xpath('/OpenSimDocument/Model/BodySet/objects/Body'):
    print(body.get("name"))
    for i in range(len(body.getchildren())):
        print(body.getchildren()[i].text)


class ConvertedFromOsim2Biorbd:
    def __init__(self, name, path, originfile):
        self.name = name
        self.path = path
        self.originfile = originfile
        self.file = open(self.name, 'x')


    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def create_xlm(self):
        file = open(self.name, 'x')
        file.write('File extracted from', self.originfile, '/n')

    def write(self):

def main():
    ####
    self = open(name, 'x')


if __name__ == "__main__":
    main()

