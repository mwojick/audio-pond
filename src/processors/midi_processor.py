"""MIDI processor for Audio Pond."""

from pathlib import Path
from mido import MidiFile, MidiTrack, MetaMessage


class MidiProcessor:
    """Handles MIDI file manipulation."""

    def __init__(self, output_dir: Path):
        """Initialize the MIDI processor.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir

    def trim_midi_silence(self, midi_path: Path) -> Path:
        """Remove initial silence from MIDI file.

        Args:
            midi_path: Path to the input MIDI file

        Returns:
            Path to the trimmed MIDI file
        """
        # Load the file
        mid = MidiFile(str(midi_path))

        # First, determine the absolute time (in ticks) of each message and find the earliest note_on event.
        offset = None
        for track in mid.tracks:
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                # Check for note_on events with a non-zero velocity (ignore note_on with velocity 0 which are note offs)
                if msg.type == "note_on" and msg.velocity > 0:
                    if offset is None or abs_time < offset:
                        offset = abs_time

        # If no note_on was found, there's nothing to trim.
        if offset is None:
            offset = 0

        # Now subtract the offset from every message in each track and recalc delta times.
        for track in mid.tracks:
            abs_times = []
            running_time = 0
            # First compute new absolute times (ensuring they don't go below 0)
            for msg in track:
                running_time += msg.time
                new_time = running_time - offset
                abs_times.append(new_time if new_time > 0 else 0)
            # Then convert absolute times back to delta times
            prev = 0
            for i, msg in enumerate(track):
                new_delta = abs_times[i] - prev
                msg.time = new_delta
                prev = abs_times[i]

        # Save the trimmed MIDI file
        output_path = self.output_dir / "2_transcription_trimmed.midi"
        mid.save(str(output_path))

        return output_path

    def adjust_note_durations(self, midi_path: Path, target_bpm: float) -> Path:
        """Adjust note durations to match the target tempo, accounting for the transcriber's 120 BPM assumption.

        Args:
            midi_path: Path to the input MIDI file
            target_bpm: The actual BPM the piece should be played at

        Returns:
            Path to the duration-adjusted MIDI file
        """
        # Load the file
        mid = MidiFile(str(midi_path))

        # Calculate scale factor based on the transcriber's 120 BPM assumption
        scale_factor = target_bpm / 120.0

        for track in mid.tracks:
            for msg in track:
                if msg.type == "set_tempo":
                    # Tempo is in microseconds per beat
                    msg.tempo = int(msg.tempo / scale_factor)

                # Scale all time values
                elif hasattr(msg, "time"):
                    msg.time = int(msg.time * scale_factor)

        # Save the adjusted MIDI file
        output_path = self.output_dir / "2_transcription_duration_adjusted.midi"
        mid.save(str(output_path))

        return output_path

    def split_midi_tracks(self, midi_path: Path) -> Path:
        """Split MIDI file into treble and bass tracks.

        Args:
            midi_path: Path to the input MIDI file

        Returns:
            Path to the split MIDI file
        """
        # Load original MIDI file
        mid = MidiFile(str(midi_path))

        new_mid = MidiFile()
        new_mid.ticks_per_beat = mid.ticks_per_beat

        # Create two tracks (treble + bass)
        treble_track = MidiTrack()
        bass_track = MidiTrack()
        new_mid.tracks = [[], treble_track, bass_track]

        treble_track.append(MetaMessage("track_name", name="Upper", time=0))
        bass_track.append(MetaMessage("track_name", name="Lower", time=0))

        # Define the note threshold: notes below C4 (MIDI 60) go to bass,
        # notes at or above C4 go to treble
        NOTE_THRESHOLD = 60

        # Collect all messages from all tracks
        all_messages = []
        for track in mid.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                all_messages.append((msg, current_time))

        treble_msgs = []
        bass_msgs = []

        for msg, time in all_messages:
            if msg.type == "set_tempo":
                bass_msgs.append((msg, time))
                treble_msgs.append((msg, time))
            elif msg.type == "time_signature":
                bass_msgs.append((msg, time))
                treble_msgs.append((msg, time))
            elif msg.type == "note_on" or msg.type == "note_off":
                if msg.note >= NOTE_THRESHOLD:
                    # upper voice
                    msg.channel = 0
                    treble_msgs.append((msg, time))
                else:
                    # lower voice
                    msg.channel = 1
                    bass_msgs.append((msg, time))

        # Convert absolute times back to delta times for each track
        def convert_to_delta_time(messages):
            delta_messages = []
            prev_time = 0
            for msg, abs_time in sorted(messages, key=lambda x: x[1]):
                delta = abs_time - prev_time
                msg.time = int(delta)
                delta_messages.append(msg)
                prev_time = abs_time
            return delta_messages

        # Convert and add messages to tracks
        for msg in convert_to_delta_time(treble_msgs):
            treble_track.append(msg)
        for msg in convert_to_delta_time(bass_msgs):
            bass_track.append(msg)

        # Ensure each track ends with an end_of_track message
        for track in [treble_track, bass_track]:
            if track[-1].type != "end_of_track":
                track.append(MetaMessage("end_of_track", time=0))

        # Save the new MIDI file
        output_path = self.output_dir / "2_transcription_split.midi"
        new_mid.save(str(output_path))

        return output_path
