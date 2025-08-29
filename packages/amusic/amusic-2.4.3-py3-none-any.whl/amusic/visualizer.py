# amusic/visualizer.py
# This script contains the MidiVisualizer class, which generates a video from a MIDI file.
# It includes built-in logic to handle a soundfont or fall back to a silent video,
# and now correctly calculates the total video duration based on the MIDI file's content.

import sys
import os
import subprocess
import shutil
import mido
import pygame
import urllib.request

class MidiVisualizer:
    """
    A class to generate MIDI visualizations by rendering frames
    with Pygame and compiling them into a video with FFmpeg.
    It handles soundfont downloading and correctly calculates
    the video duration from the MIDI file's events.
    """
    SOUNDFONT_PATH = 'soundfont.sf2'
    
    def __init__(self, midi_file_path, output_video_filename, resolution, fps, min_visual_gap_seconds, falling_note_color, pressed_key_color):
        self.midi_file_path = midi_file_path
        self.output_video_filename = output_video_filename
        self.width = resolution[0]
        self.height = resolution[1]
        self.fps = fps
        self.min_visual_gap = min_visual_gap_seconds
        
        # Determine the soundfont path, checking for existence only
        self.soundfont_path = self._get_soundfont_path()

        self.note_speed = 900  # Pixels per second, increased for higher piano

        # Visual properties
        self.piano_key_height = self.height * 0.2
        self.piano_start_y = self.height * 0.8
        self.min_note_height = 4
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

    def _get_soundfont_path(self):
        """
        Checks for a local soundfont file and returns the path.
        If not found, it returns None.
        """
        if os.path.exists(self.SOUNDFONT_PATH):
            print(f"Info: Found existing soundfont at {self.SOUNDFONT_PATH}.")
            return self.SOUNDFONT_PATH
        else:
            print("Info: Soundfont not found. Will proceed with a video-only render (no sound).")
            return None

    def _get_key_x_position(self, note_number):
        """Calculates the x-position for a given MIDI note number on the piano."""
        midi_start_note = 21
        note_name_in_octave = note_number % 12
        black_key_indices = {1, 3, 6, 8, 10}

        white_key_count = 0
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12
            if note_name_in_octave not in black_key_indices:
                white_key_count += 1
        
        x_pos = white_key_count * self.white_key_width
        
        if note_name_in_octave in black_key_indices:
            if note_name_in_octave in {1, 3}:
                x_pos = x_pos - self.white_key_width * 0.25
            elif note_name_in_octave in {6, 8, 10}:
                x_pos = x_pos + self.white_key_width * 0.25
            x_pos -= self.black_key_width / 2
        
        return x_pos

    def _draw_piano(self, screen, active_notes):
        """Draws a piano keyboard at the bottom of the screen with highlighting."""
        black_key_indices = {1, 3, 6, 8, 10}
        
        white_key_count = 0
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12
            
            if note_name_in_octave not in black_key_indices:
                x = white_key_count * self.white_key_width
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
        
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12

            if note_name_in_octave in black_key_indices:
                x = self._get_key_x_position(midi_note)
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

        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        
        try:
            mid = mido.MidiFile(self.midi_file_path)
        except Exception as e:
            raise RuntimeError(f"Error loading MIDI file: {e}")
        
        # New, more robust duration calculation
        notes = []
        open_notes = {}
        last_note_end_time = 0.0
        current_time_seconds = 0.0
        microseconds_per_beat = 500000  # Default tempo

        # Use mido.merge_tracks for a single, time-ordered stream
        for msg in mido.merge_tracks(mid.tracks):
            # Update tempo if a set_tempo message is found
            if msg.type == 'set_tempo':
                microseconds_per_beat = msg.tempo
            
            # Advance time in seconds
            current_time_seconds += mido.tick2second(msg.time, mid.ticks_per_beat, microseconds_per_beat)

            if msg.type == 'note_on' and msg.velocity > 0:
                open_notes[(msg.note, msg.channel)] = current_time_seconds
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                note_key = (msg.note, msg.channel)
                if note_key in open_notes:
                    start_time = open_notes.pop(note_key)
                    end_time = current_time_seconds
                    notes.append({
                        'note': msg.note,
                        'start': start_time,
                        'end': end_time,
                        'duration': end_time - start_time
                    })
                    last_note_end_time = max(last_note_end_time, end_time)

        # Handle notes without a note_off message by using the final timestamp
        for note_key, start_time in open_notes.items():
            notes.append({
                'note': note_key[0],
                'start': start_time,
                'end': current_time_seconds,
                'duration': current_time_seconds - start_time
            })
            last_note_end_time = max(last_note_end_time, current_time_seconds)
            
        # Add a small buffer to the end of the video
        total_time = last_note_end_time + 1.0
        total_frames = int(total_time * self.fps)
        
        print(f"Info: Calculated video duration based on the last note ending at {last_note_end_time:.2f}s. Final frames: {total_frames}.")

        # Determine the FFmpeg command based on soundfont availability
        ffmpeg_cmd_base = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', f'{self.width}x{self.height}',
            '-r', str(self.fps),
            '-i', '-',
        ]

        if self.soundfont_path is not None:
            ffmpeg_cmd_audio = [
                '-i', self.soundfont_path,
                '-af', 'pan=stereo|c0=c0|c1=c1',
                '-c:a', 'aac',
                '-strict', 'experimental'
            ]
            ffmpeg_cmd_base.extend(ffmpeg_cmd_audio)
        else:
            print("Info: Soundfont not found. Rendering video without sound.")
            # Add a silent audio track to avoid FFmpeg errors with no audio input
            ffmpeg_cmd_base.extend(['-f', 'lavfi', '-i', 'anullsrc', '-c:a', 'aac'])

        ffmpeg_cmd_base.extend([
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            self.output_video_filename
        ])
        
        proc = subprocess.Popen(ffmpeg_cmd_base, stdin=subprocess.PIPE)
        
        for frame_count in range(total_frames):
            current_time = frame_count / self.fps
            screen.fill(self.background_color)
            
            active_notes_to_highlight = set()
            for note in notes:
                travel_time = self.piano_start_y / self.note_speed
                descent_start_time = note['start'] - travel_time

                if current_time >= descent_start_time and current_time <= note['end']:
                    note_height = max(self.min_note_height, self.note_speed * note['duration'])
                    y_pos_top = (current_time - descent_start_time) * self.note_speed
                    
                    if current_time >= note['start']:
                        active_notes_to_highlight.add(note['note'])
                        y_pos_top = self.piano_start_y
                        note_height = self.note_speed * (note['end'] - current_time)
                        if note_height < 0:
                            note_height = 0
                    
                    x_pos = self._get_key_x_position(note['note'])
                    
                    if x_pos is not None:
                        key_width = self.white_key_width if note['note'] % 12 not in {1, 3, 6, 8, 10} else self.black_key_width
                        pygame.draw.rect(screen, self.note_color, (x_pos, y_pos_top, key_width, note_height))
            
            self._draw_piano(screen, active_notes_to_highlight)
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
