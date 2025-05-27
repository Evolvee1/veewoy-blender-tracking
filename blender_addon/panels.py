# panels.py
# Define custom Blender UI panels for the add-on here.

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup
from . import utils
import threading
import websocket
import time

class ImportDataProperties(PropertyGroup):
    keypoints_path: StringProperty(
        name="Keypoints JSON",
        description="Path to keypoints.json file",
        subtype='FILE_PATH'
    )
    phonemes_path: StringProperty(
        name="Phonemes JSON",
        description="Path to phonemes.json file",
        subtype='FILE_PATH'
    )

class IMPORT_OT_load_data(Operator):
    bl_idname = "import.load_data"
    bl_label = "Import Animation Data"
    bl_description = "Load keypoints and phoneme data for animation"

    def execute(self, context):
        props = context.scene.import_data_props
        try:
            keypoints = utils.load_keypoints_json(props.keypoints_path)
            phonemes = utils.load_phonemes_json(props.phonemes_path)
            self.report({'INFO'}, f"Loaded {len(keypoints)} frames and {len(phonemes)} phoneme entries.")
            # Store or process data as needed (e.g., attach to scene, cache, etc.)
            context.scene.keypoints_data = keypoints
            context.scene.phonemes_data = phonemes
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load data: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}

class IMPORT_PT_data_panel(Panel):
    bl_label = "Animation Data Import"
    bl_idname = "IMPORT_PT_data_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '2D Animation'

    def draw(self, context):
        layout = self.layout
        props = context.scene.import_data_props
        layout.prop(props, "keypoints_path")
        layout.prop(props, "phonemes_path")
        layout.operator("import.load_data", text="Import Data")

class LiveLinkProperties(PropertyGroup):
    link_status: StringProperty(
        name="Link Status",
        description="Current status of the live link",
        default="Disconnected"
    )
    is_connected: BoolProperty(
        name="Is Connected",
        description="Is the live link connected?",
        default=False
    )
    ws_url: StringProperty(
        name="WebSocket URL",
        description="WebSocket server URL",
        default="ws://localhost:8765"
    )

class LIVELINK_OT_toggle_link(Operator):
    bl_idname = "livelink.toggle_link"
    bl_label = "Connect/Disconnect Live Link"
    bl_description = "Connect or disconnect to the live link WebSocket server"

    _ws_thread = None
    _ws = None

    def execute(self, context):
        props = context.scene.livelink_props
        if not props.is_connected:
            # Connect
            def ws_thread_func():
                try:
                    props.link_status = "Connecting..."
                    self._ws = websocket.WebSocket()
                    self._ws.connect(props.ws_url)
                    props.is_connected = True
                    props.link_status = "Connected"
                    while props.is_connected:
                        msg = self._ws.recv()
                        # For now, just print or store the message
                        print(f"Received: {msg}")
                        time.sleep(0.01)
                except Exception as e:
                    props.link_status = f"Error: {e}"
                    props.is_connected = False
                finally:
                    if self._ws:
                        self._ws.close()
                    props.link_status = "Disconnected"
                    props.is_connected = False
            self._ws_thread = threading.Thread(target=ws_thread_func, daemon=True)
            self._ws_thread.start()
        else:
            # Disconnect
            props.is_connected = False
            props.link_status = "Disconnecting..."
        return {'FINISHED'}

class LIVELINK_PT_panel(Panel):
    bl_label = "Live Link"
    bl_idname = "LIVELINK_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '2D Animation'

    def draw(self, context):
        layout = self.layout
        props = context.scene.livelink_props
        layout.label(text=f"Status: {props.link_status}")
        layout.prop(props, "ws_url")
        layout.operator("livelink.toggle_link", text=("Disconnect" if props.is_connected else "Connect"))

def register():
    bpy.utils.register_class(ImportDataProperties)
    bpy.utils.register_class(IMPORT_OT_load_data)
    bpy.utils.register_class(IMPORT_PT_data_panel)
    bpy.utils.register_class(LiveLinkProperties)
    bpy.utils.register_class(LIVELINK_OT_toggle_link)
    bpy.utils.register_class(LIVELINK_PT_panel)
    bpy.types.Scene.import_data_props = bpy.props.PointerProperty(type=ImportDataProperties)
    bpy.types.Scene.livelink_props = bpy.props.PointerProperty(type=LiveLinkProperties)

def unregister():
    bpy.utils.unregister_class(ImportDataProperties)
    bpy.utils.unregister_class(IMPORT_OT_load_data)
    bpy.utils.unregister_class(IMPORT_PT_data_panel)
    bpy.utils.unregister_class(LiveLinkProperties)
    bpy.utils.unregister_class(LIVELINK_OT_toggle_link)
    bpy.utils.unregister_class(LIVELINK_PT_panel)
    del bpy.types.Scene.import_data_props
    del bpy.types.Scene.livelink_props 