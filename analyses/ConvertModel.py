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
            if line.find('//') == -1:
                raw_line = line.split("\t")
                new_l = []
                for word in raw_line:
                    if word != '':
                        for element in word.split(' '):
                            if element != '':
                                new_l.append(element)
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
        self.markers = []

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

    def add_marker(self, marker):
        if type(marker) != Marker:
            assert 'wrong type of marker'
        elif marker.get_parent != self.name:
            assert 'this marker does not belong to this segment'
        else:
            self.markers.append(marker)

    def get_markers(self):
        return self.markers

    def set_markers(self, list_of_markers):
        self.markers = []
        for element in list_of_markers:
            self.add_marker(element)
        return list_of_markers


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


class MuscleGroup:
    def __init__(self, name, origin_parent, insertion_parent):
        self.name = name
        self.origin_parent = origin_parent
        self.insertion_parent = insertion_parent
        self.muscles = []

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name
        return self.name

    def get_origin_parent(self):
        return self.origin_parent

    def set_origin_parent(self, new_origin_parent):
        self.origin_parent = new_origin_parent
        return self.origin_parent

    def get_insertion_parent(self):
        return self.insertion_parent

    def set_insertion_parent(self, new_insertion_parent):
        self.insertion_parent = new_insertion_parent
        return self.insertion_parent

    def add_muscle(self, muscle):
        if type(muscle) != Muscle:
            assert 'wrong type of muscle'
        if muscle.get_muscle_group() != self.name:
            assert 'this muscle does not belong to this muscle group'
        self.muscles.append(muscle)
        return self.muscles

    def get_muscles(self):
        return self.muscles

    def set_muscles(self, list_of_muscles):
        self.muscles = []
        for element in list_of_muscles:
            self.add_muscle(element)
        return list_of_muscles


class Muscle:
    def __init__(self, name, _type, state_type, muscle_group, origin_position, insertion_position, optimal_length,
                 maximal_force, tendon_slack_length, pennation_angle, max_velocity):
        self.name = name
        self._type = _type
        self.state_type = state_type
        self.muscle_group = muscle_group
        self.origin_position = origin_position
        self.insertion_position = insertion_position
        self.optimal_length = optimal_length
        self.maximal_force = maximal_force
        self.tendon_slack_length = tendon_slack_length
        self.pennation_angle = pennation_angle
        self.max_velocity = max_velocity
        self.pathpoints = []

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name
        return self.name

    def get_type(self):
        return self._type

    def set_type(self, new_type):
        self._type = new_type
        return self._type

    def get_state_type(self):
        return self.state_type

    def set_state_type(self, new_state_type):
        self.state_type = new_state_type
        return self.state_type

    def get_muscle_group(self):
        return self.muscle_group

    def set_muscle_group(self, new_muscle_group):
        self.muscle_group = new_muscle_group
        return self.muscle_group

    def get_origin_position(self):
        return self.origin_position

    def set_origin_position(self, new_origin_position):
        self.origin_position = new_origin_position
        return self.origin_position

    def get_insertion_position(self):
        return self.insertion_position

    def set_insertion_position(self, new_insertion_position):
        self.insertion_position = new_insertion_position
        return self.insertion_position

    def get_optimal_length(self):
        return self.optimal_length

    def set_optimal_length(self, new_optimal_length):
        self.optimal_length = new_optimal_length
        return self.optimal_length

    def get_maximal_force(self):
        return self.maximal_force

    def set_maximal_force(self, new_maximal_force):
        self.maximal_force = new_maximal_force
        return self.maximal_force

    def get_tendon_slack_length(self):
        return self.tendon_slack_length

    def set_tendon_slack_length(self, new_tendon_slack_length):
        self.tendon_slack_length = new_tendon_slack_length
        return self.tendon_slack_length

    def get_pennation_angle(self):
        return self.pennation_angle

    def set_pennation_angle(self, new_pennation_angle):
        self.pennation_angle = new_pennation_angle
        return self.pennation_angle

    def get_max_velocity(self):
        return self.max_velocity

    def set_max_velocity(self, new_max_velocity):
        self.max_velocity = new_max_velocity
        return self.max_velocity

    def get_pathpoints(self):
        return self.pathpoints

    def add_pathpoint(self, pathpoint):
        if type(pathpoint) != Pathpoint:
            assert 'wrong type of pathpoint'
        else:
            self.pathpoints.append(pathpoint)

    def set_pathpoints(self, list_of_pathpoints):
        self.pathpoints = []
        for element in list_of_pathpoints:
            self.add_pathpoint(element)
        return list_of_pathpoints


