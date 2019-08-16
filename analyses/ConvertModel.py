import numpy as np
import math
from numpy.linalg import inv
import biorbd


def coord_sys(axis):
    # define orthonormal coordinate system with given z-axis
    [a, b, c] = axis
    if a == 0:
        if b == 0:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], ''
            else:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'z'
        else:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'y'
            else:
                y_temp = [0, - c /b, 1]
    else:
        if b == 0:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'x'
            else:
                y_temp = [- c /a, 0, 1]
        else:
            y_temp = [- b /a, 1, 0]
    z_temp = [a, b, c]
    x_temp = np.cross(y_temp, z_temp)
    norm_x_temp = np.linalg.norm(x_temp)
    norm_z_temp = np.linalg.norm(z_temp)
    x = [1/norm_x_temp*x_el for x_el in x_temp]
    z = [1/norm_z_temp*z_el for z_el in z_temp]
    y = [y_el for y_el in np.cross(z, x)]
    return [x, y, z], ''


class OrthoMatrix:
    def __init__(self, translation=[0, 0, 0], rotation_1=[0, 0, 0], rotation_2=[0, 0, 0], rotation_3=[0, 0, 0]):
        self.trans = np.transpose(np.array([translation]))
        self.axe_1 = rotation_1  # axis of rotation for theta_1
        self.axe_2 = rotation_2  # axis of rotation for theta_2
        self.axe_3 = rotation_3  # axis of rotation for theta_3
        self.rot_1 = np.transpose(np.array(coord_sys(self.axe_1)[0]))  # rotation matrix for theta_1
        self.rot_2 = np.transpose(np.array(coord_sys(self.axe_2)[0]))  # rotation matrix for theta_2
        self.rot_3 = np.transpose(np.array(coord_sys(self.axe_3)[0]))  # rotation matrix for theta_3
        self.rotation_matrix = self.rot_3.dot(self.rot_2.dot(self.rot_1))  # rotation matrix for
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)

    def get_rotation_matrix(self):
        return self.rotation_matrix

    def set_rotation_matrix(self, rotation_matrix):
        self.rotation_matrix = rotation_matrix

    def get_translation(self):
        return self.trans

    def set_translation(self, trans):
        self.trans = trans

    def get_matrix(self):
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)
        return self.matrix

    def transpose(self):
        self.rotation_matrix = np.transpose(self.rotation_matrix)
        self.trans = -self.rotation_matrix.dot(self.trans)
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)
        return self.matrix

    def product(self, other):
        self.rotation_matrix = self.rotation_matrix.dot(other.get_rotation_matrix())
        self.trans = self.trans + other.get_translation()
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)

    def get_axis(self):
        return coord_sys(self.axe_1)[1] + coord_sys(self.axe_2)[1] + coord_sys(self.axe_3)[1]


def out_product(rotomatrix_1, rotomatrix_2):
    rotomatrix_prod = OrthoMatrix()
    rotomatrix_prod.set_translation(rotomatrix_1.get_translation() + rotomatrix_2.get_translation())
    rotomatrix_prod.set_rotation_matrix(rotomatrix_1.get_rotation_matrix().dot(rotomatrix_2.get_rotation_matrix()))
    rotomatrix_prod.get_matrix()
    return rotomatrix_prod


def get_words(_model):
    file = open(_model, "r")
    all_lines = file.readlines()
    all_words = []
    for line in all_lines:
        line = line[:-1]
        if line != '':
            if line.split(" ")[0].find('//') == -1:
                raw_line = line.split("\t")
                new_l = []
                for word in raw_line:
                    if word != '':
                        new_l.append(word)
                all_words.append(new_l)
    return all_words


class Segment:
    def __init__(self, name, parent, rot_trans_matrix, dof_rotation, dof_translation, mass, inertia, com):
        self.name = name
        self.parent = parent
        self.rot_trans_matrix = rot_trans_matrix
        self.dof_rotation = dof_rotation
        self.dof_translation = dof_translation
        self.mass = mass
        self.inertia = inertia
        self.com = com

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_parent(self):
        return self.parent

    def set_parent(self, new_parent):
        self.name = new_parent

    def get_rot_trans_matrix(self):
        return self.rot_trans_matrix

    def set_rot_trans_matrix(self, new_rot_trans_matrix):
        self.rot_trans_matrix = new_rot_trans_matrix

    def get_dof_rotation(self):
        return self.dof_rotation

    def set_dof_rotation(self, new_dof_rotation):
        self.dof_rotation = new_dof_rotation

    def get_dof_translation(self):
        return self.dof_translation

    def set_dof_translation(self, new_dof_translation):
        self.dof_translation = new_dof_translation

    def get_mass(self):
        return self.mass

    def set_mass(self, new_mass):
        self.mass = new_mass

    def get_inertia(self):
        return self.inertia

    def set_inertia(self, new_inertia):
        self.inertia = new_inertia

    def get_com(self):
        return self.com

    def set_com(self, new_com):
        self.com = new_com

# TODO add element marker to segment


