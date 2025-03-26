# FlowTwin - Web App

This is the Django folder project that contains the web application under the _udtApp_ folder. The application provides various interactive functionalities that exploits the FlowTwin services. 
These include access to both real-time and historical, as well as the traffic model calibration, simulation and results pages.

## Project Structure
The project follows the standard Django stucture, where the running application folder is the _udtApp_:
```plaintext
udtBackEnd
│── udtApp               # Contains application logic for the webApp backend.
│   │── migrations/      # Stores migration files for database schema changes.
│   │── static/          # Contains static files such as CSS, JavaScript, and images.
│   │── templates/       # Holds the HTML files for view management.
│   │── templatetags/    # Defines custom template tags and filters.
│   │── __init__.py      # Marks the directory as a Python package.
│   │── admin.py         # Registers models for Django’s admin interface.
│   │── apps.py          # Configures the application.
│   │── forms.py         # Defines Django forms for user input handling.
│   │── models.py        # Manages the association with database entities.
│   │── tests.py         # Contains test cases to ensure application reliability.
│   │── urls.py          # Defines the available URL routes.
│   │── views.py         # Handles HTTP requests and responses.
│── udtBackEnd           # Handles backend functionality for the WebApp.
│── db.sqlite3           # SQLite database file storing application data.
│── manage.py            # Entry point for managing the WebApp backend.
```
## Pages
The Web App is structured in separate pages, in which specific functionalities are implemented. Within some of them, interactive Grafana dashboards are embedded in order to visualize the current status of the infrastructure and the history of the data
The implemented pages are listed below
- **Entity List**: the entity list is a page that collects all the entities registered by the Context Broker. The list can be filtered by entity type (e.g., RoadSegment). Selecting a specific entity takes you to the detail page, where the attributes, creation and last modification date are shown. For traffic loops, a graphical dashboard showing the history of readings has been integrated.
- **Monitor**: this page shows a general Grafana dashboard showing values over time associated with all registered devices.
- **Calibrator**: on this page you can set up a simulation process with calibrated traffic models. In fact, there is a form where you select the macromodel, the car-following model and its associated parameters, as well as indicate the date and time of the measurements you want to simulate. Once everything is set up, you can run the simulation, which will take place off-screen. When the simulation is finished, the results will be visible within the Results page.
- **Results**:
