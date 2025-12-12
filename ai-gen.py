# ============================================
# Simple chord + melody analysis helper
# ============================================

from typing import List, Dict, Any

# --------------------------------------------
# Basic pitch-class helpers
# --------------------------------------------

NOTE_TO_PC = {
    "C": 0,  "B#": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4,  "Fb": 4,
    "F": 5,  "E#": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}

PC_TO_SHARP_NAME = {
    0: "C", 1: "C#", 2: "D", 3: "Eb",
    4: "E", 5: "F", 6: "F#", 7: "G",
    8: "Ab", 9: "A", 10: "Bb", 11: "B",
}

def normalize_note(name: str) -> str:
    """Normalize note name (upper-case, strip spaces)."""
    return name.strip().replace('♭', 'b').replace('♯', '#').upper()

def note_to_pc(name: str) -> int:
    name = normalize_note(name)
    if name not in NOTE_TO_PC:
        raise ValueError(f"Unknown note name: {name}")
    return NOTE_TO_PC[name]

# --------------------------------------------
# Scales and modes
# --------------------------------------------

# Major scale intervals from tonic: 1–7
MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]

MODE_NAMES = {
    1: "Ionian (major)",
    2: "Dorian",
    3: "Phrygian",
    4: "Lydian",
    5: "Mixolydian",
    6: "Aeolian (natural minor)",
    7: "Locrian",
}

def build_major_scale_pcs(tonic: str) -> List[int]:
    t_pc = note_to_pc(tonic)
    return [(t_pc + i) % 12 for i in MAJOR_INTERVALS]

def rotate_intervals(mode_degree: int) -> List[int]:
    """Return intervals (0–11) for a mode, relative to its tonic,
    built by rotating the major scale intervals."""
    # Rotate major intervals so that mode_degree becomes 1
    shifted = MAJOR_INTERVALS[mode_degree - 1:] + MAJOR_INTERVALS[:mode_degree - 1]
    tonic_offset = shifted[0]
    return [ (i - tonic_offset) % 12 for i in shifted ]

# --------------------------------------------
# Chord parsing
# --------------------------------------------

def parse_chord_symbol(symbol: str) -> Dict[str, Any]:
    """
    Very simple parser.
    Supports roots like 'G', 'Gb', 'F#' and qualities like:
    - maj7, M7
    - m, m7
    - 7, 9, 13, b9, #9, b13, #11, etc (dominant)
    """
    s = symbol.strip()
    s = s.replace('♭', 'b').replace('♯', '#')
    # root: first letter + optional #/b
    if len(s) >= 2 and s[1] in ['#', 'b']:
        root = s[:2]
        rest = s[2:]
    else:
        root = s[0]
        rest = s[1:]

    root = normalize_note(root)

    quality = "maj"   # default
    dominant = False
    minor = False
    maj7 = False
    extensions = []

    r_lower = rest.lower()

    if "maj" in r_lower or "ma7" in r_lower or "maj7" in r_lower or "∆" in r_lower:
        quality = "maj"
        maj7 = True
    elif "m" in r_lower and "maj" not in r_lower:  # crude: 'm' means minor
        quality = "min"
        minor = True
    elif "7" in r_lower or "9" in r_lower or "13" in r_lower:
        quality = "dom"
        dominant = True

    # Dominant chord if has 7/9/13 but not maj or minor
    # Collect alterations (b9, #9, b13, #11, etc)
    for alt in ["b9", "#9", "b13", "#11"]:
        if alt in r_lower:
            extensions.append(alt)

    return {
        "symbol": symbol,
        "root": root,
        "quality": quality,   # 'maj', 'min', 'dom'
        "dominant": dominant,
        "minor": minor,
        "maj7": maj7,
        "extensions": extensions,
    }

# --------------------------------------------
# Roman numeral + mode in global key
# --------------------------------------------

def get_degree_in_key(root: str, global_key: str) -> int:
    """Return scale degree (1–7) of root in global major key, or 0 if not diatonic."""
    pcs = build_major_scale_pcs(global_key)
    root_pc = note_to_pc(root)
    if root_pc in pcs:
        return pcs.index(root_pc) + 1
    return 0

def roman_for_degree(degree: int, chord_quality: str) -> str:
    romans = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}
    if degree == 0:
        return "N/A"
    base = romans[degree]
    if chord_quality == "maj":
        return base
    elif chord_quality == "min":
        return base.lower()
    elif chord_quality == "dom":
        return base  # dominant often uppercase
    else:
        return base

