import bpy
import os
import glob
from PIL import Image

# try:
    # from PIL import Image
# except:
    # import subprocess, ctypes, sys    

    # subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    # environ_copy = dict(os.environ)
    # environ_copy["PYTHONNOUSERSITE"] = "1"

    # def is_admin():
        # try:
            # return ctypes.windll.shell32.IsUserAnAdmin()
        # except:
            # return False

    # if is_admin():
        # subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True, env=environ_copy)        

    # else:
    #    Re-run the program with admin rights
        # proceed = ctypes.windll.user32.MessageBoxW(0, "If you click 'OK', next screen will ask you to use admin right. If you agree, blender python will install 'Pillow' package.", "Install 'Pillow'",  1)
        # if proceed == 1:
            # ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(["-m", "pip", "install", "pillow"]), None, 1)
    #        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(["-m", "pip", "uninstall", "pillow"]), None, 1)
            # ctypes.windll.user32.MessageBoxW(0, "Wait for the other shell to install 'Pillow'. Once it finished installing, click 'OK'.", "Waiting",  1)
    
    # from PIL import Image

# bl_info = {
    # "name": "Optimize images",
    # "author": "HT",
    # "version": (1, 0),
    # "blender": (4, 1, 0),
    # "location": "Outliner right click menu",
    # "description": "Optimize images of selected objects and save them in a specified folder",
    # "warning": "",
    # "support": "COMMUNITY",
    # "doc_url": "",
    # "tracker_url": "",
    # "category": "Object"
# }

def main_optim_image_files(operator, context):
    materials = mk_set_mats_of_sel_obs(context)
    images = mk_set_imgs_of_mats(materials)
    
    optim_cpath_img(images, operator.img_dir, operator.use_subfolder, operator.skip_img)

def mk_set_mats_of_sel_obs(context):
    materials = set()

    for obj in context.selected_objects:
        for mat_slot in obj.material_slots.values():
            materials.add(mat_slot.material)

    return materials

def mk_set_imgs_of_mats(materials):
    images = set()

    for mat in materials:
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                images.add(node.image)

    return images

def optim_cpath_img(images, img_dir, use_subfolder, skip_img):
    img_dir_prev = ""
    for image in images:
        image_fullpath = image.filepath
        image_filename = image_fullpath.split("\\")[-1]
        img_dir_new = img_dir + image_fullpath.split("\\")[-2] + "\\" if use_subfolder else img_dir
        
        if use_subfolder and (img_dir_new!=img_dir_prev):
            os.makedirs(img_dir_new, exist_ok=True)

        if skip_img and (len(glob.glob(img_dir_new + image_filename))>=1):
            pass
        else:
            img_dat = Image.open(image_fullpath)
            if image.file_format == "PNG":
                img_dat = img_dat.convert("P", palette=Image.ADAPTIVE, colors=256)
            img_dat.save(img_dir_new + image_filename, optimize=True, quality=60)
            
        image.filepath = img_dir_new + image_filename
        
        img_dir_prev = img_dir_new
                               
class OptimImageFilesOperator(bpy.types.Operator):

    bl_idname = "object.optim_image_files"
    bl_label = "Optimize image files"
    bl_description = "Optimize image files of selected objects and save them in a speficied folder"
    bl_options = {'REGISTER', 'UNDO'}
    
    img_dir: bpy.props.StringProperty(
        name="Folder",
        description="Folder to save new image files.",
        subtype="DIR_PATH"
    )
    use_subfolder: bpy.props.BoolProperty(
        name="Use subfolder",
        description="Use subfolder for image files. If checked, subfolders will be automatically created under the folder above",
        default=True
    )
    skip_img: bpy.props.BoolProperty(
        name="Skip already optimized images",
        description="If checked, it will skip images that are already saved in the folder above. If materials refer to image files in a different folder, it will change the reference to image files in the folder above.",
        default=True
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="Settings for optim image files")    

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "img_dir")
        layout.prop(self, "use_subfolder")
        layout.prop(self, "skip_img")
    
    def execute(self, context):
        main_optim_image_files(self, context)
        return {'FINISHED'}
 
# def menu_fn(self, context):
    # self.layout.separator()
    # self.layout.operator_context = "INVOKE_DEFAULT"
    # self.layout.operator(OptimImageFilesOperator.bl_idname)

# classes = [
    # OptimImageFilesOperator,
# ]

# def register():
    # for c in classes:
        # bpy.utils.register_class(c)
    # bpy.types.OUTLINER_MT_object.append(menu_fn)


# def unregister():
    # bpy.types.OUTLINER_MT_object.remove(menu_fn)
    # for c in classes:
        # bpy.utils.unregister_class(c)

# if __name__ == "__main__":
    # register()