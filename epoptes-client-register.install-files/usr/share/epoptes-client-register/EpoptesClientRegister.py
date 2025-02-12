#!/usr/bin/env python
# -*- coding: utf-8 -*

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import signal
import gettext
import sys
import threading
import copy
import subprocess
import os
import N4dManager
import xmlrpc.client as n4dclient
import ssl
import time
import Dialog
#import HomeEraserServer

signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.textdomain('epoptes-client-register')
_ = gettext.gettext



class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

#class_spinner



class EpoptesClientRegister:
	
	DEBUG=False

	server="server"

	n4d_var_code="CENTER_CODE"
	n4d_var_classroom="CONTROLLED_CLASSROOM"
	
	server_list=[]
	aulas=[]
	
	def dprint(self,arg):
		if EpoptesClientRegister.DEBUG:
			print("[EpoptesClientRegisterGUI] %s"%arg)
		
	#def dprint	
	
	
	def __init__(self,args_dic):

		self.n4d_man=N4dManager.N4dManager()
		self.n4d_man.set_server(args_dic[self.server])
		print("Server is: %s"%args_dic[self.server])
		print(args_dic)

		
		if args_dic["gui"]:
			
			self.start_gui()
			GObject.threads_init()
			Gtk.main()
		
	#def __init__(self):

	
	def start_gui(self):

		builder=Gtk.Builder()
		builder.set_translation_domain('epoptes-client-register-gui')
		builder.add_from_file("/usr/share/epoptes-client-register/rsrc/epoptes-client-register.ui")
		self.main_window=builder.get_object("main_window")
		self.main_window.set_icon_from_file('/usr/share/epoptes-client-register/rsrc/n4d-epoptes.svg')

		self.main_box=builder.get_object("main_box")
		self.login_box=builder.get_object("login_box")
		self.main_content_box=builder.get_object("main_content_box")
		
		self.stack=Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack.set_transition_duration(500)
		self.stack.add_titled(self.login_box,"login","login")
		self.stack.add_titled(self.main_content_box,"main","main")
		
		self.stack.show_all()
		
		self.main_box.pack_start(self.stack,True,True,5)
		
		self.login_button=builder.get_object("login_button")
		self.entry_user=builder.get_object("entry3")
		self.entry_password=builder.get_object("entry1")
		self.login_msg_label=builder.get_object("login_msg_label")
		
		#self.separator3 = builder.get_object("separator3")
		#self.separator4 = builder.get_object("separator4")

		self.refresh_button=builder.get_object("refresh_button")
		#self.refresh_button.set_label("Refresh")
		self.ok_button=builder.get_object("ok_button")
		self.cancel_button=builder.get_object("cancel_button")
		self.center_code_label=builder.get_object("label1")
		self.center_code=builder.get_object("entry2")
		self.aula_combo=builder.get_object("aula_combo")
		self.register_msg_label=builder.get_object("register_msg_label")
		
		#test si tenemos listado de Ips reseervadas para los servers de los carritos
		# generacion listado de carros disponibles
		context=ssl._create_unverified_context()
		c_local=n4dclient.ServerProxy('https://localhost:9779',context=context,allow_none=True)
		epoptes_servers=c_local.get_variable("EPOPTES_SERVERS")
		print(epoptes_servers)
		#server_list=epoptes_servers["return"]
		if self.server_list==None:
			print("Network Variable is empty, please call to SAI.")
			self.login_button.set_sensitive(False)
			self.login_msg_label.set_text(_("You don't have reserved server Ips..."))
			sys.exit(1)
		for elem in epoptes_servers["return"]:
			self.server_list.append(elem.split('/')[0])
		print("EPOPTES_SERVERS: %s"%(self.server_list))

		#generate carritos list for combobox
		for count,ele in enumerate(self.server_list,start=1):
			self.aulas.append('Carro '  +str(count))
		print('Carritos List: %s'%self.aulas)
		self.login_button.set_sensitive(True)

		cod_center=self.cod_center_capture()
		aula_store_dates=self.comboboxAulas()

		self.center_code.hide()
		self.refresh_button.hide()
		self.center_code_label.hide()

		self.center_code.set_text(cod_center)

		self.aula_combo.set_model(aula_store_dates)
		self.aula_combo.connect("changed", self.on_aula_combo_changed)
		self.renderer_text = Gtk.CellRendererText()
		self.aula_combo.pack_start(self.renderer_text, True)
		self.aula_combo.add_attribute(self.renderer_text, "text", 0)
		
		self.spinner=builder.get_object("spinner")
			
		
		
		self.set_css_info()
		
		self.connect_signals()		
		self.main_window.show()
		
	#def start_gui
	




	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()                     
		f=Gio.File.new_for_path("/usr/share/epoptes-client-register/EpoptesClientRegister.css")
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
		
		self.refresh_button.set_name("OPTION_BUTTON")
		self.login_button.set_name("OPTION_BUTTON")
		self.ok_button.set_name("OPTION_BUTTON")
		self.cancel_button.set_name("OPTION_BUTTON")
			
	#def set-css_info
	
	
	def connect_signals(self):
			
		self.main_window.connect("destroy",Gtk.main_quit)
		
		
		self.login_button.connect("clicked",self.login_clicked)
		self.refresh_button.connect("clicked",self.refresh_clicked)
		self.entry_password.connect("activate",self.entries_press_event)

		self.ok_button.connect("clicked",self.press_ok_button)
		self.cancel_button.connect("clicked",self.press_cancel_button)
		
	#def connect_signals



	# SIGNALS #######################################################	
	
	def entries_press_event(self,entry):
		
		self.login_clicked(None)
		
	#def entries_press_event
	


	def login_clicked(self,button):
		
		self.login_button.set_sensitive(False)
		self.login_msg_label.set_text(_("Validating user..."))
		
		user=self.entry_user.get_text()
		password=self.entry_password.get_text()
		self.user_val=(user,password)
		server="localhost"
		
		self.validate_user(user,password)
		
	#def login_clicked



	def press_ok_button(self,button):

		try:
			#file="/etc/default/epoptes-client"
			self.ok_button.set_sensitive(False)
			self.cancel_button.set_sensitive(False)
			aula=self.on_aula_combo_changed(self.aula_combo)
			center_code=self.center_code.get_text()
			
			if "Error" in center_code  or  "Error" in aula:
				self.register_msg_label.set_markup("<span foreground='red'>"+_("Error Computer registering")+"</span>")
				self.dprint("Error Computer registering")
				self.register_msg_label.set_markup("<span foreground='red'>"+_("Error Computer registering")+"</span>")
				
			else:
				if "None" in aula:
					self.register_msg_label.set_markup("<span foreground='blue'>"+_("Registered failed, please select one clasroom in list.")+"</span>")
					self.dprint("Registered failed, please select one clasroom in list.")
					self.register_msg_label.set_markup("<span foreground='red'>"+_("Registered failed, please select one clasroom in list.")+"</span>")
				else:
					print("- Center Code: %s"%center_code)
					print("- Aula: %s"%aula)
					if aula=='Aula':
						index=0
					else:
						for i, elem in enumerate(self.aulas):
							if elem == aula:
								index=i
					for i, elem in enumerate(self.server_list):
						if i == index:
							ipserver=elem
					
					fail_set_variable=False
					self.dprint("Computer registered")
					if self.n4d_man.set_variable(self.n4d_var_code,center_code):
						self.dprint("     - Center Code: %s"%center_code)
					else:
						fail_set_variable=True
					if self.n4d_man.set_variable(self.n4d_var_classroom,aula):
						self.dprint("     - Classroom: %s"%aula)
					else:
						fail_set_variable=True

					if fail_set_variable:
						self.dprint("Error Computer registered")
						self.register_msg_label.set_markup("<span foreground='red'>"+_("Error Computer registered")+"</span>")
					else:
						self.register_msg_label.set_markup("<span foreground='blue'>"+_("Computer registered  - Carrito:%s - Please restart the Xsession "%(aula))+"</span>")
						
			self.ok_button.set_sensitive(True)
			self.cancel_button.set_sensitive(True)

		except Exception as e:
			self.dprint("Exception Error Computer registered")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Exception Error Computer registered")+"</span>")
			return "Exception Error Computer registered"
		
	#def press_ok_button


	def press_cancel_button(self,button):

		try:
			Gtk.main_quit()
			sys.exit(0)

		except Exception as e:
			self.dprint("Error press_ok_button")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error press_ok_button")+"</span>")
			return "Error press_ok_button"
		
	#def press_ok_button
	



	def validate_user(self,user,password):
		
		t=threading.Thread(target=self.n4d_man.validate_user,args=(user,password,))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.validate_user_listener,t)
		
	#def validate_user
	
	def validate_user_listener(self,thread):
			
		if thread.is_alive():
			return True
				
		self.login_button.set_sensitive(True)
		
		if not self.n4d_man.user_validated:
			print("error validando usuario")
			print(self.n4d_man.user_validated)
			self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user, please only net admin users.")+"</span>")
		else:
			group_found=False
			for g in ["admins","root","sudo","adm"]:
				if g in self.n4d_man.user_groups:
					group_found=True
					break

					
			if group_found:
				# ***START LOG
				self.dprint("")
				self.dprint("** START EPOPTES CLIENT REGISTER GUI **")
				self.dprint("   --------------------------------------------")
				self.dprint("")
				# ##########

				#Test N4d Variables
				fail_get_variable=False
				text_solved=""
				#Initial values from N4D variables
				self.var_code_value=self.n4d_man.get_variable(self.n4d_var_code)
				if self.var_code_value[0]:
					self.center_code.set_text(self.var_code_value[1])
				else:
					fail_get_variable=True
					text_solved=text_solved+"Code value is empty. "

				self.var_classroom_value=self.n4d_man.get_variable(self.n4d_var_classroom)
				self.dprint(self.var_classroom_value)
				if self.var_classroom_value[0]:
					if self.var_classroom_value[1]!="Aula":
						fail_get_variable=True
						self.set_aula_combo(self.var_classroom_value[1])
					else:
						self.set_aula_combo('Aula')
						text_solved=text_solved+"Initial Aula value is empty."
				else:
					self.set_aula_combo('Aula')
					text_solved=text_solved+"Initial Aula value is empty."

				if fail_get_variable:
					self.dprint(text_solved)
					self.register_msg_label.set_markup("<span foreground='blue'>"+text_solved+"</span>")

				

				self.stack.set_visible_child_name("main")
				
			else:
				self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user, please only net admin users.")+"</span>")

	#def validate_user_listener



	def cod_center_capture(self):
		try:
			cod_center="46XXXXX"
			return cod_center
		except Exception as e:
			self.dprint("Error cod_center")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error cod_center")+"</span>")
			return "Error cod_center"

	#def cod_center_capture



	def refresh_clicked(self,button):
		try:
			cod_center=self.cod_center_capture()
			self.center_code.set_text(cod_center)
			self.dprint("Refresh Cod Center, new value: %s"%cod_center)
			self.register_msg_label.set_markup("<span foreground='blue'>"+_("Cod Center recalculated")+"</span>")
			return True
		except Exception as e:
			self.dprint("Error refresh_clicked")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error refresh_clicked")+"</span>")
			return "Error refresh_clicked"

	#def cod_center_capture




	def comboboxAulas(self):
		try:
			aula_store = Gtk.ListStore(str)
			aula_store.append(['Aula'])
			for aula in self.aulas:
				aula_store.append([aula])
			return aula_store
		except Exception as e:
			self.dprint("Error comboboxAulas")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error comboboxAulas")+"</span>")
			return "Error comboboxAulas"

	#def comboboxaulas




	def on_aula_combo_changed(self,combo):
		try:
			tree_iter = combo.get_active_iter()
			aula="None"
			if tree_iter is not None:
				model = combo.get_model()
				aula = model[tree_iter][0]
				self.dprint("Selected: aula=%s" % aula)
			return aula
		except Exception as e:
			self.dprint("Error on_aula_combo_changed")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error on_aula_combo_changed")+"</span>")
			return "Error on_aula_combo_changed"

	#def on_aula_combo_changed


	def set_aula_combo(self,aula):
		try:
			model = self.aula_combo.get_model()
			self.dprint(model)
			self.dprint(model[model.get_iter_first()][0])
			tree_iter=model.get_iter_first()
			while tree_iter is not None:
				if aula in model[tree_iter][0]:
					self.aula_combo.set_active_iter(tree_iter)
					return True
				tree_iter=model.iter_next(tree_iter)

			return False
			self.dprint("Aula is not in combobox")

		except Exception as e:
			self.dprint("Error set_aula_combo")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error set_aula_combo")+"</span>")
			return "Error set_aula_combo"

	#def on_aula_combo_changed
	
	
	def set_new_epoptes_server(self,file,server):
		try:
			file_tmp="/tmp/epoptes_hosts.tmp"
			if os.path.isfile(file_tmp):
				os.remove(file_tmp)
			file_orig=open(file, "r")
			lines=file_orig.readlines()
			newlines = []
			for line in lines:
				if not "server" in line:
					newlines.append(line)
			line = "%s server\n"%server	
			newlines.append(line)
			file_orig.close()
			f=open(file_tmp,"a")
			f.writelines(newlines)
			f.close()
			#os.system('touch /etc/pepito_grillo')
			if os.path.isfile(file):
				os.remove(file)
			os.system('mv %s %s'%(file_tmp, file))
			
			return True
		
		except Exception as e:
			self.dprint("Error set_new_epoptes_server")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error set_new_epoptes_server")+"</span>")
			return False
			
	#def_set_new_epoptes_server
	
	

	def restart_client_service(self):
		try:
			cmd="systemctl restart epoptes-client.service"
			os.system(cmd)
			self.dprint("Restarting epoptes-client-service...")
			return True

		except Exception as e:
			self.dprint("Error restart_client_service")
			self.register_msg_label.set_markup("<span foreground='red'>"+_("Error restart_client_service")+"</span>")
			return "Error restart_client_service"

	#def restart_client_service



#class LliurexPerfilreset


if __name__=="__main__":
	
	pass
	