def mode_for_degree(degree: int) -> str:
    return MODE_NAMES.get(degree, "Non-diatonic")

def detect_tritone_sub(chord_info: Dict[str, Any], global_key: str) -> str:
    """Very conservative: bII7 in major key = tritone sub of V."""
    if not chord_info["dominant"]:
        return ""
    tonic_pc = note_to_pc(global_key)
    b2_pc = (tonic_pc + 1) % 12
    root_pc = note_to_pc(chord_info["root"])
    if root_pc == b2_pc:
        return "Tritone substitution of V7"
    return ""

def detect_modal_borrowing(degree: int, chord_info: Dict[str, Any]) -> str:
    """Very simple: minor iv in major key."""
    if degree == 4 and chord_info["minor"]:
        return "Borrowed from parallel minor (iv)"
    return ""

# --------------------------------------------
# Map melody notes to chord-scale degrees
# --------------------------------------------

DEGREE_LABELS = {
    0: "1",
    1: "b2",
    2: "2",
    3: "b3",
    4: "3",
    5: "4",
    6: "b5",
    7: "5",
    8: "#5",
    9: "6",
    10: "b7",
    11: "7",
}

def build_mode_scale(root: str, degree_in_key: int) -> List[int]:
    """
    Build a 7-note mode scale for the chord, using the church mode
    associated with its scale degree in the global key.
    """
    root_pc = note_to_pc(root)
    # mode built from root with appropriate interval pattern
    intervals = rotate_intervals(degree_in_key if degree_in_key != 0 else 1)
    return [(root_pc + i) % 12 for i in intervals]

def pitch_to_chord_degree(pc: int, chord_root_pc: int) -> str:
    """Return scale-degree label (1, b2, 2, b3, 3, ..., 7) relative to chord root."""
    semitone = (pc - chord_root_pc) % 12
    return DEGREE_LABELS.get(semitone, f"?({semitone})")

# --------------------------------------------
# Melody function classification
# --------------------------------------------

def analyze_melody_functions(
    melody_pcs: List[int],
    chord_scale_pcs: List[int],
    chord_root_pc: int,
) -> Dict[int, List[str]]:
    """
    VERY simple heuristic classification of notes in a single-chord context.
    Returns dict: index -> [labels].
    Labels: 'guide_tone', 'arpeggio', 'scale_line',
            'upper_neighbor', 'lower_neighbor',
            'passing', 'chromatic_passing'
    """
    n = len(melody_pcs)
    labels: Dict[int, List[str]] = {i: [] for i in range(n)}

    # Identify chord tones (1,3,5,7) in this mode (use major-ish mapping)
    chord_tone_semitones = [0, 4, 7, 11]  # 1,3,5,7 above root in semitones
    chord_tones = [ (chord_root_pc + x) % 12 for x in chord_tone_semitones ]
    guide_tones = [ (chord_root_pc + 4) % 12, (chord_root_pc + 11) % 12 ]  # 3 & 7

    for i, pc in enumerate(melody_pcs):
        if pc in guide_tones:
            labels[i].append("guide_tone")
        elif pc in chord_tones:
            labels[i].append("chord_tone")

    # Scale lines: three consecutive stepwise notes
    for i in range(1, n - 1):
        a, b, c = melody_pcs[i - 1], melody_pcs[i], melody_pcs[i + 1]
        d1 = (b - a) % 12
        d2 = (c - b) % 12
        if d1 in (1, 2, 10, 11) and d2 == d1:  # crude ascending/descending step
            labels[i - 1].append("scale_line")
            labels[i].append("scale_line")
            labels[i + 1].append("scale_line")

    # Neighbor tones (upper / lower)
    for i in range(1, n - 1):
        a, b, c = melody_pcs[i - 1], melody_pcs[i], melody_pcs[i + 1]
        if a == c and a in chord_tones:
            step = (b - a) % 12
            if step in (1, 2):  # up
                labels[i].append("upper_neighbor")
            elif step in (10, 11):  # down
                labels[i].append("lower_neighbor")

    # Passing and chromatic passing
    for i in range(1, n - 1):
        a, b, c = melody_pcs[i - 1], melody_pcs[i], melody_pcs[i + 1]
        # require chord tones on ends, non-chord in middle
        if a in chord_tones and c in chord_tones and b not in chord_tones:
            up = (b - a) % 12
            down = (c - b) % 12
            if up in (1, 2, 10, 11) and down in (1, 2, 10, 11):
                # if b in chord scale -> passing; else chromatic passing
                if b in chord_scale_pcs:
                    labels[i].append("passing_tone")
                else:
                    labels[i].append("chromatic_passing_tone")

    return labels

