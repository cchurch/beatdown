NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi_note_to_int(v):
    for n, note in enumerate(NOTES):
        if str(v).upper().startswith(note.upper()):
            return (int(str(v)[len(note):]) + 2) * 12 + n
    raise ValueError('invalid note')


def int_to_midi_note(v):
    return '{:s}{:d}'.format(NOTES[int(v) % 12], int(v) // 12 - 2)
