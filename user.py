import subprocess
from os import path
from tkinter import *
from tkinter import messagebox
import listen
import record_controller as rc


class MicToMusic(Tk):
	def __init__(self):
		super().__init__()
		self.listener = listen.Listener()
		self.control = rc.RecordController(self.listener)
		self.title("Microphone to Music")
		self.geometry("600x700")

		# label for clef drop down menu
		self.clef_label = Label(self, text="Clef:")
		self.clef_label.grid(row=0, column=0, sticky=W)

		# clef drop down menu, def value set to treble
		self.clef_var = StringVar(self)
		self.clef_var.set("treble")
		self.clef_menu = OptionMenu(self, self.clef_var, "treble", "bass")
		self.clef_menu.grid(row=0, column=1, columnspan=2, sticky=W)

		# label for time signature menu
		self.time_sig = StringVar()
		self.time_label = Label(self, text="Time Signature:")
		self.time_label.grid(row=1, column=0, columnspan=3, sticky=W)

		# time signature text entry menu, default value of 4/4
		self.time_sig_menu = Entry(self, width=4)
		self.time_sig_menu.insert(END, "4/4")
		self.time_sig_menu.grid(row=1, column=2, columnspan=1, sticky=W)

		# record and stop recording buttons
		self.record_b = Button(self, text="Record", command=lambda: self.record())
		self.record_b.grid(row=2, column=0, columnspan=2, sticky=W)
		self.stop_b = Button(self, text="Stop", command=lambda: self.stop_r())
		self.stop_b.grid(row=2, column=1, sticky=W)

		# generate lily pond code button
		self.gen = Button(
			self,
			text="Generate Lilypond",
			command=lambda: self.generate()
		)
		self.gen.grid(row=3, column=0, sticky=W, columnspan=2)

		# write current contents of text widget to my_lily.ly
		self.save_b = Button(self, text="Save Lilypond", command=lambda: self.save_file())
		self.save_b.grid(row=3, column=2)

		# open pdf of sheet music in system's default pdf viewer
		self.b_open = Button(self, text="View Sheet Music", command=lambda: self.open_pdf())
		self.b_open.grid(row=3, column=3, sticky=W)

		# text widget that will display generated lily pond code
		self.lily_edit = Text(self, width=600, height=600)
		self.lily_edit.grid(row=4, column=0, columnspan=600)

	# runs gen_lily and writes generated lilypond code to text widget
	def generate(self):
		self.time_sig.set(self.time_sig_menu.get())
		matched = re.match(r'\d?\d/\d?\d', self.time_sig.get())
		# Error if user enters time signature that doesn't fit typical pattern
		if not bool(matched):
			messagebox.showerror("", "Please enter a valid time signature.")
			return

		if not path.exists("output.wav"):
			messagebox.showerror("", "Please make sure you have recorded first.")
			return

		self.lily_edit.delete("1.0", "end")
		self.listener.gen_lily(self.clef_var.get(), self.time_sig.get())
		with open("my_lily.ly", 'r') as f:
			self.lily_edit.insert(INSERT, f.read())
		f.close()

	# write content of text widget to my_lily.ly
	def save_file(self):
		f = open("my_lily.ly", 'w')
		f.write(self.lily_edit.get('1.0', 'end'))
		f.close()

	@staticmethod
	def open_pdf():
		p = subprocess.Popen(["lilypond", "-fpdf", "./my_lily.ly"], shell=True)
		p.wait()
		subprocess.Popen("my_lily.pdf", shell=True)

	def record(self):
		if path.exists("output.wav"):
			result = messagebox.askquestion("", "Do you wish to overwrite output.wav?")
			if result == 'yes':
				self.listener = listen.Listener()
				self.control = rc.RecordController(self.listener)
				self.control.start()
			else:
				return
		else:
			self.control.start()

	def stop_r(self):
		if self.control.stop_threads.isSet():
			messagebox.showerror("", "You are not currently recording.")
			return
		else:
			self.control.stop()


if __name__ == "__main__":
	window = MicToMusic()
	window.mainloop()

# TODO add image in top right of window
# TODO add note length optional command
