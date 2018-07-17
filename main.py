import monitoring
import mqtt_domoticz
from  open_weather import * 


host = 'localhost'
port =  1883 
url = 'http://api.openweathermap.org/data/2.5/forecast?q=toulouse,fr&APPID=da4129fd505da7e78ad1da77ef375160&units=metric&lang=fr'





def main(): 
    
    startForcast(url);

    mqtt_transfert = mqtt_domoticz() ; 
    mqtt_transfert.runMqqt_domoritcz() ; 

    moni = monitoring(host,port); 
    moni.runMonitoring() ;

    while True : 
        pass ;

if __name__ == '__main__':
    main()
    


