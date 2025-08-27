from iman import *
import datetime
import pytz
from win32com.propsys import propsys, pscon


def get_age(a):
    years = a//365
    rooz_baqimande= a%365
    
    mah = rooz_baqimande//30
    rooz_baqimande_2 = rooz_baqimande%30
    
    return ("%sy_%sm_%sd" %(D(years,2) , D(mah,2) , D(rooz_baqimande_2,2)))

def get(fname):
   properties = propsys.SHGetPropertyStoreFromParsingName(fname)
   dt = properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
   t = datetime.date(dt.year,dt.month,dt.day)
   return (t)