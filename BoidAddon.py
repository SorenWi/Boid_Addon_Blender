from abc import abstractmethod
import operator
import bpy
import numpy as np

class Boid:
    def __init__(self, instance) -> None:
        self.instance = instance
        self.last_pos = (0,0,0)
        self.velocity = (0,1,0)
        self.max_speed = 1
        self.max_force = 0.1
    
    def move(self):
        self.last_pos = tuple(self.instance.location)
        self.instance.location = add_tuples(self.instance.location, self.velocity)
    
    def apply_steering_force(self, desired):
        des_limted = limit_vector(desired, self.max_speed)
        steer_v = subtract_tuples(des_limted, self.velocity)
        steer_f = limit_vector(steer_v, self.max_force)
        self.velocity = limit_vector(add_tuples(self.velocity, steer_f), self.max_speed)
    
    def calc_velocity(self):
        """
        Call all rule functions
        """
        self.apply_steering_force((1, 0, 0))
    
    def add_keyframe(self, frame):
        self.instance.keyframe_insert(data_path="location", frame=frame)
    
    def update(self, boids, frame):
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
            boid.select_set(True)
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