class Marker:
    def __init__(self, name, parent, position, technical):
        self.name = name
        self.parent = parent
        self.position = position
        self.technical = technical

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_parent(self):
        return self.parent

    def set_parent(self, new_parent):
        self.parent = new_parent

    def get_position(self):
        return self.position

    def set_position(self, new_position):
        self.position = new_position

    def get_technical(self):
        return self.technical

    def set_technical(self, new_technical):
        self.technical = new_technical

# TODO create class for group of muscles
# TODO create class for muscles

class BiorbdModel:
    def __init__(self, model):
        self.model = model
        self.words = get_words(self.model)
        self.segments = []
        self.markers = []

        number_line = 0

        name_segment = ''
        parent_segment = ''
        rot_trans_matrix = [[], [], []]
        dof_translation = ''
        dof_rotation = ''
        mass = 0
        inertia = [[], [], []]
        com = []

        name_marker = ''
        parent_marker = ''
        position_marker = []
        technical = ''
        while number_line < len(self.words):
            print(number_line)
            line = self.words[number_line]
            if line[0] == 'segment':
                name_segment = line[1]
                number_line += 1
                continue
            if line[0] == 'parent':
                parent_segment = line[1]
                number_line += 1
                continue
            if line[0] == 'RT':
                rot_trans_matrix[0] = self.words[number_line + 1]
                rot_trans_matrix[1] = self.words[number_line + 2]
                rot_trans_matrix[2] = self.words[number_line + 3]
                number_line += 4
                continue
            if line[0] == 'translations':
                dof_translation = line[1]
                number_line += 1
                continue
            if line[0] == 'rotations':
                dof_rotation = line[1]
                number_line += 1
                continue
            if line[0] == 'mass':
                mass = line[1]
                number_line += 1
                continue
            if line[0] == 'inertia':
                inertia[0] = self.words[number_line + 1]
                inertia[1] = self.words[number_line + 2]
                inertia[2] = self.words[number_line + 3]
                number_line += 4
                continue
            if line[0] == 'com':
                com.append(line[1])
                com.append(line[2])
                com.append(line[3])
                number_line += 1
                continue
            if line[0] == 'endsegment':
                self.segments.append(Segment(name_segment, parent_segment, rot_trans_matrix,
                                             dof_rotation, dof_translation, mass, inertia, com))
                number_line += 1
                name_segment = ''
                parent_segment = ''
                rot_trans_matrix = [[], [], []]
                dof_translation = ''
                dof_rotation = ''
                mass = 0
                inertia = [[], [], []]
                com = []
                continue
            if line[0] == 'marker':
                name_marker = line[1]
                number_line += 1
                continue
            if line[0] == 'parent':
                parent_marker = line[1]
                number_line += 1
                continue
            if line[0] == 'position':
                position_marker.append(line[1])
                position_marker.append(line[2])
                position_marker.append(line[3])
                number_line += 1
                continue
            if line[0].find('technical'):
                technical = line[-1]
            if line[0] == 'endmarker':
                self.markers.append(Marker(name_marker, parent_marker, position_marker, technical))
                number_line += 1
                name_marker = ''
                parent_marker = ''
                position_marker = []
                technical = ''
                continue
            else:
                number_line += 1
                continue

    def add_segment(self, new_segment):
        if type(new_segment) != Segment:
            assert 'wrong type of segment'
        self.segments.append(new_segment)
        return new_segment

    def get_number_of_segments(self):
        return len(self.segments)

    def get_segment(self, segment_index):
        return self.segments[segment_index]

    def get_relative_position(self, segment_index):
        segment = self.get_segment(segment_index)
        rot_trans_matrix = segment.get_rot_trans_matrix()
        return [float(rot_trans_matrix[0][2]), float(rot_trans_matrix[1][2]), float(rot_trans_matrix[2][2])]

    def set_relative_position(self, segment_index, new_relative_position):
        if len(new_relative_position) != 3:
            assert 'wrong size of vector to set new relative position of the segment'
        rot_trans_matrix = self.get_segment(segment_index).get_rot_trans_matrix()
        rot_trans_matrix[0][2] = str(new_relative_position[0])
        rot_trans_matrix[1][2] = str(new_relative_position[1])
        rot_trans_matrix[2][2] = str(new_relative_position[2])
        self.get_segment(segment_index).set_rot_trans_matrix(rot_trans_matrix)
        return rot_trans_matrix

    def length_segment(self, segment_index):
        relative_position = self.get_relative_position(segment_index)
        return math.sqrt(relative_position[0]**2 + relative_position[1]**2 + relative_position[2]**2)

    def normalize_segment(self, segment_index):
        length = self.length_segment(segment_index)
        relative_position = self.get_relative_position(segment_index)
        for element in relative_position:
            element /= length
        self.set_relative_position(segment_index, relative_position)
        return relative_position

    def normalize_model(self):
        for i in range(self.get_number_of_segments()):
            self.normalize_segment(i)
        return 0


def main():
    model = BiorbdModel('../models/model_Clara/AdaJef_1g_Model.s2mMod')
    model.normalize_model()
    return 0


if __name__ == "__main__":
    main()
