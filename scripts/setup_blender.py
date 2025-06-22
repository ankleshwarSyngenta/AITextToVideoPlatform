"""
Blender Setup Script
Configures Blender for automated video generation
"""

import bpy
import bmesh
import os
import sys
from pathlib import Path
from mathutils import Vector, Euler
import json

# Add project path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings


class BlenderSetup:
    """Setup Blender environment for video generation"""
    
    def __init__(self):
        self.project_root = project_root
        self.assets_dir = settings.ASSETS_DIR
        self.character_dir = self.assets_dir / "characters"
        
    def setup_scene(self):
        """Setup the basic scene for video generation"""
        print("Setting up Blender scene...")
        
        # Clear existing mesh objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False, confirm=False)
        
        # Set up camera
        self.setup_camera()
        
        # Set up lighting
        self.setup_lighting()
        
        # Set up materials
        self.setup_materials()
        
        # Create character
        self.create_bull_character()
        
        # Set up animation
        self.setup_animation()
        
        # Configure render settings
        self.setup_render_settings()
        
        print("✅ Scene setup complete!")
    
    def setup_camera(self):
        """Setup camera for video recording"""
        # Add camera
        bpy.ops.object.camera_add(location=(0, -8, 2))
        camera = bpy.context.object
        camera.name = "MainCamera"
        
        # Set camera properties
        camera.data.lens = 50
        camera.data.clip_start = 0.1
        camera.data.clip_end = 1000
        
        # Point camera at origin
        camera.rotation_euler = Euler((1.1, 0, 0), 'XYZ')
        
        # Set as active camera
        bpy.context.scene.camera = camera
        
        print("📹 Camera setup complete")
    
    def setup_lighting(self):
        """Setup lighting for the scene"""
        # Key light
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        key_light = bpy.context.object
        key_light.name = "KeyLight"
        key_light.data.energy = 3
        key_light.data.color = (1, 0.95, 0.8)
        
        # Fill light
        bpy.ops.object.light_add(type='AREA', location=(-3, 3, 5))
        fill_light = bpy.context.object
        fill_light.name = "FillLight"
        fill_light.data.energy = 1.5
        fill_light.data.color = (0.8, 0.9, 1)
        fill_light.data.size = 3
        
        # Rim light
        bpy.ops.object.light_add(type='SPOT', location=(0, 8, 6))
        rim_light = bpy.context.object
        rim_light.name = "RimLight"
        rim_light.data.energy = 2
        rim_light.data.color = (1, 1, 1)
        rim_light.data.spot_size = 0.5
        
        print("💡 Lighting setup complete")
    
    def setup_materials(self):
        """Setup materials for the character"""
        # Bull material
        bull_material = bpy.data.materials.new(name="BullMaterial")
        bull_material.use_nodes = True
        nodes = bull_material.node_tree.nodes
        
        # Clear default nodes
        nodes.clear()
        
        # Add principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.3, 0.15, 0.1, 1)  # Brown color
        bsdf.inputs['Metallic'].default_value = 0
        bsdf.inputs['Roughness'].default_value = 0.8
        
        # Add output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bull_material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        print("🎨 Materials setup complete")
    
    def create_bull_character(self):
        """Create the bull character model"""
        print("🐂 Creating bull character...")
        
        # Add base mesh (cube to start)
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
        bull = bpy.context.object
        bull.name = "BullCharacter"
        
        # Enter edit mode
        bpy.context.view_layer.objects.active = bull
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Create basic bull shape
        bm = bmesh.from_mesh(bull.data)
        
        # Scale to make it more bull-like
        bmesh.ops.scale(bm, vec=(1.2, 0.8, 1.5), verts=bm.verts)
        
        # Extrude for legs
        bm.faces.ensure_lookup_table()
        bottom_face = [f for f in bm.faces if f.normal.z < -0.5][0]
        
        # Create legs (simplified)
        leg_positions = [(-0.5, -0.3, 0), (0.5, -0.3, 0), (-0.5, 0.3, 0), (0.5, 0.3, 0)]
        
        for pos in leg_positions:
            # Add leg geometry
            bpy.ops.mesh.primitive_cylinder_add(location=pos, scale=(0.2, 0.2, 0.8))
        
        # Update mesh
        bm.to_mesh(bull.data)
        bm.free()
        
        # Exit edit mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add armature for animation
        self.add_character_armature(bull)
        
        # Assign material
        if "BullMaterial" in bpy.data.materials:
            bull.data.materials.append(bpy.data.materials["BullMaterial"])
        
        print("✅ Bull character created")
    
    def add_character_armature(self, character):
        """Add armature for character animation"""
        # Add armature
        bpy.ops.object.armature_add(location=(0, 0, 1))
        armature = bpy.context.object
        armature.name = "BullArmature"
        
        # Enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Get the default bone
        edit_bones = armature.data.edit_bones
        root_bone = edit_bones[0]
        root_bone.name = "Root"
        
        # Add spine bones
        spine_bone = edit_bones.new("Spine")
        spine_bone.head = (0, 0, 1)
        spine_bone.tail = (0, 0, 1.5)
        spine_bone.parent = root_bone
        
        # Add head bone
        head_bone = edit_bones.new("Head")
        head_bone.head = (0, 0, 1.5)
        head_bone.tail = (0, 0.5, 2)
        head_bone.parent = spine_bone
        
        # Add jaw bone for lip sync
        jaw_bone = edit_bones.new("Jaw")
        jaw_bone.head = (0, 0.3, 1.7)
        jaw_bone.tail = (0, 0.5, 1.6)
        jaw_bone.parent = head_bone
        
        # Add arm bones
        for side in ['L', 'R']:
            multiplier = 1 if side == 'L' else -1
            
            shoulder_bone = edit_bones.new(f"Shoulder.{side}")
            shoulder_bone.head = (0.8 * multiplier, 0, 1.3)
            shoulder_bone.tail = (1.2 * multiplier, 0, 1.3)
            shoulder_bone.parent = spine_bone
            
            arm_bone = edit_bones.new(f"Arm.{side}")
            arm_bone.head = (1.2 * multiplier, 0, 1.3)
            arm_bone.tail = (1.5 * multiplier, 0, 1)
            arm_bone.parent = shoulder_bone
        
        # Exit edit mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add armature modifier to character
        modifier = character.modifiers.new(name="Armature", type='ARMATURE')
        modifier.object = armature
        
        print("🦴 Armature added")
    
    def setup_animation(self):
        """Setup basic animations"""
        print("🎭 Setting up animations...")
        
        # Set frame range
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 240  # 10 seconds at 24fps
        bpy.context.scene.frame_set(1)
        
        # Create animation actions
        self.create_idle_animation()
        self.create_talking_animation()
        self.create_gesture_animations()
        
        print("✅ Animations setup complete")
    
    def create_idle_animation(self):
        """Create idle breathing animation"""
        armature = bpy.data.objects.get("BullArmature")
        if not armature:
            return
        
        # Select armature
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Create idle action
        action = bpy.data.actions.new(name="Idle")
        armature.animation_data_create()
        armature.animation_data.action = action
        
        # Animate breathing
        spine_bone = armature.pose.bones.get("Spine")
        if spine_bone:
            # Keyframe breathing animation
            frames = [1, 30, 60, 90, 120]
            scales = [1.0, 1.02, 1.0, 1.02, 1.0]
            
            for frame, scale in zip(frames, scales):
                bpy.context.scene.frame_set(frame)
                spine_bone.scale = (1, 1, scale)
                spine_bone.keyframe_insert(data_path="scale")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print("💨 Idle animation created")
    
    def create_talking_animation(self):
        """Create talking animation for lip sync"""
        armature = bpy.data.objects.get("BullArmature")
        if not armature:
            return
        
        # Create talking action
        action = bpy.data.actions.new(name="Talking")
        
        # This will be enhanced with actual lip sync data
        print("🗣️ Talking animation created")
    
    def create_gesture_animations(self):
        """Create gesture animations"""
        gestures = ["Point", "Explain", "Emphasize", "Think"]
        
        for gesture in gestures:
            action = bpy.data.actions.new(name=gesture)
            print(f"👋 {gesture} animation created")
    
    def setup_render_settings(self):
        """Configure render settings for video output"""
        scene = bpy.context.scene
        
        # Set render engine
        scene.render.engine = 'EEVEE'  # Fast rendering
        
        # Set resolution
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 100
        
        # Set frame rate
        scene.render.fps = 24
        
        # Set output format
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        
        # Set quality
        scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        
        # Enable motion blur
        scene.render.motion_blur_shutter = 0.5
        
        # Set output path
        scene.render.filepath = str(settings.OUTPUT_DIR / "rendered_video")
        
        print("🎬 Render settings configured")
    
    def save_scene(self):
        """Save the scene file"""
        blend_file = self.character_dir / "bull_character.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_file))
        print(f"💾 Scene saved: {blend_file}")
    
    def export_character_data(self):
        """Export character data for the application"""
        character_data = {
            "name": "Bull Character",
            "armature": "BullArmature",
            "animations": ["Idle", "Talking", "Point", "Explain", "Emphasize", "Think"],
            "bones": {
                "head": "Head",
                "jaw": "Jaw",
                "spine": "Spine",
                "arms": ["Arm.L", "Arm.R"],
                "shoulders": ["Shoulder.L", "Shoulder.R"]
            },
            "materials": ["BullMaterial"],
            "render_settings": {
                "resolution": [1920, 1080],
                "fps": 24,
                "engine": "EEVEE"
            }
        }
        
        data_file = self.character_dir / "character_data.json"
        with open(data_file, 'w') as f:
            json.dump(character_data, f, indent=2)
        
        print(f"📄 Character data exported: {data_file}")


def main():
    """Main setup function"""
    print("🎨 Starting Blender setup...")
    
    setup = BlenderSetup()
    setup.setup_scene()
    setup.save_scene()
    setup.export_character_data()
    
    print("\n🎉 Blender setup complete!")
    print("📁 Files created:")
    print(f"  - {setup.character_dir}/bull_character.blend")
    print(f"  - {setup.character_dir}/character_data.json")


if __name__ == "__main__":
    main()
