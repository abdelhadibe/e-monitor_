
    def homeDevice_update(self, device_name, in_planning, start_time, stop_time, priority, power_consumption, achieved):
    	my_device = dict();
    	my_device['name'] = device_type ; 
    	my_device['in_planning'] = in_planning;
    	my_device['start_time'] = start_time; 
    	my_device['stop_time'] = stop_time; 
    	my_device['elapsed_time'] = "" ; 
        my_device['time_to_run'] = None
    	my_device['priority'] = priority ; 
    	my_device['power_consumption'] = power_consumption ; 
    	my_device['energy_consumption'] = 0; 
    	my_device['power_demande'] = "15" ;
        my_device['is_running'] = "False"
    	my_device['achieved'] = achieved ; 

    	return my_device ; 

    def device_search(self, planner, remaing) : 
    	for k,device in planner.items() : 
    		if(device['in_planning'] == "True") :
    			if( device['power_demande'] < self._remaining_power) : 
    				device['start_time'] = datetime.datetime.now() ;
    				return device ; 
    		else:
    			return 0 ;  


self._consumed_power ; 
self._remaining_power ; 

def update_remaining_time(self, planner):
    for k,d in planner.items(): 
        if(d['in_planning'] == True):
            if(d['is_running'] == True):
                d['stop_time'] = datetime.datetime.now() ; 
                d['elapsed_time'] = self.get_elapsed_time(d['start_time'], d['stop_time']) ; 

def device_control(self, planner):
    for k,d in  planner.items():
        if (d['elapsed_time'] >= d['time_to_run'] ):

            device_name = d['name'] ; 
            device['stop_time'] = datetime.datetime.now() ; 
            self.sendSwitch_cmd(device_name, "Off") ;





self._remaining_power = self._photoVol_prodution - self._consumed_power ; 

if(self._remaining_power > 0 ) :
    device = self.device_search(planner, remaining );
    if(device != 0):
        if(device['on_marche'] == False ) :
            device['start_time'] = datetime.datetime.now() ;
            device['on_marche'] = True ; 
            device_name = device['name']; 
            self.sendSwitch_cmd(device_name, "On") ; 
self.update_remaining_time(planner);
self.device_control(planner) ; 
