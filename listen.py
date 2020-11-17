import wave
from math import isclose
import pyaudio
from aubio import notes, source, tempo, onset
from numpy import median, diff

frames = []
# global constants defined here so record() can be looped through by a thread
# number of frames signals are split into
CHUNK = 1024
FORM = pyaudio.paInt16
SAMPLES = 2
# frame sampling rate
RATE = 44100
PY_AUDIO = pyaudio.PyAudio()
STREAM = PY_AUDIO.open(format=FORM, channels=SAMPLES, rate=RATE, input=True, frames_per_buffer=CHUNK)


# reads in data from stream, thread will loop when user presses record
def record():
	data = STREAM.read(CHUNK)
	frames.append(data)


# stops stream, terminates PyAudio instance, writes data to output.wav
def finalize_wav():
	# close microphone stream
	STREAM.stop_stream()
	STREAM.close()
	PY_AUDIO.terminate()

	# output recording to output.wav
	wave_filename = "output.wav"
	wf = wave.open(wave_filename, 'wb')
	wf.setnchannels(SAMPLES)
	wf.setsampwidth(PY_AUDIO.get_sample_size(FORM))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()


# returns every midi value of notes from wave file
def get_notes(file_name):
	# TODO include rests
	down_sample = 1
	sample_rate = 44100 // down_sample
	# fft size
	win_s = 512 // down_sample
	# hop size
	hop_s = 256 // down_sample

	s = source(file_name, sample_rate, hop_s)
	sample_rate = s.samplerate

	notes_o = notes("default", win_s, hop_s, sample_rate)

	# total number of frames read
	total_frames = 0
	# list containing all read in notes
	all_notes = []

	while True:
		# extract notes from output.wav and append ot all_notes list
		o_samples, read = s()
		new_note = notes_o(o_samples)
		if new_note[0] != 0:
			all_notes.append(new_note[0])
		total_frames += read
		if read < hop_s:
			break

	return all_notes


# returns bpm of recorded wave file
def get_bpm(file_name):
	down_sample = 1
	sample_rate = 44100 // down_sample
	# fft size
	win_s = 512 // down_sample
	# hop size
	hop_s = 256 // down_sample
	s = source(file_name, sample_rate, hop_s)
	sample_rate = s.samplerate
	tempo_o = tempo("default", win_s, hop_s, sample_rate)

	# List of beats, in samples
	beats = []
	total_frames = 0

	while True:
		# extract beats from .wav file
		o_samples, read = s()
		is_beat = tempo_o(o_samples)
		if is_beat:
			this_beat = tempo_o.get_last_s()
			beats.append(this_beat)
		total_frames += read
		if read < hop_s:
			break

	bpm = 0
	if len(beats) > 1:
		# use beats to find bpm of .wav file
		if len(beats) < 4:
			print("too few beats found")
		bpm = 60. / diff(beats)
		bpm = median(bpm)
	else:
		print("no beats found")

	return round(bpm, 0)


# returns list of note onset times from wave file
def get_onsets(file_name):
	down_sample = 1
	sample_rate = 44100 // down_sample
	# fft size
	win_s = 512 // down_sample
	# hop size
	hop_s = 256 // down_sample
	s = source(file_name, sample_rate, hop_s)
	sample_rate = s.samplerate

	onsets_o = onset("default", win_s, hop_s, sample_rate)

	# list of onsets, in samples
	onsets = []

	# total number of frames read
	total_frames = 0
	while True:
		o_samples, read = s()
		if onsets_o(o_samples):
			onsets.append(round(onsets_o.get_last_s(), 3))
		total_frames += read
		if read < hop_s:
			break

	return onsets


# finds musical length of each note where b_note is the note that gets the beat
def note_length(onsets, beats_per, b_note):
	# list of note lengths in the order they were played
	note_lengths = []
	# calculate beats per second
	bps = (60 / beats_per) * b_note
	for index in range(len(onsets)-1):
		if index != len(onsets)-1:
			note_lengths.append(round(float(onsets[index+1]-onsets[index])/bps, 2))

	# TODO calculate actual last note length
	note_lengths.append(0.25)

	return note_lengths


