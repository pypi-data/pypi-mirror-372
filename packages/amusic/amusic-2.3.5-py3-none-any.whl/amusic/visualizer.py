# visualizer.py
# This module provides a class to create MIDI visualizations by rendering frames
# with Pygame and compiling them into a video with FFmpeg.

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
        self.note_speed = 600  # Pixels per second

        # Visual properties
        self.piano_key_height = self.height * 0.1  # 10% of video height
        self.piano_start_y = self.height - self.piano_key_height - 20
        self.min_note_height = 4  # Minimum height for very short notes
        # There are 52 white keys on an an 88-key piano
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
        self.particles = []

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

    def _draw_piano(self, screen):
        """Draws a piano keyboard at the bottom of the screen."""
        black_key_indices = {1, 3, 6, 8, 10}
        
        # First, draw all white keys
        white_key_count = 0
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12
            
            if note_name_in_octave not in black_key_indices:
                x = white_key_count * self.white_key_width
                pygame.draw.rect(
                    screen,
                    self.white_key_color,
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
                
                pygame.draw.rect(
                    screen,
                    self.black_key_color,
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
        
        # Use mido's built-in length property for a robust total duration calculation.
        total_time = mid.length
        total_frames = int(total_time * self.fps)

        # Pre-process all note on/off events into a timeline
        notes = []
        open_notes = {}
        
        # Process MIDI events with correct time conversion.
        current_time = 0.0
        microseconds_per_beat = 500000  # Default to 120 bpm
        ticks_per_beat = mid.ticks_per_beat
        
        # Process each track to get absolute times for all note events.
        for track_index, track in enumerate(mid.tracks):
            current_time = 0.0
            for msg in track:
                # Convert delta time from ticks to seconds
                if ticks_per_beat > 0:
                    delta_time_seconds = mido.tick2second(msg.time, ticks_per_beat, microseconds_per_beat)
                else:
                    # Handle cases where ticks_per_beat is zero to prevent division by zero.
                    delta_time_seconds = 0.0
                current_time += delta_time_seconds

                if msg.type == 'note_on' and msg.velocity > 0:
                    open_notes[(track_index, msg.note, msg.channel)] = current_time
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_key = (track_index, msg.note, msg.channel)
                    if note_key in open_notes:
                        start_time = open_notes.pop(note_key)
                        notes.append({
                            'note': msg.note,
                            'start': start_time,
                            'end': current_time,
                            'duration': current_time - start_time
                        })
        
        # Any remaining notes in open_notes are held until the end of the song.
        # Their end time is the total duration of the MIDI file.
        for note_key, start_time in open_notes.items():
            notes.append({
                'note': note_key[1],
                'start': start_time,
                'end': total_time,
                'duration': total_time - start_time
            })
            
        # Use FFmpeg subprocess to pipe video frames directly
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
        
        # Rendering loop
        for frame_count in range(total_frames):
            current_time = frame_count / self.fps
            
            # Clear the screen first
            screen.fill(self.background_color)
            
            # Now, draw the piano keyboard so notes can fall on top of it.
            self._draw_piano(screen)
            
            # Draw falling notes
            # The time it takes for a note to travel from the top to the piano.
            travel_time = self.piano_start_y / self.note_speed
            
            for note in notes:
                # Calculate the time when the note should start appearing on screen
                spawn_time = note['start'] - travel_time
                
                # Only draw the note if it's within the on-screen time window
                if current_time >= spawn_time and current_time < note['end']:
                    # Calculate the note's y position (top of the rectangle)
                    # The y position is based on the time since the note 'spawned'
                    y_pos = (current_time - spawn_time) * self.note_speed
                    
                    # The height of the note is based on its duration, with a minimum height
                    note_height = max(self.min_note_height, self.note_speed * note['duration'])
                    
                    x_pos = self._get_key_x_position(note['note'])
                    
                    if x_pos is not None:
                        key_width = self.white_key_width
                        note_name = note['note'] % 12
                        if note_name in {1, 3, 6, 8, 10}:
                            key_width = self.black_key_width
                        
                        if y_pos <= self.piano_start_y and note['note'] not in self.active_keys:
                            self.active_keys[note['note']] = {'start_time': current_time, 'duration': 0.1}
                            self._create_particles(x_pos + key_width / 2, self.piano_start_y)

                        pygame.draw.rect(screen, self.note_color, (x_pos, y_pos, key_width, note_height))
            
            # Update and draw key highlights and particles on top of the piano
            self._update_effects(current_time)
            self._draw_effects(screen)
            
            pygame.display.flip()
            
            # Write the frame data directly to FFmpeg
            frame_data = pygame.image.tostring(screen, 'RGB')
            proc.stdin.write(frame_data)
            
        # Close the pipe and wait for FFmpeg to finish
        proc.stdin.close()
        proc.wait()
        
        pygame.quit()
        
        if proc.returncode != 0:
            raise RuntimeError(f"An error occurred during FFmpeg execution. Return code: {proc.returncode}")
        
        print(f"SUCCESS: Video saved to: {self.output_video_filename}")

    def _update_effects(self, current_time):
        """Updates the state of active key highlights and particles."""
        keys_to_remove = [note for note, data in self.active_keys.items() if current_time - data['start_time'] > data['duration']]
        for note in keys_to_remove:
            del self.active_keys[note]

        self.particles = [p for p in self.particles if p['alpha'] > 0]
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] -= 10
            p['size'] -= 0.1

    def _draw_effects(self, screen):
        """Draws key highlights and particles."""
        for note in self.active_keys:
            x_pos = self._get_key_x_position(note)
            key_width = self.white_key_width
            note_name = note % 12
            if note_name in {1, 3, 6, 8, 10}:
                key_width = self.black_key_width
            
            highlight_surface = pygame.Surface((key_width, self.piano_key_height), pygame.SRCALPHA)
            highlight_surface.fill(self.highlight_color + (80,))
            screen.blit(highlight_surface, (x_pos, self.piano_start_y))

        for p in self.particles:
            if p['alpha'] > 0:
                particle_color = p['color'] + (int(p['alpha']),)
                pygame.draw.circle(screen, particle_color, (int(p['x']), int(p['y'])), int(p['size']))

    def _create_particles(self, x, y, count=10):
        """Creates a burst of particles at a given position."""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 3)
            vx = speed * pygame.math.Vector2(1, 0).rotate(angle)[0]
            vy = speed * pygame.math.Vector2(1, 0).rotate(angle)[1]

            self.particles.append({
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'alpha': 255,
                'size': random.uniform(2, 5),
                'color': self.note_color
            })
