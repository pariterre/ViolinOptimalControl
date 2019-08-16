import numpy as np
from lxml import etree
import inspect



def new_text(element):
    if type(element) == str:
        return element
    else:
        return element.text


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


def index_go_to(_root, _tag, _attrib='False', _attribvalue='', index=''):
    # return index to go to _tag which can have condition on its attribute
    i = 0
    for _child in _root:
        if type(_child) == str:
            return ''
        if _attrib != 'False':
            if _child.tag == _tag and _child.get(_attrib) == _attribvalue:
                return index+'[{}]'.format(i)
            else:
                i += 1
        else:
            if _child.tag == _tag:
                return index+'[{}]'.format(i)
            else:
                i += 1
    # not found in children, go to grand children
    else:
        j = 0
        if _root is not None:
            for _child in _root:
                a = index_go_to(_child, _tag, _attrib, _attribvalue, index+'[{}]'.format(j))
                if a:
                    return index_go_to(_child, _tag, _attrib, _attribvalue, index+'[{}]'.format(j))
                else:
                    j += 1
            else:
                return None


def go_to(_root, _tag, _attrib='False', _attribvalue=''):
    # return element corresponding to _tag
    # which can have condition on its attribute
    _index = index_go_to(_root, _tag, _attrib, _attribvalue)
    if _index is None:
        return 'None'
    else:
        _index = index_go_to(_root, _tag, _attrib, _attribvalue)
        return eval(retrieve_name(_root)+_index)




def linear_fun(_t):
    return _t


