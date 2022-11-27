import bpy

class RegisterBoidOperator(bpy.types.Operator):
    bl_idname = "object.register_boid"
    bl_label = "Register"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH')

    def execute(self, context):
        BoidDataCore.addBoids(bpy.context.selected_objects)
        return {'FINISHED'}


class UnregisterBoidOperator(bpy.types.Operator):
    bl_idname = "object.unregister_boid"
    bl_label = "Unregister"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH')

    def execute(self, context):
        BoidDataCore.removeBoids(bpy.context.selected_objects)
        
        return {'FINISHED'}
  
    
class TestOperator(bpy.types.Operator):
    bl_idname = "object.test_boid"
    bl_label = "Test"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.type == 'MESH')

    def execute(self, context):
        print(BoidDataCore.getBoids())
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
        
        row = layout.row()
        row.operator(RegisterBoidOperator.bl_idname)
        
        row = layout.row()
        row.operator(UnregisterBoidOperator.bl_idname)
        
        row = layout.row()
        row.operator(TestOperator.bl_idname)


def register():
    bpy.utils.register_class(BoidUIPanel)
    bpy.utils.register_class(RegisterBoidOperator)
    bpy.utils.register_class(UnregisterBoidOperator)
    bpy.utils.register_class(TestOperator)


def unregister():
    bpy.utils.unregister_class(BoidUIPanel)
    bpy.utils.unregister_class(RegisterBoidOperator)
    bpy.utils.unregister_class(UnregisterBoidOperator)
    bpy.utils.unregister_class(TestOperator)


if __name__ == "__main__":
    register()
