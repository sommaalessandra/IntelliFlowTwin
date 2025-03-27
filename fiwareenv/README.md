# FIWARE Platform Deployment

This Docker Compose setup creates a FIWARE-powered smart city platform that integrates IoT devices, manages real-time context data, and enables historical analysis. Below is a detailed explanation of the core components and their interactions:
  -  **Orion-LD Context Broker**: Orion-LD acts as the central nervous system of the platform. As an NGSI-LD compliant context broker, it manages digital representations of physical entities (e.g., roads, induction loop sensors, traffic light system). When a sensor sends new data (like vehicle counts), 
Orion-LD updates the corresponding entity's state and propagates these changes to subscribed services (e.g. QuantumLeap for managing historical data). It relies on **MongoDB** to persistently store entity data and exposes its API for CRUD operations and subscriptions.

  -  **IoT Agent-JSON**:This component serves as the bridge between physical IoT devices and the FIWARE ecosystem. When a device (e.g., traffic loop) registers with its API key, the IoT Agent translates raw device data into NGSI-LD format. It uses **MongoDB** to maintain a registry of connected devices and their metadata.

  -  **QuantumLeap + TimescaleDB**: QuantumLeap works as the platform's historic data manager. Whenever Orion-LD updates an entity, QuantumLeap captures the change and stores a timestamped record in **TimescaleDB** – a PostgreSQL extension optimized for time-series data. This enables powerful temporal queries, and it's capable
to speed up frequent queries, by leveraging **Redis** as an in-memory cache layer.

  -  **Grafana**: Grafana connects to TimescaleDB to create dynamic dashboards showing time-series trends, geographic distributions (using PostGIS coordinates), and real-time metrics. Pre-installed plugins enhance its capabilities for spatial and temporal data analysis.


### Key Interactions
1. **Device Onboarding**:  
   A traffic sensor registers via the IoT Agent, which in turn it creates an NGSI-LD entity in Orion-LD.

2. **Data Pipeline**:

   The pipeline can be summarized in this flow:
   
    ```beginSensor → Raw data → IoT Agent (JSON-to-NGSI conversion) → Orion-LD (entity update) → QuantumLeap (historical storage in TimescaleDB).```
   
   An emulated sensor begins the transmission of new raw data to the IoT Agent. Here, IoT Agent converts the raw data into NGSI-LD format and send it to Orion-LD Context Broker.
   Through its subscription mechanism, Orion-LD notifies QuantumLeap of data change in the registered entities. QuantumLeap add a timestamp to the data and archives the change into TimescaleDB.
   

4. **Monitoring**:  
   Engineers query Orion-LD's API for real-time status, while Grafana pulls historical data from TimescaleDB for trend analysis.
### How to run
to start the service, you can simply run:
```
docker-compose up -d
```
