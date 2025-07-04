import json

def change_json(json_data, key, value):
    """
    Change the value of a specific key in a JSON object.

    :param json_data: The JSON data as a string or dictionary.
    :param key: The key whose value needs to be changed.
    :param value: The new value to set for the specified key.
    :return: The updated JSON data as a string.
    """
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    json_data[key] = value

    return json.dumps(json_data, indent=4)