# creates tuple list with pairs of note values and note lengths
def pair_value_length(note_values, note_lengths):
	complete_notes = list(zip(note_values, note_lengths))
	return complete_notes


# writes lily pond source code to .ly file
def to_lily_pond(complete_notes, time_sig, clef):
	# note values in lily code
	lily_names = []
	# note lengths in lily code
	lily_lengths = []
	for note in complete_notes:
		lily_names.append(get_lily_note_name(note[0]))
		lily_lengths.append(get_lily_note_length(note[1]))

	lily_code = zip(lily_names, lily_lengths)

	lily_file = open("my_lily.ly", "a")
	lily_file.write("{\n\t\\time " + time_sig + "\n\t\\clef " + clef + "\n\t")

	lily_file.write(' '.join('%s%s' % x for x in lily_code))

	lily_file.write("\n}")
	lily_file.close()


# returns corresponding lilypond for given midi_note
# only called if midi_note is below C3
def get_low_oct(midi_note):
	if midi_note == 36:
		return "c,"
	if midi_note == 37:
		return "cis,"
	if midi_note == 38:
		return "d,"
	if midi_note == 39:
		return "dis,"
	if midi_note == 40:
		return "e,"
	if midi_note == 41:
		return "f,"
	if midi_note == 42:
		return "fis,"
	if midi_note == 43:
		return "g,"
	if midi_note == 44:
		return "gis,"
	if midi_note == 45:
		return "a,"
	if midi_note == 46:
		return "ais,"
	if midi_note == 47:
		return "b,"


# returns lily pond code for corresponding midi note
def get_lily_note_name(midi_note):
	if midi_note < 48:
		return get_low_oct(midi_note)

	oct_count = 0
	for i in range(48, 97, 12):
		if midi_note == i:
			return "c" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(49, 86, 12):
		if midi_note == i:
			return "cis" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(50, 87, 12):
		if midi_note == i:
			return "d" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(51, 88, 12):
		if midi_note == i:
			return "dis" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(52, 89, 12):
		if midi_note == i:
			return "e" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(53, 90, 12):
		if midi_note == i:
			return "f" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(54, 91, 12):
		if midi_note == i:
			return "fis" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(55, 92, 12):
		if midi_note == i:
			return "g" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(56, 93, 12):
		if midi_note == i:
			return "gis" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(57, 94, 12):
		if midi_note == i:
			return "a" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(58, 95, 12):
		if midi_note == i:
			return "ais" + "'"*oct_count
		oct_count = oct_count + 1

	oct_count = 0
	for i in range(59, 96, 12):
		if midi_note == i:
			return "b" + "'"*oct_count
		oct_count = oct_count + 1

	# invalid midi note value
	return ""
# TODO add key signatures possibly


# returns lily pond code for corresponding note length in decimal form
def get_lily_note_length(decimal_length):
	# whole note
	if isclose(decimal_length, 1, abs_tol=0.015):
		return "1"
	# dotted half note
	if isclose(decimal_length, 0.75, abs_tol=0.015):
		return "2."
	# half note
	if isclose(decimal_length, 0.5, abs_tol=0.015):
		return "2"
	# quarter note
	if isclose(decimal_length, 0.25, abs_tol=0.015):
		return "4"
	# eight note
	if isclose(decimal_length, 0.12, abs_tol=0.015):
		return "8"
	# invalid note length
	else:
		return ""
	# TODO allow for more note lengths


def gen_lily(clef, time_sig):
	file = "output.wav"
	n = get_notes(file)
	o = get_onsets(file)
	b = get_bpm(file)

	lengths = note_length(o, b, int(time_sig[2]))
	all_notes = pair_value_length(n, lengths)

	to_lily_pond(all_notes, time_sig, clef)
