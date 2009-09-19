#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet
import gobject
import praytime
import datetime
import sys

class PraytimeApplet:
  applet=None
  timeout_interval=1000
  iid = 0
  delta = 0
  label=None
  next_pray_name=None

  def __init__(self,applet,iid):
    self.applet=applet
    self.iid=iid
    self.delta=self.getNextDeltaPrayTime()
    self.label = gtk.Label(self.parseDeltaPrayTime())
    applet.add(self.label)
    self.create_menu()
    applet.show_all()
    gobject.timeout_add(self.timeout_interval, self.timeout_callback, self)

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
    dialog=gtk.Dialog('gPraytime Preferences')
    ok_button = gtk.Button(stock=gtk.STOCK_OK)
    dialog.action_area.pack_start(ok_button,True,True,0)
    ok_button.show()
    cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
    dialog.action_area.pack_start(cancel_button,True,True,0)
    cancel_button.show()

    table = gtk.Table(3,2,False)
    
    timezone_label = gtk.Label('Time Zone')
    timezone_label.show()
    table.attach(timezone_label,0,1,0,1)
    timezone_entry = gtk.Entry()
    timezone_entry.show()
    table.attach(timezone_entry,1,2,0,1)
    table.show()
    
    latitude_label = gtk.Label('Latitude')
    latitude_label.show()
    table.attach(latitude_label,0,1,1,2)
    latitude_entry = gtk.Entry()
    latitude_entry.show()
    table.attach(latitude_entry,1,2,1,2)
    table.show()

    longitude_label = gtk.Label('Longitude')
    longitude_label.show()
    table.attach(longitude_label,0,1,2,3)
    longitude_entry = gtk.Entry()
    longitude_entry.show()
    table.attach(longitude_entry,1,2,2,3)
    table.show() 
        

    dialog.vbox.pack_start(table,True,True,0)
    dialog.show()

  def parseDeltaPrayTime(self):
    hours = self.delta.seconds/3600
    minutes = (self.delta.seconds-(hours)*3600)/60
    if hours == 0:
      seconds = self.delta.seconds-(minutes)*60
      return str(minutes)+":"+str(seconds)+" to "+self.next_pray_name
    else:
      return str(hours)+":"+str(minutes)+" to "+self.next_pray_name
 
  def timeout_callback(self,event):
    if self.delta.seconds == 0:
      self.label.set_label("Now "+self.next_pray_name)
      self.delta=self.getNextDeltaPrayTime()
    else:
      text_delta=self.parseDeltaPrayTime()
      if self.label.get_label!=text_delta:
        self.label.set_label(text_delta)
      self.delta-=datetime.timedelta(0,1)
    return 1
  
  def getNextDeltaPrayTime(self):
    praytimes = praytime.PrayTime(datetime.date.today(),-6 , 106.650002, 7)
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
      praytimes = praytime.PrayTime(tomorrow,-6,106.650002,7);
      praytimes = praytimes.getPrayTimes()
      next_praytime = datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day,praytimes[0]['hour'],praytimes[0]['minute'])
      self.next_pray_name=praytimes[0]['name']
    
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

  


