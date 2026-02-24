bl_info = {
    "name": "RGB Mask Tools",
    "author": "Aleksandr Panichevskii",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Material > My Tools",
    "description": "Автоматизация импорта и настройки шейдера для рисования RGB маске по 4 тайловым сетам: подготовка UV0_Base, UV1_Tiled, смешивание 4 тайловых сетов по RGB-маске, автозагрузка пар _a/_n с валидацией и восстановление материала.",
    "category": "Material",
}

import bpy
import os
from bpy_extras.io_utils import ImportHelper

# --- НАСТРОЙКИ ---
SOURCE_MATERIAL_NAME = "Layered_Mat" 
BLEND_FILE_NAME = "LayeredShader.blend"
REQUIRED_UV = ["UV0_Base", "UV1_Tiled"]
CORE_NAMES = ["Albedo", "Metallic", "Roughness", "Normal"]
EXTENSIONS = {".png", ".jpg", ".tga", ".exr", ".jpeg", ".bmp"}

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def is_already_loaded(filepath):
    abs_path = bpy.path.abspath(filepath)
    for img in bpy.data.images:
        if img.filepath and bpy.path.abspath(img.filepath) == abs_path:
            return True
    return False

def get_smart_image(filepath):
    abs_path = bpy.path.abspath(filepath)
    img = None
    for i in bpy.data.images:
        if i.filepath and bpy.path.abspath(i.filepath) == abs_path:
            i.reload()
            img = i
            break
    if not img:
        img = bpy.data.images.load(filepath, check_existing=True)
    if bpy.data.is_saved:
        try: img.filepath = bpy.path.relpath(img.filepath)
        except ValueError: pass
    return img

# --- ФУНКЦИИ ОБНОВЛЕНИЯ НОД ---

def update_invert_node(mat, node_name, value):
    if mat and mat.node_tree:
        node = mat.node_tree.nodes.get(node_name)
        if node and node.type == 'INVERT':
            node.inputs[0].default_value = 1.0 if value else 0.0

def update_base_n(self, context): update_invert_node(self, "BaseNormal_Invert", self.invert_base_n)
def update_n0(self, context): update_invert_node(self, "Normal0_Invert", self.invert_n0)
def update_n1(self, context): update_invert_node(self, "Normal1_Invert", self.invert_n1)
def update_n2(self, context): update_invert_node(self, "Normal2_Invert", self.invert_n2)
def update_n3(self, context): update_invert_node(self, "Normal3_Invert", self.invert_n3)

# --- ОПЕРАТОРЫ ---

class MATERIAL_OT_SetupAndImport(bpy.types.Operator):
    bl_idname = "material.setup_and_import"
    bl_label = "Подготовить модель к рисованию" 
    bl_description = "Полная очистка и пересоздание структуры материала и UV"
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Выберите меш-объект")
            return {'CANCELLED'}

        mesh = obj.data
        for i, name in enumerate(REQUIRED_UV):
            if len(mesh.uv_layers) <= i: mesh.uv_layers.new(name=name)
            else: mesh.uv_layers[i].name = name

        existing_mat = bpy.data.materials.get(SOURCE_MATERIAL_NAME)
        if existing_mat:
            bpy.data.materials.remove(existing_mat, do_unlink=True)

        for img in bpy.data.images:
            if img.name not in ["Render Result", "Viewer Node"]:

                #img.use_fake_user = False

                img.user_clear() 

        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = None

        images_to_remove = [img for img in bpy.data.images if img.users == 0]
        for img in images_to_remove:
            if img.name not in ["Render Result", "Viewer Node"]:
                bpy.data.images.remove(img)

        script_dir = os.path.dirname(__file__)
        library_path = os.path.join(script_dir, BLEND_FILE_NAME)

        if not os.path.exists(library_path):
            self.report({'ERROR'}, f"Файл {BLEND_FILE_NAME} не найден!")
            return {'CANCELLED'}

        with bpy.data.libraries.load(library_path, link=False) as (data_from, data_to):
            if SOURCE_MATERIAL_NAME in data_from.materials:
                data_to.materials = [SOURCE_MATERIAL_NAME]
            else:
                self.report({'ERROR'}, f"Материал {SOURCE_MATERIAL_NAME} не найден!")
                return {'CANCELLED'}

        new_mat = data_to.materials[0]
        if mesh.materials: mesh.materials[0] = new_mat
        else: mesh.materials.append(new_mat)

        return {'FINISHED'}

