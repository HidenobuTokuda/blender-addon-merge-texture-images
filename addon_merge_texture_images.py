import bpy   # アドオン開発者に対して用意しているAPIを利用する


# アドオンに関する情報を保持する、bl_info変数
bl_info = {
    "name": "Merge texture images",
    "author": "HT",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "Outliner right click menu",
    "description": "Merge texture images of selected objects",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}

def main_merge_texture_images(operator, context):
    
    add_activate_uv_layer(context, new_uv_map_name=operator.new_uv_map_name)
    uv_smart_project_with_margin(image_margin_uv_project=operator.image_margin_uv_project)

    newImage = add_set_activate_image_shader(context, new_texture_name=operator.new_texture_name, image_width=operator.image_width, image_height=operator.image_height)    
    set_do_bake(context, image_margin_bake=operator.image_margin_bake)
    
    remove_old_uv_layers(context, keep_uv_map_name=operator.new_uv_map_name)    
    add_append_link_material(context, newImage, new_material_name=operator.new_material_name, new_texture_name=operator.new_texture_name)
    remove_old_material_slots(context, keep_material_name=operator.new_material_name)
    remove_unused_materials()
    remove_unused_images()
    
    if operator.image_save:
        newImage.save(filepath=f"{operator.new_texture_name}.png")

def add_activate_uv_layer(context, new_uv_map_name="mergedUvMap"):
    for obj in context.selected_objects:
        if new_uv_map_name in obj.data.uv_layers:
            obj.data.uv_layers.remove(obj.data.uv_layers[new_uv_map_name])
            
        new_uv_map = obj.data.uv_layers.new(name=new_uv_map_name)
        new_uv_map.active = True

def uv_smart_project_with_margin(image_margin_uv_project=0.01):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()

    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(margin=image_margin_uv_project)
    bpy.ops.object.mode_set(mode='OBJECT')

def add_set_activate_image_shader(context, new_texture_name="mergedTexture", image_width=1024, image_height=1024):
    newImage = bpy.data.images.new(new_texture_name, image_width, image_height, alpha=True)

    for obj in context.selected_objects:
        for mat_slot in obj.material_slots.values():
            
            mat = mat_slot.material
            
            for node in mat.node_tree.nodes:
                node.select = False
            
            tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex.label = new_texture_name
            tex.name = new_texture_name
            tex.image = newImage
            tex.select = True
            mat.node_tree.nodes.active = tex
            
    return newImage

def set_do_bake(context, image_margin_bake=1):
    context.scene.render.engine = 'CYCLES'
    context.scene.cycles.bake_type = 'DIFFUSE'
    context.scene.render.bake.use_pass_direct = False
    context.scene.render.bake.use_pass_indirect = False
    context.scene.render.bake.margin = image_margin_bake

    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=image_margin_bake, margin_type="ADJACENT_FACES", target='IMAGE_TEXTURES', save_mode='INTERNAL', use_clear=True)

def remove_old_uv_layers(context, keep_uv_map_name="mergedUvMap"):
    for obj in context.selected_objects:
        uv_names = []
        for uv_layer in obj.data.uv_layers:
            if uv_layer.name != keep_uv_map_name:
                uv_names.append(uv_layer.name)

        for uv_name in uv_names:
            obj.data.uv_layers.remove(obj.data.uv_layers[uv_name])

def add_append_link_material(context, newImage, new_material_name="mergedMaterial", new_texture_name="mergedTexture"):
    new_mat = bpy.data.materials.new(new_material_name)
    new_mat.use_nodes = True
    for obj in context.selected_objects:
        obj.data.materials.append(new_mat)
        new_mat_index = obj.material_slots.find(new_material_name)
        obj.active_material_index = new_mat_index
        
    tex = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.label = new_texture_name
    tex.name = new_texture_name
    tex.image = newImage

    new_mat.node_tree.links.new(
        new_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"], 
        tex.outputs["Color"]
    )        
    
def remove_old_material_slots(context, keep_material_name="mergedMaterial"):
    for obj in context.selected_objects:
        mat_indexex_remove = []
        for mat_slot in obj.material_slots.values():
            if mat_slot.material.name != keep_material_name:
                mat_indexex_remove.append(obj.material_slots.find(mat_slot.material.name))
        
        for mat_index_remove in mat_indexex_remove:
            context.view_layer.objects.active = obj    
            obj.active_material_index = mat_index_remove
            bpy.ops.object.material_slot_remove()
    
