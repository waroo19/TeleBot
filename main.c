/*
 * Copyright (C) 2019 Javier FILEIV <javier.fileiv@gmail.com>
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     examples
 * @{
 *
 * @file        main.c
 * @brief       Example using MQTT Paho package from RIOT
 *
 * @author      Javier FILEIV <javier.fileiv@gmail.com>
 *
 * @}
 */

#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include "timex.h"
#include "ztimer.h"
#include "shell.h"
#include "thread.h"
#include "mutex.h"
#include "paho_mqtt.h"
#include "MQTTClient.h"
#include "pthread.h"

#define MAIN_QUEUE_SIZE     (8)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

#define BUF_SIZE                        1024
#define MQTT_VERSION_v311               4       /* MQTT v3.1.1 version is 4 */
#define COMMAND_TIMEOUT_MS              4000

#ifndef DEFAULT_MQTT_CLIENT_ID
#define DEFAULT_MQTT_CLIENT_ID          ""
#endif

#ifndef DEFAULT_MQTT_USER
#define DEFAULT_MQTT_USER               ""
#endif

#ifndef DEFAULT_MQTT_PWD
#define DEFAULT_MQTT_PWD                ""
#endif

/**
 * @brief Default MQTT port
 */
#define DEFAULT_MQTT_PORT               1883

/**
 * @brief Keepalive timeout in seconds
 */
#define DEFAULT_KEEPALIVE_SEC           10

#ifndef MAX_LEN_TOPIC
#define MAX_LEN_TOPIC                   100
#endif

#ifndef MAX_TOPICS
#define MAX_TOPICS                      4
#endif

#define IS_CLEAN_SESSION                1
#define IS_RETAINED_MSG                 1

static MQTTClient client;
static Network network;
static int topic_cnt = 0;
static char _topic_to_subscribe[MAX_TOPICS][MAX_LEN_TOPIC];

static unsigned get_qos(const char *str)
{
    int qos = atoi(str);

    switch (qos) {
    case 1:     return QOS1;
    case 2:     return QOS2;
    default:    return QOS0;
    }
}

static void _on_msg_received(MessageData *data)
{
    printf("paho_mqtt_example: message received on topic"
           " %.*s: %.*s\n",
           (int)data->topicName->lenstring.len,
           data->topicName->lenstring.data, (int)data->message->payloadlen,
           (char *)data->message->payload);
}

static int _cmd_discon(int argc, char **argv)
{
    (void)argc;
    (void)argv;

    topic_cnt = 0;
    int res = MQTTDisconnect(&client);
    if (res < 0) {
        printf("mqtt_example: Unable to disconnect\n");
    }
    else {
        printf("mqtt_example: Disconnect successful\n");
    }

    NetworkDisconnect(&network);
    return res;
}

static int _cmd_con(int argc, char **argv)
{
    if (argc < 2) {
        printf(
            "usage: %s <brokerip addr> [port] [clientID] [user] [password] "
            "[keepalivetime]\n",
            argv[0]);
        return 1;
    }

    char *remote_ip = argv[1];

    int ret = -1;

    /* ensure client isn't connected in case of a new connection */
    if (client.isconnected) {
        printf("mqtt_example: client already connected, disconnecting it\n");
        MQTTDisconnect(&client);
        NetworkDisconnect(&network);
    }

    int port = DEFAULT_MQTT_PORT;
    if (argc > 2) {
        port = atoi(argv[2]);
    }

    MQTTPacket_connectData data = MQTTPacket_connectData_initializer;
    data.MQTTVersion = MQTT_VERSION_v311;

    data.clientID.cstring = DEFAULT_MQTT_CLIENT_ID;
    if (argc > 3) {
        data.clientID.cstring = argv[3];
    }

    data.username.cstring = DEFAULT_MQTT_USER;
    if (argc > 4) {
        data.username.cstring = argv[4];
    }

    data.password.cstring = DEFAULT_MQTT_PWD;
    if (argc > 5) {
        data.password.cstring = argv[5];
    }

    data.keepAliveInterval = DEFAULT_KEEPALIVE_SEC;
    if (argc > 6) {
        data.keepAliveInterval = atoi(argv[6]);
    }

    data.cleansession = IS_CLEAN_SESSION;
    data.willFlag = 0;

    printf("mqtt_example: Connecting to MQTT Broker from %s %d\n",
            remote_ip, port);
    printf("mqtt_example: Trying to connect to %s, port: %d\n",
            remote_ip, port);
    ret = NetworkConnect(&network, remote_ip, port);
    if (ret < 0) {
        printf("mqtt_example: Unable to connect\n");
        return ret;
    }

    printf("user:%s clientId:%s password:%s\n", data.username.cstring,
             data.clientID.cstring, data.password.cstring);
    ret = MQTTConnect(&client, &data);
    if (ret < 0) {
        printf("mqtt_example: Unable to connect client %d\n", ret);
        _cmd_discon(0, NULL);
        return ret;
    }
    else {
        printf("mqtt_example: Connection successfully\n");
    }

    return (ret > 0) ? 0 : 1;
}

