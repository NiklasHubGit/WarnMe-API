import paho.mqtt.client as mqtt
import sqlite3
import time
from google.auth.transport import requests
from google.oauth2 import service_account
import subprocess
import json

#test json data
data_json_test = '{"end_device_ids": {"device_id": "eui-7066e1fffe000eca", "application_ids": {"application_id": "temp-sens-jgo"}, "dev_eui": "7066E1FFFE000ECA", "join_eui": "7066E1FFFE000ECB", "dev_addr": "260BE53E"}, "correlation_ids": ["gs:uplink:01HHPZZ6KFE2E8XTWGMRBX8SJ8"], "received_at": "2023-12-15T15:01:57.181695121Z", "uplink_message": {"session_key_id": "AYwG+6TGzAJoi0BBJDCPog==", "f_port": 10, "f_cnt": 35938, "frm_payload": "BAAABQQGARo=", "decoded_payload": {"Distance": 282, "Supply_Voltage": 1284, "TX_Reason": "App_Cycle_Event"}, "rx_metadata": [{"gateway_ids": {"gateway_id": "sfz-ox-gateway", "eui": "DCA632FFFE0CBFCA"}, "timestamp": 156415380, "rssi": -121, "channel_rssi": -121, "snr": -4, "location": {"latitude": 48.0649113325448, "longitude": 9.95434820652008, "altitude": 589, "source": "SOURCE_REGISTRY"}, "uplink_token": "ChwKGgoOc2Z6LW94LWdhdGV3YXkSCNymMv/+DL/KEJTrykoaDAjk1PGrBhCXs+zQAyCglNXYxoMq",  "channel_index" : 2,"received_at": "2023-12-15T15:01:55.777266933Z"}], "settings": {"data_rate": {"lora": {"bandwidth": 125000, "spreading_factor": 10, "coding_rate": "4/5"}}, "frequency": "867300000", "timestamp": 156415380}, "received_at": "2023-12-15T15:01:56.975634628Z", "consumed_airtime": "0.370688s", "network_ids": {"net_id": "000013", "ns_id": "EC656E0000000181", "tenant_id": "ttn", "cluster_id": "eu1", "cluster_address": "eu1.cloud.thethings.network"}}}'
def send_push_notification():
    #this will error because i obviously dont want to upload the service account file

    url = 'https://fcm.googleapis.com/v1/projects/hochwasserwarnapp/messages:send'
    def generate_access_token(service_account_file):
    
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    
        request = requests.Request()
        credentials.refresh(request)
    
        return credentials.token
    
    access_token = generate_access_token('hochwasserwarnapp-4b01ebd06065.json')
    
    print(access_token)
    
    device_token = "fZ6XUTdkTw6uraSiT8Wk5Q:APA91bGn8zuzTxsyy7eYgFs5pkQxQg6fSGZOynox_E7b-6Ywqrm6h7VfyeioCicm7VvWJ1zbOhr-1d5ljNRAaewwFFKbZXCBgfsG1Mpf_H-3mz6BxRk8kiFizYcd9a393e6clXzNtPr-"
    #device_token = "fb_4MNJkRy6au12yiqKWMv:APA91bEEmfX2uJfdSJGJckqddRd8MPXh60witO9yAKg1j-lPDn6L38fBYt2g1aG1k-2TsId3SNIo4ojFMl8GEfMB_Xc3YHC2EdTZ5xN26OV1fZXz7pe0ybFH1zH_-xfjby4QgqoEDV5C"
    data = {
        "message": {
            #"token": device_token,
            "topic" : "nah",
            "notification": {
                "title": "WARNUNG",
                "body": "Es gibt ein Hochwasser in Ochsenhausen!!!",
            },
            "android": {
                "notification": {
                    "sound": "default",  # You can change this to the desired sound file name
                    "sticky": "true",
                    "vibrate_timings" : ["10.5s"],
                    "notification_count": 2
                }
            }
        }
    }
    
    # Convert data to a JSON string
    data_json = json.dumps(data)
    
    # Build the cURL command as a list
    curl_command = [
        'curl',
        '-X', 'POST',
        url,
        '-H', f'Authorization: Bearer {access_token}',
        '-H', 'Content-Type: application/json',
        '-d', data_json
    ]
    
    # Execute the cURL command
    process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    
    # Print the response
    print(output.decode('utf-8'))
    print(error.decode('utf-8'))
    time.sleep(3600)
    
    
    # i use subprocess because i already had a working curl command and i just wanted to use it in python
    # maybe i will use the requersts library in the future
    
