# FIWARE Platform Deployment

This Docker Compose setup creates a FIWARE-powered smart city platform that integrates IoT devices, manages real-time context data, and enables historical analysis. Below is a detailed explanation of the core components and their interactions:

### **Orion-LD Context Broker**  

Orion-LD acts as the central nervous system of the platform. As an NGSI-LD compliant context broker, it manages digital representations of physical entities (e.g., roads, induction loop sensors, traffic light system). When a sensor sends new data (like vehicle counts), 
Orion-LD updates the corresponding entity's state and propagates these changes to subscribed services (e.g. QuantumLeap for managing historical data). It relies on **MongoDB** to persistently store entity data and exposes its API for CRUD operations and subscriptions.


### **IoT Agent-JSON**  
This component serves as the bridge between physical IoT devices and the FIWARE ecosystem. When a device (e.g., traffic loop) registers with its API key, the IoT Agent translates raw device data into NGSI-LD format. It uses **MongoDB** to maintain a registry of connected devices and their metadata.



### How to run
to start the service, you can simply run:
```
docker-compose up -d
```
