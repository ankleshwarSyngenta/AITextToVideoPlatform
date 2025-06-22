"""
Animation Engine Module
Handles 3D character animation and lip-sync for text-to-video generation
"""

import bpy
import bmesh
import mathutils
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import json
import wave
import struct
from loguru import logger


@dataclass
class AnimationCue:
    """Animation cue data structure"""
    timestamp: float
    duration: float
    animation_type: str
    intensity: float
    parameters: Dict[str, Any]


@dataclass
class LipSyncData:
    """Lip-sync data structure"""
    phonemes: List[str]
    timestamps: List[float]
    intensities: List[float]
    mouth_shapes: List[str]


class BlenderAnimationEngine:
    """3D Animation engine using Blender Python API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.character_model = None
        self.scene = None
        self.animation_data = {}
        self.lip_sync_data = None
        
        # Animation parameters
        self.frame_rate = config.get('frame_rate', 24)
        self.scene_duration = 0
        
        # Phoneme to mouth shape mapping
        self.phoneme_mapping = {
            'A': 'A', 'E': 'E', 'I': 'I', 'O': 'O', 'U': 'U',
            'B': 'M', 'P': 'M', 'M': 'M',
            'F': 'F', 'V': 'F',
            'TH': 'TH', 'S': 'S', 'Z': 'S',
            'L': 'L', 'R': 'L',
            'T': 'T', 'D': 'T', 'N': 'T',
            'K': 'K', 'G': 'K',
            'SILENCE': 'CLOSED'
        }
        
        self._setup_blender_scene()
    
    def _setup_blender_scene(self):
        """Initialize Blender scene for animation"""
        try:
            # Clear existing scene
            bpy.ops.wm.read_factory_settings(use_empty=True)
            
            # Set up scene properties
            scene = bpy.context.scene
            scene.frame_set(1)
            scene.frame_start = 1
            scene.render.fps = self.frame_rate
            
            # Add lighting
            self._setup_lighting()
            
            # Add camera
            self._setup_camera()
            
            # Load or create character model
            self._load_character_model()
            
            self.scene = scene
            logger.info("Blender scene initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Blender scene: {e}")
            raise
    
    def _setup_lighting(self):
        """Setup scene lighting"""
        # Add sun light
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.object
        sun.data.energy = 3.0
        sun.name = "Sun_Main"
        
        # Add fill light
        bpy.ops.object.light_add(type='AREA', location=(-5, 5, 8))
        fill_light = bpy.context.object
        fill_light.data.energy = 1.5
        fill_light.name = "Fill_Light"
        
        # Add rim light
        bpy.ops.object.light_add(type='SPOT', location=(0, -8, 6))
        rim_light = bpy.context.object
        rim_light.data.energy = 2.0
        rim_light.name = "Rim_Light"
    
    def _setup_camera(self):
        """Setup scene camera"""
        bpy.ops.object.camera_add(location=(0, -8, 2))
        camera = bpy.context.object
        camera.name = "Main_Camera"
        
        # Set camera as active
        bpy.context.scene.camera = camera
        
        # Configure camera settings
        camera.data.lens = 50
        camera.data.sensor_width = 36
        
        # Look at origin
        camera.rotation_euler = (1.1, 0, 0)
    
    def _load_character_model(self):
        """Load or create the 3D bull character model"""
        try:
            # Try to load existing model
            model_path = Path(self.config.get('character_model_path', ''))
            
            if model_path.exists() and model_path.suffix.lower() in ['.blend', '.fbx', '.obj']:
                self._import_character_model(model_path)
            else:
                # Create basic bull character
                self._create_basic_bull_character()
                
        except Exception as e:
            logger.warning(f"Failed to load character model: {e}, creating basic model")
            self._create_basic_bull_character()
    
    def _import_character_model(self, model_path: Path):
        """Import character model from file"""
        if model_path.suffix.lower() == '.blend':
            # Import from Blender file
            with bpy.data.libraries.load(str(model_path)) as (data_from, data_to):
                data_to.objects = data_from.objects
            
            # Link objects to scene
            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.collection.objects.link(obj)
                    if 'bull' in obj.name.lower() or 'character' in obj.name.lower():
                        self.character_model = obj
                        
        elif model_path.suffix.lower() == '.fbx':
            bpy.ops.import_scene.fbx(filepath=str(model_path))
            # Find the imported character
            for obj in bpy.context.selected_objects:
                if obj.type == 'MESH':
                    self.character_model = obj
                    break
                    
        elif model_path.suffix.lower() == '.obj':
            bpy.ops.import_scene.obj(filepath=str(model_path))
            for obj in bpy.context.selected_objects:
                if obj.type == 'MESH':
                    self.character_model = obj
                    break
    
    def _create_basic_bull_character(self):
        """Create a basic bull character using Blender primitives"""
        # Create body (cylinder)
        bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3, location=(0, 0, 1))
        body = bpy.context.object
        body.name = "Bull_Body"
        body.scale = (1.2, 0.8, 1.0)
        
        # Create head (sphere)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 3.5))
        head = bpy.context.object
        head.name = "Bull_Head"
        head.scale = (1.2, 1.0, 0.8)
        
        # Create horns
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, radius2=0.02, vertices=8, depth=0.8, location=(-0.5, 0, 4.2))
        horn1 = bpy.context.object
        horn1.name = "Bull_Horn_L"
        horn1.rotation_euler = (0, 0.3, 0)
        
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, radius2=0.02, vertices=8, depth=0.8, location=(0.5, 0, 4.2))
        horn2 = bpy.context.object
        horn2.name = "Bull_Horn_R"
        horn2.rotation_euler = (0, -0.3, 0)
        
        # Create legs
        leg_positions = [(-0.8, -0.5, -0.5), (0.8, -0.5, -0.5), (-0.8, 0.5, -0.5), (0.8, 0.5, -0.5)]
        for i, pos in enumerate(leg_positions):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.5, location=pos)
            leg = bpy.context.object
            leg.name = f"Bull_Leg_{i+1}"
        
        # Create eyes
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(-0.3, -0.8, 3.7))
        eye1 = bpy.context.object
        eye1.name = "Bull_Eye_L"
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0.3, -0.8, 3.7))
        eye2 = bpy.context.object
        eye2.name = "Bull_Eye_R"
        
        # Create nose/snout
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(0, -1.0, 3.2))
        snout = bpy.context.object
        snout.name = "Bull_Snout"
        snout.rotation_euler = (1.57, 0, 0)  # Rotate 90 degrees
        
        # Parent all parts to head for easier animation
        head.select_set(True)
        bpy.context.view_layer.objects.active = head
        
        # Select all bull parts
        bull_parts = [body, horn1, horn2, eye1, eye2, snout]
        for part in bull_parts:
            part.select_set(True)
        
        # Parent to head
        bpy.ops.object.parent_set(type='OBJECT')
        
        # Set the head as the main character model
        self.character_model = head
        
        # Add materials
        self._add_character_materials()
        
        logger.info("Basic bull character created")
    
    def _add_character_materials(self):
        """Add materials to the character"""
        # Bull brown material
        bull_material = bpy.data.materials.new(name="Bull_Brown")
        bull_material.use_nodes = True
        bull_material.node_tree.clear()
        
        # Add nodes
        bsdf = bull_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        output = bull_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        
        # Set brown color
        bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8
        
        # Connect nodes
        bull_material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Apply to bull objects
        for obj in bpy.data.objects:
            if obj.name.startswith('Bull_') and obj.type == 'MESH':
                if obj.data.materials:
                    obj.data.materials[0] = bull_material
                else:
                    obj.data.materials.append(bull_material)
    
    def generate_lip_sync_data(self, audio_file: str, phonemes: List[str], timestamps: List[float]) -> LipSyncData:
        """Generate lip-sync data from audio analysis"""
        try:
            # Analyze audio for lip-sync
            mouth_shapes = []
            intensities = []
            
            for phoneme in phonemes:
                # Map phoneme to mouth shape
                mouth_shape = self.phoneme_mapping.get(phoneme, 'CLOSED')
                mouth_shapes.append(mouth_shape)
                
                # Calculate intensity based on phoneme type
                if phoneme in ['A', 'E', 'I', 'O', 'U']:
                    intensity = 0.8  # High intensity for vowels
                elif phoneme == 'SILENCE':
                    intensity = 0.0
                else:
                    intensity = 0.6  # Medium intensity for consonants
                
                intensities.append(intensity)
            
            return LipSyncData(
                phonemes=phonemes,
                timestamps=timestamps,
                intensities=intensities,
                mouth_shapes=mouth_shapes
            )
            
        except Exception as e:
            logger.error(f"Failed to generate lip-sync data: {e}")
            raise
    
    def animate_character(self, animation_cues: List[AnimationCue], lip_sync_data: LipSyncData, duration: float):
        """Animate the character based on cues and lip-sync data"""
        try:
            if not self.character_model:
                raise ValueError("No character model loaded")
            
            # Set animation duration
            self.scene_duration = duration
            end_frame = int(duration * self.frame_rate)
            bpy.context.scene.frame_end = end_frame
            
            # Clear existing animations
            self._clear_animations()
            
            # Apply lip-sync animation
            self._animate_lip_sync(lip_sync_data)
            
            # Apply gesture animations
            self._animate_gestures(animation_cues)
            
            # Apply idle animation
            self._animate_idle_motion()
            
            logger.info(f"Character animation completed for {duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to animate character: {e}")
            raise
    
    def _clear_animations(self):
        """Clear existing animations"""
        for obj in bpy.data.objects:
            if obj.animation_data:
                obj.animation_data.action = None
    
    def _animate_lip_sync(self, lip_sync_data: LipSyncData):
        """Animate lip-sync based on phoneme data"""
        if not lip_sync_data or not self.character_model:
            return
        
        # Find the snout/mouth object
        mouth_obj = None
        for obj in bpy.data.objects:
            if 'snout' in obj.name.lower() or 'mouth' in obj.name.lower():
                mouth_obj = obj
                break
        
        if not mouth_obj:
            logger.warning("No mouth object found for lip-sync")
            return
        
        # Create action for mouth animation
        if not mouth_obj.animation_data:
            mouth_obj.animation_data_create()
        
        action = bpy.data.actions.new(name="Lip_Sync")
        mouth_obj.animation_data.action = action
        
        # Create fcurves for mouth animation
        scale_y_curve = action.fcurves.new(data_path="scale", index=1)  # Y-scale
        scale_z_curve = action.fcurves.new(data_path="scale", index=2)  # Z-scale
        
        # Animate based on phonemes
        for i, (timestamp, mouth_shape, intensity) in enumerate(zip(
            lip_sync_data.timestamps, lip_sync_data.mouth_shapes, lip_sync_data.intensities
        )):
            frame = int(timestamp * self.frame_rate)
            
            # Calculate mouth shape parameters
            if mouth_shape in ['A', 'O']:
                y_scale = 1.0 + (intensity * 0.5)  # Open mouth
                z_scale = 1.0 + (intensity * 0.3)
            elif mouth_shape in ['E', 'I']:
                y_scale = 1.0 + (intensity * 0.3)  # Slightly open
                z_scale = 1.0 - (intensity * 0.2)
            elif mouth_shape == 'M':
                y_scale = 1.0 - (intensity * 0.2)  # Closed mouth
                z_scale = 1.0
            else:  # Default/CLOSED
                y_scale = 1.0
                z_scale = 1.0
            
            # Insert keyframes
            scale_y_curve.keyframe_points.insert(frame, y_scale)
            scale_z_curve.keyframe_points.insert(frame, z_scale)
        
        # Set interpolation mode
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'
    
    def _animate_gestures(self, animation_cues: List[AnimationCue]):
        """Animate character gestures based on animation cues"""
        if not self.character_model or not animation_cues:
            return
        
        # Create action for gesture animation
        if not self.character_model.animation_data:
            self.character_model.animation_data_create()
        
        action = bpy.data.actions.new(name="Gestures")
        self.character_model.animation_data.action = action
        
        # Create fcurves for rotation
        rotation_x_curve = action.fcurves.new(data_path="rotation_euler", index=0)
        rotation_y_curve = action.fcurves.new(data_path="rotation_euler", index=1)
        rotation_z_curve = action.fcurves.new(data_path="rotation_euler", index=2)
        
        for cue in animation_cues:
            start_frame = int(cue.timestamp * self.frame_rate)
            end_frame = int((cue.timestamp + cue.duration) * self.frame_rate)
            
            # Apply animation based on type
            if cue.animation_type == 'pointing':
                self._add_pointing_gesture(rotation_y_curve, start_frame, end_frame, cue.intensity)
            elif cue.animation_type == 'emphasis':
                self._add_emphasis_gesture(rotation_x_curve, start_frame, end_frame, cue.intensity)
            elif cue.animation_type == 'questioning':
                self._add_questioning_gesture(rotation_z_curve, start_frame, end_frame, cue.intensity)
            elif cue.animation_type == 'thinking':
                self._add_thinking_gesture(rotation_x_curve, rotation_y_curve, start_frame, end_frame, cue.intensity)
        
        # Set interpolation mode
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'
    
    def _add_pointing_gesture(self, rotation_curve, start_frame: int, end_frame: int, intensity: float):
        """Add pointing gesture animation"""
        mid_frame = (start_frame + end_frame) // 2
        
        # Keyframes: start -> peak -> end
        rotation_curve.keyframe_points.insert(start_frame, 0)
        rotation_curve.keyframe_points.insert(mid_frame, intensity * 0.3)  # 0.3 radians
        rotation_curve.keyframe_points.insert(end_frame, 0)
    
    def _add_emphasis_gesture(self, rotation_curve, start_frame: int, end_frame: int, intensity: float):
        """Add emphasis gesture animation"""
        mid_frame = (start_frame + end_frame) // 2
        
        # Keyframes: start -> peak -> end
        rotation_curve.keyframe_points.insert(start_frame, 0)
        rotation_curve.keyframe_points.insert(mid_frame, intensity * -0.2)  # Slight nod
        rotation_curve.keyframe_points.insert(end_frame, 0)
    
    def _add_questioning_gesture(self, rotation_curve, start_frame: int, end_frame: int, intensity: float):
        """Add questioning gesture animation"""
        mid_frame = (start_frame + end_frame) // 2
        
        # Keyframes: start -> tilt -> end
        rotation_curve.keyframe_points.insert(start_frame, 0)
        rotation_curve.keyframe_points.insert(mid_frame, intensity * 0.2)  # Head tilt
        rotation_curve.keyframe_points.insert(end_frame, 0)
    
    def _add_thinking_gesture(self, rotation_x_curve, rotation_y_curve, start_frame: int, end_frame: int, intensity: float):
        """Add thinking gesture animation"""
        quarter_frame = start_frame + (end_frame - start_frame) // 4
        mid_frame = (start_frame + end_frame) // 2
        three_quarter_frame = start_frame + 3 * (end_frame - start_frame) // 4
        
        # Slow head movement for thinking
        rotation_x_curve.keyframe_points.insert(start_frame, 0)
        rotation_x_curve.keyframe_points.insert(quarter_frame, intensity * -0.1)
        rotation_x_curve.keyframe_points.insert(mid_frame, 0)
        rotation_x_curve.keyframe_points.insert(three_quarter_frame, intensity * 0.1)
        rotation_x_curve.keyframe_points.insert(end_frame, 0)
        
        rotation_y_curve.keyframe_points.insert(start_frame, 0)
        rotation_y_curve.keyframe_points.insert(quarter_frame, intensity * 0.15)
        rotation_y_curve.keyframe_points.insert(mid_frame, 0)
        rotation_y_curve.keyframe_points.insert(three_quarter_frame, intensity * -0.15)
        rotation_y_curve.keyframe_points.insert(end_frame, 0)
    
    def _animate_idle_motion(self):
        """Add subtle idle animation for natural movement"""
        if not self.character_model:
            return
        
        # Add breathing animation
        if not self.character_model.animation_data:
            self.character_model.animation_data_create()
        
        if not self.character_model.animation_data.action:
            self.character_model.animation_data.action = bpy.data.actions.new(name="Idle")
        
        action = self.character_model.animation_data.action
        
        # Create breathing cycle (scale animation)
        scale_curve = action.fcurves.new(data_path="scale", index=2)  # Z-scale
        
        breathing_cycle = 4.0  # 4 seconds per breath
        end_frame = int(self.scene_duration * self.frame_rate)
        
        for frame in range(1, end_frame, int(breathing_cycle * self.frame_rate)):
            # Breathe in
            scale_curve.keyframe_points.insert(frame, 1.0)
            scale_curve.keyframe_points.insert(frame + int(breathing_cycle * self.frame_rate / 2), 1.05)
            scale_curve.keyframe_points.insert(frame + int(breathing_cycle * self.frame_rate), 1.0)
        
        # Set interpolation mode
        for keyframe in scale_curve.keyframe_points:
            keyframe.interpolation = 'BEZIER'
    
    def export_animation(self, output_path: str, format: str = 'fbx') -> str:
        """Export the animated scene"""
        try:
            output_file = Path(output_path)
            
            if format.lower() == 'fbx':
                bpy.ops.export_scene.fbx(
                    filepath=str(output_file.with_suffix('.fbx')),
                    use_selection=False,
                    bake_anim=True,
                    bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=True,
                    bake_anim_use_all_actions=True
                )
            elif format.lower() == 'blend':
                bpy.ops.wm.save_as_mainfile(filepath=str(output_file.with_suffix('.blend')))
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Animation exported to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to export animation: {e}")
            raise


def create_animation_engine(config: Dict[str, Any]) -> BlenderAnimationEngine:
    """Factory function to create animation engine"""
    return BlenderAnimationEngine(config)
