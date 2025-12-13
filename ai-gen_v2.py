from typing import List, Dict, Any, Tuple

# ============================================================
# CONFIG / CONSTANTS (keep most variables here)
# ============================================================

GLOBAL_KEY = "G"     # global major key center
DEBUG = 0            # 0..5 (0 = no debug, 5 = max)

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

MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # 7-note set

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

ROMANS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}

# 21-mode catalog: each is a 7-note set described by intervals from its root.
# Ordering matters for tie-break: Major-family first, then Melodic-minor, then Harmonic-minor.

MODE_CATALOG: List[Dict[str, Any]] = []

def _build_catalog():
    # Major family (7)
    major_modes = [
        ("Ionian (major)",                 [0, 2, 4, 5, 7, 9, 11]),
        ("Dorian",                         [0, 2, 3, 5, 7, 9, 10]),
        ("Phrygian",                       [0, 1, 3, 5, 7, 8, 10]),
        ("Lydian",                         [0, 2, 4, 6, 7, 9, 11]),
        ("Mixolydian",                     [0, 2, 4, 5, 7, 9, 10]),
        ("Aeolian (natural minor)",        [0, 2, 3, 5, 7, 8, 10]),
        ("Locrian",                        [0, 1, 3, 5, 6, 8, 10]),
    ]

    # Melodic minor family (7) (ascending melodic minor)
    melodic_minor_modes = [
        ("Melodic minor",                  [0, 2, 3, 5, 7, 9, 11]),
        ("Dorian b2",                       [0, 1, 3, 5, 7, 9, 10]),
        ("Lydian augmented",                [0, 2, 4, 6, 8, 9, 11]),
        ("Lydian dominant",                 [0, 2, 4, 6, 7, 9, 10]),
        ("Mixolydian b6",                   [0, 2, 4, 5, 7, 8, 10]),
        ("Locrian #2",                      [0, 2, 3, 5, 6, 8, 10]),
        ("Altered (super locrian)",         [0, 1, 3, 4, 6, 8, 10]),
    ]

    # Harmonic minor family (7)
    harmonic_minor_modes = [
        ("Harmonic minor",                  [0, 2, 3, 5, 7, 8, 11]),
        ("Locrian #6",                      [0, 1, 3, 5, 6, 9, 10]),
        ("Ionian #5",                       [0, 2, 4, 5, 8, 9, 11]),
        ("Dorian #4",                       [0, 2, 3, 6, 7, 9, 10]),
        ("Phrygian dominant",               [0, 1, 4, 5, 7, 8, 10]),
        ("Lydian #2",                       [0, 3, 4, 6, 7, 9, 11]),
        ("Altered diminished",              [0, 1, 3, 4, 6, 7, 9]),  # sometimes called "Ultralocrian"
    ]

    # store
    for fam_i, (family, modes) in enumerate([
        ("major", major_modes),
        ("melodic_minor", melodic_minor_modes),
        ("harmonic_minor", harmonic_minor_modes),
    ]):
        for mode_i, (name, intervals) in enumerate(modes):
            MODE_CATALOG.append({
                "family": family,
                "family_rank": fam_i,     # tie-break: smaller is preferred
                "mode_rank": mode_i,       # within family
                "name": name,
                "intervals": intervals
            })

_build_catalog()

# ============================================================
# BASIC HELPERS
# ============================================================

def dprint(level: int, msg: str) -> None:
    if DEBUG >= level:
        print(msg)

def normalize_note(name: str) -> str:
    s = name.strip().replace("♭", "b").replace("♯", "#")
    if not s:
        return s
    return s[0].upper() + s[1:]

def note_to_pc(name: str) -> int:
    name = normalize_note(name)
    if name not in NOTE_TO_PC:
        raise ValueError(f"Unknown note name: {name}")
    return NOTE_TO_PC[name]

def build_scale_from_intervals(root_pc: int, intervals: List[int]) -> List[int]:
    return [(root_pc + i) % 12 for i in intervals]