def algorithmus():
    #this fucntion needs to go to the db which is not ideal 
    #i will change it in the future so the algortihm gets its values directly from the mqtt function
    tables = ("hw1gen2", "hw5gen1", "hw6gen1", "hw7gen1")
    min_dis = (50, 300, 400, 200)
    alarms = 0

    con = sqlite3.connect("sensor_data.db")
    cur = con.cursor()
    
    matrix = [cur.execute(f"SELECT distance FROM {table} ORDER BY received_at DESC LIMIT 5;").fetchall() for table in tables]
    matrix_rel = [cur.execute(f"SELECT distance, received_at FROM {table} ORDER BY received_at DESC LIMIT 30;").fetchall() for table in tables]


    def percentdecrease (list_all, alarms):
        list_dis = [item[0] for item in list_all]
        halblen = int((len(list_dis)/2))
        avgnew = sum(list_dis[:halblen]) / halblen
        avgold = sum(list_dis[halblen:]) / halblen
        percentdecrease = 100 - (avgnew/avgold*100)
        print(f"avgnew: {avgnew} avgold: {avgold} distance percent decrease {percentdecrease}" )
        if percentdecrease > 30:
            alarms += 1
        return alarms

    for list_all in matrix_rel:
        alarms = percentdecrease(list_all, alarms)


    bolean_matrix = [[messwert[0] < min_dis[i] for messwert in matrix[i]] for i in range(4)]
    
    for bolean_list in bolean_matrix:
        if all(bolean_list): 
            alarms += 1

    print(f"alarms: {alarms}")
    if alarms >=2:
        send_push_notification()



def database(data_json, table):
    data_dict = json.loads(data_json)
    def getitem(*args):
        temp = data_dict
        try:
            for i in args:
                temp = temp[i]
            return temp
        except Exception as e:
            return 9999
                
    # Connect to SQLite database
    con = sqlite3.connect("warnMeApi/express-api/sensor_data.db")
    cur = con.cursor()
    
    cur.execute(f"""
    INSERT INTO {table} VALUES (
        :device_id, 
        :application_id,
        :dev_eui,
        :join_eui,
        :dev_addr,
        :correlation_id,
        :received_at,
        :session_key_id,
        :f_port,
        :f_cnt,
        :frm_payload,
        :distance,
        :supply_voltage,
        :tx_reason,
        :gateway_id,
        :gateway_eui,
        :timestamp,
        :rssi,
        :channel_rssi,
        :snr,
        :latitude,
        :longitude,
        :altitude,
        :source,
        :uplink_token,
        :channel_index,
        :settings_data_rate_bandwidth,
        :settings_data_rate_spreading_factor,
        :settings_data_rate_coding_rate,
        :settings_frequency,
        :settings_timestamp,
        :consumed_airtime,
        :network_net_id,
        :network_ns_id,
        :network_tenant_id,
        :network_cluster_id,
        :network_cluster_address
    )
    """, {
    'device_id': getitem('end_device_ids', 'device_id'),
    'application_id': getitem('end_device_ids', 'application_ids', 'application_id'),
    'dev_eui': getitem('end_device_ids', 'dev_eui'),
    'join_eui': getitem('end_device_ids', 'join_eui'),
    'dev_addr': getitem('end_device_ids', 'dev_addr'),
    'correlation_id': getitem('correlation_ids', 0),
    'received_at': getitem('received_at'),
    'session_key_id': getitem('uplink_message', 'session_key_id'),
    'f_port': getitem('uplink_message', 'f_port'),
    'f_cnt': getitem('uplink_message', 'f_cnt'),
    'frm_payload': getitem('uplink_message', 'frm_payload'),
    'distance': getitem('uplink_message', 'decoded_payload', 'Distance'),
    'supply_voltage': getitem('uplink_message', 'decoded_payload', 'Supply_Voltage'),
    'tx_reason': getitem('uplink_message', 'decoded_payload', 'TX_Reason'),
    'gateway_id': getitem('uplink_message', 'rx_metadata', 0, 'gateway_ids', 'gateway_id'),
    'gateway_eui': getitem('uplink_message', 'rx_metadata', 0, 'gateway_ids', 'eui'),
    'timestamp': getitem('uplink_message', 'rx_metadata', 0, 'timestamp'),
    'rssi': getitem('uplink_message', 'rx_metadata', 0, 'rssi'),
    'channel_rssi': getitem('uplink_message', 'rx_metadata', 0, 'channel_rssi'),
    'snr': getitem('uplink_message', 'rx_metadata', 0, 'snr'),
    'latitude': getitem('uplink_message', 'rx_metadata', 0, 'location', 'latitude'),
    'longitude': getitem('uplink_message', 'rx_metadata', 0, 'location', 'longitude'),
    'altitude': getitem('uplink_message', 'rx_metadata', 0, 'location', 'altitude'),
    'source': getitem('uplink_message', 'rx_metadata', 0, 'location', 'source'),
    'uplink_token': getitem('uplink_message', 'rx_metadata', 0, 'uplink_token'),
    'channel_index': getitem('uplink_message', 'rx_metadata', 0, 'channel_index'),
    'settings_data_rate_bandwidth': getitem('uplink_message', 'settings', 'data_rate', 'lora', 'bandwidth'),
    'settings_data_rate_spreading_factor': getitem('uplink_message', 'settings', 'data_rate', 'lora', 'spreading_factor'),
    'settings_data_rate_coding_rate': getitem('uplink_message', 'settings', 'data_rate', 'lora', 'coding_rate'),
    'settings_frequency': getitem('uplink_message', 'settings', 'frequency'),
    'settings_timestamp': getitem('uplink_message', 'settings', 'timestamp'),
    'consumed_airtime': getitem('uplink_message', 'consumed_airtime'),
    'network_net_id': getitem('uplink_message', 'network_ids', 'net_id'),
    'network_ns_id': getitem('uplink_message', 'network_ids', 'ns_id'),
    'network_tenant_id': getitem('uplink_message', 'network_ids', 'tenant_id'),
    'network_cluster_id': getitem('uplink_message', 'network_ids', 'cluster_id'),
    'network_cluster_address': getitem('uplink_message', 'network_ids', 'cluster_address')
}) 
    con.commit()
    
    
    con.close()
