# pylint: disable=invalid-name
"""
A blender addon creating and animating boids
"""
import operator
from enum import Enum #  pylint: disable=import-error
import mathutils # pylint: disable=import-error
import numpy as np # pylint: disable=import-error
import bpy # pylint: disable=import-error

class BoidType(Enum):
    """
    Type of boid that determines how boid is handled
    """
    NORMAL = 0
    PREY = 1
    PREDATOR = 2

class Boid:
    """
    The Boid class handling all actions related to boids.
    """
    def __init__(self, instance) -> None:
        self.instance = instance
        self.last_pos = tuple(self.instance.location)
        self.velocity = (0,0,0)
        self.boids_in_range = []
        self.type = BoidType.NORMAL

    def set_type(self, boid_type):
        """
        Sets boid type
        """
        self.type = boid_type

    def get_type(self):
        """
        Returns boid type
        """
        return self.type

    def move(self):
        """
        Moves the Boid to its new location using it calculated velocity.
        """
        self.last_pos = tuple(self.instance.location)
        self.instance.location = add_tuples(self.instance.location, self.velocity)

    def rotate(self):
        """
        Rotates the Boid towards it direction vector
        """
        velocity = self.velocity
        direction_vector = mathutils.Vector(velocity)
        self.instance.rotation_mode = "XYZ"
        self.instance.rotation_euler = direction_vector.to_track_quat('X', 'Z').to_euler()

    def get_steering_force(self, desired, settings):
        """
        Calculates a steering vector towards a desired direction
        """
        steer = set_vector_magnitude(desired, settings.max_speed)
        steer = subtract_tuples(steer, self.velocity)
        steer = limit_vector(steer, settings.max_force)

        return steer

    def calc_velocity(self, settings):
        """
        Call all rule functions
        """

        if len(self.boids_in_range) == 0:
            return

        cohesion = self.cohesion(settings)
        alignment = self.alignment(settings)
        separation = self.separation(settings)

        self.velocity = add_tuples(cohesion, self.velocity)
        self.velocity = add_tuples(alignment, self.velocity)
        self.velocity = add_tuples(separation, self.velocity)

        self.velocity = set_vector_magnitude(self.velocity, settings.max_speed)

    def add_keyframe(self, frame):
        """
        Adds a keyframe of the current position and rotation to the desired frame
        """
        self.instance.keyframe_insert(data_path="location", frame=frame)
        self.instance.keyframe_insert(data_path="rotation_euler", frame=frame)

    def calc_boids_in_range(self, all_boids, settings):
        """
        Gets all Boid Objects in range
        """
        self.boids_in_range = []
        for boid in all_boids:
            distance = calc_v_len(subtract_tuples(boid.last_pos, tuple(self.instance.location)))
            if (distance <= settings.vision_radius and boid != self):
                self.boids_in_range.append(boid)

    def cohesion(self, settings):
        """
        Calculates the cohesion force.
        """
        average_location = average_of_tuples([boid.last_pos for boid in self.boids_in_range])
        cohesion_steer = self.get_steering_force(
            subtract_tuples(average_location, self.instance.location),
            settings)
        cohesion_steer = multiply_tuple_with_number(cohesion_steer, settings.cohesion_strength)

        return cohesion_steer

    def alignment(self, settings):
        """
        Calculates the alignment force
        """
        average_velocity = average_of_tuples([boid.velocity for boid in self.boids_in_range])
        alignment_steer = self.get_steering_force(average_velocity, settings)
        alignment_steer = multiply_tuple_with_number(alignment_steer, settings.alignment_strength)

        return alignment_steer

    def separation(self, settings):
        """
        Calculates the separation force
        """
        average_separation = average_of_tuples(
            [subtract_tuples(self.instance.location, boid.last_pos) for boid in self.boids_in_range]
            )
        separation_steer = self.get_steering_force(average_separation, settings)
        separation_steer = multiply_tuple_with_number(separation_steer,
                                                      settings.separation_strength)

        return separation_steer


    def update(self, all_boids, frame, settings):
        """
        Calls all function needed to update the position of a boid
        """
        self.calc_boids_in_range(all_boids, settings)
        self.add_keyframe(frame)
        self.calc_velocity(settings)
        self.move()
        self.rotate()

    def delete_keyframes(self):
        """
        Deletes all keyframes
        """
        self.instance.animation_data_clear()