def build_major_scale_pcs(tonic: str) -> List[int]:
    t_pc = note_to_pc(tonic)
    return [(t_pc + i) % 12 for i in MAJOR_INTERVALS]

def pitch_to_degree_label(note_pc: int, root_pc: int) -> str:
    return DEGREE_LABELS[(note_pc - root_pc) % 12]

# ============================================================
# CHORD PARSING + REQUIRED TONES
# ============================================================

def parse_chord_symbol(symbol: str) -> Dict[str, Any]:
    """
    Parses roots like D, Db, F#
    Parses qualities: maj7 / M7, m / m7, dominant by presence of 7/9/13 without maj/min marker.
    Parses alterations: b9, #9, b13, #11, b5, #5
    Also recognizes plain extensions: 9, 11, 13 (as unaltered).
    """
    s = symbol.strip().replace("♭", "b").replace("♯", "#")
    if not s:
        raise ValueError("Empty chord symbol.")

    # root letter + optional accidental
    if len(s) >= 2 and s[1] in ("b", "#"):
        root, rest = s[:2], s[2:]
    else:
        root, rest = s[0], s[1:]

    root = normalize_note(root)
    r = rest.lower()

    # Quality
    quality = "maj"
    if "maj" in r or "ma7" in r or "maj7" in r or "∆" in r:
        quality = "maj"
    elif r.startswith("m") or "min" in r:
        quality = "min"

    # Dominant (7/9/13) when not maj/min explicitly
    dominant = False
    if any(x in r for x in ["7", "9", "11", "13"]) and ("maj" not in r and not (r.startswith("m") or "min" in r)):
        quality = "dom"
        dominant = True

    # Extract alterations and extensions
    # We treat "b9" etc as explicit, and "9"/"11"/"13" as plain extensions if present.
    alts = []
    for a in ["b9", "#9", "b13", "#11", "b5", "#5"]:
        if a in r:
            alts.append(a)

    exts = []
    for e in ["13", "11", "9", "7"]:  # check longer first
        if e in r:
            exts.append(e)

    return {
        "symbol": symbol,
        "root": root,
        "quality": quality,      # 'maj', 'min', 'dom'
        "dominant": dominant,
        "alts": alts,
        "exts": exts,
    }

def chord_required_semitones(ch: Dict[str, Any]) -> Tuple[List[int], List[int]]:
    """
    Returns (core_tones, extra_tones) as semitone offsets from chord root.
    core_tones: identity tones (triad + 7 if present/assumed by quality)
    extra_tones: extensions/alterations (9/11/13, b9, #9, #11, b13, etc)
    """
    q = ch["quality"]
    exts = ch["exts"]
    alts = set(ch["alts"])

    # core: 1 + 3/b3 + 5 + 7/b7 depending on chord quality
    if q == "maj":
        core = [0, 4, 7] + ([11] if ("7" in exts or "maj7" in ch["symbol"].lower() or "ma7" in ch["symbol"].lower()) else [])
    elif q == "min":
        core = [0, 3, 7] + ([10] if ("7" in exts or "m7" in ch["symbol"].lower()) else [])
    else:  # dom
        core = [0, 4, 7, 10]  # dominant implies b7

    extra: List[int] = []

    # plain extensions (if written)
    if "9" in exts:
        extra.append(2)
    if "11" in exts:
        extra.append(5)
    if "13" in exts:
        extra.append(9)

    # alterations override / add
    if "b9" in alts:
        extra.append(1)
    if "#9" in alts:
        extra.append(3)
    if "#11" in alts:
        extra.append(6)
    if "b13" in alts:
        extra.append(8)
    if "b5" in alts:
        extra.append(6)
    if "#5" in alts:
        extra.append(8)

    # remove duplicates while preserving order
    def uniq(xs: List[int]) -> List[int]:
        out = []
        seen = set()
        for x in xs:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out

    return uniq(core), uniq(extra)

