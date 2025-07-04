# -*- coding: utf-8 -*-
# /usr/bin/env python
# Example code to use Adafruit_CircuitPython_BME280

import socket
import time
import sys
import re
#change_json is imported to change the data format to JSON
import change_json
#get_to_bme280.py is imported to use the BME280 sensor
import get_to_bme280

SERVER = 'localhost'
WAITING_PORT = 8765
MESSAGE_FROM_CLIENT = "Hello, I am a client."

WAIT_INTERVAL = 5  # seconds
def client(hostname_v1 = SERVER, waiting_port_v1 = WAITING_PORT, message1 = MESSAGE_FROM_CLIENT):
   
    
    node_s = hostname_v1
    port_s = waiting_port_v1
    client_name = socket.gethostname()

    try:
        count = 0
        while True:

            # socoket for receiving and sending data
            # AF_INET     : IPv4
            # SOCK_STREAM : TCP
            socket_r_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_r_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("node_s:", node_s,  " port_s:", str(port_s))
            socket_r_s.connect((node_s, port_s))
            print('Connecting to the server. '
                + 'node: ' + node_s + '  '
                + 'port: ' + str(port_s))

            message1.append(get_to_bme280.get_bme280_data())
            message1.append(client_name)

            data_s_str = change_json.change_json(message1, "client_name", client_name)

            socket_r_s.send(data_s_str)

            print('I (a client) have just sent data __' 
                + str(data_s_str)
                + '__ to the server ' + node_s + ' .')

            socket_r_s.close()

            time.sleep(WAIT_INTERVAL)

            count = count + 1
            if count > 100:
                print("End of the client.")
                # break
                pass

    except KeyboardInterrupt:
        print("Ctrl-C is hit!")
        print("End of this client.")

def hostname_check(hostname_v):
    while True:
            try:
                yes_no = str(input(f"now hostname{hostname_v} . Are you OKey? y/n "))
                if (yes_no == "n"):
                    onetime_hostname_v = input("Please input the hostname: ")
                    # ...existing code...
                    check = re.match(
                        r"^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\."
                        r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\."
                        r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\."
                        r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$",
                        onetime_hostname_v
                    )
                    # ...existing code...
                    if not check:
                        print("Please input the hostname again.")
                        return False
                    else:
                        hostname_v = onetime_hostname_v
                        print("hostname_v is set to:", hostname_v)
                        return True
                elif (yes_no == "y"):
                    print("hostname_v is set to:", hostname_v)
                    return True
                else:
                    pass
            except ValueError:
                print("Please input the hostname again.")
                return False
            except KeyboardInterrupt:
                print("Ctrl-C is hit!")
                print("End of this client.")
                sys.exit(0)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                sys.exit(1)

def main():
    print("Start if __name__ == '__main__'")

    sys_argc = len(sys.argv)
    count = 1
    hostname_v = "10.192.138.250"
    waiting_port_v = 8765
    message_v = "TEST"
    hostname_v_boolean = False

    while True:
        print(count, "/", sys_argc)
        if(count >= sys_argc):
            break

        option_key = sys.argv[count]
        #print(option_key)
        if ("-h" == option_key):
            count = count + 1
            hostname_v = sys.argv[count]
            hostname_v_boolean = True
            #print(option_key, hostname_v)
        if ("-p" == option_key):
            count = count + 1
            waiting_port_v = int(sys.argv[count])
            #print(option_key, port_v)
        if ("-m" == option_key):
            count = count + 1
            message_v = sys.argv[count]
            #print(option_key, message_v)

        count = count + 1

    print("hostname_v_boolean:", hostname_v_boolean)
    print("hostname_v:", hostname_v)
    print("waiting_port_v:", waiting_port_v)
    print("message_v:", message_v)

    while not hostname_v_boolean:
        print("hostname_v is not set. Please input the hostname.")
        hostname_v_boolean = hostname_check(hostname_v)
        

    print("hostname_v:", hostname_v)

    client(hostname_v, waiting_port_v, message_v)

if __name__ == "__main__":
    main()

