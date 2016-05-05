#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from subprocess import Popen, PIPE, call
import os
import getpass
import sys

class AMPLauncher(Gtk.Window):

    def __init__(self):
        #final command variables
        self.displayMode = ""
        self.presets = []
        self.lavdoptsToggle = False
        self.lavdoptsThreads = 1
        
        Gtk.Window.__init__(self, title="AMPLauncher")
        #main box holding GUI elements
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                               homogeneous=False,
                               spacing=6)
        self.add(self.mainBox)
        #set up all GUI elements
        self.set_up_interface()
        self.load_presets()
        
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
        ##Display mode
        self.wndRadioBtn = Gtk.RadioButton.new_from_widget(None)
        self.wndRadioBtn.set_label("Windowed")
        self.fsRadioBtn = Gtk.RadioButton.new_from_widget(self.wndRadioBtn)
        self.fsRadioBtn.set_label("Fullscreen")
        self.zmRadioBtn = Gtk.RadioButton.new_from_widget(self.wndRadioBtn)
        self.zmRadioBtn.set_label("Zoomed")
        ##lavdopts
        self.useLavdoptsBtn = Gtk.CheckButton("Use lavdopts")
        self.threadsLabel = Gtk.Label("Threads(MPEG-1/2 and H.264 only):")
        self.threadsSpinBtn = Gtk.SpinButton()
        adjustment = Gtk.Adjustment(1, 1, self.get_threads(), 1)
        self.threadsSpinBtn.set_adjustment(adjustment)
        self.threadsSpinBtn.set_sensitive(False)
        #presets
        self.presetsLabel = Gtk.Label("Presets:")
        self.presetsComboBox = Gtk.ComboBoxText()#text loaded in load_presets()
        self.savePresetBtn = Gtk.Button("Save preset")
        self.runPresetBtn = Gtk.Button("Run preset")
        self.otherBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                   spacing=6)
        self.radioBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                spacing=6)
        self.threadsBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                  spacing=6)
        self.otherBox.add(self.otherLabel)
        self.radioBox.add(self.wndRadioBtn)
        self.radioBox.add(self.fsRadioBtn)
        self.radioBox.add(self.zmRadioBtn)
        self.otherBox.add(self.radioBox)
        self.otherBox.add(self.useLavdoptsBtn)
        self.threadsBox.add(self.threadsLabel)
        self.threadsBox.add(self.threadsSpinBtn)
        self.otherBox.add(self.threadsBox)
        self.presetsBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                 spacing=6)
        self.presetBtnBox = Gtk.Box(Gtk.Orientation.HORIZONTAL,
                                    spacing=6)
        self.presetBtnBox.add(self.savePresetBtn)
        self.presetBtnBox.add(self.runPresetBtn)
        self.presetsBox.add(self.presetsLabel)
        self.presetsBox.add(self.presetsComboBox)
        self.presetsBox.add(self.presetBtnBox)
        self.otherBox.add(self.presetsBox)
        self.mainBox.add(self.otherBox)        
        #Play btn
        self.playBtn = Gtk.Button("Play")
        self.mainBox.add(self.playBtn)
        #Connect all events
        self.connect_interface()

    def connect_interface(self):
        self.chooseFileBtn.connect("clicked",
                                   self.on_open_file_button_clicked)
        self.wndRadioBtn.connect("toggled",
                                 self.on_display_mode_toggled,
                                 "")
        self.fsRadioBtn.connect("toggled",
                                self.on_display_mode_toggled,
                                "-fs")
        self.zmRadioBtn.connect("toggled",
                                   self.on_display_mode_toggled,
                                   "-zoom")
        self.useLavdoptsBtn.connect("toggled",
                                       self.on_use_lavdopts_toggle)
        self.threadsSpinBtn.connect("value-changed",
                                    self.on_spin_button_value_changed)
        self.savePresetBtn.connect("clicked",
                           self.on_save_preset_button_clicked)
        self.runPresetBtn.connect("clicked",
                            self.on_run_preset_button_clicked)
        self.playBtn.connect("clicked",
                             self.on_play_button_clicked)

    def load_presets(self):
        self.path = "/home/" + getpass.getuser() + "/.AMPLauncher"
        if os.path.isdir(self.path):
            for file in os.listdir(self.path):
                self.presetsComboBox.append_text(file)
                self.presets.append(open(self.path + "/" + file).read())
        else:
            os.makedirs(self.path)
                
    def set_combo_box(self, comboBox, entries):
        for entry in entries:
            comboBox.append_text(entry)

    def get_vo_ao(self, opt):
        #get available vo/ao drivers from mplayer command
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
        #get vo/ao active combo box value
        if opt == "vo":
            value = self.vo[self.voComboBox.get_active()]
        elif opt == "ao":
            value = self.ao[self.aoComboBox.get_active()]
        index = value[2:].find(" ")+2
        return value[1:index]

    def get_threads(self):
        #get number of computer's threads using nproc command
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

    def add_filters(self, dialog):
        #Filters for file dialog
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        
    def on_use_lavdopts_toggle(self, button):
        isSensitive = self.threadsSpinBtn.get_property('sensitive')
        if isSensitive:
            self.threadsSpinBtn.set_sensitive(False)
            self.lavdoptsToggle = False
        else:
            self.threadsSpinBtn.set_sensitive(True)
            self.lavdoptsToggle = True
        
    def on_display_mode_toggled(self, button, name):
        self.displayMode = name

    def on_spin_button_value_changed(self, button):
        self.lavdoptsThreads = self.threadsSpinBtn.get_value()

    def on_save_preset_button_clicked(self, button):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK, "Enter preset name:")
        dialogBox = dialog.get_content_area()
        name = "default"
        entry = Gtk.Entry()
        entry.set_text(name)
        entry.show()
        dialogBox.add(entry)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = entry.get_text()
            dialog.destroy()
            self.save_preset(name)
            
    def on_run_preset_button_clicked(self, button):
        cmd = self.presets[self.presetsComboBox.get_active()]
        args = str(cmd).split()
        print(cmd)
        args.insert(1, self.filePathEntry.get_text())
        print(args)
        call(args)

    def save_preset(self, name):
        #save preset in form of a command (string)
        file = open(self.path + "/" + name, "w")
        cmd = ""
        for item in self.get_args():
            cmd += item + " "
        file.write(cmd)
        file.close()
        self.load_presets()
        
    def get_args(self):
        #get an array with all arguments - final command w/o filename
        args = ["mplayer",
                "-ao", self.get_vo_ao_value("ao"),
                "-vo", self.get_vo_ao_value("vo"),
                self.displayMode]
        if self.lavdoptsToggle:
            args.append("-lavdopts")
            args.append("threads=" + str(int(self.lavdoptsThreads)))
        return args
            
    def on_play_button_clicked(self, button):
        #get arguments and add filename, then execute
        args = self.get_args()
        args.insert(1, self.filePathEntry.get_text())
        call(args)

def parse_arguments():
        if sys.argv[1] == "-h":
            print("Read README on github page")
        elif sys.argv[1] == "-v":
            print("AMPLauncher v1.0 Copyright 2016 by BlinkBP")

if len(sys.argv) > 1:
    parse_arguments()
else:
    win = AMPLauncher()        
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