class BoidSettingValues(bpy.types.PropertyGroup):
    """
    Defines all Properties needed for the boids
    """
    max_speed: bpy.props.FloatProperty(
        name = "Max Speed",
        description="Sets the Max Speed",
        min=0, step=0.01, default=1)
    max_force: bpy.props.FloatProperty(
        name = "Max Force",
        description="Sets the Max Force",
        min=0, step=0.01, default=0.1)
    vision_radius: bpy.props.FloatProperty(
        name = "Vision Radius",
        description="Sets the Vision Radius",
        min=0, step=0.01, default=10)
    cohesion_strength: bpy.props.FloatProperty(
        name = "Cohesion Strength",
        description="Sets the Cohesion Strength",
        min=0, step=0.01, max=1, default=1)
    alignment_strength: bpy.props.FloatProperty(
        name = "Alignment Strength",
        description="Sets the Alignment Strength",
        min=0, step=0.01, max=1, default=1)
    separation_strength: bpy.props.FloatProperty(
        name = "Separation Strength",
        description="Sets the Separation Strength",
        min=0, step=0.01, max=1, default=0.9)


### Helper Functions ###
def add_tuples(op1, op2):
    """
    Add two tuples a and b, and return the result
    """
    return tuple(map(operator.add, op1, op2))

def subtract_tuples(op1, op2):
    """
    Subtract two tuples, a - b
    """
    return tuple(map(operator.sub, op1, op2))

def multiply_tuple_with_number(tuple_in, number):
    """
    Make scalar multiplication of tuple t and number n
    """
    return tuple([c * number for c in tuple_in])

def divide_tuple_by_number(tuple_in, number):
    """
    Divide each element of tuple t by number n
    """
    if number == 0:
        return tuple_in
    return tuple([c / number for c in tuple_in])

def set_vector_magnitude(vec, mag):
    """
    Sets magnitude of vector v to mag
    """
    return multiply_tuple_with_number(normalize_vector(vec), mag)

def normalize_vector(vec):
    """
    Make vector normalization for a vector v
    """
    if all(c == 0 for c in vec):
        return vec
    return vec / calc_v_len(vec)

def calc_v_len(vec):
    """
    Returns the magnitude of a vector v
    """
    return np.sqrt(sum([c**2 for c in vec]))

def limit_vector(vec, limit):
    """
    Limits the vector v to a magnitude [limit] if its magnitude is greater than limit
    """
    if calc_v_len(vec) <= limit:
        return vec
    return multiply_tuple_with_number(normalize_vector(vec), limit)

def average_of_tuples(t_list):
    """
    Calculates the average tuple from a list of tuples t_list
    """
    if len(t_list) == 0:
        return (0, 0, 0)
    return tuple([sum(sub_list) / len(sub_list) for sub_list in zip(*t_list)])

### Generic Operator ###
class GenericOperator(bpy.types.Operator):
    """
    Generic Operator to be used as a base for other operators.
    """
    bl_idname = "object.generic_operator"
    bl_label = "Generic Label"

    def __init__(self, method):
        self.method = method

    @classmethod
    def poll(cls, context):
        """Is just a generic function to overwrite

        Args:
            context: the context of the operator
        """
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH')

    def execute(self, _context):
        """Executes the operator

        Args:
            _context: The context of the operator
        """
        self.method(bpy.context.selected_objects)
        return {'FINISHED'}


### Related Operators ###
class AnimateBoidOperator(GenericOperator):
    """
    The operator that starts the animation
    """
    bl_idname = "object.animate_boids"
    bl_label = "Animate Boids"

    def __init__(self):
        super().__init__(BoidDataCore.animate_boids)

class RegisterBoidOperator(GenericOperator):
    """
    The operator that registers boid
    """
    bl_idname = "object.register_boid"
    bl_label = "Register"

    def __init__(self):
        super().__init__(BoidDataCore.add_boids)

