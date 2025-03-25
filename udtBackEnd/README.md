# FlowTwin - Web App

This is the Django folder project that contains the web application under the _udtApp_ folder. The application provides various interactive functionalities that exploits the FlowTwin services. 
These include access to both real-time and historical, as well as the traffic model calibration, simulation and results pages.

## Project Structure
The project follows the standard Django stucture, where the running application folder is the _udtApp_:
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
│── udtBackEnd           # Handles backend functionality for the Digital Twin WebApp.
│── db.sqlite3           # SQLite database file storing application data.
│── manage.py            # Entry point for managing the WebApp backend.

## Pages
### Entity Page
### Monitor
### Calibrator
### Results

