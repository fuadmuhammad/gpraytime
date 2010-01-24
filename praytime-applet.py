#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet
import gobject
import praytime
import datetime
import sys
import os.path as path
import math

from time import time

class PraytimeApplet:
  applet=None
  timeout_interval=1000
  iid = 0
  delta = 0
  label=None
  next_pray_name=None
  timezone_entry=None
  longitude_entry=None
  latitude_entry=None
  timezone = -6
  longitude = 7
  latitude = 106.650002
  dialog=None
  conf_file = None
  
  prev_unixtime = time()

  def __init__(self,applet,iid):
    self.applet=applet
    self.iid=iid
    self.conf_file=path.expanduser("~/.gpraytime")
    self.read_conf()
    self.delta=self.getNextDeltaPrayTime()
    self.label = gtk.Label(self.parseDeltaPrayTime())
    applet.add(self.label)
    self.create_menu()
    applet.show_all()
    gobject.timeout_add(self.timeout_interval, self.timeout_callback, self)

  def read_conf(self):
    if path.exists(self.conf_file) and path.isfile(self.conf_file):
      try:
        f = open(self.conf_file,"r") 
        self.timezone=int(f.readline())
        self.latitude=float(f.readline())
        self.longitude=float(f.readline())  
      except ValueError:
        pass


  def create_menu(self):
    xml="""
    <popup name="button3">
    <menuitem name="ItemPreferences" 
    verb="Preferences" 
    label="_Preferences" 
    pixtype="stock" 
    pixname="gtk-preferences"/>
    </popup>"""
    verbs = [('Preferences', self.show_preferences)]
    self.applet.setup_menu(xml, verbs, None)
  
  def show_preferences(self,*arguments):
    self.timezone_entry=gtk.Entry()
    self.timezone_entry.set_text(str(self.timezone))
    self.longitude_entry=gtk.Entry()
    self.longitude_entry.set_text(str(self.longitude))
    self.latitude_entry=gtk.Entry()
    self.latitude_entry.set_text(str(self.latitude))
    self.dialog=gtk.Dialog('gPraytime Preferences')
    ok_button = gtk.Button(stock=gtk.STOCK_OK)
    self.dialog.action_area.pack_start(ok_button,True,True,0)
    ok_button.show()
    ok_button.connect("clicked",self.ok_callback,"cool button")
    cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
    self.dialog.action_area.pack_start(cancel_button,True,True,0)
    cancel_button.show()
    cancel_button.connect('clicked',self.cancel_callback,"cool button")

    table = gtk.Table(3,2,False)
    
    timezone_label = gtk.Label('Time Zone')
    timezone_label.show()
    table.attach(timezone_label,0,1,0,1)
    self.timezone_entry.show()
    table.attach(self.timezone_entry,1,2,0,1)
    table.show()
    
    latitude_label = gtk.Label('Latitude')
    latitude_label.show()
    table.attach(latitude_label,0,1,1,2)
    self.latitude_entry.show()
    table.attach(self.latitude_entry,1,2,1,2)
    table.show()

    longitude_label = gtk.Label('Longitude')
    longitude_label.show()
    table.attach(longitude_label,0,1,2,3)
    self.longitude_entry.show()
    table.attach(self.longitude_entry,1,2,2,3)
    table.show()  

    self.dialog.vbox.pack_start(table,True,True,0)
    self.dialog.show()

  def ok_callback(self,widget,event):
    self.timezone=int(self.timezone_entry.get_text())
    self.latitude=float(self.latitude_entry.get_text())
    self.longitude=float(self.longitude_entry.get_text()) 
    self.next_pray_name=None
    self.delta=self.getNextDeltaPrayTime()
    self.label.set_label(self.parseDeltaPrayTime())
    self.save_to_file()

  def save_to_file(self):
    f = open(self.conf_file,"w")
    f.write(str(self.timezone)+"\n")
    f.write(str(self.latitude)+"\n")
    f.write(str(self.longitude)+"\n")
      
 
  def cancel_callback(self,widget,event):
    self.dialog.destroy()

  def parseDeltaPrayTime(self):
    hours = self.delta.seconds/3600
    minutes = (float)(self.delta.seconds-(hours)*3600)/60
    if hours == 0:
      minutes = (int(math.floor(minutes)))
      seconds = self.delta.seconds-minutes*60
      return str(minutes)+":"+str(seconds)+" to "+self.next_pray_name
    else:
      minutes = (int(math.ceil(minutes)))
      return str(hours)+":"+str(minutes)+" to "+self.next_pray_name

  def update_time(self):
   curr_unixtime = time()
   
   if self.delta.seconds == 0:
      self.label.set_label("Now "+self.next_pray_name)
      self.delta=self.getNextDeltaPrayTime()
   else:
     #anticipate if computer suspend so always check unixtime range
     time_delta = curr_unixtime-self.prev_unixtime
     if time_delta > 0.999 and time_delta < 1.02:
       self.delta-=datetime.timedelta(0,1)
     else:
       self.delta=self.getNextDeltaPrayTime()
     text_delta=self.parseDeltaPrayTime()
     if self.label.get_label!=text_delta:
        self.label.set_label(text_delta)
        
   self.prev_unixtime=curr_unixtime
 
  def timeout_callback(self,event):
    self.update_time()
    return 1
  
  def getNextDeltaPrayTime(self):
    praytimes = praytime.PrayTime(datetime.date.today(),self.latitude,self.longitude,self.timezone)
    current_time = datetime.datetime.today() 
    current_hour = current_time.hour
    current_minute = current_time.minute
    for time in praytimes.getPrayTimes():
      next_praytime = datetime.datetime(current_time.year,current_time.month,current_time.day,time['hour'],time['minute'])
      if current_time <= next_praytime:
          self.next_pray_name = time['name']
          break
    #praytime for fajr next day
    if not self.next_pray_name:
      tomorrow = datetime.date.today()+datetime.timedelta(1)
      praytimes = praytime.PrayTime(tomorrow,self.timezone,self.latitude,self.longitude);
      praytimes = praytimes.getPrayTimes()
      next_praytime = datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day,praytimes[0]['hour'],praytimes[0]['minute'])
      self.next_pray_name=praytimes[0]['name']
    
    current_time = datetime.datetime.today()
    delta =  next_praytime-current_time
    return delta

  def properties(self,event,data=None):
    self.preferences.show()


def praytime_factory(applet, iid):
 #   print "Creating new applet instance"
    PraytimeApplet(applet,iid)
    return gtk.TRUE

#print "Starting factory"
#gnomeapplet.bonobo_factory("OAFIID:GNOME_PraytimeApplet_Factory", 
#                           gnomeapplet.Applet.__gtype__, 
#                           "PrayTime", "0", praytime_factory)
#print "Factory ended"

if len(sys.argv) == 2 and sys.argv[1] == "run-in-window":   
  main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
  main_window.set_title("Python Applet")
  main_window.connect("destroy", gtk.main_quit) 
  app = gnomeapplet.Applet()
  praytime_factory(app, None)
  app.reparent(main_window)
  main_window.show_all()
  gtk.main()
  sys.exit()
else:
  gnomeapplet.bonobo_factory("OAFIID:GNOME_PraytimeApplet_Factory",
                           gnomeapplet.Applet.__gtype__,
                           "PrayTime", "0", praytime_factory)

  


