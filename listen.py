import pyaudio
import wave
from aubio import notes, source, tempo, onset
from numpy import median, diff


def print_tests():
	# file = record_wav()
	file = "hot-cross-buns.wav"
	n = get_notes(file)
	o = get_onsets(file)
	b = get_bpm(file)
	lengths = note_length(o, b)
	all_notes = pair_value_length(n, lengths)

	print("NOTES: ")
	for i in n:
		print(i, end=" ")
	print()

	print("ONSETS: ")
	for i in o:
		print(i, end=" ")
	print()

	print("BPM: ")
	print(b)

	print("LENGTHS: ")
	for i in lengths:
		print(i, end=" ")
	print()

	print("PAIRED NOTES AND LENGTHS: ")
	for x, y in all_notes:
		print("( ", x, y, " )", end=" ")
	print()
	print("LILY NOTE NAMES AND LENGTHS: ")
	to_lily_pond(all_notes)


# reads input from microphone and writes to wave file
def record_wav():
	# number of frames signals are split into
	chunk = 1024
	form = pyaudio.paInt16
	samples = 2
	# frame sampling rate
	rt = 44100
	# output file of audio recording
	wave_filename = "output.wav"

	p = pyaudio.PyAudio()

	stream = p.open(format=form, channels=samples, rate=rt, input=True, frames_per_buffer=chunk)

	print("* recording")

	frames = []

	while True:
		try:
			data = stream.read(chunk)
			frames.append(data)
		# break with ctrl+c
		except KeyboardInterrupt:
			break

	print("* done recording")

	# close microphone stream
	stream.stop_stream()
	stream.close()
	p.terminate()

	# output recording to output.wav
	wf = wave.open(wave_filename, 'wb')
	wf.setnchannels(samples)
	wf.setsampwidth(p.get_sample_size(form))
	wf.setframerate(rt)
	wf.writeframes(b''.join(frames))
	wf.close()

	return wave_filename


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
		samples, read = s()
		new_note = notes_o(samples)
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
		samples, read = s()
		is_beat = tempo_o(samples)
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
		samples, read = s()
		if onsets_o(samples):
			onsets.append(round(onsets_o.get_last_s(), 3))
		total_frames += read
		if read < hop_s:
			break

	return onsets


# finds musical length of each note
def note_length(onsets, beats_per):
	# list of note lengths in the order they were played
	note_lengths = []
	# TODO: replace 4 with number of beats per measure
	# calculate beats per second
	bps = (60 / beats_per) * 4
	for index in range(len(onsets)):
		if index != 0:
			note_lengths.append(round(float(onsets[index] - onsets[index-1])/bps, 2))
		else:
			note_lengths.append(round(float(onsets[index+1] - onsets[index])/bps, 2))

	return note_lengths


def pair_value_length(note_values, note_lengths):
	complete_notes = list(zip(note_values, note_lengths))
	return complete_notes


def to_lily_pond(complete_notes):
	for note in complete_notes:
		print(get_lily_note_name(note[0]))
	# TODO note lengths


def get_lily_note_name(midi_note):
	for i in range(24, 97, 12):
		if midi_note == i:
			return "c"
	for i in range(25, 86, 12):
		if midi_note == i:
			return "cis"
	for i in range(26, 87, 12):
		if midi_note == i:
			return "d"
	for i in range(27, 88, 12):
		if midi_note == i:
			return "dis"
	for i in range(28, 89, 12):
		if midi_note == i:
			return "e"
	for i in range(29, 90, 12):
		if midi_note == i:
			return "f"
	for i in range(30, 91, 12):
		if midi_note == i:
			return "fis"
	for i in range(31, 92, 12):
		if midi_note == i:
			return "g"
	for i in range(32, 93, 12):
		if midi_note == i:
			return "gis"
	for i in range(33, 94, 12):
		if midi_note == i:
			return "a"
	for i in range(34, 95, 12):
		if midi_note == i:
			return "ais"
	for i in range(35, 96, 12):
		if midi_note == i:
			return "b"
# TODO: return different if key signature is sharp or flat


# TODO def get_lily_note_lengths


if __name__ == "__main__":
	print_tests()
