# IntelliFlowTwin - library classes

This directory contains the core Python classes and modules used in the **IntelliFlowTwin** platform, which integrates traffic simulators, FIWARE components, and multiple data backends. The system follows a **modular architecture**, ensuring interoperability across simulation engines, context brokers, and databases.

## Folder Structure Overview


### Core Modules (`/classes/`)
-  `Agent.py`  
  Provides the interface to the **FIWARE IoT Agent**. It is responsible for pushing and receiving IoT-related data (e.g., traffic loops, traffic lights) using the FIWARE protocol.

- `Broker.py`  
  Handles communication with the **Orion-LD Context Broker** (NGSI-LD standard). It allows entities to be created, updated, and queried in a semantically enriched format (NGSI-LD), which supports advanced relationships and context-aware operations.

- `SumoSimulator.py`  
  Interfaces with the **SUMO traffic simulator**. It acts as a bridge between the system and the **SUMO traffic simulator**. It offers methods to initialize simulations, monitor their progress, and extract relevant outputs. These simulations can be driven by real data or synthetic scenarios generated within the platform, and their results are used for both evaluation and model refinement.

- `DataManager.py`  
Abstracts access to the various databases in the platform. Includes specific implementations for:
  - **TimescaleDB**: storing time-series and historical traffic data.
  - **MongoDB**: managing flexible, unstructured or semi-structured entity data.
- `DigitalTwinManager.py`  
A "facade" class that orchestrates and coordinates the use of all other modules.  
Provides a unified interface for traffic planning, simulation control, data retrieval, and integration with FIWARE. It provides a simplified API to manage complex workflows such as starting a simulation, fetching historical data, and pushing results into visualization pipelines.

- `Planner.py`  
   The process of building and configuring simulations is handled by the `Planner.py` module. One of its key components is the `ScenarioGenerator` class, which is capable of generating realistic vehicle routes (`.rou.xml` files for SUMO) based on observed traffic patterns or predefined crossing data.

- `SubscriptionManager.py`  
  It is responsible for managing **context subscriptions** within the Orion-LD Broker. These subscriptions are crucial for triggering specific actions or forwarding data to other components when certain changes occur in the system. In our case, it has been extended to support integration with **QuantumLeap** component, for storing historical data.

- `TrafficModeler.py`  
  this module is dedicated to traffic modeling. It supports the construction of both **macroscopic models** (which describe traffic in terms of aggregate variables like flow, speed, and density) and **microscopic models** (as executed within SUMO).
 Beyond model creation, it includes tools for evaluating simulation outcomes.

---

### Utility Modules (`/utils/`)
- **`preprocessingUtils.py`**  
  Provides functions for preprocessing traffic data, such as filtering, normalization, and formatting.

- **`generalUtils.py`**  
  Contains general-purpose functions, especially for data conversion and utility operations used throughout the project.

---

### Project-Wide Configuration
To mantain centralized configuration of absolute paths, model references, and environment-related constants, the file `constants.py` defines key variable such as:
- Absolute paths to data directories (`/data/digitalshadow`, `/data/realworlddata`, etc.).
- FIWARE and Smart Data Model references.
- Paths to the SUMO network and related files.
- Preprocessed traffic datasets.

This file allows consistent access and usage of critical paths and constants throughout the FlowTwin modules. Any changes in directory names or dataset structure should be reflected here to ensure seamless integration across all components.
