from Temp_Humidity_Sensor import DHT11_Reader
import paho.mqtt.client as mqttc
import time
import datetime
import requests
import json

class PublishData(object):

    def __init__(self, url, sensor_t_h,roomId, client):
        self.url = url
        self.sensor_t_h = sensor_t_h
        self.client = client
        self.roomId=roomId

    def load_topics(self):
        # sending request to the resource catalog to get the topics related to the room id
        try:
            self.respond = requests.get(self.url)
            json_format = json.loads(self.respond.text)
	   # print(json_format)
            self.DHT_Topic = json_format["topic"]["dhtTopic"]
            print("PublishData:: BROKER VARIABLES ARE READY")
        except:
	  #  print(json_format)
            print("PublishData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print ('CONN ACK received with code: ' + str(rc))
        print ("at time: " + str(current_time))
        return str(rc)

    @classmethod
    def on_publish(cls, client, userdata, mid):
        # get the current time
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("mid: " + str(mid))
        print ("at time: " + str(current_time))
        print("--------------------------------------------------------------------")
        return str(mid)

    def publish_sensor_data(self):
        #This function will publish the data related to temperature and humidity
        try:
            inputJsonFromTHSensor = self.sensor_t_h.sensorData()
            inputData = json.loads(inputJsonFromTHSensor)
            temp = inputData["temperature"]
            hum = inputData["humidity"]
            time1 = inputData["time"]
            print("TRACE CHECK- PUBLISH SENSOR DATA: ",temp,hum,time1)
            outputJson=json.dumps({"subject":"temp_hum_data","roomId":self.roomId, "temperature": temp, "humidity": hum, "time":time1})
            msg_info = client.publish(self.DHT_Topic, str(outputJson), qos=1)
            print("\nMessage is published.")
            #if msg_info.is_published() == True:
            #    print ("\nMessage is published.")
            # This call will block until the message is published
            #msg_info.wait_for_publish()
            return ("HELLO", json_format)
        except:
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print("PublishData: ERROR IN PUBLISHING DATA RELATED TO THE SENSORS")
            print ("at time: " + str(current_time))


if __name__ == '__main__':

    try:
        # reading the config file to set the resource catalog url and the room id
        file = open("config_file.json", "r")
        json_string = file.read()
        file.close()
    except:
        raise KeyError("***** PublishData: ERROR IN READING CONFIG FILE *****")

    config_json = json.loads(json_string)
    resourceCatalogIP = config_json["reSourceCatalog"]["url"]
    roomId = config_json["reSourceCatalog"]["roomId"]
    url = resourceCatalogIP + roomId
   # print(url)
   # xx=requests.get(url)
   # print(xx)
    try:
        # create an object from ReadingDHT class
        sensor_data = DHT11_Reader()
	#print(sensor_data)
    except:
        print("PublishData: ERROR IN GETTING DATA FROM SENSOR ")

    client = mqttc.Client()
    sens = PublishData(url, sensor_data,roomId, client)

    while True:
        sens.load_topics()
        try:
            #requesting the vroker info from resource catalog
            respond = requests.get(resourceCatalogIP+"broker")
            json_format = json.loads(respond.text)
            broker_ip = json_format["ip"]
            port = json_format["port"]
        except:
            print("PublishData: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP")

        try:
            client.on_connect = PublishData.on_connect
            client.on_publish = PublishData.on_publish
            client.connect(broker_ip, int(port))
            client.loop_start()
        except:
            print("PublishData: ERROR IN CONNECTING TO THE BROKER")

        while True:
            sens.load_topics()
            sens.publish_sensor_data()
            time.sleep(30)