# --------------------------------------------
# Main entry function
# --------------------------------------------

def analyze_chord_and_melody(
    chord_symbol: str,
    global_key: str,
    melody_notes: List[str],
) -> Dict[str, Any]:
    """
    Main function user will call.
    Returns a dict with:
      - 'chord_info'
      - 'degree_in_key'
      - 'roman'
      - 'mode'
      - 'tritone_sub', 'modal_borrowing'
      - 'note_degrees' (list of degree labels per melody note)
      - 'functions' (index -> [labels])
    """
    chord_info = parse_chord_symbol(chord_symbol)
    degree = get_degree_in_key(chord_info["root"], global_key)
    roman = roman_for_degree(degree, chord_info["quality"])
    mode_name = mode_for_degree(degree)

    tri_sub = detect_tritone_sub(chord_info, global_key)
    modal_borrow = detect_modal_borrowing(degree, chord_info)

    # Build chord-scale as mode from chord root
    if degree == 0:
        # non-diatonic: just use major scale from root as crude fallback
        chord_scale_pcs = build_major_scale_pcs(chord_info["root"])
    else:
        chord_scale_pcs = build_mode_scale(chord_info["root"], degree)

    chord_root_pc = note_to_pc(chord_info["root"])
    melody_pcs = [note_to_pc(n) for n in melody_notes]
    note_degrees = [
        pitch_to_chord_degree(pc, chord_root_pc) for pc in melody_pcs
    ]

    functions = analyze_melody_functions(melody_pcs, chord_scale_pcs, chord_root_pc)

    return {
        "chord_info": chord_info,
        "degree_in_key": degree,
        "roman": roman,
        "mode": mode_name,
        "tritone_sub": tri_sub,
        "modal_borrowing": modal_borrow,
        "note_degrees": note_degrees,
        "functions": functions,
    }

# --------------------------------------------
# Example usage
# --------------------------------------------
if __name__ == "__main__":
    GLOBAL_KEY = "G"  # preconfigured global major key

    print("Interactive chord/melody analyzer")
    print("Global key is set to:", GLOBAL_KEY)
    print("Type lines like:  Eb7: D, E, G, B")
    print('Type "quit" to exit.\n')

    while True:
        line = input("Enter [chord]: key1, key2, ...  > ").strip()

        # quit condition
        if line.lower() == "quit":
            print("Goodbye.")
            break

        # basic validation
        if ":" not in line:
            print("Error: input must be in the form  [chord]: key1, key2, ...")
            continue

        chord_part, melody_part = line.split(":", 1)
        chord = chord_part.strip()
        melody_raw = melody_part.strip()

        if not chord or not melody_raw:
            print("Error: missing chord or melody notes. Try again.")
            continue

        # parse melody notes, allow extra spaces
        melody_tokens = [tok.strip() for tok in melody_raw.split(",")]
        melody = [tok for tok in melody_tokens if tok]

        if not melody:
            print("Error: no valid note names found after ':'. Try again.")
            continue

        try:
            result = analyze_chord_and_melody(chord, GLOBAL_KEY, melody)
        except ValueError as e:
            # catches unknown note names or similar parsing issues
            print(f"Error while analyzing: {e}")
            print("Please check your chord and note names and try again.")
            continue

        print("\n====================================")
        print("Chord:", chord)
        print("In key of", GLOBAL_KEY)
        print("Degree in key:", result["degree_in_key"])
        print("Roman numeral:", result["roman"])
        print("Mode:", result["mode"])
        if result["tritone_sub"]:
            print("Note:", result["tritone_sub"])
        if result["modal_borrowing"]:
            print("Note:", result["modal_borrowing"])

        print("\nMelody note degrees (per chord):")
        for note, deg in zip(melody, result["note_degrees"]):
            print(f"  {note:3} -> {deg}")

        print("\nFunctions per note index:")
        for i, labels in result["functions"].items():
            if labels:
                print(f"  index {i}, note {melody[i]}: {', '.join(labels)}")
        print("====================================\n")
