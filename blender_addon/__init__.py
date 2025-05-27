bl_info = {
    "name": "2D Grease Pencil Animation Plugin",
    "blender": (3, 0, 0),
    "category": "Animation",
    "author": "Your Name",
    "version": (0, 1, 0),
    "description": "Animate Blender skeleton rigs and Grease Pencil with video/camera and lipsync audio input."
}

import bpy

# Import operators, panels, etc. here
from . import operators, panels, utils

def register():
    # Register classes, panels, operators
    panels.register()
    # (Add operators.register() if you add custom operators)

def unregister():
    # Unregister classes, panels, operators
    panels.unregister()
    # (Add operators.unregister() if you add custom operators)

if __name__ == "__main__":
    register() 