# ============================================================
# ROMAN NUMERAL IN GLOBAL MAJOR KEY
# ============================================================

def degree_in_global_major(chord_root: str, global_key: str) -> int:
    scale = build_major_scale_pcs(global_key)
    r_pc = note_to_pc(chord_root)
    return scale.index(r_pc) + 1 if r_pc in scale else 0

def roman_for_degree(deg: int, quality: str) -> str:
    if deg == 0:
        return "N/A"
    base = ROMANS[deg]
    return base.lower() if quality == "min" else base

# ============================================================
# 21-MODE MATCHING ENGINE
# ============================================================

def mode_match_rank(
    root_pc: int,
    core: List[int],
    extra: List[int],
    melody_pcs: List[int],
    mode: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Scoring idea:
    - core tones should strongly be present in mode (big penalty if missing)
    - extra (extensions/alterations) should be present if possible (smaller penalty)
    - melody notes in mode add points, weighted by order (earlier notes count slightly more)
    """
    mode_pcs = set(build_scale_from_intervals(root_pc, mode["intervals"]))

    core_pcs = {(root_pc + s) % 12 for s in core}
    extra_pcs = {(root_pc + s) % 12 for s in extra}

    missing_core = [pc for pc in core_pcs if pc not in mode_pcs]
    missing_extra = [pc for pc in extra_pcs if pc not in mode_pcs]

    # melody match with order weighting
    n = max(len(melody_pcs), 1)
    weights = [(n - i) / n for i in range(n)]  # first notes slightly heavier
    melody_hits = []
    melody_score = 0.0
    for i, pc in enumerate(melody_pcs):
        hit = (pc in mode_pcs)
        melody_hits.append(hit)
        if hit:
            melody_score += 1.0 * weights[i]

    # penalties / bonuses
    score = 0.0
    score += 4.0 * (len(core_pcs) - len(missing_core))
    score -= 10.0 * len(missing_core)
    score += 1.5 * (len(extra_pcs) - len(missing_extra))
    score -= 2.5 * len(missing_extra)
    score += melody_score

    return {
        "mode": mode,
        "score": score,
        "missing_core": missing_core,
        "missing_extra": missing_extra,
        "melody_score": melody_score,
        "melody_hits": melody_hits,
    }

def choose_modes_21(
    chord_info: Dict[str, Any],
    melody_pcs: List[int],
) -> Dict[str, Any]:
    root_pc = note_to_pc(chord_info["root"])
    core, extra = chord_required_semitones(chord_info)

    dprint(4, f"[debug] chord root pc={root_pc}, core semitones={core}, extra semitones={extra}")

    ranked = []
    for mode in MODE_CATALOG:
        r = mode_match_rank(root_pc, core, extra, melody_pcs, mode)
        ranked.append(r)

    # Sort:
    # 1) higher score
    # 2) prefer major-family first (family_rank)
    # 3) prefer earlier mode_rank
    ranked.sort(key=lambda x: (-x["score"], x["mode"]["family_rank"], x["mode"]["mode_rank"]))

    if DEBUG >= 5:
        for k in range(min(10, len(ranked))):
            m = ranked[k]
            dprint(5, f"[debug] rank {k+1}: {m['mode']['family']}::{m['mode']['name']} score={m['score']:.3f} "
                      f"missing_core={len(m['missing_core'])} missing_extra={len(m['missing_extra'])} "
                      f"melody_score={m['melody_score']:.3f}")

    best = ranked[0]
    # include some alternatives that are close
    alternatives = ranked[1:6]

    return {
        "best": best,
        "alternatives": alternatives,
    }

# ============================================================
# SIMPLE MELODY FUNCTION TAGS (per chord)
# ============================================================

def analyze_melody_functions(melody_pcs: List[int], root_pc: int, quality: str) -> Dict[int, List[str]]:
    """
    Heuristics, minimal and local:
    - chord_tone: chord triad + 7 (based on quality)
    - guide_tone: the 3rd and 7th relative to root (major 3rd + maj7 assumed for maj7-ish,
                 minor 3rd + b7 for minor7-ish, major3 + b7 for dominant)
    - scale_line: 3 stepwise notes
    - neighbor: a == c and b step away
    - passing / chromatic passing: between two chord tones
    """
    n = len(melody_pcs)
    labels: Dict[int, List[str]] = {i: [] for i in range(n)}

    if quality == "maj":
        chord_tones = {(root_pc + s) % 12 for s in [0, 4, 7, 11]}
        guide_tones = {(root_pc + 4) % 12, (root_pc + 11) % 12}
    elif quality == "min":
        chord_tones = {(root_pc + s) % 12 for s in [0, 3, 7, 10]}
        guide_tones = {(root_pc + 3) % 12, (root_pc + 10) % 12}
    else:
        chord_tones = {(root_pc + s) % 12 for s in [0, 4, 7, 10]}
        guide_tones = {(root_pc + 4) % 12, (root_pc + 10) % 12}

    for i, pc in enumerate(melody_pcs):
        if pc in guide_tones:
            labels[i].append("guide_tone")
        if pc in chord_tones:
            labels[i].append("chord_tone")

    # scale line
    for i in range(1, n - 1):
        a, b, c = melody_pcs[i - 1], melody_pcs[i], melody_pcs[i + 1]
        d1 = (b - a) % 12
        d2 = (c - b) % 12
        if d1 in (1, 2, 10, 11) and d2 == d1:
            labels[i - 1].append("scale_line")
            labels[i].append("scale_line")
            labels[i + 1].append("scale_line")

    # neighbors
    for i in range(1, n - 1):
        a, b, c = melody_pcs[i - 1], melody_pcs[i], melody_pcs[i + 1]
        if a == c and a in chord_tones:
            step = (b - a) % 12
            if step in (1, 2):
                labels[i].append("upper_neighbor")
            elif step in (10, 11):
                labels[i].append("lower_neighbor")

    # passing / chromatic passing (no scale context; purely chord-tone bridge)
    for i in range(1, n - 1):
        a, b, c = melody_pcs[i - 1], melody_pcs[i], melody_pcs[i + 1]
        if a in chord_tones and c in chord_tones and b not in chord_tones:
            up = (b - a) % 12
            down = (c - b) % 12
            if up in (1, 2, 10, 11) and down in (1, 2, 10, 11):
                # if b is diatonic to either end? we don't know scale here, so treat semitone as chromatic
                if up == 1 or down == 1 or up == 11 or down == 11:
                    labels[i].append("chromatic_passing_tone")
                else:
                    labels[i].append("passing_tone")

    return labels

# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_chord_and_melody(chord_symbol: str, melody_notes: List[str], global_key: str) -> Dict[str, Any]:
    chord = parse_chord_symbol(chord_symbol)
    melody_pcs = [note_to_pc(n) for n in melody_notes]

    deg = degree_in_global_major(chord["root"], global_key)
    roman = roman_for_degree(deg, chord["quality"])

    dprint(3, f"[debug] parsed chord={chord} deg={deg} roman={roman}")

    mode_choice = choose_modes_21(chord, melody_pcs)
    best = mode_choice["best"]
    best_mode = best["mode"]

    root_pc = note_to_pc(chord["root"])
    melody_degrees = [pitch_to_degree_label(pc, root_pc) for pc in melody_pcs]

    functions = analyze_melody_functions(melody_pcs, root_pc, chord["quality"])

    return {
        "global_key": global_key,
        "chord": chord,
        "degree_in_key": deg,
        "roman": roman,
        "best_mode": {
            "family": best_mode["family"],
            "name": best_mode["name"],
            "score": best["score"],
            "melody_score": best["melody_score"],
            "missing_core": best["missing_core"],
            "missing_extra": best["missing_extra"],
        },
        "alternatives": [
            {
                "family": a["mode"]["family"],
                "name": a["mode"]["name"],
                "score": a["score"],
                "melody_score": a["melody_score"],
                "missing_core": a["missing_core"],
                "missing_extra": a["missing_extra"],
            }
            for a in mode_choice["alternatives"]
        ],
        "melody_notes": [normalize_note(n) for n in melody_notes],
        "melody_degrees": melody_degrees,
        "functions": functions,
    }

# ============================================================
# CLI
# ============================================================

def parse_cli_line(line: str) -> Tuple[str, List[str]]:
    """
    Expects: [chord]: note1, note2, ...
    Allows commas or whitespace between notes.
    """
    if ":" not in line:
        raise ValueError("Input must contain ':' like  D7b9b13: F#, A, C, Eb, Bb")

    chord_part, melody_part = line.split(":", 1)
    chord = chord_part.strip()
    if not chord:
        raise ValueError("Missing chord before ':'.")

    melody_raw = melody_part.strip()
    if not melody_raw:
        raise ValueError("Missing melody notes after ':'.")

    if "," in melody_raw:
        tokens = [t.strip() for t in melody_raw.split(",")]
    else:
        tokens = [t.strip() for t in melody_raw.split()]

    notes = [t for t in tokens if t]
    if not notes:
        raise ValueError("No valid note names parsed.")

    return chord, notes

def main():
    global DEBUG

    print("Interactive chord/melody analyzer (21-mode matching)")
    print(f"Global key: {GLOBAL_KEY} major")
    print(f"Debug level: {DEBUG} (0..5)")
    print("Input format: [chord]: note1, note2, note3 ...")
    print('Commands: "quit", or "debug=N" to set debug level.\n')

    while True:
        s = input("Enter > ").strip()
        if not s:
            continue
        if s.lower() == "quit":
            print("Goodbye.")
            break
        if s.lower().startswith("debug="):
            try:
                DEBUG = int(s.split("=", 1)[1].strip())
                if DEBUG < 0 or DEBUG > 5:
                    raise ValueError
                print(f"Debug set to {DEBUG}.")
            except ValueError:
                print("Error: debug must be an integer 0..5.")
            continue

        try:
            chord, notes = parse_cli_line(s)
            result = analyze_chord_and_melody(chord, notes, GLOBAL_KEY)
        except ValueError as e:
            print(f"Error: {e}")
            print("Please type again.")
            continue

        print("\n====================================")
        print(f"Chord: {result['chord']['symbol']} (root {result['chord']['root']}, quality {result['chord']['quality']})")
        print(f"Global key: {result['global_key']} major")
        print(f"Roman numeral (by root in global key): {result['roman']} (degree {result['degree_in_key']})")

        bm = result["best_mode"]
        print("\nBest mode match (rooted on chord root):")
        print(f"  {bm['family']} :: {bm['name']}")
        print(f"  score={bm['score']:.3f} (melody_score={bm['melody_score']:.3f})")
        if bm["missing_core"]:
            print(f"  WARNING missing core chord tones (pcs): {bm['missing_core']}")
        if bm["missing_extra"]:
            print(f"  missing extension/alteration tones (pcs): {bm['missing_extra']}")

        print("\nAlternatives:")
        for a in result["alternatives"]:
            print(f"  - {a['family']} :: {a['name']}  score={a['score']:.3f}  melody_score={a['melody_score']:.3f}"
                  f"  missing_core={len(a['missing_core'])} missing_extra={len(a['missing_extra'])}")

        print("\nMelody numeral labels (relative to chord root):")
        for i, (n, deg) in enumerate(zip(result["melody_notes"], result["melody_degrees"])):
            print(f"  [{i}] {n:3} -> {deg}")

        print("\nPer-note function tags:")
        for i, labs in result["functions"].items():
            if labs:
                print(f"  index {i}, note {result['melody_notes'][i]}: {', '.join(sorted(set(labs)))}")

        print("====================================\n")

if __name__ == "__main__":
    main()
