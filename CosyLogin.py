import requests
import argparse

# Replace these with your actual Cosy login details

sysID = ""
modeNumber = ""
hibState = ""

# Cosy API endpoints
base_url = "https://cosy.geotogether.com/api/userapi/"



def login_to_cosy(username, password):
    try:
        login_url = base_url + "account/login"
        response = requests.post(login_url, json={"name":"waynesaggers@waynesaggers.co.uk","emailAddress":"waynesaggers@waynesaggers.co.uk","password":"Mi26e4u?"})
        response.raise_for_status()
        data = response.json()
        # Extract the token for future requests
        return data["token"]
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return None

def get_current_temperature(token,systemID):
    data_url = base_url + "system/cosy-live-data/"+systemID
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(data_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        temperature = data["temperatureList"][0]["value"]
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving temperature: {e}")
        return None
    
def set_heating_mode(auth_token, systemID, mode, duration):
    print(mode)
    if mode == "1":
        print("got this far")
        set_mode_url = base_url + "system/cosy-cancelallevents/" + systemID + "?zone=0"
        headers = {
        "Authorization": f"Bearer {auth_token}",
        }
        
        params = {
        "zone": "0"
        }
        
        response = requests.delete(set_mode_url, headers=headers)

        if response.status_code == 200:
            print("Slumber successfully enabled!")
        else:
            print(f"Failed to set heating mode: {response.status_code} - {response.text}")

    else:
        
        set_mode_url = base_url + "system/cosy-adhocmode/" + systemID
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "modeId": mode,
            "startOffset": 0,
            "duration": duration,
            "welcomeHomeActive": False,
            "zone": "0"
        }
        response = requests.post(set_mode_url, json=payload, headers=headers)

        if response.status_code == 200:
            if mode == "2":
                print("Comfy successfully enabled!")
            if mode == "3":
             print("Cosy sucessfully enabled!")
        
        else:
            print(f"Failed to set heating mode: {response.status_code} - {response.text}")

def set_hibernate(auth_token, systemID, value):
    set_mode_url = base_url + "system/cosy-instandby/" + systemID
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "value": value,
    }

    response = requests.post(set_mode_url, json=payload, headers=headers)

    if response.status_code == 200:
        if value == "true":
            print("Hibernate successfully enabled!")
        if value == "false":
            print("Hibernate sucessfully disabled!")
        
    else:
        print(f"Failed to set heating mode: {response.status_code} - {response.text}")

def getAllSettings(auth_token, systemID):
    
    data_url = base_url + "system/all-cosy-settings/" + systemID
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(data_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        #temperature = data["temperatureSetPoints"]["slumberTemperature"]
        #print(temperature)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving settings: {e}")
        return None

def getSystemId(auth_token):
    data_url = base_url + "user/detail-systems?peripherals=true"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        }
        
    params = {
        "peripherals": "true"
        }
        
    response = requests.get(data_url, headers=headers)
    data = response.json()

    if response.status_code == 200:
        systemId = data["systemRoles"][0]["systemId"]
        return systemId
    else:
        print(f"Failed to get system ID: {response.status_code} - {response.text}")

        return None
    
def setModeTemp(auth_token,SystemId,mode,temp):
        # Set the temp of the passed mode.  
        requestUrl = base_url + "system/cosy-temperature-set-points/" + SystemId
        
        # Begin by constructing the payload
        currentData = getAllSettings(auth_token,SystemId)
        setPoints = currentData["temperatureSetPoints"]
        setMode = mode + "Temperature"
        setPoints[setMode] = temp

        headers = {
            "Authorization": f"Bearer {auth_token}",
         "Content-Type": "application/json"
        }
        payload = setPoints

        response = requests.post(requestUrl, json=payload, headers=headers)

        if response.status_code == 200:
            print(mode "temperature set to " + temp + " degrees!" )
           
        else:
            print(f"Failed to set temperature: {response.status_code} - {response.text}")


        return None
    

def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Control Geo Cosy Thermostats.")
    parser.add_argument('--username', type=str, required=True, help="Your Cosy username.")
    parser.add_argument('--password', type=str, required=True, help="Your Cosy password.")
    parser.add_argument('--mode', type=str, choices=['slumber', 'comfy', 'cosy'], required=False, help="The mode to set (slumber, comfy or cosy). Must be accompanied by --duration")
    parser.add_argument('--currenttemp', action='store_true', help="Get the current temperature reading.")
    parser.add_argument('--hibernate', type=str, choices=['on', 'off'], required=False, help="Set hibernate state (on or off).")
    parser.add_argument('--duration', type=int, help="Duration for the mode in minutes.")
    parser.add_argument('--modetemp', type=str, choices=['slumber', 'comfy', 'cosy'], required=False, help="The mode to set temperature for (slumber, comfy or cosy). Must be accompanied by --value")
    parser.add_argument('--value', type=float, help="Temperature to set the specified mode to eg. 20.5")
    args = parser.parse_args()


    # Log in and retrieve the token
    token = login_to_cosy(args.username, args.password)
    if not token:
        print("Failed to log in.")
        return
    
    # Get the system ID
    sysID = getSystemId(token)
    
 
    
    if args.currenttemp:
        # Get the current temperature
        temperature = get_current_temperature(token,sysID)
        if temperature is not None:
            print(f"Current temperature: {temperature}°C")
        else:
            print("Failed to retrieve temperature.")
    
    if args.mode and args.duration is None:
        parser.error("--duration is required when --mode is specified.")
    elif args.mode is None and args.duration:
        parser.error("--mode must be specified when --duration is provided.")
    if args.mode is not None:
        # Set Current Mode
        reqMode = args.mode
        if reqMode == "slumber":
            modeNumber = "1"
        if reqMode == "comfy":
            modeNumber = "2"
        if reqMode == "cosy":
            modeNumber = "3"
        set_heating_mode(token,sysID,modeNumber,args.duration)

    if args.hibernate is not None:
        valCheck = args.hibernate
        if valCheck == "on":
            hibState = "true"
            
        if args.hibernate == "off":
            hibState = "false"
        set_hibernate(token,sysID,hibState) 
    
    #doHibernate = set_hibernate(token,"true")
    print(sysID)
    if args.modetemp is not None:
        setModeTemp(token,sysID,"cosy",args.value)
    

if __name__ == "__main__":
    main()