class UnregisterBoidOperator(GenericOperator):
    """
    The Operator that removes boids from the list
    """
    bl_idname = "object.unregister_boid"
    bl_label = "Unregister"

    def __init__(self):
        super().__init__(BoidDataCore.remove_boids)

class TestOperator(GenericOperator):
    """
    Debug Operator
    TODO: Remove
    """
    bl_idname = "object.test_boid"
    bl_label = "Test"

    def __init__(self):
        super().__init__(BoidDataCore.generic_method)

    def execute(self, _context):
        print(BoidDataCore.get_boids())
        return {'FINISHED'}


class SelectBoidsOperator(GenericOperator):
    """
    The operator that selects all boids
    """
    bl_idname = "object.select_boids"
    bl_label = "Select Boids"

    def __init__(self):
        super().__init__(BoidDataCore.generic_method)

    def execute(self, _context):
        #Deselect all first
        bpy.ops.object.select_all(action='DESELECT')
        for boid in BoidDataCore.get_boids():
            boid.instance.select_set(True)
        return {'FINISHED'}


class BoidDataCore():
    """
    The Core Class handling all Boid related operations
    """
    _boids = []

    @staticmethod
    def load_data():
        """
        Debug Function
        TODO: Remove
        """
        print("loading")

    @staticmethod
    def get_boids():
        """
        Gets all boids from the _boids Object
        """
        for boid in BoidDataCore._boids:
            try:
                boid.instance.name
            except: # pylint: disable=bare-except
                BoidDataCore._boids.remove(boid)

        return BoidDataCore._boids

    @staticmethod
    def remove_boids(boids):
        """
        Removes the selected boids from the list
        """
        BoidDataCore._boids = [
            boid for boid in BoidDataCore.get_boids() if boid.instance not in boids]

    @staticmethod
    def add_boids(boids):
        """
        Adds the selected boids to the list
        """
        for boid in boids:
            boid_obj = Boid(boid)
            if BoidDataCore.get_boids().count(boid_obj) < 1:
                BoidDataCore._boids.append(boid_obj)

    @staticmethod
    def animate_boids(_b):
        """
        Starts the animation
        """
        scene = bpy.data.scenes["Scene"]
        settings = bpy.context.scene.boid_settings
        for boid in BoidDataCore.get_boids():
            boid.delete_keyframes()
        for frame in range(scene.frame_start, scene.frame_end + 1):
            for boid in BoidDataCore.get_boids():
                boid.update(BoidDataCore.get_boids(), frame, settings)

    def generic_method(self):
        """
        Needed for blender
        """

operators = [
    RegisterBoidOperator,
    UnregisterBoidOperator,
    TestOperator,
    SelectBoidsOperator,
    AnimateBoidOperator]
class BoidUIPanel(bpy.types.Panel):
    """
    Generates the UI for the addon
    """
    bl_label = "Boids"
    bl_idname = "VIEW3D_PT_Boids"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Boids"

    def draw(self, context):
        """
        Generates the layout
        """
        layout = self.layout

        row = layout.row()
        row.label(text="Operators")

        for op in operators:
            row = layout.row()
            row.operator(op.bl_idname)

        row = layout.row()
        row.label(text = "Boid Settings")

        properties = ["max_speed", "max_force", "vision_radius", "cohesion_strength",
                     "alignment_strength", "separation_strength"]
        obj = context.scene.boid_settings

        for prop in properties:
            row = layout.row()
            row.prop(data = obj, property = prop)



def register():
    """
    Registers all operators and classes
    """
    bpy.utils.register_class(BoidSettingValues)
    bpy.types.Scene.boid_settings = bpy.props.PointerProperty(type=BoidSettingValues)
    bpy.utils.register_class(BoidUIPanel)
    for op in operators:
        bpy.utils.register_class(op)

def unregister():
    """
    Unregisters registered classes
    """
    bpy.utils.unregister_class(BoidUIPanel)
    bpy.utils.unregister_class(BoidSettingValues)
    for op in operators:
        bpy.utils.register_class(op)


if __name__ == "__main__":
    try:
        unregister()
    except: # pylint: disable=bare-except
        pass
    register()
