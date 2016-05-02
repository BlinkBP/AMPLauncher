#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from subprocess import Popen, PIPE

class AMPLauncher(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="AMPLauncher")
        
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                               homogeneous=False,
                               spacing=6)
        self.add(self.mainBox)
        self.set_up_interface()

    def set_up_interface(self):
        #Filepath entry
        self.filePathEntry = Gtk.Entry()
        self.fileBox = Gtk.Box(homogeneous=True,spacing=6)
        self.fileBox.add(self.filePathEntry)
        #File dialog button
        self.chooseFileBtn = Gtk.Button(label="Open File")
        self.chooseFileBtn.connect("clicked", self.on_open_file_clicked)
        self.fileBox.add(self.chooseFileBtn)
        self.mainBox.add(self.fileBox)
        #ao/vo combo boxes
        self.voLabel = Gtk.Label("Select video driver:")
        self.aoLabel = Gtk.Label("Select audio driver:")
        self.voComboBox = Gtk.ComboBoxText()
        self.aoComboBox = Gtk.ComboBoxText()
        self.set_combo_box(self.voComboBox, self.get_vo_ao("vo"))
        self.set_combo_box(self.aoComboBox, self.get_vo_ao("ao"))
        self.comboBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                spacing=6)
        self.comboBox.add(self.voLabel)
        self.comboBox.add(self.voComboBox)
        self.comboBox.add(self.aoLabel)
        self.comboBox.add(self.aoComboBox)
        self.mainBox.add(self.comboBox)
        #lavdopts
        self.lavdoptsLabel = Gtk.Label("lavdopts (MPEG-1/2 and H.264 only):")
        self.fsCheckBtn = Gtk.CheckButton("Fullscreen")
        self.fsCheckBtn.connect("toggled", self.on_fullscreen_toggle)
        self.threadsSpinBtn = Gtk.SpinButton()
        adjustment = Gtk.Adjustment(1, 1, self.get_threads(), 1)
        self.threadsSpinBtn.set_adjustment(adjustment)
        self.lavdoptsBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                   spacing=6)
        self.lavdoptsBox.add(self.lavdoptsLabel)
        self.lavdoptsBox.add(self.fsCheckBtn)
        self.lavdoptsBox.add(self.threadsSpinBtn)
        self.mainBox.add(self.lavdoptsBox)
        
    def set_combo_box(self, comboBox, entries):
        for entry in entries:
            comboBox.append_text(entry)

    def get_vo_ao(self, opt):
        args = ["mplayer", "-" + opt, "help"]
        out, err = Popen(args, stdout=PIPE).communicate()
        output = out.decode("utf-8")
        output = output.replace("\t", " ")
        index = output.find(":")
        vo = str.split(output[index+2:], '\n')
        return vo[:-2]

    def get_threads(self):
        args = ["nproc", "--all"]
        out, err = Popen(args, stdout=PIPE).communicate()
        return int(out.decode("utf-8"))

    def on_fullscreen_toggle(self, button):
        pass
    
    def on_open_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a video file",
                                       self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file_path.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        
win = AMPLauncher()        
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
