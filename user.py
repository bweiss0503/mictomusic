from tkinter import *
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
		clef_label = Label(self, text="Clef:")
		clef_label.grid(row=0, sticky=W)

		# clef drop down menu, def value set to treble
		self.clef_var = StringVar(self)
		self.clef_var.set("treble")
		self.clef_menu = OptionMenu(self, self.clef_var, "treble", "bass")
		self.clef_menu.grid(row=0, column=2, sticky=W)

		# label for time signature menu
		self.time_sig = StringVar()
		self.time_label = Label(self, text="Time Signature:")
		self.time_label.grid(row=1, column=0, columnspan=2, sticky=W)

		# time signature text entry menu
		self.time_sig_menu = Entry(self, width=5)
		self.time_sig_menu.insert(END, "4/4")
		self.time_sig_menu.grid(row=1, column=2)
		# set default value so user doesn't have to press enter
		self.time_sig.set(self.time_sig_menu.get())
		self.set_t = Button(self, text="enter", command=lambda: self.time_sig.set(self.time_sig_menu.get()))
		self.set_t.grid(row=1, column=3, sticky=W)

		# record and stop recording buttons
		self.record_b = Button(self, text="record", command=self.control.start)
		self.record_b.grid(row=2, column=0, sticky=W)
		self.stop_b = Button(self, text="stop", command=self.control.stop)
		self.stop_b.grid(row=2, column=1)

		# text widget that will display generated lily pond code
		self.lily_edit = Text(self, width=600, height=600)
		self.lily_edit.grid(row=4, column=0, columnspan=600)

		# generate lily pond code button
		self.gen = Button(
			self,
			text="generate lilypond",
			command=lambda: self.generate()
		)
		self.gen.grid(row=3, column=0, sticky=W, columnspan=2)

		# write current contents of text widget to my_lily.ly
		self.save_b = Button(self, text="save lilypond", command=lambda: self.save_file())
		self.save_b.grid(row=3, column=2)

	# runs gen_lily and writes generated lilypond code to text widget
	def generate(self):
		self.listener.gen_lily(self.clef_var.get(), self.time_sig.get())
		with open("my_lily.ly", 'r') as f:
			self.lily_edit.insert(INSERT, f.read())
		f.close()

	# write content of text widget to my_lily.ly
	def save_file(self):
		f = open("my_lily.ly", 'w')
		f.write(self.lily_edit.get('1.0', 'end'))
		f.close()


if __name__ == "__main__":
	window = MicToMusic()
	window.mainloop()