class MotFile:
    def __init__(self, path, osim_model_path, time_frame=300, time_init=0, time_end=1, data_fun=linear_fun, add_velocities=False, add_accelerations=False):

        self.path = path
        self.osim_model_path = osim_model_path

        self.data_origin = etree.parse(self.osim_model_path)
        self.root = self.data_origin.getroot()
        self.time_frame = time_frame
        self.time_init = time_init
        self.time_end = time_end
        self.add_velocities = add_velocities
        self.add_acceleration = add_accelerations

        def all_joints():
            list_joint = []
            index_joints = index_go_to(self.root, 'CustomJoint')
            if index_joints is not None:
                list_index = list(index_joints)
                tronc_list_index = list_index[:len(list_index) - 2]
                tronc_index = ''.join(tronc_list_index)
                i = int(list_index[len(list_index) - 2])
                while True:
                    try:
                        new_joint = eval('self.root' + tronc_index + str(i) + ']').get('name')
                        if new_text(go_to(self.root, 'CustomJoint', 'name', new_joint)) != 'None':

                            list_joint.append(new_joint)
                        i += 1
                    except Exception as e:
                        # print('Error', e)
                        break
            return list_joint

        def dof_of_joint(_joint):
            # joint type is 'CustomJoint'
            # 'WeldJoint' type do not have degrees of freedom
            dof = []
            _index_dof = index_go_to(go_to(self.root, 'CustomJoint', 'name', _joint), 'Coordinate')
            if _index_dof is None:
                return []
            else:
                _list_index = list(_index_dof)
                _tronc_list_index = _list_index[:len(_list_index) - 2]
                _tronc_index = ''.join(_tronc_list_index)
                _index_root = index_go_to(self.root, 'CustomJoint', 'name', _joint)
                _index_tronc_total = _index_root + _tronc_index
                i = 0
                while True:
                    try:
                        child = eval('self.root' + _index_tronc_total + str(i) + ']')
                        if child.get('name') is not None:
                            dof.append(child.get("name"))
                        i += 1
                    except Exception as e:
                        # print('Error', e)
                        break
            return dof

        self.all_joints = all_joints()

        self.all_dof = []
        for i in range(len(self.all_joints)):
            joint = self.all_joints[i]
            temp_dof = dof_of_joint(joint)
            for el in temp_dof:
                self.all_dof.append([joint, el])
        self.total_number_dof = len(self.all_dof)
        self.column_number = self.total_number_dof * (1 + add_velocities) + 1
        self.time_vector = np.linspace(self.time_init, self.time_end, self.time_frame)

        # File header
        self.file = open(self.path, 'w')
        self.file.write('Coordinates\n'
                        'version=1\n'
                        'nRows = ' + str(self.time_frame) + '\n'
                        'nColumns = ' + str(self.column_number) + '\n'
                        'inDegrees=yes\n'
                        'endheader\n')

        self.positions = []

        # Write data
        self.first_line = 'time'
        for i in range(self.total_number_dof):
            self.first_line += '\t'+ '/jointset/' + self.all_dof[i][0] + '/' + self.all_dof[i][1] + '/value'
            if add_velocities:
                self.first_line += '\t' + '/jointset/' + self.all_dof[i][0] + '/' + self.all_dof[i][1] + '/speed'
            if add_accelerations:
                self.first_line += '\t' + '/jointset/' + self.all_dof[i][0] + '/' + self.all_dof[i][1] + '/acceleration'
        self.file.write(self.first_line + '\n')

        self.line = ''
        self.q = [[] for i in range(self.total_number_dof)]
        self.q_dot = [[0] for i in range(self.total_number_dof)]
        self.q_ddot = [[0] for i in range(self.total_number_dof)]

        self.data_fun = data_fun

    def get_q(self):
        return self.q

    def get_q_dot(self):
        return self.q_dot

    def get_positions(self):
        return self.positions

    def add_position(self, new_position):
        if len(new_position) != self.total_number_dof:
            raise Exception('New position does not have the right number of coordinates.\n'
                            'Model has {} degrees of freedom'.format(self.total_number_dof))
        else:
            self.positions.append(new_position)

    def clear_position(self):
        self.positions = []

    def set_positions(self, positions_to_be_set):
        self.clear_position()
        for position in positions_to_be_set:
            self.add_position(position)

    def create_data(self):
        if len(self.positions) <= 1:
            raise Exception('Not enough positions have been set for the model\n'
                            'You have set {} position.\n'
                            'You must set at least 2 positions'.format(len(self.positions)))
        else:
            number_step = len(self.positions) - 1
            k = 0
            for j in range(self.time_frame):
                normalized_time = (j-k*self.time_frame/number_step)*number_step/self.time_frame
                if normalized_time >= 1:
                    k += 1
                for i in range(self.total_number_dof):
                    self.q[i].append((self.positions[k+1][i]-self.positions[k][i])*self.data_fun(normalized_time) + self.positions[k][i])
            if self.add_velocities:
                for i in range(self.total_number_dof):
                    for j in range(self.time_frame-1):
                        self.q_dot[i].append((self.q[i][j+1]-self.q[i][j])/(self.time_vector[j+1]-self.time_vector[j]))
                if self.add_acceleration:
                    for i in range(self.total_number_dof):
                        for j in range(self.time_frame-1):
                            self.q_ddot[i].append((self.q_dot[i][j+1]-self.q_dot[i][j])/(self.time_vector[j+1]-self.time_vector[j]))

            for j in range(self.time_frame):
                self.line = '\t'
                self.line += str(self.time_vector[j])
                for i in range(self.total_number_dof):
                    self.line += '\t' + str(self.q[i][j])
                    if self.add_velocities:
                        self.line += '\t' + str(self.q_dot[i][j])
                        if self.add_acceleration:
                            self.line += '\t' + str(self.q_ddot[i][j])
                self.file.write(self.line + '\n')



def main():
    motion = MotFile(
        '../models/motion-arm26.mot',
        "../models/Opensim_model/arm26.osim", 500, 0, 10, linear_fun, False, False)

    motion.set_positions([[0, 0], [45, 45], [90, 90], [0, 0]])

    motion.create_data()


if __name__ == "__main__":
    main()