static int _cmd_pub(int argc, char **argv)
{
    enum QoS qos = QOS0;

    if (argc < 3) {
        printf("usage: %s <topic name> <string msg> [QoS level]\n",
               argv[0]);
        return 1;
    }
    if (argc == 4) {
        qos = get_qos(argv[3]);
    }
    MQTTMessage message;
    message.qos = qos;
    message.retained = IS_RETAINED_MSG;
    message.payload = argv[2];
    message.payloadlen = strlen(message.payload);

    int rc;
    if ((rc = MQTTPublish(&client, argv[1], &message)) < 0) {
        printf("mqtt_example: Unable to publish (%d)\n", rc);
    }
    else {
        printf("mqtt_example: Message (%s) has been published to topic %s"
               "with QOS %d\n",
               (char *)message.payload, argv[1], (int)message.qos);
    }

    return rc;
}

static int _cmd_sub(int argc, char **argv)
{
    enum QoS qos = QOS0;

    if (argc < 2) {
        printf("usage: %s <topic name> [QoS level]\n", argv[0]);
        return 1;
    }

    if (argc >= 3) {
        qos = get_qos(argv[2]);
    }

    if (topic_cnt > MAX_TOPICS) {
        printf("mqtt_example: Already subscribed to max %d topics,"
                "call 'unsub' command\n", topic_cnt);
        return -1;
    }

    if (strlen(argv[1]) > MAX_LEN_TOPIC) {
        printf("mqtt_example: Not subscribing, topic too long %s\n", argv[1]);
        return -1;
    }
    strncpy(_topic_to_subscribe[topic_cnt], argv[1], strlen(argv[1]));

    printf("mqtt_example: Subscribing to %s\n", _topic_to_subscribe[topic_cnt]);
    int ret = MQTTSubscribe(&client,
              _topic_to_subscribe[topic_cnt], qos, _on_msg_received);
    if (ret < 0) {
        printf("mqtt_example: Unable to subscribe to %s (%d)\n",
               _topic_to_subscribe[topic_cnt], ret);
        _cmd_discon(0, NULL);
    }
    else {
        printf("mqtt_example: Now subscribed to %s, QOS %d\n",
               argv[1], (int) qos);
        topic_cnt++;
    }
    return ret;
}

static int _cmd_unsub(int argc, char **argv)
{
    if (argc < 2) {
        printf("usage %s <topic name>\n", argv[0]);
        return 1;
    }

    int ret = MQTTUnsubscribe(&client, argv[1]);

    if (ret < 0) {
        printf("mqtt_example: Unable to unsubscribe from topic: %s\n", argv[1]);
        _cmd_discon(0, NULL);
    }
    else {
        printf("mqtt_example: Unsubscribed from topic:%s\n", argv[1]);
        topic_cnt--;
    }
    return ret;
}

/*---------------------new funtions------------------------*/
typedef struct {
    char topic[64];
    char payload[64];
} Message;

