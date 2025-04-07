# City Emulator
Having no direct access to city sensor and actuators, the **City Emulator** is introduced to overcome this limitation by emulating traffic flow data and control mechanism. The City Emulator is implemented through two Python components in this folder:  

1. **`MobilityVirtualEnvironment.py`**: Emulates behavior of the real city system of Bologna. Using real traffic data obtained from Bologna Open Data, the component emulates the traffic loop sensors that measure the number of passing cars. 
   
3. **`PhysicalSystemConnector.py`**: Defines core classes for city entities:
   - **Device**: base class used for representing a city device.
   - **Sensors/Actuators**: extends device class, implementing transmission functions.   
   - **PhysicalSystemConnector**: A class that binds devices (sensors/actuators) to physical entities (e.g., roads).

### Operational Workflow

The emulator operates in two stages, both interacting with the FIWARE IoT Agent. The stages are detailed in two separate functions:

<figure align="center">
<img
  src="https://github.com/user-attachments/assets/06f47387-b0be-437c-97ae-722c69f05147"
  alt="City-Emulation-flow">
</figure>


1. **`setupPhysicalSystem`**  
   - Reads traffic data from `data/mvenvdata/` (Open Data traffic flow measurements).  
   - Initializes roads and their associated devices using instaces of `PhysicalSystemConnector` class.  
   - Registers all devices (linked to a specific road) to the IoT Agent.  

2. **`startPhysicalSystem`**  
   - Collects and filters data to be emulated by date.
   - Activates the city emulation by initiating **hourly data transmission** from registered sensors to the IoT Agent. Once all data for the current timeslot has been transmitted, the process pauses for one hour before advancing to the next timeslot.
  
As long as new data is available, the emulator is able to transmit data, effectively emulating sending information process.

## Example: Adding a Sensor to a Road

Below is a minimal example of how to instantiate a road and connect a traffic loop sensor to it using the `PhysicalSystemConnector`.

```python
from PhysicalSystemConnector import Sensor, PhysicalSystemConnector

# Instantiate a road
road = PhysicalSystemConnector("R001", "Via Emilia")

# Instantiate a traffic loop sensor
traffic_loop = Sensor(
    device_partialid="TL123",
    devicekey="IOT_AGENT_API_KEY",
    name="TL_Emilia",
    sensortype="Traffic Loop"
)

# Attach the sensor to the road
road.addSensor(traffic_loop)
