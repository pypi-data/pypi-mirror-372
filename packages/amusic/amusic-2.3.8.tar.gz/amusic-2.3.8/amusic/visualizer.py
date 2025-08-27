# visualizer.py
# This script is part of the 'amusic' library to create a MIDI visualization.

import sys
import os
import subprocess
import shutil
import mido
import pygame
import random

class MidiVisualizer:
    """
    A class to generate MIDI visualizations by rendering frames
    with Pygame and compiling them into a video with FFmpeg.
    """
    def __init__(self, midi_file_path, output_video_filename, resolution, fps, min_visual_gap_seconds, falling_note_color, pressed_key_color, soundfont_path=None):
        self.midi_file_path = midi_file_path
        self.output_video_filename = output_video_filename
        self.width = resolution[0]
        self.height = resolution[1]
        self.fps = fps
        self.min_visual_gap = min_visual_gap_seconds
        self.soundfont_path = soundfont_path
        
        self.temp_dir = 'temp_frames'
        self.note_speed = 900  # Pixels per second, increased for higher piano

        # Visual properties
        self.piano_key_height = self.height * 0.2  # Set to a fixed height to avoid stretching issues
        self.piano_start_y = self.height * 0.8  # Piano starts 80% of the way down the screen
        self.min_note_height = 4  # Minimum height for very short notes
        # There are 52 white keys on an 88-key piano
        self.white_key_width = self.width / 52.0
        self.black_key_width = self.white_key_width * 0.6
        self.black_key_height = self.piano_key_height * 0.6

        # Colors
        self.white_key_color = (255, 255, 255)
        self.black_key_color = (0, 0, 0)
        self.note_color = falling_note_color
        self.highlight_color = pressed_key_color
        self.background_color = (0, 0, 0)
        
        # Data structures for effects
        self.active_keys = {}
        self.particles = [] # No longer used but kept for future enhancements

    def _get_key_x_position(self, note_number):
        """Calculates the x-position for a given MIDI note number on the piano."""
        midi_start_note = 21
        note_name_in_octave = note_number % 12
        black_key_indices = {1, 3, 6, 8, 10}

        # Calculate the position based on white keys
        white_key_count = 0
        for i in range(note_number - midi_start_note):
            if (midi_start_note + i) % 12 not in black_key_indices:
                white_key_count += 1
        
        x_pos = white_key_count * self.white_key_width
        
        # Adjust position for black keys
        if note_name_in_octave in black_key_indices:
            if note_name_in_octave in {1, 3}:
                # C# and D# are offset relative to the white key to their left
                x_pos = x_pos - self.white_key_width * 0.25
            elif note_name_in_octave in {6, 8, 10}:
                # F#, G#, A# are offset relative to the white key to their right
                x_pos = x_pos + self.white_key_width * 0.25
            x_pos -= self.black_key_width / 2
        
        return x_pos

    def _draw_piano(self, screen, active_notes):
        """Draws a piano keyboard at the bottom of the screen with highlighting."""
        black_key_indices = {1, 3, 6, 8, 10}
        
        # First, draw all white keys
        white_key_count = 0
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12
            
            if note_name_in_octave not in black_key_indices:
                x = white_key_count * self.white_key_width
                
                # Check if the key should be highlighted
                color = self.highlight_color if midi_note in active_notes else self.white_key_color
                
                pygame.draw.rect(
                    screen,
                    color,
                    (x, self.piano_start_y, self.white_key_width, self.piano_key_height)
                )
                pygame.draw.rect(
                    screen,
                    (100, 100, 100),
                    (x, self.piano_start_y, self.white_key_width, self.piano_key_height),
                    1
                )
                white_key_count += 1
        
        # Then, draw all black keys on top
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12

            if note_name_in_octave in black_key_indices:
                x = self._get_key_x_position(midi_note)
                
                # Check if the key should be highlighted
                color = self.highlight_color if midi_note in active_notes else self.black_key_color

                pygame.draw.rect(
                    screen,
                    color,
                    (x, self.piano_start_y, self.black_key_width, self.black_key_height)
                )

    def create_visualizer_video(self):
        """
        Renders a MIDI file visualization to a video file.
        This method is called directly by the render script.
        """
        if not os.path.exists(self.midi_file_path):
            raise FileNotFoundError(f"MIDI file not found at {self.midi_file_path}")

        print(f"DEBUG: Rendering video to {self.output_video_filename}...")

        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        
        # Load MIDI file
        try:
            mid = mido.MidiFile(self.midi_file_path)
        except Exception as e:
            raise RuntimeError(f"Error loading MIDI file: {e}")
        
        total_time = mid.length
        total_frames = int(total_time * self.fps)

        # Pre-process all note on/off events into a timeline
        notes = []
        open_notes = {}
        
        current_time = 0.0
        microseconds_per_beat = 500000
        ticks_per_beat = mid.ticks_per_beat
        
        for track_index, track in enumerate(mid.tracks):
            current_track_time = 0.0
            for msg in track:
                if ticks_per_beat > 0:
                    delta_time_seconds = mido.tick2second(msg.time, ticks_per_beat, microseconds_per_beat)
                else:
                    delta_time_seconds = 0.0
                current_track_time += delta_time_seconds

                if msg.type == 'note_on' and msg.velocity > 0:
                    open_notes[(track_index, msg.note, msg.channel)] = current_track_time
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_key = (track_index, msg.note, msg.channel)
                    if note_key in open_notes:
                        start_time = open_notes.pop(note_key)
                        notes.append({
                            'note': msg.note,
                            'start': start_time,
                            'end': current_track_time,
                            'duration': current_track_time - start_time
                        })
        
        for note_key, start_time in open_notes.items():
            notes.append({
                'note': note_key[1],
                'start': start_time,
                'end': total_time,
                'duration': total_time - start_time
            })
            
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', f'{self.width}x{self.height}',
            '-r', str(self.fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            self.output_video_filename
        ]
        
        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        
        for frame_count in range(total_frames):
            current_time = frame_count / self.fps
            
            # Clear the screen first
            screen.fill(self.background_color)
            
            # Draw falling notes first (bottom layer)
            active_notes_to_highlight = set()
            for note in notes:
                # The time it takes for a note to fall from the top of the screen to the piano keys.
                travel_time = self.piano_start_y / self.note_speed

                # Check if the note is currently in its falling or held state.
                # It's visible if the current time is between when it starts falling and when it ends.
                if current_time >= note['start'] - travel_time and current_time <= note['end']:
                    
                    # Calculate the height of the note bar based on its duration.
                    note_height = max(self.min_note_height, self.note_speed * note['duration'])
                    
                    # Calculate the Y position of the note's top.
                    # This formula ensures the bottom of the note bar hits the piano at exactly note['start'].
                    y_pos_top = self.piano_start_y - ((note['start'] - current_time) * self.note_speed)

                    # Check if the note's bottom has reached or passed the piano keys.
                    if current_time >= note['start']:
                        # The note has hit the key, so add it to the highlight list
                        active_notes_to_highlight.add(note['note'])
                        
                        # Adjust note_height to shrink it as the note duration passes.
                        note_height = self.note_speed * (note['end'] - current_time)
                        if note_height < 0: note_height = 0
                        
                        # The note bar should now be drawn starting from the piano's top edge
                        y_pos_top = self.piano_start_y
                    
                    x_pos = self._get_key_x_position(note['note'])
                    
                    if x_pos is not None:
                        key_width = self.white_key_width if note['note'] % 12 not in {1, 3, 6, 8, 10} else self.black_key_width
                        pygame.draw.rect(screen, self.note_color, (x_pos, y_pos_top, key_width, note_height))
            
            # Now, draw the piano keyboard on top of the notes (top layer)
            self._draw_piano(screen, active_notes_to_highlight)
            
            # Update key highlights - remove notes that have been held for their full duration
            self.active_keys = active_notes_to_highlight
            
            pygame.display.flip()
            
            frame_data = pygame.image.tostring(screen, 'RGB')
            proc.stdin.write(frame_data)
            
        proc.stdin.close()
        proc.wait()
        
        pygame.quit()
        
        if proc.returncode != 0:
            raise RuntimeError(f"An error occurred during FFmpeg execution. Return code: {proc.returncode}")
        
        print(f"SUCCESS: Video saved to: {self.output_video_filename}")
