bl_info = {
    "name": "Optimize 3D models",
    "author": "HT",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "Outliner right click menu",
    "description": "Collection of right click menus to optimize selected objects. It includes optimizing image files and merge texture images",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}

if "bpy" in locals():
    import imp
    imp.reload(merge_texture_images)
    imp.reload(optim_image_files)
else:
    from . import merge_texture_images
    from . import optim_image_files

import bpy

import os
import glob

try:
    from PIL import Image
except:
    import subprocess, ctypes, sys    

    subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if is_admin():
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True, env=environ_copy)        

    else:
        # Re-run the program with admin rights
        proceed = ctypes.windll.user32.MessageBoxW(0, "If you click 'OK', next screen will ask you to use admin right. If you agree, blender python will install 'Pillow' package.", "Install 'Pillow'",  1)
        if proceed == 1:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(["-m", "pip", "install", "pillow"]), None, 1)
            #ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(["-m", "pip", "uninstall", "pillow"]), None, 1)
            ctypes.windll.user32.MessageBoxW(0, "Wait for the other shell to install 'Pillow'. Once it finished installing, click 'OK'.", "Waiting",  1)
    
    from PIL import Image


def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator_context = "INVOKE_DEFAULT"
    self.layout.operator(optim_image_files.OptimImageFilesOperator.bl_idname)

    self.layout.separator()
    self.layout.operator_context = "INVOKE_DEFAULT"
    self.layout.operator(merge_texture_images.MergeTextureImagesOperator.bl_idname)
    self.layout.menu(merge_texture_images.RemoveUnusedObjectsMenu.bl_idname)

classes = [
    optim_image_files.OptimImageFilesOperator,
    merge_texture_images.MergeTextureImagesOperator,
    merge_texture_images.RemoveUnusedMaterialsOperator,
    merge_texture_images.RemoveUnusedImagesOperator,
    merge_texture_images.RemoveUnusedObjectsMenu,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.OUTLINER_MT_object.append(menu_fn)


def unregister():
    bpy.types.OUTLINER_MT_object.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
   