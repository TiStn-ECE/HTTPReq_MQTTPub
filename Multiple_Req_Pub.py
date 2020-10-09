import paho.mqtt.client as mqqt
import requests
import json
import time

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass

def publishToBroker(jsonData, dest):
    topic = "/oneM2M/req/access-key/antares-cse/json"
    payload = {
        "m2m:rqp": {
        "fr": "access-key",
        "to": "/antares-cse/antares-id/app-name/device-name",
        "op": 1,
        "rqi": 123456,
        "pc": {
        "m2m:cin": {   
            "cnf": "message",
            "con": "{\"your-first-data\":the-integer-value,\"your-second-data\":\"the-string-data\"}"
                }
            },
        "ty": 4
        }
    }
    jsonObject = json.dumps(payload, sort_keys=True, indent=4)
    data = json.loads(jsonObject)
    data["m2m:rqp"]["to"] = dest    #change destination device
    data["m2m:rqp"]["pc"]["m2m:cin"]["con"] = json.dumps(jsonData)  #change content
    print("Payload\n\n")
    print(json.dumps(data, sort_keys=True, indent=4))
    broker = "mqtt.antares.id"
    port = 1883
    mqttc = mqqt.Client()
    mqttc.connect(broker, port)
    mqttc.on_publish = on_publish
    mqttc.publish(topic, json.dumps(data))

def converter(contentPayload):
    jsonData = {}
    evomoParam = {
        "temperature" : "T",
        "humidity" : "H",
        "Light_Intensity" : "L",
        "Soil_Moistue" : "M",
        "Acidity" : "K",
        "Water_Level" : "W",
        "CO2" : "C",
        "Barometic_Pressure" : "P",
        "Voc_Gas" : "G",
        "Air_Quality" : "A",
        "Wind_Speed" : "S",
        "Rain_Fall" : "R",
        "Ammonia" : "O",
        "Soil_NPK" : "N",
        "Volumetric_Water_Content" : "B",
        "Bulk_Electrical_Conductivity" : "E",
        "Linear_Position" : "X",
        "Tilt" : "I",
        "battery" : "V",
        "Power" : "J",
        "Current" : "Q"
    }
    for key, value in contentPayload.items():
        for evomoKey, evomoValue in evomoParam.items():
            if(key == evomoKey):
                jsonData[evomoValue] = float(value)
    return jsonData

def myRequest(url, dest):
    head = {
    "X-M2M-Origin" : "access-key",
    "Content-Type" : "application/json;ty=4",
    "Accept" : "application/json"
    }
    response = requests.get(url, headers=head)
    statusCode = response.status_code
    if(statusCode == 200):
        print("Status Code : OK")
        data = json.loads(response.text)
        # print(data)
        contentPayload = json.loads(data["m2m:cin"]["con"])
        jsonData = converter(contentPayload)
        publishToBroker(jsonData, dest)
        # batt = dataFix['battery']
        # humi = dataFix['humidity']
        # jsonData = toJson(batt, humi)
        # print(jsonData)
        # print(response.text)

while True:
    try:
        URL = {
            "URL_1" : "Publish_Device_1(Destination_Payload)",
            "URL_2" : "Publish_Device_2(Destination_Payload)"
        }
        for url, dest in URL.items():
            myRequest(url, dest)
        time.sleep(3)
    except KeyboardInterrupt:
        print("Something Error!!")
        break