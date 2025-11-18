import major

import unittest

class MajorScaleTest(unittest.TestCase):
    def test_from_note_int(self):
        scale = major.MajorScale.from_note_int(0)
        self.assertEqual(scale.root, "A")
        self.assertEqual(scale.octave, 4)
        self.assertEqual(scale.scale, ["A", "B", "C#", "D", "E", "F#", "G#"])
        
    def test_get_major_scale(self):
        scale = major.MajorScale.from_note_int(0)
        self.assertEqual(scale.get_major_scale(), ["A", "B", "C#", "D", "E", "F#", "G#"])
        
    def test_get_minor_scale(self):
        scale = major.MajorScale.from_note_int(0)
        self.assertEqual(scale.get_minor_scale(), ["A", "B", "C#", "D", "E", "F#", "G#"])
        

if __name__ == "__main__":
    unittest.main()