from tkinter import *
import listen
from threading import Thread, Event


# class for stoppable thread
# runs record while active and finalize_wav upon termination
class RecordController(object):
	def __init__(self):
		self.thread = None
		self.stop_threads = Event()

	def loop(self):
		while not self.stop_threads.is_set():
			listen.record()

	def start(self):
		self.stop_threads.clear()
		self.thread = Thread(target=self.loop)
		self.thread.start()

	def stop(self):
		self.stop_threads.set()
		self.thread.join()
		self.thread = None
		listen.finalize_wav()


# runs gen_lily and writes generated lilypond code to text widget
def generate():
	listen.gen_lily(clef_var.get(), time_sig.get())
	with open("my_lily.ly", 'r') as f:
		lily_edit.insert(INSERT, f.read())
	f.close()


# write content of text widget to my_lily.ly
def save_file():
	f = open("my_lily.ly", 'w')
	f.write(lily_edit.get('1.0', 'end'))
	f.close()


# tkinter object
window = Tk()
# Working title
window.title("Microphone to Music")
window.geometry("700x900")

# label for clef drop down menu
clef_label = Label(window, text="Clef:")
clef_label.grid(row=0, sticky=W)

# clef drop down menu, def value set to treble
clef_var = StringVar(window)
clef_var.set("treble")
clef_menu = OptionMenu(window, clef_var, "treble", "bass")
clef_menu.grid(row=0, column=2, sticky=W)

# label for time signature menu
time_sig = StringVar()
time_label = Label(window, text="Time Signature:")
time_label.grid(row=1, column=0, columnspan=2, sticky=W)

# time signature text entry menu
time_sig_menu = Entry(window, width=5)
time_sig_menu.insert(END, "4/4")
time_sig_menu.grid(row=1, column=2)
set_t = Button(window, text="enter", command=lambda: time_sig.set(time_sig_menu.get()))
set_t.grid(row=1, column=3, sticky=W)

# record and stop recording buttons
control = RecordController()
record_b = Button(window, text="record", command=control.start)
record_b.grid(row=2, column=0, sticky=W)
stop_b = Button(window, text="stop", command=control.stop)
stop_b.grid(row=2, column=1)

# text widget that will display generated lily pond code
lily_edit = Text(window, width=700, height=700)
lily_edit.grid(row=4, column=0, columnspan=700)

# generate lily pond code button
gen_b = Button(window, text="generate lilypond", command=lambda: generate())
gen_b.grid(row=3, column=0, sticky=W, columnspan=2)

# write current contents of text widget to my_lily.ly
save_b = Button(window, text="save lilypond", command=lambda: save_file())
save_b.grid(row=3, column=2)

window.mainloop()
