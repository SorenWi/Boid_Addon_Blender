from abc import abstractmethod
import operator
import bpy
import numpy as np

class Boid:
    def __init__(self, instance) -> None:
        self.instance = instance
        self.last_pos = (0,0,0)
        self.velocity = (0,0,0)
        self.max_speed = 1
        self.max_force = 0.1
        self.vision_radius = 10
        self.cohesion_strength = 1
        self.alignment_strength = 1
        self.separation_strength = 2
        self.separation_range = 4

    def move(self):
        self.last_pos = tuple(self.instance.location)
        self.instance.location = add_tuples(self.instance.location, self.velocity)
    
    def get_steering_force(self, desired):
        steer = set_vector_magnitude(desired, self.max_speed)
        steer = subtract_tuples(steer, self.velocity)
        steer = limit_vector(steer, self.max_force)

        return steer
    
    def calc_velocity(self):
        """
        Call all rule functions
        """

        if len(self.boids_in_range) == 0:
            return

        cohesion = self.cohesion()
        alignment = self.alignment()
        separation = self.separation()

        self.velocity = add_tuples(cohesion, self.velocity)
        self.velocity = add_tuples(alignment, self.velocity)
        self.velocity = add_tuples(separation, self.velocity)

    
    def add_keyframe(self, frame):
        self.instance.keyframe_insert(data_path="location", frame=frame)

    def calc_boids_in_range(self, all_boids):
        self.boids_in_range = []
        for boid in all_boids:
            distance = calc_v_len(boid.instance.location - self.instance.location)
            if (distance <= self.vision_radius and boid != self):
                self.boids_in_range.append(boid)
    
    def cohesion(self):
        average_location = average_of_tuples([boid.instance.location for boid in self.boids_in_range])
        cohesion_steer = self.get_steering_force(subtract_tuples(average_location, self.instance.location))
        cohesion_steer = multiply_tuple_with_number(cohesion_steer, self.cohesion_strength)

        return cohesion_steer

    def alignment(self):
        average_velocity = average_of_tuples([boid.velocity for boid in self.boids_in_range])
        alignment_steer = self.get_steering_force(average_velocity)
        alignment_steer = multiply_tuple_with_number(alignment_steer, self.alignment_strength)

        return alignment_steer

    def separation(self):     
        average_separation = average_of_tuples([subtract_tuples(self.instance.location, boid.instance.location) for boid in self.boids_in_range])
        separation_steer = self.get_steering_force(average_separation)
        separation_steer = multiply_tuple_with_number(separation_steer, self.separation_strength)

        return separation_steer

    
    def update(self, all_boids, frame):
        self.calc_boids_in_range(all_boids)
        self.add_keyframe(frame)
        self.calc_velocity()
        self.move()
    
    def delete_keyframes(self):
        self.instance.animation_data_clear()

### Helper Functions ###
def add_tuples(a, b):
    """
    Add two tuples a and b, and return the result
    """
    return tuple(map(operator.add, a, b))

def subtract_tuples(a, b):
    """
    Subtract two tuples, a - b
    """
    return tuple(map(operator.sub, a, b))

def multiply_tuple_with_number(t, n):
    """
    Make scalar multiplication of tuple t and number n
    """
    return tuple([c * n for c in t])

def divide_tuple_by_number(t, n):
    """
    Divide each element of tuple t by number n
    """
    if n == 0:
        return t
    return tuple([c / n for c in t])

def set_vector_magnitude(v, mag):
    """
    Sets magnitude of vector v to mag
    """
    return multiply_tuple_with_number(normalize_vector(v), mag)

def normalize_vector(v):
    """
    Make vector normalization for a vector v
    """
    if all(c == 0 for c in v):
        return v
    return v / calc_v_len(v)

def calc_v_len(v):
    """
    Returns the magnitude of a vector v
    """
    return np.sqrt(sum([c**2 for c in v]))

def limit_vector(v, limit):
    """
    Limits the vector v to a magnitude [limit] if its magnitude is greater than limit
    """
    if calc_v_len(v) <= limit:
        return v
    return multiply_tuple_with_number(normalize_vector(v), limit)

def average_of_tuples(t_list):
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
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH')

    def execute(self, context):
        self.method(bpy.context.selected_objects)
        return {'FINISHED'}


### Related Operators ###
class AnimateBoidOperator(GenericOperator):
    bl_idname = "object.animate_boids"
    bl_label = "Animate Boids"

    def __init__(self):
        super().__init__(BoidDataCore.animateBoids)

class RegisterBoidOperator(GenericOperator):
    bl_idname = "object.register_boid"
    bl_label = "Register"

    def __init__(self):
        super().__init__(BoidDataCore.addBoids)

class UnregisterBoidOperator(GenericOperator):
    bl_idname = "object.unregister_boid"
    bl_label = "Unregister"

    def __init__(self):
        super().__init__(BoidDataCore.removeBoids)
  
    
class TestOperator(GenericOperator):
    bl_idname = "object.test_boid"
    bl_label = "Test"

    def __init__(self):
        super().__init__(BoidDataCore.generic_method)

    def execute(self, context):
        print(BoidDataCore.getBoids())
        return {'FINISHED'}


class SelectBoidsOperator(GenericOperator):
    bl_idname = "object.select_boids"
    bl_label = "Select Boids"

    def __init__(self):
        super().__init__(BoidDataCore.generic_method)

    def execute(self, context):
        #Deselect all first
        bpy.ops.object.select_all(action='DESELECT')
        boids = BoidDataCore.boids
        for boid in boids:
            boid.instance.select_set(True)
        return {'FINISHED'}


class BoidDataCore():
    boids = []
    
    def loadData():
        print("loading")
    
    def getBoids():
        return BoidDataCore.boids
    
    def removeBoids(boids):
        for boid in boids:
            b = Boid(boid)
            if BoidDataCore.boids.count(b) > 0:
                BoidDataCore.boids.remove(b)
    
    def addBoids(boids):
        for boid in boids:
            b = Boid(boid)
            if BoidDataCore.boids.count(b) < 1:
                BoidDataCore.boids.append(b)
    
    def animateBoids(_b):
        scene = bpy.data.scenes["Scene"]
        for boid in BoidDataCore.boids:
            boid.delete_keyframes()
        for frame in range(scene.frame_start, scene.frame_end + 1):
            for boid in BoidDataCore.boids:
                boid.update(BoidDataCore.boids, frame)

    @abstractmethod
    def generic_method():
        pass
            

operators = [RegisterBoidOperator, UnregisterBoidOperator, TestOperator, SelectBoidsOperator, AnimateBoidOperator]
class BoidUIPanel(bpy.types.Panel):
    bl_label = "Boids"
    bl_idname = "VIEW3D_PT_Boids"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Boids"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Operators")

        for op in operators:
            row = layout.row()
            row.operator(op.bl_idname)



def register():
    bpy.utils.register_class(BoidUIPanel)
    for op in operators:
        bpy.utils.register_class(op)


def unregister():
    bpy.utils.unregister_class(BoidUIPanel)
    for op in operators:
        bpy.utils.register_class(op)


if __name__ == "__main__":
    register()