#database(data_json_test)

# gives connection message
def on_connect(client,userdata,flags, rc ):
    print("Connected with result code:"+str(rc))
    # subscribe for all devices of user
    client.subscribe('v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000eca/up')
    client.subscribe('v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000798/up')
    client.subscribe('v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000ebc/up')
    client.subscribe('v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000c96/up')
    client.subscribe('v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000794/up')
    client.subscribe('v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe0004ee/up')
 # gives message from device
def on_message(client,userdata,msg):
    print("Topic",msg.topic + "\nMessage:" + str(msg.payload))
    if msg.topic == 'v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000ebc/up':
        database(msg.payload, "hw1gen2")
    elif msg.topic == 'v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000eca/up':
        database(msg.payload, "hw2gen2")
    elif msg.topic == 'v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000c96/up':
        database(msg.payload, "hw7gen1")
    elif msg.topic == 'v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000798/up':
        database(msg.payload, "hw5gen1")
    elif msg.topic == 'v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe000794/up':
        database(msg.payload, "hw6gen1")
    elif msg.topic == 'v3/temp-sens-jgo@ttn/devices/eui-7066e1fffe0004ee/up':
        # livedemo sensor fuer die jufo präsentation
        demoalgo();
    else:
        database(msg.payload, "temp")
def demoalgo(payload):
    parsed_payload = json.loads(payload)
    print(parsed_payload)
    distance = parsed_payload["uplink_message"]["decoded_payload"]["Distance"]
    if( distance > 17 ):
        send_push_notification()

mqttc= mqtt.Client()
mqttc.on_connect=on_connect
mqttc.on_message=on_message
from secrets import MQTT_USERNAME, MQTT_PASSWORD
mqttc.username_pw_set(MQTT_USERNAME, password=MQTT_PASSWORD)

mqttc.connect("eu1.cloud.thethings.network",1883)
mqttc.loop_start()
demoalgo(data_json_test)
while True:
    #algorithmus()
    time.sleep(60)
