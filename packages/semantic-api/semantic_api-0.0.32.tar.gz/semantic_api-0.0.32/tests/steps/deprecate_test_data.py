from typing_extensions import Final
from semantic.common.common_types import TerminusRef
from semantic.fera.fera_types.type_constructors import JointState, joint_state

type1: str = 'JointState'
typeFail:Final = 'notfoundtype'
name1:str = 'a-unique-id'
name2:str = 'a-different-unique-id'

shoulder_pan_name = 'shoulder_pan_joint'
shoulder_pan_path = 'UR10+ur10+base_link+shoulder_pan_joint'
parent: TerminusRef = {"@ref": "UsdPrim_UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef_URI"}



'''
    name should come from parent name
    need:
        parent uri emulator
        parent name getter
'''
joint_state_test1 = joint_state(name1, 't1','t2', 27, parent, 0.1, 0.2, 0.3)
joint_state_test2 = joint_state(name2, 't1','t2', 27, parent, 0.1, 0.2, 0.3)


float6 = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]