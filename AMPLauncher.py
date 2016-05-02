#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from subprocess import Popen, PIPE

class AMPLauncher(Gtk.Window):

    def __init__(self):
        self.fullscreenToggle = False
        self.lavdoptsToggle = False
        self.lavdoptsThreads = 1
        Gtk.Window.__init__(self, title="AMPLauncher")
        
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                               homogeneous=False,
                               spacing=6)
        self.add(self.mainBox)
        self.set_up_interface()

    def set_up_interface(self):
        #Filepath
        self.filePathEntry = Gtk.Entry()
        self.chooseFileBtn = Gtk.Button(label="Open File")
        self.fileGrid = Gtk.Grid()
        self.filePathEntry.set_hexpand(True)
        self.fileGrid.attach(self.filePathEntry,
                             0,
                             0,
                             2,
                             1)
        self.fileGrid.attach_next_to(self.chooseFileBtn,
                                     self.filePathEntry,
                                     Gtk.PositionType.RIGHT,
                                     1,
                                     1)
        self.mainBox.add(self.fileGrid)
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
        #other options
        self.otherLabel = Gtk.Label("Other options:")
        self.fsCheckBtn = Gtk.CheckButton("Fullscreen")
        self.useLavdoptsBtn = Gtk.CheckButton("Use lavdopts")
        self.threadsLabel = Gtk.Label("Threads(MPEG-1/2 and H.264 only):")
        self.threadsSpinBtn = Gtk.SpinButton()
        adjustment = Gtk.Adjustment(1, 1, self.get_threads(), 1)
        self.threadsSpinBtn.set_adjustment(adjustment)
        self.threadsSpinBtn.set_sensitive(False)
        self.otherBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                   spacing=6)
        self.threadsBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                  spacing=6)
        self.otherBox.add(self.otherLabel)
        self.otherBox.add(self.fsCheckBtn)
        self.otherBox.add(self.useLavdoptsBtn)
        self.threadsBox.add(self.threadsLabel)
        self.threadsBox.add(self.threadsSpinBtn)
        self.otherBox.add(self.threadsBox)
        self.mainBox.add(self.otherBox)
        #Play btn
        self.playBtn = Gtk.Button("Play")
        self.mainBox.add(self.playBtn)
        self.connect_interface()

    def connect_interface(self):
        self.chooseFileBtn.connect("clicked",
                                   self.on_open_file_button_clicked)
        self.useLavdoptsBtn.connect("toggled",
                                       self.on_use_lavdopts_toggle)
        self.fsCheckBtn.connect("toggled",
                                self.on_fullscreen_toggle)
        self.threadsSpinBtn.connect("value-changed",
                                    self.on_spin_button_value_changed)
        self.playBtn.connect("clicked",
                             self.on_play_button_clicked)
        
        
    def set_combo_box(self, comboBox, entries):
        for entry in entries:
            comboBox.append_text(entry)

    def get_vo_ao(self, opt):
        args = ["mplayer", "-" + opt, "help"]
        out, err = Popen(args, stdout=PIPE).communicate()
        output = out.decode("utf-8")
        output = output.replace("\t", " ")
        index = output.find(":")
        o = str.split(output[index+2:], '\n')
        if opt == "vo":
            self.vo = o[:-2]
        elif opt == "ao":
            self.ao = o[:-2]
        return o[:-2]

    def get_vo_ao_value(self, opt):
        if opt == "vo":
            value = self.vo[self.voComboBox.get_active()]
        elif opt == "ao":
            value = self.ao[self.aoComboBox.get_active()]
        index = value[2:].find(" ")+2
        return value[1:index]

    def get_threads(self):
        args = ["nproc", "--all"]
        out, err = Popen(args, stdout=PIPE).communicate()
        return int(out.decode("utf-8"))
    
    def on_open_file_button_clicked(self, widget):
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
            self.filePathEntry.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def on_use_lavdopts_toggle(self, button):
        isSensitive = self.threadsSpinBtn.get_property('sensitive')
        if isSensitive:
            self.threadsSpinBtn.set_sensitive(False)
            self.lavdoptsToggle = False
        else:
            self.threadsSpinBtn.set_sensitive(True)
            self.lavdoptsToggle = True
        
    def on_fullscreen_toggle(self, button):
        if self.fullscreenToggle:
            self.fullscreenToggle = False
        else:
            self.fullscreenToggle = True

    def on_spin_button_value_changed(self, button):
        self.lavdoptsThreads = self.threadsSpinBtn.get_value()

    def on_play_button_clicked(self, button):
        args = ["mplayer", '"' + self.filePathEntry.get_text() + '"',
                "-ao", self.get_vo_ao_value("ao"),
                "-vo", self.get_vo_ao_value("vo")]
        print(args)
        
    def add_filters(self, dialog):
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        
win = AMPLauncher()        
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
