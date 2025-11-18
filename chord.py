from major import MajorScale,Note

intervals_triad = {
    (4,3): "major",
    (3,4): "minor",
    (3,3): "diminished",
    (4,4): "augmented"
}

triad_intervals = {
    "major": [4,3],
    "minor": [3,4],
    "diminished": [3,3],
    "augmented": [4,4]
}

seven_chord_intervals = {
    "dominant": [4,3,3],
    "diminished": [3,4,3],
    "half-diminished": [3,3,4],
    "augmented major": [4,4,3],
    "minor-major": [3,4,4],
    "major": [4,3,4],
    "full-diminished": [3,3,3]
}

intervals_seven_chord = {
    (4,3,3): ("major-minor 7","dominant 7","7"),
    (3,4,3): ("minor-minor 7","diminished 7","m7"),
    (3,3,4): ("diminished-minor 7","half-diminished 7","m7b5"),
    (4,4,3): ("augmented major 7","augmented major 7","M7#5"),
    (3,4,4): ("minor-major 7","minor-major 7","mM7"),
    (4,3,4): ("major-major 7","major 7","M7"),
    (3,3,3): ("diminished-diminished 7","full-diminished 7","dim7"),
}

Roman_numerals = ["I","II","III","IV","V","VI","VII"]

class Chord:
    def __init__(self, root:Note, keys:list[Note]=None, zero_indexed:bool=False):
        """
        Build a chord object.
        Args:
            root: Note, the root note of the chord
            keys: list[str], the notes of the chord, default is None, if want to build with initial triad, use build_triad method
            zero_indexed: bool, if the keys are zero indexed, default is False
        """
        self.root = root
        self.major = MajorScale(root)
        self.keys = keys
        self.zero_indexed = zero_indexed

    def get_intervals(self) -> list[int]:
        """
        Get the intervals of the chord.
        Returns:
            list[int], the quality of the chord, empty list if not built yet
        """
        if self.keys is None:
            return []
        difference = [self.keys[i].code - self.keys[i-1].code for i in range(1, len(self.keys))]
        return difference

    def __str__(self) -> str:
        return f"{self.get_quality()} chord under major scale {self.root.get_name()}"

class Triad(Chord): 
    def __init__(self, root:Note, keys:list[Note]=None, zero_indexed:bool=False):
        if len(keys) != 3:
            raise ValueError("Triad must have 3 keys")
        super().__init__(root, keys, zero_indexed)
    
    @classmethod
    def build_triad(self, root:Note, starting_index:int=1, quality:str=None) -> 'Triad':
        """
        Build a triad chord object.
        Args:
            root: Note, the root note of the chord
            starting_index: int, the starting index of the chord, default is 1
            quality: str, the quality of the chord, default is None
        """
        keys = self.get_triad(starting_index, quality)
        return Triad(root, keys, self.zero_indexed)

    def get_triad(self, starting_index:int, quality:str=None) -> list[Note]:
        """
        Get a triad chord from the major scale.
        Args:
            starting_index: int, the starting index of the chord, default is 1, assume is positive indexed
            quality: str, the quality of the chord ["major", "minor", "diminished", "augmented"], default is None
        Returns:
            list[Note], the triad chord
        """
        if not self.zero_indexed:
            starting_index = starting_index - 1
        triad = [self.major.root + starting_index]
        major_notes=self.major.get_major_scale(starting_index+6)
        if quality is None:
            # major triad from selected note
            for i in range(starting_index, starting_index + 5,2):
                triad.append(major_notes[i])
        else:
            # major triad from quality, note may not be in major scale
            if quality not in triad_intervals:
                raise ValueError(f"Invalid quality: {quality}")
            current_note_code = major_notes[starting_index].code
            for interval in triad_intervals[quality]:
                current_note_code += interval
                triad.append(Note.from_int(current_note_code, self.root.is_sharp))
        return triad

    def get_quality(self) -> str:
        """
        Get the quality of the chord.
        Returns:
            str, the quality of the chord, empty string if not built yet
        """
        intervals=tuple(self.get_intervals())
        if intervals not in triad_intervals.keys():
            return "Unknown chord"
        return triad_intervals[intervals]

    def __str__(self) -> str:
        return f"{self.keys[0].get_name()}{self.get_quality()} triad under major scale {self.root.get_name()}"
    