static int auto_con(void){
    
    // define IP Address
    char *remote_ip = "2600:1f18:7ac:707:da1d:73f:7776:9c50" ;
    int ret = -1;
    /* ensure client isn't connected in case of a new connection */
    if (client.isconnected) {
        printf("mqtt_example: client already connected, disconnecting it\n");
        MQTTDisconnect(&client);
        NetworkDisconnect(&network);
    }
    int port = DEFAULT_MQTT_PORT;
    MQTTPacket_connectData data = MQTTPacket_connectData_initializer;
    data.MQTTVersion = MQTT_VERSION_v311;

    data.clientID.cstring = DEFAULT_MQTT_CLIENT_ID;
    data.username.cstring = DEFAULT_MQTT_USER;
    data.password.cstring = DEFAULT_MQTT_PWD;
    data.keepAliveInterval = DEFAULT_KEEPALIVE_SEC;
    
    data.cleansession = IS_CLEAN_SESSION;
    data.willFlag = 0;

    printf("mqtt_example: Connecting to MQTT Broker from %s %d\n",
            remote_ip, port);
    printf("mqtt_example: Trying to connect to %s, port: %d\n",
            remote_ip, port);
    ret = NetworkConnect(&network, remote_ip, port);
    if (ret < 0) {
        printf("mqtt_example: Unable to connect\n");
        return ret;
    }

    printf("user:%s clientId:%s password:%s\n", data.username.cstring,
             data.clientID.cstring, data.password.cstring);
    ret = MQTTConnect(&client, &data);
    if (ret < 0) {
        printf("mqtt_example: Unable to connect client %d\n", ret);
        _cmd_discon(0, NULL);
        return ret;
    }
    else {
        printf("mqtt_example: Connection successfully\n");
    }

    return (ret > 0) ? 0 : 1;


}

// Define a struct to hold topic-message pairs
typedef struct {
    char *topic;
    char *message;
} TopicMessagePair;
/* void *auto_pub(void *threadid ) {
    
    enum QoS qos = 0; 
    const char* topic = "sensors/light";
    char* remessage ="off";
    MQTTMessage message;
    message.qos = qos; 
    message.retained = IS_RETAINED_MSG; 
    message.payload = (void *)remessage;;
    message.payloadlen = strlen(message.payload);
     long tid;
    tid = (long)threadid;
   printf("Hello World! It's me, thread #%ld!\n", tid);
    printf("Before MQTTPublish\n");
    int rc = MQTTPublish(&client, topic, &message);
    printf("After MQTTPublish\n");
    if (rc < 0) {
        printf("mqtt_example: Unable to publish (%d)\n", rc);
    }
    else {
        printf("mqtt_example: Message (%s) has been published to topic %s"
               "with QOS %d\n",
               (char *)message.payload, topic, (int)message.qos);
    }

     pthread_exit(NULL);
    
    

} */
/* void *PrintHello(void *threadid)
{
   long tid;
   tid = (long)threadid;
   printf("Hello World! It's me, thread #%ld!\n", tid);
   pthread_exit(NULL);
}
 */

void on_msg_updated(MessageData *data) {
    // Extract topic and payload from the message
   /*  char topic_buf[128];
    char payload_buf[128];
     */
    printf("paho_mqtt_example: message received on topic"
           " %.*s: %.*s\n",
           (int)data->topicName->lenstring.len,
           data->topicName->lenstring.data, (int)data->message->payloadlen,
           (char *)data->message->payload);
   /*  strncpy(topic_buf, data->topicName->lenstring.data, data->topicName->lenstring.len);
    topic_buf[data->topicName->lenstring.len] = '\0';
    strncpy(payload_buf, (char *)data->message->payload, data->message->payloadlen);
    payload_buf[data->message->payloadlen] = '\0'; */
    
    // Update the corresponding message based on the topic
    /* if (strcmp(topic_buf, "sensors/light") == 0 && strcmp(payload_buf, "turn_on") == 0) {
        printf("Testing light--------------------------- \n");
        pthread_t thread_id; 
        printf("Before Thread\n"); 
        pthread_create(&thread_id, NULL, auto_pub, NULL); 
        pthread_join(thread_id, NULL);
        printf("After Thread\n"); 
        
    } */
}



