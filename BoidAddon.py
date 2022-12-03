from abc import abstractmethod
import bpy

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
        super().__init__(BoidDataCore.addBoids)

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
            if BoidDataCore.boids.count(boid) > 0:
                BoidDataCore.boids.remove(boid)
    
    def addBoids(boids):
        for boid in boids:
            if BoidDataCore.boids.count(boid) < 1:
                BoidDataCore.boids.append(boid)
    
    def setBoids(boids):
        BoidDataCore.boids = boids 
    
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
