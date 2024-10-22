from PIL import Image, ImageFilter
import numpy as np
import moviepy.video.io.ImageSequenceClip
from .bezier import UnitBezier, bezier_progress
from .timeline import parse_timeline

class Editor:
    def __init__(self, width, height, fps=30, bgcolor=(0, 0, 0)):
        """
        Initialize the Editor with video parameters.
        
        :param width: Width of the video in pixels.
        :param height: Height of the video in pixels.
        :param fps: Frames per second (default is 30).
        :param bgcolor: Background color of the video (default is black).
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.bgcolor = bgcolor
        self.frames = []
        self.image_cache = {}

    def load_timeline(self, timeline):
        """
        Load and parse the timeline for the video.
        
        :param timeline: List of timeline dictionaries, defining the video structure and effects.
        """
        self.frames = parse_timeline(timeline)

    def apply_effects(self, img, effects):
        """
        Apply effects such as scale, blur, and rotation to an image.
        
        :param img: PIL image to apply effects on.
        :param effects: Dictionary of effects to apply (scale, blur, rotate).
        :return: The transformed image.
        """
        # Apply scaling
        if 'scale' in effects and effects['scale'] != 1:
            scale = effects['scale']
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        # Apply blur
        if 'blur' in effects:
            img = img.filter(ImageFilter.GaussianBlur(radius=effects['blur']))

        # Apply rotation
        if 'rotate' in effects:
            img = img.rotate(effects['rotate'], expand=True)

        return img

    def render_frame(self, frame_assets):
        """
        Render a single frame by compositing all assets on the background.
        
        :param frame_assets: List of assets to be composited on the frame.
        :return: A NumPy array representing the rendered frame.
        """
        # Create the base background image for the frame
        base_bg = Image.new("RGB", (self.width, self.height), self.bgcolor)
        
        # Process each asset in the frame
        for asset in frame_assets:
            # Load image (with caching for performance)
            src = asset['src']
            if src not in self.image_cache:
                img = Image.open(src)
                self.image_cache[src] = img
            else:
                img = self.image_cache[src]

            # Apply any effects
            img = self.apply_effects(img, asset)

            # Paste the image onto the background at the specified position
            base_bg.paste(img, asset['pos'], img if img.mode == 'RGBA' else None)

        return np.array(base_bg)

    def render_video(self, output_file):
        """
        Render the entire video based on the parsed timeline frames.
        
        :param output_file: Path to the output video file.
        """
        rendered_frames = []

        # Render each frame in sequence
        for frame in self.frames:
            frame_assets = frame  # Each 'frame' contains all assets for that frame
            rendered_frame = self.render_frame(frame_assets)
            rendered_frames.append(rendered_frame)

        # Create video clip from rendered frames
        movie_clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(rendered_frames, fps=self.fps)
        movie_clip.write_videofile(output_file)

    def clear_cache(self):
        """Clear the cached images to free up memory."""
        self.image_cache = {}

    def add_frame(self, frame_assets):
        """
        Add a new frame to the video manually.
        
        :param frame_assets: List of assets for the new frame.
        """
        self.frames.append(frame_assets)

    def reset(self):
        """Reset the Editor by clearing all frames and cache."""
        self.frames = []
        self.clear_cache()