class SevenChord(Chord):
    def __init__(self, root:Note, keys:list[Note]=None, zero_indexed:bool=False):
        if len(keys) != 4:
            raise ValueError("Seven chord must have 4 keys")
        super().__init__(root, keys, zero_indexed)

    @classmethod
    def build_seven_chord(self, root:Note, starting_index:int=1, quality:str=None) -> 'SevenChord':
        """
        Build a seven chord object.
        Args:
            root: str, the root note of the chord
            starting_index: int, the starting note index of the chord, default is 1
            quality: str, the quality of the chord, default is None
        """
        keys = self.get_seven_chord(self, starting_index, quality)
        return SevenChord(root, keys, self.zero_indexed)
    
    def get_seven_chord(self, starting_index:int, quality:str=None) -> list[Note]:
        """
        Get a seven chord from the major scale.
        Args:
            starting_index: int, the starting index of the chord, default is 1, assume is positive indexed
            quality: str, the quality of the chord ["dominant", "diminished", "half-diminished", "augmented major", "minor-major", "major", "full-diminished"], default is None
        Returns:
            list[Note], the seven chord
        """
        print(type(self))
        if not self.zero_indexed:
            starting_index = starting_index - 1
        major_notes = self.major.get_major_scale(starting_index+8)
        seven_chord = []
        if quality is None:
            # major seven chord from selected note
            for i in range(starting_index, starting_index + 8,2):
                seven_chord.append(major_notes[i])
        else:
            # major seven chord from quality, note may not be in major scale
            if quality not in seven_chord_intervals:
                raise ValueError(f"Invalid quality: {quality}")
            current_note_code = major_notes[starting_index].code
            for interval in seven_chord_intervals[quality]:
                current_note_code += interval
                seven_chord.append(Note.from_int(current_note_code, self.root.is_sharp))
        return seven_chord

    def get_quality(self, name_type:str="shortest") -> str:
        """
        Get the quality of the chord.
        Args:
            name_type: str, the type of the name, default is "shortest", can be "short" or "full"
        Returns:
            str, the quality of the chord, empty string if not built yet
        """
        intervals=tuple(self.get_intervals())
        if intervals not in intervals_seven_chord.keys():
            return "Unknown chord"
        if name_type == "shortest":
            return f'{self.keys[0].get_name()}{intervals_seven_chord[intervals][0]} '
        elif name_type == "short":
            return f'{self.keys[0].get_name()}{intervals_seven_chord[intervals][1]} '
        elif name_type == "full":
            return f'{self.keys[0].get_name()}{intervals_seven_chord[intervals][2]} '
        else:
            raise ValueError(f"Invalid name type: {name_type}")
    
    def is_primary_dominant(self) -> bool:
        """
        Check if the chord is a primary dominant chord.
        Returns:
            bool, True if the chord is a primary dominant chord (I, IV, V), False otherwise
        """
        intervals=tuple(self.get_intervals())
        if intervals not in intervals_seven_chord.keys():
            return False
        if self.keys[0]-self.root==0 and intervals==seven_chord_intervals["major"]:
            return True
        elif self.keys[0]-self.root==5 and intervals==seven_chord_intervals["major"]:
            return True
        elif self.keys[0]-self.root==7 and intervals==seven_chord_intervals["dominant"]:
            return True
        else:
            return False


    def is_secondary_dominant(self) -> bool:
        """
        Check if the chord is a secondary dominant chord.
        Returns:
            bool, True if the chord is a secondary chord (ii, iii, vi, vii*), False otherwise
        """
        intervals=tuple(self.get_intervals())
        if intervals not in intervals_seven_chord.keys():
            return False
        if self.keys[0]-self.root==2 and intervals==seven_chord_intervals["minor"]:
            return True
        elif self.keys[0]-self.root==4 and intervals==seven_chord_intervals["minor"]:
            return True
        elif self.keys[0]-self.root==7 and intervals==seven_chord_intervals["minor"]:
            return True
        elif self.keys[0]-self.root==9 and intervals==seven_chord_intervals["diminished"]:
            return True
        else:
            return False

    def get_secondary_dominant(self) -> 'SevenChord':
        """
        Get the secondary dominant chord.
        Returns:
            Chord, the secondary dominant chord
        """
        if not((self.is_secondary_dominant() or self.is_primary_dominant()) and self.get_intervals()!=seven_chord_intervals["diminished"]):
            raise ValueError("Chord is not primary or secondary dominant")
        root_note = self.keys[0]-2
        return SevenChord.build_seven_chord(root_note, starting_index=8, quality='dominant')

    def tritone_substitution(self) -> 'SevenChord':
        """
        Get the tritone substitution of the chord.
        Returns:
            Chord, the tritone substitution chord
        """
        if self.get_quality()!="dominant":
            raise ValueError("Chord is not dominant")
        root_note = self.keys[2]-4
        return SevenChord.build_seven_chord(root_note, starting_index=8, quality='dominant')

    def __str__(self) -> str:
        return f"{self.keys[0].get_name()}{self.get_quality()} seven chord under major scale {self.root.get_name()}"

if __name__ == "__main__":
    words=""
    while words != "quit":
        words = input("Enter a root note for chord: ")
        chord = SevenChord.build_seven_chord(Note(words), quality='dominant')
        print([note.get_name() for note in chord.keys])