import requests
import json
import sys
from requests.auth import HTTPDigestAuth


ENDPOINT = "/parameter.json"
QUERYTELEGRAM = (
    '{"prot":"coco","telegramm":[[10,0,1,4176,0,0,0,0],[10,0,1,3793,0,0,0,0],[10,0,1,3792,0,0,0,0],[10,0,1,12,0,0,0,0],[10,0,1,14,0,0,0,0],[10,0,1,3101,0,0,0,0],[10,0,1,325,0,0,0,0],[10,0,1,3197,0,0,0,0],[6,0,1,5,0,0],[6,0,1,274,0,0],[6,0,1,8,0,0],[10,0,1,81,0,0,0,0],[10,0,1,1497,0,0,0,0],[10,0,1,1498,0,0,0,0], [10,0,1,466,0,0,0,0], [10,0,1,82,0,0,0,0], [10,0,1,83,0,0,0,0], [10,0,1,1,0,0,0,0], [10,0,1,373,0,0,0,0]]}'
)

# [10,0,1,4176,0,0,0,0],
VALUE = 1
TEMP = 2
DECIMAL_VALUE = 3

# ID, Name, Value/Temp
QUERIES = [[3793, "Oil Meter", VALUE], [4176, "Load Setting", DECIMAL_VALUE], [12, "Outside Temperature", TEMP], [14, "Warm Water Temperature", TEMP], [3101, "Flow Temperature", TEMP], [325, "Flue Gas Temperature", TEMP], [5, "Room Temperature", TEMP], [274, "Operation Mode", VALUE], [8, "Mixed External Temperature", TEMP], [81, "Flame", VALUE], [1497, "Gas Valve 1", VALUE], [1498, "Gas Valve 2", VALUE], [466, "Pump", VALUE], [82, "Heating", VALUE], [83, "Warm Water", VALUE], [1, "Error", VALUE], [373, "Operation Phase", VALUE]]


def getTemperture(lowByte, highByte):
    return (lowByte + 265 * highByte) / 10


def getValue(lowByte, highByte):
    return lowByte + 265 * highByte


def getDecimalValue(lowByte, highByte):
    return (lowByte + 265 * highByte) / 10


def process_values(server, username, password):
    try:
        req = requests.post(
            "http://" + server + ENDPOINT,
            auth=HTTPDigestAuth(username, password),
            data=QUERYTELEGRAM,
            timeout=5)
        telegram = json.loads(req.text)["telegramm"]
        result = {}
        for message in telegram:
            for reading in QUERIES:
                # print(reading)
                if message[3] == reading[0]:
                    if reading[2] == TEMP:
                        result[reading[1]] = getTemperture(message[6], message[7])
                    elif reading[2] == VALUE:
                        result[reading[1]] = getValue(message[6], message[7])
                    elif reading[2] == DECIMAL_VALUE:
                        result[reading[1]] = getDecimalValue(message[6], message[7])
            # special handling for oil meter
            if message[3] == 3792:
                result["Oil Meter"] = result["Oil Meter"]+message[6]*1000
        return json.dumps(result)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return None
