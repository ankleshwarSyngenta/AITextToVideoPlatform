"""
Video Renderer Module
Handles video generation, compositing, and effects for text-to-video platform
"""

import cv2
import numpy as np
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import json
import wave
import threading
import time
from loguru import logger


@dataclass
class VideoConfig:
    """Video configuration settings"""
    width: int = 1920
    height: int = 1080
    fps: int = 24
    bitrate: str = "5000k"
    codec: str = "h264"
    format: str = "mp4"
    quality: str = "high"


@dataclass
class RenderJob:
    """Render job configuration"""
    scenes: List[str]
    audio_file: str
    output_path: str
    effects: List[Dict[str, Any]]
    transitions: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class VideoRenderer:
    """Advanced video renderer with effects and compositing"""
    
    def __init__(self, config: VideoConfig):
        self.config = config
        self.temp_dir = Path(tempfile.mkdtemp(prefix="video_render_"))
        self.render_progress = 0.0
        self.render_status = "idle"
        
        # Video processing tools
        self.ffmpeg_path = self._find_ffmpeg()
        self.blender_path = self._find_blender()
        
        # Effects and transitions
        self._setup_effects_library()
        
        logger.info(f"VideoRenderer initialized with {config.width}x{config.height}@{config.fps}fps")
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg installation"""
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning("FFmpeg not found in PATH")
                return None
        except Exception as e:
            logger.warning(f"Failed to find FFmpeg: {e}")
            return None
    
    def _find_blender(self) -> Optional[str]:
        """Find Blender installation"""
        try:
            result = subprocess.run(['which', 'blender'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning("Blender not found in PATH")
                return None
        except Exception as e:
            logger.warning(f"Failed to find Blender: {e}")
            return None
    
    def _setup_effects_library(self):
        """Setup video effects library"""
        self.effects = {
            'fade_in': self._apply_fade_in,
            'fade_out': self._apply_fade_out,
            'zoom_in': self._apply_zoom_in,
            'zoom_out': self._apply_zoom_out,
            'pan_left': self._apply_pan_left,
            'pan_right': self._apply_pan_right,
            'blur': self._apply_blur,
            'sharpen': self._apply_sharpen,
            'color_correction': self._apply_color_correction,
            'vignette': self._apply_vignette
        }
        
        self.transitions = {
            'crossfade': self._transition_crossfade,
            'wipe': self._transition_wipe,
            'slide': self._transition_slide,
            'fade': self._transition_fade
        }
    
    def render_from_blender(self, blend_file: str, audio_file: str, output_path: str, 
                          effects: Optional[List[Dict[str, Any]]] = None) -> str:
        """Render video from Blender animation file"""
        try:
            self.render_status = "rendering"
            self.render_progress = 0.0
            
            logger.info(f"Starting Blender render: {blend_file}")
            
            # Create temporary directory for frames
            frames_dir = self.temp_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            
            # Render frames from Blender
            self._render_blender_frames(blend_file, frames_dir)
            
            # Apply post-processing effects
            if effects:
                self._apply_post_effects(frames_dir, effects)
            
            # Combine frames with audio
            final_video = self._combine_frames_and_audio(frames_dir, audio_file, output_path)
            
            self.render_status = "completed"
            self.render_progress = 100.0
            
            logger.info(f"Video render completed: {final_video}")
            return final_video
            
        except Exception as e:
            self.render_status = "failed"
            logger.error(f"Render failed: {e}")
            raise
    
    def _render_blender_frames(self, blend_file: str, output_dir: Path):
        """Render frames from Blender file"""
        if not self.blender_path:
            raise RuntimeError("Blender not found. Please install Blender.")
        
        try:
            # Blender command to render frames
            cmd = [
                self.blender_path,
                "--background",
                blend_file,
                "--render-output", str(output_dir / "frame_"),
                "--render-format", "PNG",
                "--render-anim"
            ]
            
            logger.info(f"Running Blender render: {' '.join(cmd)}")
            
            # Run Blender with progress tracking
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress
            self._monitor_blender_progress(process)
            
            # Wait for completion
            process.wait()
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                raise RuntimeError(f"Blender render failed: {stderr}")
            
            logger.info("Blender frames rendered successfully")
            
        except Exception as e:
            logger.error(f"Failed to render Blender frames: {e}")
            raise
    
    def _monitor_blender_progress(self, process):
        """Monitor Blender render progress"""
        def read_output():
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Parse Blender output for progress
                if "Fra:" in line:
                    try:
                        # Extract frame number
                        parts = line.split()
                        frame_idx = parts.index("Fra:") + 1
                        if frame_idx < len(parts):
                            frame_num = int(parts[frame_idx])
                            # Estimate progress (assuming 0-50% for Blender render)
                            self.render_progress = min(50.0, frame_num / 100.0 * 50.0)
                    except (ValueError, IndexError):
                        pass
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=read_output)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _apply_post_effects(self, frames_dir: Path, effects: List[Dict[str, Any]]):
        """Apply post-processing effects to rendered frames"""
        frame_files = sorted(list(frames_dir.glob("*.png")))
        
        if not frame_files:
            logger.warning("No frames found for post-processing")
            return
        
        logger.info(f"Applying effects to {len(frame_files)} frames")
        
        for i, frame_file in enumerate(frame_files):
            # Load frame
            frame = cv2.imread(str(frame_file))
            if frame is None:
                continue
            
            # Apply effects
            for effect in effects:
                effect_type = effect.get('type')
                if effect_type in self.effects:
                    frame = self.effects[effect_type](frame, effect.get('params', {}))
            
            # Save processed frame
            cv2.imwrite(str(frame_file), frame)
            
            # Update progress (50-80% for effects)
            self.render_progress = 50.0 + (i / len(frame_files)) * 30.0
    
    def _combine_frames_and_audio(self, frames_dir: Path, audio_file: str, output_path: str) -> str:
        """Combine rendered frames with audio using FFmpeg"""
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
        
        try:
            frame_pattern = str(frames_dir / "frame_%04d.png")
            
            # FFmpeg command to combine frames and audio
            cmd = [
                self.ffmpeg_path,
                "-y",  # Overwrite output
                "-framerate", str(self.config.fps),
                "-i", frame_pattern,
                "-i", audio_file,
                "-c:v", self.config.codec,
                "-b:v", self.config.bitrate,
                "-c:a", "aac",
                "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-shortest",  # Match shortest stream
                output_path
            ]
            
            logger.info(f"Running FFmpeg: {' '.join(cmd)}")
            
            # Run FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor FFmpeg progress
            self._monitor_ffmpeg_progress(process)
            
            # Wait for completion
            process.wait()
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                raise RuntimeError(f"FFmpeg failed: {stderr}")
            
            # Update progress to 100%
            self.render_progress = 100.0
            
            logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to combine frames and audio: {e}")
            raise
    
    def _monitor_ffmpeg_progress(self, process):
        """Monitor FFmpeg progress"""
        def read_output():
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                
                # Parse FFmpeg output for progress
                if "frame=" in line:
                    try:
                        # Extract frame number
                        frame_part = line.split("frame=")[1].split()[0]
                        frame_num = int(frame_part)
                        # Estimate progress (80-100% for FFmpeg)
                        self.render_progress = 80.0 + min(20.0, frame_num / 100.0 * 20.0)
                    except (ValueError, IndexError):
                        pass
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=read_output)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def create_slideshow_video(self, images: List[str], audio_file: str, output_path: str,
                             duration_per_image: float = 3.0) -> str:
        """Create a slideshow video from images"""
        try:
            self.render_status = "rendering"
            self.render_progress = 0.0
            
            if not self.ffmpeg_path:
                raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
            
            # Validate inputs
            if not images:
                raise ValueError("No images provided for slideshow")
            
            for image in images:
                if not os.path.exists(image):
                    raise FileNotFoundError(f"Image not found: {image}")
            
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Create input file list for FFmpeg
            input_file = self.temp_dir / "input_list.txt"
            with open(input_file, 'w') as f:
                for image in images:
                    # Use absolute path
                    abs_image_path = os.path.abspath(image)
                    f.write(f"file '{abs_image_path}'\n")
                    f.write(f"duration {duration_per_image}\n")
                # Add last image again for proper ending
                if images:
                    abs_last_image = os.path.abspath(images[-1])
                    f.write(f"file '{abs_last_image}'\n")
            
            logger.info(f"Input list created: {input_file}")
            
            # Verify input file content
            with open(input_file, 'r') as f:
                logger.debug(f"Input file content:\n{f.read()}")
            
            # FFmpeg command for slideshow
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(input_file),
                "-i", audio_file,
                "-c:v", self.config.codec,
                "-b:v", self.config.bitrate,
                "-c:a", "aac",
                "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-vf", f"scale={self.config.width}:{self.config.height}",
                "-shortest",
                output_path
            ]
            
            logger.info(f"Creating slideshow: {' '.join(cmd)}")
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg stdout: {result.stdout}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                raise RuntimeError(f"FFmpeg slideshow failed: {result.stderr}")
            
            self.render_status = "completed"
            self.render_progress = 100.0
            
            logger.info(f"Slideshow created: {output_path}")
            return output_path
            
        except Exception as e:
            self.render_status = "failed"
            logger.error(f"Slideshow creation failed: {e}")
            raise
    
    def add_text_overlay(self, video_path: str, text_overlays: List[Dict[str, Any]], 
                        output_path: str) -> str:
        """Add text overlays to video"""
        try:
            if not self.ffmpeg_path:
                raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
            
            # Build filter complex for text overlays
            filters = []
            input_label = "0:v"
            
            for i, overlay in enumerate(text_overlays):
                text = overlay.get('text', '')
                start_time = overlay.get('start_time', 0)
                duration = overlay.get('duration', 5)
                font_size = overlay.get('font_size', 24)
                color = overlay.get('color', 'white')
                position = overlay.get('position', 'bottom')
                
                # Position mapping
                pos_map = {
                    'top': '(w-text_w)/2:50',
                    'bottom': '(w-text_w)/2:h-100',
                    'center': '(w-text_w)/2:(h-text_h)/2',
                    'top-left': '50:50',
                    'top-right': 'w-text_w-50:50',
                    'bottom-left': '50:h-100',
                    'bottom-right': 'w-text_w-50:h-100'
                }
                
                xy = pos_map.get(position, '(w-text_w)/2:h-100')
                
                # Create drawtext filter
                filter_str = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={color}:" \
                           f"x={xy}:enable='between(t,{start_time},{start_time + duration})'"
                
                output_label = f"overlay{i}"
                filters.append(f"[{input_label}]{filter_str}[{output_label}]")
                input_label = output_label
            
            filter_complex = ";".join(filters)
            
            # FFmpeg command with text overlays
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", video_path,
                "-filter_complex", filter_complex,
                "-map", f"[{input_label}]",
                "-map", "0:a",
                "-c:a", "copy",
                output_path
            ]
            
            logger.info(f"Adding text overlays: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Text overlay failed: {result.stderr}")
            
            logger.info(f"Text overlays added: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to add text overlays: {e}")
            raise
    
    # Effect implementation methods
    def _apply_fade_in(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply fade in effect"""
        alpha = params.get('alpha', 0.5)
        faded = frame.astype(np.float32) * alpha
        return faded.astype(np.uint8)
    
    def _apply_fade_out(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply fade out effect"""
        alpha = params.get('alpha', 0.5)
        faded = frame.astype(np.float32) * (1.0 - alpha)
        return faded.astype(np.uint8)
    
    def _apply_zoom_in(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply zoom in effect"""
        zoom_factor = params.get('zoom_factor', 1.2)
        h, w = frame.shape[:2]
        
        # Calculate crop area
        new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
        y_start = (h - new_h) // 2
        x_start = (w - new_w) // 2
        
        # Crop and resize
        cropped = frame[y_start:y_start + new_h, x_start:x_start + new_w]
        zoomed = cv2.resize(cropped, (w, h))
        
        return zoomed
    
    def _apply_zoom_out(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply zoom out effect"""
        zoom_factor = params.get('zoom_factor', 0.8)
        h, w = frame.shape[:2]
        
        # Resize smaller
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        resized = cv2.resize(frame, (new_w, new_h))
        
        # Create black background
        result = np.zeros_like(frame)
        
        # Center the resized frame
        y_start = (h - new_h) // 2
        x_start = (w - new_w) // 2
        result[y_start:y_start + new_h, x_start:x_start + new_w] = resized
        
        return result
    
    def _apply_pan_left(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply pan left effect"""
        offset = params.get('offset', 50)
        h, w = frame.shape[:2]
        
        # Create transformation matrix
        M = np.float32([[1, 0, -offset], [0, 1, 0]])
        panned = cv2.warpAffine(frame, M, (w, h))
        
        return panned
    
    def _apply_pan_right(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply pan right effect"""
        offset = params.get('offset', 50)
        h, w = frame.shape[:2]
        
        # Create transformation matrix
        M = np.float32([[1, 0, offset], [0, 1, 0]])
        panned = cv2.warpAffine(frame, M, (w, h))
        
        return panned
    
    def _apply_blur(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply blur effect"""
        kernel_size = params.get('kernel_size', 15)
        if kernel_size % 2 == 0:
            kernel_size += 1  # Ensure odd number
        
        blurred = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        return blurred
    
    def _apply_sharpen(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply sharpen effect"""
        strength = params.get('strength', 1.0)
        
        # Sharpen kernel
        kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]]) * strength
        
        sharpened = cv2.filter2D(frame, -1, kernel)
        return sharpened
    
    def _apply_color_correction(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply color correction"""
        brightness = params.get('brightness', 0)
        contrast = params.get('contrast', 1.0)
        saturation = params.get('saturation', 1.0)
        
        # Apply brightness and contrast
        corrected = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
        
        # Apply saturation
        if saturation != 1.0:
            hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] *= saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            corrected = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return corrected
    
    def _apply_vignette(self, frame: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply vignette effect"""
        strength = params.get('strength', 0.5)
        h, w = frame.shape[:2]
        
        # Create vignette mask
        center_x, center_y = w // 2, h // 2
        max_radius = np.sqrt(center_x**2 + center_y**2)
        
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Normalize distance
        distance = distance / max_radius
        
        # Create vignette
        vignette = 1 - (distance * strength)
        vignette = np.clip(vignette, 0, 1)
        
        # Apply vignette
        result = frame.astype(np.float32)
        for i in range(frame.shape[2]):
            result[:, :, i] *= vignette
        
        return result.astype(np.uint8)
    
    # Transition implementation methods
    def _transition_crossfade(self, frame1: np.ndarray, frame2: np.ndarray, 
                            progress: float) -> np.ndarray:
        """Crossfade transition"""
        alpha = progress
        result = frame1.astype(np.float32) * (1 - alpha) + frame2.astype(np.float32) * alpha
        return result.astype(np.uint8)
    
    def _transition_wipe(self, frame1: np.ndarray, frame2: np.ndarray, 
                       progress: float) -> np.ndarray:
        """Wipe transition"""
        h, w = frame1.shape[:2]
        split_x = int(w * progress)
        
        result = frame1.copy()
        result[:, :split_x] = frame2[:, :split_x]
        
        return result
    
    def _transition_slide(self, frame1: np.ndarray, frame2: np.ndarray, 
                        progress: float) -> np.ndarray:
        """Slide transition"""
        h, w = frame1.shape[:2]
        offset = int(w * progress)
        
        result = np.zeros_like(frame1)
        
        # Slide frame1 out
        if offset < w:
            result[:, offset:] = frame1[:, :w-offset]
        
        # Slide frame2 in
        if offset > 0:
            result[:, :offset] = frame2[:, w-offset:]
        
        return result
    
    def _transition_fade(self, frame1: np.ndarray, frame2: np.ndarray, 
                       progress: float) -> np.ndarray:
        """Fade transition"""
        if progress < 0.5:
            # Fade out frame1
            alpha = 1 - (progress * 2)
            result = frame1.astype(np.float32) * alpha
        else:
            # Fade in frame2
            alpha = (progress - 0.5) * 2
            result = frame2.astype(np.float32) * alpha
        
        return result.astype(np.uint8)
    
    def get_render_progress(self) -> Tuple[float, str]:
        """Get current render progress"""
        return self.render_progress, self.render_status
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files: {e}")


def create_video_renderer(config: Dict[str, Any]) -> VideoRenderer:
    """Factory function to create video renderer"""
    video_config = VideoConfig(
        width=config.get('width', 1920),
        height=config.get('height', 1080),
        fps=config.get('fps', 24),
        bitrate=config.get('bitrate', '5000k'),
        codec=config.get('codec', 'h264'),
        format=config.get('format', 'mp4'),
        quality=config.get('quality', 'high')
    )
    
    return VideoRenderer(video_config)