class MATERIAL_OT_LoadTextureSet(bpy.types.Operator, ImportHelper):
    bl_idname = "material.load_texture_set"
    bl_label = "Выбрать Albedo (_a)"
    index: bpy.props.IntProperty(options={'HIDDEN'})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*_a.*;*_A.*", options={'HIDDEN'})

    def execute(self, context):
        if is_already_loaded(self.filepath):
            self.report({'ERROR'}, "Эта текстура уже загружена!")
            return {'CANCELLED'}
        
        mat = context.material
        directory = os.path.dirname(self.filepath)
        name_part, ext = os.path.splitext(os.path.basename(self.filepath))
        base_name = name_part[:-2] if name_part.lower().endswith('_a') else name_part
        path_n = os.path.join(directory, base_name + "_n" + ext)
        
        if not os.path.exists(path_n):
            self.report({'ERROR'}, f"Файл нормалей '{base_name}_n{ext}' не найден!")
            return {'CANCELLED'}

        node_a = mat.node_tree.nodes.get(f"Tex_Albedo{self.index}")
        if node_a: node_a.image = get_smart_image(self.filepath)
        
        img_n = get_smart_image(path_n)
        img_n.colorspace_settings.name = 'Non-Color'
        node_n = mat.node_tree.nodes.get(f"Tex_Normal{self.index}")
        if node_n: node_n.image = img_n
        return {'FINISHED'}

class MATERIAL_OT_LoadSingleCore(bpy.types.Operator, ImportHelper):
    bl_idname = "material.load_single_core"
    bl_label = "Выбрать текстуру"
    node_name: bpy.props.StringProperty()
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if is_already_loaded(self.filepath):
            self.report({'ERROR'}, "Текстура уже в проекте!")
            return {'CANCELLED'}
        mat = context.material
        node = mat.node_tree.nodes.get(self.node_name)
        if node:
            img = get_smart_image(self.filepath)
            if self.node_name != "Albedo": img.colorspace_settings.name = 'Non-Color'
            node.image = img
        return {'FINISHED'}

class MATERIAL_OT_CreateRGBMask(bpy.types.Operator):
    bl_idname = "material.create_rgb_mask"
    bl_label = "Создать RGB маску"
    bl_description = "Текстура с именем 'Mask_MESHNAME' по которой нужно рисовать маски"
    def execute(self, context):
        mat = context.material
        mask_node = mat.node_tree.nodes.get("RGB_Mask")
        if mask_node and not mask_node.image:
            new_img = bpy.data.images.new(name=f"Mask_{context.active_object.name}", width=2048, height=2048, alpha=True)
            new_img.generated_color = (0, 0, 0, 1)
            mask_node.image = new_img
        return {'FINISHED'}

class MATERIAL_OT_LoadCoreFolder(bpy.types.Operator):
    bl_idname = "material.load_core_folder"
    bl_label = "Загрузить папку текстур"
    bl_description = "Ожидается что в папке будут текстуры с именами Albedo, Normal, Metallic, Roughness"
    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    def execute(self, context):
        mat = context.material
        files = os.listdir(self.directory)
        for target in CORE_NAMES:
            node = mat.node_tree.nodes.get(target)
            if not node: continue
            for f in files:
                name, ext = os.path.splitext(f)
                full_path = os.path.join(self.directory, f)
                if name.lower() == target.lower() and ext.lower() in EXTENSIONS:
                    if not is_already_loaded(full_path):
                        img = get_smart_image(full_path)
                        if target != "Albedo": img.colorspace_settings.name = 'Non-Color'
                        node.image = img
                    break
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# --- ИНТЕРФЕЙС ПАНЕЛИ ---

