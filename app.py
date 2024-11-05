import redis
import json
import os

from flask import Flask, jsonify, request


app = Flask(__name__)

def connect_to_redis(host='localhost', port=6379, password=None):
    try:
        redis_client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            decode_responses=True 
        )
        
        redis_client.ping()
        print("Connected to Redis!")
        return redis_client
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        return None
    
REDIS_HOST = os.getenv("REDIS_HOST", "some-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))   
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None) 

redis_client = connect_to_redis(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

####################################################################################
### Use this if you want to test the API                                           #
### and store some data in the Redis database                                      #
###                                                                                #
### this will store test data located in test_data.json in the Redis database      #
### the key will be the index of the data in the JSON file                         # 
### and the value will be the data itself                                          #
# with open('test_data.json') as f:                                                #               
#     for idx, data in enumerate(json.load(f)):                                    #
#         data_str = json.dumps(data)                                              #                   
#         redis_client.set(idx, data_str)                                          #
#         print(f"Stored {idx} in Redis")                                          #       
####################################################################################

@app.route('/songs', methods=['GET'])
def get_songs():
    song_id = request.args.get('id')
    
    if not song_id:
        return jsonify({"error": "No song ID provided"}), 400
    
    value = redis_client.get(song_id)
    
    if value is None:
        return jsonify({"error": f"No data found for song ID: {song_id}"}), 404
    
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON data"}), 500
    
    return jsonify({"id": song_id, "data": data})


if __name__ == '__main__':
    app.run(debug=True)