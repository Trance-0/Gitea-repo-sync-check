import numpy as np
import gradio as gr
from major import MajorScale,chromatic,chromatic_notes_set,Note

# sample rate, default is 48000
sr = 48000

def generate_tone(note, octave, duration):
    note_in_scale = Note(chromatic[note][0], octave)
    frequency = note_in_scale.get_frequency()
    # debug print
    # print(note_in_scale,frequency)
    duration = int(duration)
    audio = np.linspace(0, duration, duration * sr)
    audio = (20000 * np.sin(audio * (2 * np.pi * frequency))).astype(np.int16)
    return sr, audio

def generate_rhythm(rhythm, duration_per_note):
    rhythms = rhythm.split(",")
    audio = np.zeros(int(duration_per_note * len(rhythms) * sr))
    for i, rhythm_note in enumerate(rhythms):
        if rhythm != "x":
            if rhythm_note[:-1] not in chromatic_notes_set:
                raise ValueError(f"Invalid note: {rhythm_note}")
            note = Note(rhythm_note[:-1], int(rhythm_note[-1]))
            # debug print
            print(note, note.get_frequency(), note.code)
            segment_audio = np.linspace(0, duration_per_note, duration_per_note * sr)
            segment_audio = (20000 * np.sin(segment_audio * (2 * np.pi * note.get_frequency()))).astype(np.int16)
            audio[int(i * duration_per_note * sr):int((i + 1) * duration_per_note * sr)] = segment_audio
        else:
            audio[int(i * duration_per_note * sr):int((i + 1) * duration_per_note * sr)] = 0
    return sr, audio.astype(np.int16)

demo = gr.Interface(
    # generate_tone,
    # [
    #     gr.Dropdown(chromatic, type="index"),
    #     gr.Slider(0, 10, step=1),
    #     gr.Textbox(value="1", label="Duration in seconds"),
    # ],
    # "audio",
    generate_rhythm,
    [
        gr.Textbox(value="C4,D4,E4,F4,G4,A4,B4,C5", label="Rhythm"),
        gr.Slider(0, 10, value=1, step=1, label="Duration per note"),
    ],
    "audio",
)
if __name__ == "__main__":
    demo.launch()