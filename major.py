chromatic=[('A','A'),
      ('A#','Bb'),
        ('B','B'),
        ('C','C'),
        ('C#','Db'),
        ('D','D'),
        ('D#','Eb'),
        ('E','E'),
        ('F','F'),
        ('F#','Gb'),
        ('G','G'),
        ('G#','Ab')]
chromatic_notes_set=set(note for pair in chromatic for note in pair)
major_scale_intervals = [2,2,1,2,2,2,1]
natural_minor_scale_intervals = [2,1,2,2,1,2,2]
harmonic_minor_scale_intervals = [2,1,2,2,1,3,1]
melodic_minor_scale_intervals = [2,1,2,2,2,2,1]
# use A4 as 0th note, note octave number change from B to C.
a4_freq = 440

class Note:
    def __init__(self, note:str, octave:int=4):
        if note not in chromatic_notes_set:
            raise ValueError(f"Invalid note: {note}, must be in {chromatic_notes_set}")
        self.is_sharp = 'b' not in note
        self.position = next(i for i, v in enumerate(chromatic) if note in v)
        self.octave_position = self.position
        # if octave_position is greater than or equal to 3 (C), subtract 12
        if self.octave_position >= 3:
            self.octave_position -= 12
        self.code = 12 * (octave - 3) + self.octave_position

    @classmethod
    def from_int(self, code:int, is_sharp:bool=True) -> 'Note':
        note = chromatic[code % len(chromatic)][0] if is_sharp else chromatic[code % len(chromatic)][1]
        return Note(note, code // 12 + 4)
    
    def whole_step(self, invert:bool=False) -> 'Note':
        return self.from_int(self.code + 2) if not invert else self.from_int(self.code - 2)

    def half_step(self, invert:bool=False) -> 'Note':
        return self.from_int(self.code + 1) if not invert else self.from_int(self.code - 1)

    def __add__(self, other) -> 'Note' or int:
        """
        Add a note or an integer to a note.
        Args:
            other: Note or int, the note or integer to add
        Returns:
            Note, the result of the addition
        """
        if isinstance(other, Note):
            return self.from_int(self.code + other.code)
        elif isinstance(other, int):
            return self.from_int(self.code + other)
        else:
            raise ValueError(f"Instance of {type(other)} is not supported")

    def __sub__(self, other) -> 'Note' or int:
        """
        Subtract a note or an integer from a note.
        Args:
            other: Note or int, the note or integer to subtract
        Returns:
            Note, the result of the subtraction
            int, the result of the subtraction if other is an integer
        """
        if isinstance(other, Note):
            return self.from_int(self.code - other.code)
        elif isinstance(other, int):
            return self.code - other
        else:
            raise ValueError(f"Instance of {type(other)} is not supported")

    def __eq__(self, other: 'Note') -> bool:
        return self.code == other.code

    def enharmonic_equivalent(self) -> 'Note':
        return chromatic[self.position%12][1 if self.is_sharp else 0]

    def get_frequency(self) -> float:
        """
        Get the frequency of a note.
        Returns:
            float, the frequency of the note
        """
        return a4_freq * 2 ** ((self.code) / 12)

    def get_name(self) -> str:
        return chromatic[self.position][0] if self.is_sharp else chromatic[self.position][1]

    def get_octave(self) -> int:
        """
        Get the octave of a note.
        A4 is 0, A#4 is 1, B4 is 2, C5 is 3 (change octave), etc.
        Returns:
            int, the octave of the note
        """
        return (self.code - self.octave_position) // 12 + 4

    def __str__(self) -> str:
        return f"{self.get_name()}{self.get_octave()}"

class MajorScale:
    def __init__(self, root:Note):
        if not isinstance(root, Note):
            raise ValueError(f"Root must be a Note object, got {type(root)}")
        self.root = root

    @classmethod
    def from_note_int(self, root_code:int, is_sharp:bool=True) -> 'MajorScale':
        return MajorScale(Note.from_int(root_code, is_sharp))

    @classmethod
    def from_note_name(self, root_name:str, octave:int=4) -> 'MajorScale':
        return MajorScale(Note(root_name, octave))

    def is_in_scale(self, list_of_notes:list[Note]) -> bool:
        """
        Check if a list of notes is in the major scale.
        Args:
            list_of_notes: list[Note], the list of notes to check
        Returns:
            bool, True if the list of notes is in the major scale, False otherwise
        """
        for note in list_of_notes:
            if note.code not in [note.code for note in self.get_major_scale()]:
                return False
        return True

    def get_major_scale(self, length:int=7) -> list[Note]:
        scale = []
        scale.append(self.root)
        cur_note_pos = self.root.code
        interval_index = 0
        for _ in range(length):
            cur_note_pos += major_scale_intervals[interval_index]
            # keep sharp notation
            scale.append(Note.from_int(cur_note_pos, self.root.is_sharp))
            interval_index = (interval_index + 1) % len(major_scale_intervals)
        return scale

    def get_minor_scale(self, type:str='natural', length:int=7) -> list[Note]:
        scale = []
        scale.append(self.root)
        cur_note_pos = self.root.code
        minor_scale_intervals=natural_minor_scale_intervals
        if type!='natural':
            if type=='harmonic':
                minor_scale_intervals=harmonic_minor_scale_intervals
            elif type=='melodic':
                minor_scale_intervals=melodic_minor_scale_intervals
            else:
                raise ValueError("Invalid minor scale type. Choose 'natural', 'harmonic', or 'melodic'.")
        interval_index = 0
        for _ in range(length):
            cur_note_pos += minor_scale_intervals[interval_index]
            # keep sharp notation
            scale.append(Note.from_int(cur_note_pos, self.root.is_sharp))
            interval_index = (interval_index + 1) % len(minor_scale_intervals)
        return scale

    def get_parallel_minor(self) -> 'MajorScale':
        """
        Get the parallel minor scale.
        Returns:
            MajorScale, the parallel minor scale
        """
        return MajorScale(self.root+5)


if __name__ == "__main__":
    a=input("Enter a root note for major scale: ")
    while a != "quit":
        if a not in chromatic_notes_set: 
            a = input("Invalid note. Enter a root note for major scale: ")
            continue
        major_scale = MajorScale.from_note_name(a)
        print(f"Major scale for {a}: {[note.get_name() for note in major_scale.get_major_scale()]}")
        print(f"Natural minor scale for {a}: {[note.get_name() for note in major_scale.get_minor_scale('natural')]}")
        print(f"Harmonic minor scale for {a}: {[note.get_name() for note in major_scale.get_minor_scale('harmonic')]}")
        print(f"Melodic minor scale for {a}: {[note.get_name() for note in major_scale.get_minor_scale('melodic')]}")
        a=input("Enter a root note for major scale: ")