class Pathpoint:
    def __init__(self, name, parent, muscle, muscle_group, position):
        self.name = name
        self.parent = parent
        self.muscle = muscle
        self.muscle_group = muscle_group
        self.position = position

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name
        return self.name

    def get_parent(self):
        return self.parent

    def set_parent(self, new_parent):
        self.parent = new_parent
        return self.parent

    def get_muscle(self):
        return self.muscle

    def set_muscle(self, new_muscle):
        self.muscle = new_muscle
        return self.muscle

    def get_muscle_group(self):
        return self.muscle_group

    def set_muscle_group(self, new_muscle_group):
        self.muscle_group = new_muscle_group
        return self.muscle_group

    def get_position(self):
        return self.position

    def set_position(self, new_position):
        self.position = new_position
        return self.position


class BiorbdModel:
    def __init__(self, model):
        self.model = model
        self.words = get_words(self.model)
        self.segments = []
        self.markers = []
        self.muscle_groups = []
        self.muscles = []
        self.pathpoints = []
        self.path = ''
        self.file = open(model, "r")
        self.version = 3

    def read(self):
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

        muscle_group_name = ''
        muscle_group_origin_parent = ''
        muscle_group_insertion_parent = ''

        muscle_name = ''
        muscle_type = ''
        muscle_state_type = ''
        muscle_group = ''
        origin_position = []
        insertion_position = []
        optimal_length = ''
        maximal_force = ''
        tendon_slack_length = ''
        pennation_angle = ''
        max_velocity = ''

        pathpoint_name = ''
        pathpoint_parent = ''
        pathpoint_muscle = ''
        pathpoint_muscle_group = ''
        pathpoint_position = []

        while number_line < len(self.words):
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
                self.segments[-1].add_marker(self.markers[-1])
                number_line += 1
                name_marker = ''
                parent_marker = ''
                position_marker = []
                technical = ''
                continue
            if line[0] == 'musclegroup':
                muscle_group_name = line[1]
                number_line += 1
                continue
            if line[0] == 'OriginParent':
                muscle_group_origin_parent = line[1]
                number_line += 1
                continue
            if line[0] == 'InsertionParent':
                muscle_group_insertion_parent = line[1]
                number_line += 1
                continue
            if line[0] == 'endmusclegroup':
                self.muscle_groups.append(MuscleGroup(muscle_group_name,
                                                      muscle_group_origin_parent, muscle_group_insertion_parent))
                number_line += 1
                muscle_group_name = ''
                muscle_group_origin_parent = ''
                muscle_group_insertion_parent = ''
                continue

            if line[0] == 'muscle':
                muscle_name = line[1]
                number_line += 1
                continue
            if line[0] == 'Type':
                muscle_type = line[1]
                number_line += 1
                continue
            if line[0] == 'statetype':
                muscle_state_type = line[1]
                number_line += 1
                continue
            if line[0] == 'musclegroup':
                muscle_group = line[1]
                number_line += 1
                continue
            if line[0] == 'OriginPosition':
                origin_position = line[1]
                number_line += 1
                continue
            if line[0] == 'InsertionPosition':
                insertion_position = line[1]
                number_line += 1
                continue
            if line[0] == 'optimalLength':
                optimal_length = line[1]
                number_line += 1
                continue
            if line[0] == 'maximalForce':
                maximal_force = line[1]
                number_line += 1
                continue
            if line[0] == 'tendonSlackLength':
                tendon_slack_length = line[1]
                number_line += 1
                continue
            if line[0] == 'pennationAngle':
                pennation_angle = line[1]
                number_line += 1
                continue
            if line[0] == 'maxVelocity':
                max_velocity = line[1]
                number_line += 1
                continue
            if line[0] == 'endmuscle':
                self.muscles.append(Muscle(muscle_name, muscle_type, muscle_state_type, muscle_group, origin_position, insertion_position, optimal_length,
            maximal_force, tendon_slack_length, pennation_angle, max_velocity))
                self.muscle_groups[-1].add_muscle(self.muscles[-1])
                muscle_name = ''
                muscle_type = ''
                muscle_state_type = ''
                muscle_group = ''
                origin_position = []
                insertion_position = []
                optimal_length = ''
                maximal_force = ''
                tendon_slack_length = ''
                pennation_angle = ''
                max_velocity = ''
                number_line += 1
                continue

            if line[0] == 'viapoint':
                pathpoint_name = line[1]
                number_line += 1
                continue
            if line[0] == 'parent':
                pathpoint_parent = line[1]
                number_line += 1
                continue
            if line[0] == 'muscle':
                pathpoint_muscle = line[1]
                number_line += 1
                continue
            if line[0] == 'muscle_group':
                pathpoint_muscle_group = line[1]
                number_line += 1
                continue
            if line[0] == 'position':
                pathpoint_position = line[1]
                number_line += 1
                continue
            if line[0] == 'endviapoint':
                self.pathpoints.append(Pathpoint(pathpoint_name, pathpoint_parent, pathpoint_muscle, pathpoint_muscle_group, pathpoint_position))
                self.muscles[-1].add_pathpoint(self.pathpoints[-1])
                pathpoint_name = ''
                pathpoint_parent = ''
                pathpoint_muscle = ''
                pathpoint_muscle_group = ''
                pathpoint_position = []
                number_line += 1
                continue
            else:
                number_line += 1
                continue

    def add_muscle_group(self, new_muscle_group):
        if type(new_muscle_group) != MuscleGroup:
            assert 'wrong type of muscle group'
        self.muscle_groups.append(new_muscle_group)
        return new_muscle_group

    def get_number_of_muscle_groups(self):
        return len(self.muscle_groups)

    def get_total_muscle_number(self):
        res = 0
        for muscle_group in self.muscle_groups:
            res += len(muscle_group.get_muscles())
        return res

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

    def set_segment_length(self, segment_index, new_segment_length):
        length = self.length_segment(segment_index)
        relative_position = self.get_relative_position(segment_index)
        for element in relative_position:
            element *= new_segment_length/length
        self.set_relative_position(segment_index, relative_position)
        return relative_position

    def normalize_model(self):
        for i in range(self.get_number_of_segments()):
            self.normalize_segment(i)
        return 0

    def write_segment(self, segment_index):
        segment = self.segments[segment_index]
        _name = segment.get_name()
        parent_name = segment.get_parent()
        rt_in_matrix = 1
        dof_total_trans = segment.get_dof_translation()
        dof_total_rot = segment.get_dof_rotation()
        mass = segment.get_mass()
        com = segment.get_com()
        # writing data
        self.file.write('\t// Segment\n')
        self.file.write('\tsegment\t{}\n'.format(_name)) if _name != 'None' else self.write('')
        self.file.write('\t\tparent\t{} \n'.format(parent_name)) if parent_name != '' else True
        self.file.write('\t\tRTinMatrix\t{}\n'.format(rt_in_matrix)) if rt_in_matrix != 'None' else self.write('')
        self.file.write('\t\tRT\n')
        for i in range(3):
            self.file.write('\t\t')
            for j in range(3):
                self.file.write('\t{}'.format(segment.get_rot_trans_matrix()[i][j]))
            self.file.write('\n')
        self.file.write('\t\ttranslations {}\n'.format(dof_total_trans)) if dof_total_trans != '' else True
        self.file.write('\t\trotations {}\n'.format(dof_total_rot)) if dof_total_rot != '' else True
        self.file.write('\t\tmass {}\n'.format(mass)) if mass != '' else True
        self.file.write('\t\tinertia\n')
        if segment.get_inertia() != [[], [], []]:
            for i in range(3):
                self.file.write('\t\t')
                for j in range(3):
                    self.file.write('\t{}'.format(segment.get_inertia()[i][j]))
                self.file.write('\n')
        self.file.write('\t\tcom\t{}\n'.format(com)) if com != '' else True
        self.file.write('    endsegment\n')
        return 0

    def write_marker(self, segment_index, marker_index):
        marker = self.segments[segment_index].get_markers()[marker_index]
        self.file.write('\n\tmarker\t{}'.format(marker.get_name()))
        self.file.write('\n\t\tparent\t{}'.format(marker.get_parent()))
        self.file.write('\n\t\tposition\t{}'.format(marker.get_position()))
        self.file.write('\n\tendmarker\n')
        return 0

    def write_muscle_group(self, muscle_group_index):
        # TODO complete
        return 0

    def write_muscle(self, muscle_group_index, muscle_index):
        # TODO complete
        return  0

    def write_pathpoint(self, muscle_group_index, muscle_index, pathpoint_index):
        # TODO complete
        return 0

    def rewrite(self, path, with_markers=True, with_muscles=True, with_pathpoints=True):
        self.file = open(path, 'w')
        self.path = path
        self.file.write('version ' + self.version + '\n')
        self.file.write('\n// File extracted from ' + self.model)
        self.file.write('\n')

        self.file.write('\n// SEGMENT DEFINITION\n')
        for i in range(self.get_number_of_segments()):
            self.printing_segment(i)
            if with_markers:
                markers = self.segments[i].get_markers
                if markers:
                    self.write('\t// Markers\n')
                    for j in range(len(markers)):
                        self.write_marker(i, j)
        if with_muscles:
            self.file.write('\n// MUSCLE DEFINIION\n')
            for i in range(len(self.muscle_groups)):
                self.write_muscle_group(i)
                for j in range(len(self.muscle_groups[i].get_muscles())):
                    self.printing_muscle(i, j)
                    if with_pathpoints:
                        pathpoints = self.muscle_groups[i].get_muscles()[j].get_pathpoints()
                        if pathpoints:
                            for k in range(len(markers)):
                                self.write_pathpoint(i, j, k)
        return 0


def main():
    model = BiorbdModel('../models/model_Clara/AdaJef_1g_Model.s2mMod')
    model2 = BiorbdModel('../models/conv-arm26.bioMod')
    model.read()
    model2.read()
    print(get_words('../models/conv-arm26.bioMod'))
    print(get_words('../models/model_Clara/AdaJef_1g_Model.s2mMod'))
    print(model.get_total_muscle_number())
    print(model2.get_total_muscle_number())
    return 0


if __name__ == "__main__":
    main()
