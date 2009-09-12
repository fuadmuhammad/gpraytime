'''
Created on 02 Agu 2009

@author: fuad
'''
import math
import datetime

class PrayTime:
  __jul_date = 0
  __latitude = 0
  __longitude = 0
  __timezone = 0
  __defaultConstants = [5, 6, 12, 13, 18, 18, 18]
  __MWL = [18, 1, 0, 0, 17]        
  
  TIME = ['Fajr','Sunrise','Duhr','Asr','Sunset','Maghrib','Isya']
  
  def __init__(self,date,lat,long,__timezone):
    self.__latitude = lat
    self.__longitude = long
    self.__jul_date = self.__julianDate(date.year, date.month, date.day)-self.__longitude/(15*24)
    self.__timezone = __timezone
    
    
  def __julianDate(self,year,month,day):
    if(month <= 2):
      year-=1
      month+=12
    
    A = math.floor(year/100)
    B = 2-A+math.floor(A/4)
    
    JD = math.floor(365.25*(year+4716)) + math.floor(30.6001*(month+1))+day+B-1524.5
    return JD

  def __fixAngle(self,a):
    a = a - 360.0 * (math.floor(a / 360.0))
    if(a<0):
        a+=360
    return a

  def __fixHour(self,a):
    a = a - 24.0 * (math.floor(a / 24.0))
    if(a<0):
        a+=24
    return a

  def __sunPosition(self,jd):
     d = jd - 2451545.0 
     g = self.__fixAngle(357.529 + 0.98560028* d)
     q = self.__fixAngle(280.459 + 0.98564736* d)
     L = self.__fixAngle(q + 1.915* math.sin(math.radians(g)) + 0.020* math.sin(math.radians(2*g)))

     R = 1.00014 - 0.01671* math.cos(math.radians(g)) - 0.00014*math.cos(math.radians(2*g))
     e = 23.439 - 0.00000036* d
     RA = math.degrees(math.atan2(math.cos(math.radians(e))* math.sin(math.radians(L)), math.cos(math.radians(L))))/ 15
     RA = self.__fixHour(RA)
     D = math.degrees(math.asin(math.sin(math.radians(e))* math.sin(math.radians(L))))
     EqT = q/15 - RA

     return [D,EqT]
 
  def __adjustTime(self,time):
      time +=self.__timezone-self.__longitude/15
      return time
  
  def __floatToTime24(self,time):
    time = self.__fixHour(time+ 0.5/ 60)
    hours = int(math.floor(time)) 
    minutes = int(math.floor((time-hours)* 60))
    return {'hour':int(self.__twoDigitsFormat(hours)),'minute':int(self.__twoDigitsFormat(minutes))}

  def __twoDigitsFormat(self,num):
    if (num <10):
      return '0'+ str(num)
    else:
      return str(num)
  
  def __computeMidDay(self,t):
    T = self.__sunPosition(self.__jul_date+t)[1]
    Z = self.__fixHour(12- T);
    return Z;
  
  def __computeTime(self,G,t):
    D = self.__sunPosition(self.__jul_date+t)[0]
    Z = self.__computeMidDay(t)
    V = float(1)/15* math.degrees(math.acos((-math.sin(math.radians(G))- math.sin(math.radians(D))* math.sin(math.radians(self.__latitude))) / 
            (math.cos(math.radians(D))* math.cos(math.radians(self.__latitude)))))
    if G>90:
        return Z-V
    else:
        return Z+V

  def __computeAsr(self,t):
    step = 1 #shafii = 1 Hanafi =2 
    D = self.__sunPosition(self.__jul_date+t)[0]
    G = -math.degrees(math.atan(1/(step+math.tan(math.radians(abs(self.__latitude-D))))))
    return self.__computeTime(G, t)
    
  def __getDayPortion(self,times):
    return [float(elem)/24 for elem in times]

  def __normalizeTime(self,praytimes):
    times = []
    index = 0
    for praytime in praytimes:
      praytime = self.__adjustTime(praytime)
      praytime = self.__floatToTime24(praytime)
      praytime['name']=self.TIME[index]
      times.append(praytime)
      index+=1
    return times
    
  def getPrayTimes(self):
    day_portions = self.__getDayPortion(self.__defaultConstants)
    fajr = self.__computeTime(180-self.__MWL[0], day_portions[0])
    sunrise = self.__computeTime(180-0.833,day_portions[1]) 
    dhuhr = self.__computeMidDay(day_portions[2])
    ashr = self.__computeAsr(day_portions[3])
    sunset = self.__computeTime(0.833,day_portions[4])
    maghrib = self.__computeTime(self.__MWL[2], day_portions[5])
    isha = self.__computeTime(self.__MWL[4], day_portions[6])
    return self.__normalizeTime([fajr,sunrise,dhuhr,ashr,sunset,maghrib,isha])

if __name__ == '__main__':
  p = PrayTime(datetime.date.today(),-6 , 106.650002, 7)
  print p.getPrayTimes()