def remove_unused_materials():
    for material in bpy.data.materials:
        if not material.users:
            bpy.data.materials.remove(material)

def remove_unused_images():
    for image in bpy.data.images:
        if not image.users:
            bpy.data.images.remove(image) 

class MergeTextureImagesOperator(bpy.types.Operator):

    bl_idname = "object.merge_texture_images"
    bl_label = "Merge texture images"
    bl_description = "Merge texture images of selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    new_texture_name: bpy.props.StringProperty(
        name="Texture",
        description="Name of merged texture. This is used for names of image shader and image",
        default="mergedTexture"
    )    
    new_uv_map_name: bpy.props.StringProperty(
        name="UV map",
        description="Name of merged UV map",
        default="mergedUvMap"
    )
    new_material_name: bpy.props.StringProperty(
        name="Material",
        description="Name of merged material",
        default="mergedMaterial"
    )
    image_width: bpy.props.IntProperty(
        name="Width",
        description="Width of merged image",
        subtype="PIXEL",
        min=1,
        soft_min=1,
        max=9999,
        soft_max=9999,
        default=1024
    )
    image_height: bpy.props.IntProperty(
        name="Height",
        description="Height of merged image",
        subtype="PIXEL",
        min=1,
        soft_min=1,
        max=9999,
        soft_max=9999,
        default=1024
    )
    image_margin_uv_project: bpy.props.FloatProperty(
        name="UV projection",
        description="Margin of merged image in UV projection",
        precision=3,
        min=0,
        soft_min=0,
        max=99,
        soft_max=99,
        step=1,
        default=0.01
    )
    image_margin_bake: bpy.props.IntProperty(
        name="Bake",
        description="Margin of merged image in bake",
        subtype="PIXEL",
        min=0,
        soft_min=0,
        max=99,
        soft_max=99,
        default=1
    )
    image_save: bpy.props.BoolProperty(
        name="Save",
        description="If checked, merged image will be saved. File name will be same as name of the merged texture",
        default=False
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="Settings for Merge texture images")    

    def draw(self, context):
        layout = self.layout

        layout.label(text="Name of merged data")
        layout.prop(self, "new_texture_name")
        layout.prop(self, "new_uv_map_name")
        layout.prop(self, "new_material_name")
        
        layout.separator()
        
        layout.label(text="Size of merged image")
        layout.prop(self, "image_width")
        layout.prop(self, "image_height")
        
        layout.separator()
        
        layout.label(text="Margin of image for UV projection and bake")
        layout.prop(self, "image_margin_uv_project")
        layout.prop(self, "image_margin_bake")
        
        layout.separator()
        
        layout.label(text="Save merged image")
        layout.prop(self, "image_save")
    
    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        main_merge_texture_images(self, context)
        return {'FINISHED'}

class RemoveUnusedMaterialsOperator(bpy.types.Operator):

    bl_idname = "object.remove_unused_materials"
    bl_label = "Remove unused materials"
    bl_description = "Remove unused materials"
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        remove_unused_materials()
        return {'FINISHED'}

class RemoveUnusedImagesOperator(bpy.types.Operator):

    bl_idname = "object.remove_unused_images"
    bl_label = "Remove unused images"
    bl_description = "Remove unused images"
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        remove_unused_images()
        return {'FINISHED'}
    
class RemoveUnusedObjectsMenu(bpy.types.Menu):

    bl_idname = "object.remove_unused_objects"
    bl_label = "Remove unused objects"
    bl_description = "Remove unused objects"

    def draw(self, context):
        self.layout.operator(RemoveUnusedMaterialsOperator.bl_idname, text="Materials")
        self.layout.operator(RemoveUnusedImagesOperator.bl_idname, text="Images")
                
# メニューを構築する関数
def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator_context = "INVOKE_DEFAULT"
    self.layout.operator(MergeTextureImagesOperator.bl_idname)
    self.layout.menu(RemoveUnusedObjectsMenu.bl_idname)

# Blenderに登録するクラス
classes = [
    MergeTextureImagesOperator,
    RemoveUnusedMaterialsOperator,
    RemoveUnusedImagesOperator,
    RemoveUnusedObjectsMenu,
]

# アドオン有効化時の処理
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.OUTLINER_MT_object.append(menu_fn)


# アドオン無効化時の処理
def unregister():
    bpy.types.OUTLINER_MT_object.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)


# メイン処理
if __name__ == "__main__":
    register()