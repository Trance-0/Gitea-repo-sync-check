# minimal counting function used for review

chromatic_scale = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
note_value = {e:i for i, e in enumerate(chromatic_scale)}
seven_chord_interval_name = {
    'M7#5':(4,4,3),
    'M7':(4,3,4),
    '7':(4,3,3),
    'mM7':(3,4,4),
    'm7':(3,4,3),
    'm7b5':(3,3,4),
    'dim7':(3,3,3),
}
major_scale_intervals = [2,2,1,2,2,2,1]

def get_major_scale(root):
    scale = []
    scale.append(root)
    root_index = note_value[root]
    for interval in major_scale_intervals:
        root_index = (root_index + interval) % 12
        scale.append(chromatic_scale[root_index])
    return scale

def get_number_of_half_steps(note1, note2):
    return min(abs(note_value[note1] - note_value[note2]), 12 - abs(note_value[note1] - note_value[note2]))

def _construct_chord(root, interval_type=(4,3,3)):
    chord = []
    chord.append(root)
    root_index = note_value[root]
    for interval in interval_type:
        root_index = (root_index + interval) % 12
        chord.append(chromatic_scale[root_index])
    return chord

words=""

while words != "quit":
    words = input("Enter a note or chord: ")
    notes = words.split(" ")
    if notes[0][1:] in seven_chord_interval_name.keys():
        # construct dominant 7 chord
        chord = _construct_chord(notes[0][0],seven_chord_interval_name[notes[0][1:]])
        print(chord,get_major_scale(notes[0][0]))
    else:
        # calculate the interval between notes
        res=[]
        for i in range(len(notes)-1):
            if notes[i] not in note_value or notes[i+1] not in note_value:
                print("Invalid note")
                break
            res.append(get_number_of_half_steps(notes[i], notes[i+1]))
        print(res)