class MATERIAL_PT_CustomShaderPanel(bpy.types.Panel):
    bl_label = "RGB Mask Tools"
    bl_idname = "MATERIAL_PT_custom_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        mat = context.material
        if not bpy.data.is_saved:
            layout.alert = True
            layout.label(text="SAVE FILE for relative paths!", icon='ERROR')
        
        col = layout.column(align=True)
        col.operator("material.setup_and_import", icon='FILE_REFRESH')
        col.operator("material.create_rgb_mask", icon='BRUSH_DATA')
        
        if not mat or not mat.node_tree: return
        
        # --- CORE TEXTURES ---
        layout.separator()
        box = layout.box()
        box.label(text="Core Textures (Base)", icon='NODE_MATERIAL')
        box.operator("material.load_core_folder", icon='FILEBROWSER')
        
        for name in CORE_NAMES:
            row = box.row(align=True)
            node = mat.node_tree.nodes.get(name)
            if node:
                row.prop(node, "image", text=name)
                op = row.operator("material.load_single_core", icon='FILE_REFRESH', text="")
                op.node_name = name
                if name == "Normal":
                    row = box.row()
                    row.prop(mat, "invert_base_n", text="Invert Normal (G)", icon='UV_SYNC_SELECT')
        
        # --- BASE SCALE ---
        base_scale_node = mat.node_tree.nodes.get("BaseScale")
        if base_scale_node:
            sep = box.separator()
            split = box.split(factor=0.3)
            split.label(text="Base Scale:")
            row = split.row(align=True)
            row.prop(base_scale_node.inputs[3], "default_value", index=0, text="X")
            row.prop(base_scale_node.inputs[3], "default_value", index=1, text="Y")

        # --- RGB MASK ---
        mask_node = mat.node_tree.nodes.get("RGB_Mask")
        if mask_node:
            box = layout.box()
            box.label(text="RGB Mask Texture", icon='IMAGE_DATA')
            box.prop(mask_node, "image", text="")

        # --- LAYERED TEXTURES ---
        layout.separator()
        layout.label(text="Layered Tiled Textures")
        for i in range(4):
            box = layout.box()
            row = box.row()
            row.label(text=f"Слой {i}", icon='TEXTURE')
            op = row.operator("material.load_texture_set", icon='FILEBROWSER', text="Загрузить сет")
            op.index = i
            node_a = mat.node_tree.nodes.get(f"Tex_Albedo{i}")
            if node_a: box.prop(node_a, "image", text="")
            row = box.row()
            row.prop(mat, f"invert_n{i}", text="Invert Normal (G)", icon='UV_SYNC_SELECT')
            
            node_m = mat.node_tree.nodes.get(f"Set{i}")
            if node_m and len(node_m.inputs) > 3:
                split = box.split(factor=0.3)
                split.label(text="Tile Scale:")
                row = split.row(align=True)
                row.prop(node_m.inputs[3], "default_value", index=0, text="X")
                row.prop(node_m.inputs[3], "default_value", index=1, text="Y")

# --- РЕГИСТРАЦИЯ ---

classes = (
    MATERIAL_OT_SetupAndImport, 
    MATERIAL_OT_CreateRGBMask, 
    MATERIAL_OT_LoadTextureSet, 
    MATERIAL_OT_LoadCoreFolder,
    MATERIAL_OT_LoadSingleCore,
    MATERIAL_PT_CustomShaderPanel
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Material.invert_base_n = bpy.props.BoolProperty(name="Invert Base Normal G", update=update_base_n)
    for i in range(4):
        setattr(bpy.types.Material, f"invert_n{i}", bpy.props.BoolProperty(name=f"Invert Normal {i} G", update=globals()[f"update_n{i}"]))

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Material.invert_base_n
    for i in range(4): delattr(bpy.types.Material, f"invert_n{i}")

if __name__ == "__main__":
    register()