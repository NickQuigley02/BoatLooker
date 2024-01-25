import asyncio
import websockets
import json
import time
import folium
from datetime import datetime, timezone

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

api_key = config.get('api_key')

map_center = [43, -84] 
map_zoom = 6
mymap = folium.Map(location=map_center, zoom_start=map_zoom, zoom_control=False)

def add_marker(lat, lon, ship_id):
    folium.Marker(location=[lat, lon], popup=f"Ship ID: {ship_id}").add_to(mymap)


## The basic understanding and use of this API courtesy of https://github.com/aisstream/example/tree/main/python
async def connect_ais_stream():

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": api_key, "BoundingBoxes": [[[50, -94], [41, -75]]]}

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)
        
        try:
            async for message_json in websocket:
                message = json.loads(message_json)
                message_type = message["MessageType"]

                if message_type == "PositionReport":
                    ais_message = message['Message']['PositionReport']
                    ship_data = message['MetaData']

                    print(f"[{ship_data['time_utc']}]  ShipId - {ais_message['UserID']}, Latitude - {ais_message['Latitude']}, Longitude - {ais_message['Longitude']}")
                    add_marker(ais_message['Latitude'], ais_message['Longitude'], ship_data['ShipName'])
        finally:
            await close_connection(websocket)
            
            
async def close_connection(websocket):
    await websocket.close()
    
    
if __name__ == "__main__":
    try:
        asyncio.run(connect_ais_stream())
    except KeyboardInterrupt:
        print("Program terminated by user. Closing WebSocket connection.")
    
mymap.save("map_with_markers.html")