static int auto_pubAll(void) {
   // Define an array of topic-message pairs
    TopicMessagePair pairs[] = {
        {"sensors/temperature", "temperature_data"},
        {"sensors/humidity", "humidity_data"},
        {"sensors/light", "turn_on"}
    };

    enum QoS qos = 1; 

    MQTTMessage message;
    message.qos = qos; 
    message.retained = IS_RETAINED_MSG; 
    
    int rc ;
    int num_pairs = sizeof(pairs) / sizeof(pairs[0]);

    // Publish message to each topic
    for (int i = 0; i < num_pairs; i++) {
        message.payload = (void *)pairs[i].message;
        message.payloadlen = strlen(pairs[i].message); // Payload length

        // Publish the message to the current topic
        if ((rc = MQTTPublish(&client, pairs[i].topic, &message)) < 0) {
            printf("mqtt_example: Unable to publish to topic %s (%d)\n", pairs[i].topic, rc);
        }
        else {
            printf("mqtt_example: Message (%s) has been published to topic %s with QoS %d\n",
                   (char *)message.payload, pairs[i].topic, (int)message.qos);
        }
    }

    return rc; 
}
  
static int auto_subAll(void) {
    // Define an array of topics to subscribe to
    char *topics[] = {
        "sensors/temperature",
        "sensors/humidity",
        "sensors/light"
        
    };
    
    enum QoS qos = 1;

    int ret = 0 ;
    int ntopic = sizeof(topics) / sizeof(topics[0]);
    // Subscribe to each topic 
    for (int i = 0; i < ntopic; i++) {
        ret = MQTTSubscribe(&client, topics[i], qos, on_msg_updated);
        if (ret < 0) {
            printf("mqtt_example: Unable to subscribe to topic: %s\n", topics[i]);
            return ret;
        } else {
            printf("mqtt_example: Subscribed to topic: %s\n", topics[i]);
            topic_cnt++;
        }
    }
    
    return ret;
}

void lightMessageHandler(MessageData *data){
    printf("Light HANDLER-----------------------------------------\n")    ;
    printf("paho_mqtt_example: message received on light topic"
           " %.*s: %.*s\n",
           (int)data->topicName->lenstring.len,
           data->topicName->lenstring.data, (int)data->message->payloadlen,
           (char *)data->message->payload);
    



}
static int auto_handler(void){
    int counter = 0;
    int ret = MQTTSetMessageHandler(&client, "sensors/light", lightMessageHandler);
    printf("this isc calling %d \n",ret);
    if (ret < 0) {
            printf("mqtt_example: Unable to handle to topic: sensors/light\n");
            return ret;
        } 
    else {
            counter++;
            printf("This is the %d --------------\n", counter);
            const char* topic = "response/light";
            char* payload = strdup("light_on");
            enum QoS qos = 1; 
            MQTTMessage message;
            message.qos = qos; 
            message.retained = IS_RETAINED_MSG; 
            message.payload = (void *)payload;
            message.payloadlen = strlen(message.payload);
            int rc = MQTTPublish(&client, topic, &message);
            if (rc < 0) {
                printf("mqtt_example: Unable to publish (%d)\n", rc);
            }
            else {
                printf("mqtt_example: Message (%s) has been published to topic %s"
                    "with QOS %d\n",
                    (char *)message.payload, topic, (int)message.qos);
            }
            free(payload);
            return rc;
        }

    

    

}

static const shell_command_t shell_commands[] =
{
    { "con",    "connect to MQTT broker",             _cmd_con    },
    { "discon", "disconnect from the current broker", _cmd_discon },
    { "pub",    "publish something",                  _cmd_pub    },
    { "sub",    "subscribe topic",                    _cmd_sub    },
    { "unsub",  "unsubscribe from topic",             _cmd_unsub  },
    { NULL,     NULL,                                 NULL        }
};

static unsigned char buf[BUF_SIZE];
static unsigned char readbuf[BUF_SIZE];

int main(void)
{
    if (IS_USED(MODULE_GNRC_ICMPV6_ECHO)) {
        msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);
    }
#ifdef MODULE_LWIP
    /* let LWIP initialize */
    ztimer_sleep(ZTIMER_MSEC, 1 * MS_PER_SEC);
#endif
    
    NetworkInit(&network);
    
    MQTTClientInit(&client, &network, COMMAND_TIMEOUT_MS, buf, BUF_SIZE,
                   readbuf,
                   BUF_SIZE);
    printf("Running mqtt paho test. Type help for commands info\n");

    MQTTStartTask(&client);

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    auto_con();
    auto_pubAll();

    auto_subAll();
    auto_handler();
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);
    return 0;
}
