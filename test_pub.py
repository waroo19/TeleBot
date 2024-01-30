import paho.mqtt.client as paho

broker="18.206.178.158"
port=1883

def on_publish(client,userdata,mid):             #create function for callback
    print(f"Data on published with mid value: {mid}")

def main():
    client1= paho.Client("Testing")                           #create client object
    client1.on_publish = on_publish                          #assign function to callback
    client1.connect(broker,port)                                 #establish connection
    ret= client1.publish("house/bulb1","standby")  
    print(f"Data published with mid value: {ret.mid}")
if __name__ == '__main__':
    main()