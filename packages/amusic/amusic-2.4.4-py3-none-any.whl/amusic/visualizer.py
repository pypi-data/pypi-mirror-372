import pygame
import os
import sys
import mido
import time
import subprocess
import numpy as np

OUTPUT_DIR = "videos"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


class MidiVisualizer:
    """
    A class to create MIDI visualization videos.
    It renders a piano keyboard and falling notes as they are played.
    """
    def __init__(self, midi_file, output_file="output.mp4", resolution=(1280, 720), fps=60):
        self.midi_file = midi_file
        self.output_file = os.path.join(OUTPUT_DIR, output_file)
        self.resolution = resolution
        self.fps = fps
        
        self.screen = None
        self.clock = None
        self.midi = None
        
        self.start_time = None
        self.current_time_ms = 0
        self.note_stream = []
        self.active_notes = {}
        self.event_index = 0
        
        self.colors = {
            'background': (20, 20, 20),
            'white_key': (255, 255, 255),
            'black_key': (0, 0, 0),
            'white_key_active': (255, 255, 100),
            'black_key_active': (50, 50, 50),
            'note_color': (0, 180, 255),
            'note_border': (0, 0, 0)
        }
        
        self.num_keys = 88
        self.keyboard_height = 200
        self.white_key_width = self.resolution[0] / 52
        self.black_key_width = self.white_key_width * 0.6
        self.white_key_height = self.keyboard_height
        self.black_key_height = self.keyboard_height * 0.6
        self.keyboard_y = self.resolution[1] - self.keyboard_height

        self.piano_layout = self.setup_piano_keys()

    def setup_piano_keys(self):
        """
        Calculates the position and size of each of the 88 piano keys.
        This is a critical part of ensuring the piano renders correctly.
        """
        piano_keys = []
        white_key_index = 0
        
        # Define the pattern for black keys to handle their placement
        black_key_pattern = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0] # 0 = no black key, 1 = black key
        
        # Iterate through all 88 notes (A0 to C8, MIDI notes 21 to 108)
        for midi_note in range(21, 109):
            is_black_key = black_key_pattern[(midi_note - 21) % 12] == 1
            
            if not is_black_key:
                # White key
                key_x = white_key_index * self.white_key_width
                key_y = self.keyboard_y
                key_rect = pygame.Rect(key_x, key_y, self.white_key_width, self.white_key_height)
                piano_keys.append({
                    'note': midi_note,
                    'rect': key_rect,
                    'is_black': False
                })
                white_key_index += 1
            else:
                # Black key
                # Black keys are positioned relative to the white keys below them.
                # The offset is needed to center them between the two white keys.
                key_x = (white_key_index * self.white_key_width) - (self.black_key_width / 2)
                key_y = self.keyboard_y
                key_rect = pygame.Rect(key_x, key_y, self.black_key_width, self.black_key_height)
                piano_keys.append({
                    'note': midi_note,
                    'rect': key_rect,
                    'is_black': True
                })
        
        return piano_keys

    def process_midi(self):
        """
        Parses the MIDI file and creates a stream of note-on/note-off events.
        """
        try:
            mid = mido.MidiFile(self.midi_file)
            absolute_time = 0
            for msg in mid:
                absolute_time += msg.time
                if msg.type in ['note_on', 'note_off']:
                    # Store event with note, velocity, and absolute time in milliseconds
                    self.note_stream.append({
                        'time': absolute_time * 1000,
                        'note': msg.note,
                        'type': msg.type,
                        'velocity': msg.velocity
                    })
        except FileNotFoundError:
            print(f"Error: MIDI file not found at {self.midi_file}")
            sys.exit(1)
            
    def get_key_position(self, note):
        """Helper to get the rendering position of a key based on its MIDI note number."""
        for key_data in self.piano_layout:
            if key_data['note'] == note:
                return key_data['rect'], key_data['is_black']
        return None, None
    
    def draw_piano(self):
        """
        Draws the piano keyboard on the screen, highlighting active keys.
        """
        for key_data in self.piano_layout:
            is_active = key_data['note'] in self.active_notes
            if is_active:
                color = self.colors['white_key_active'] if not key_data['is_black'] else self.colors['black_key_active']
            else:
                color = self.colors['white_key'] if not key_data['is_black'] else self.colors['black_key']
            
            pygame.draw.rect(self.screen, color, key_data['rect'])
            # Draw a border for white keys to distinguish them
            if not key_data['is_black']:
                 pygame.draw.rect(self.screen, self.colors['black_key'], key_data['rect'], 1)

    def draw_notes(self):
        """
        Draws the "falling" notes on the screen.
        """
        # Note speed (pixels per millisecond)
        note_speed = 0.5 
        
        notes_to_remove = []
        for note_id, note_data in self.active_notes.items():
            start_time = note_data['start_time']
            end_time = note_data.get('end_time')
            note = note_data['note']

            # Get key position for note placement
            key_rect, is_black = self.get_key_position(note)
            if not key_rect:
                continue

            # Calculate note position and height based on elapsed time
            current_duration = self.current_time_ms - start_time
            
            # If the note has been released, calculate its length based on duration
            if end_time:
                note_height = (end_time - start_time) * note_speed
                y_pos = self.keyboard_y - current_duration * note_speed
            else: # Note is still being held down, its length grows
                note_height = current_duration * note_speed
                y_pos = self.keyboard_y - note_height
            
            # The top of the note sprite
            note_x = key_rect.x
            note_width = key_rect.width

            note_rect = pygame.Rect(note_x, y_pos, note_width, note_height)
            
            # Draw the note sprite
            pygame.draw.rect(self.screen, self.colors['note_color'], note_rect)
            pygame.draw.rect(self.screen, self.colors['note_border'], note_rect, 1)

            # Mark for removal if the note has fallen off the screen
            if end_time and y_pos < -note_height:
                notes_to_remove.append(note_id)

        # Clean up notes that have passed
        for note_id in notes_to_remove:
            del self.active_notes[note_id]

    def _draw_and_get_frame(self):
        """
        Draws the current frame and returns it as a raw RGB byte array.
        """
        self.screen.fill(self.colors['background'])
        
        # Process MIDI events based on current time
        while self.event_index < len(self.note_stream):
            event = self.note_stream[self.event_index]
            if event['time'] <= self.current_time_ms:
                if event['type'] == 'note_on' and event['velocity'] > 0:
                    self.active_notes[event['note']] = {
                        'start_time': self.current_time_ms,
                        'note': event['note']
                    }
                elif event['type'] == 'note_off' or event['velocity'] == 0:
                    if event['note'] in self.active_notes:
                        self.active_notes[event['note']]['end_time'] = self.current_time_ms
                self.event_index += 1
            else:
                break
        
        # Draw all elements
        self.draw_piano()
        self.draw_notes()
        
        # Update the display
        pygame.display.flip()
        
        # Get frame data as a NumPy array and convert to bytes
        img_array = pygame.surfarray.array3d(pygame.display.get_surface())
        return np.swapaxes(img_array, 0, 1).tobytes()

    def render_video(self):
        """
        Uses ffmpeg to create the final video from the rendered frames.
        This method replaces the moviepy functionality.
        """
        # Determine the total duration of the MIDI file
        try:
            midi_duration = mido.MidiFile(self.midi_file).length
            print(f"MIDI file duration: {midi_duration:.2f} seconds")
        except FileNotFoundError:
            print("Could not find MIDI file to determine duration.")
            return

        # FFmpeg command to read raw video from stdin and encode to MP4
        cmd = [
            'ffmpeg',
            '-y', # Overwrite output file if it exists
            '-f', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', f"{self.resolution[0]}x{self.resolution[1]}",
            '-r', str(self.fps),
            '-i', '-', # Read from standard input
            '-an', # No audio
            '-vcodec', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '18', # High quality
            self.output_file
        ]

        print("Starting video rendering with ffmpeg...")
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        
        # Initialize pygame display
        pygame.init()
        self.screen = pygame.display.set_mode(self.resolution)
        self.clock = pygame.time.Clock()
        self.process_midi()
        
        total_frames = int(midi_duration * self.fps)
        for i in range(total_frames):
            self.current_time_ms = int((i / self.fps) * 1000)
            
            # Get the current frame as a raw byte stream
            frame_data = self._draw_and_get_frame()
            
            # Write the frame data to ffmpeg's stdin
            proc.stdin.write(frame_data)
            
            # Print progress
            sys.stdout.write(f"\rRendering frame {i+1}/{total_frames}...")
            sys.stdout.flush()

        # Close stdin and wait for the process to finish
        proc.stdin.close()
        proc.wait()
        
        print("\nVideo rendering finished.")
        print(f"Video saved to: {self.output_file}")


# Example usage
if __name__ == '__main__':
    # You MUST place a valid MIDI file named 'test.mid' in the same directory.
    # You can find free MIDI files online or create your own with a DAW.
    midi_file_path = "test.mid"
    
    # Check if the MIDI file exists
    if not os.path.exists(midi_file_path):
        print(f"Error: A MIDI file '{midi_file_path}' is required to run this script.")
        print("Please place a MIDI file in the same folder as this script.")
    else:
        # Initialize and run the visualizer
        try:
            visualizer = MidiVisualizer(midi_file=midi_file_path, resolution=(1920, 1080), fps=60)
            visualizer.render_video()
        except Exception as e:
            print(f"An error occurred during visualization: {e}")
