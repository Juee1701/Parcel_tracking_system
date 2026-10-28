PARCEL TRACKING SYSTEM - SETUP

Requirements:
- Python 3.10 or newer
- Internet connection only to install Flask the first time

Windows setup:
1. Extract this ZIP file to a folder, for example Desktop\parcel_tracking_system.
2. Open that folder in File Explorer.
3. Click the address bar, type cmd, and press Enter.
4. Run:
   py -m pip install -r requirements.txt
5. Then run:
   py app.py
   If `py` is not recognized, try `python` instead.
6. Open the address printed in the terminal, usually:
   http://127.0.0.1:5000

The database file `parcels.db` is created automatically in the project folder.
Keep the terminal open while using the website. Press Ctrl+C in the terminal to stop it.

Main pages:
- /                 Home dashboard
- /add              Add a parcel
- /track            Track a parcel
- /parcels          View all parcels
- /update/<id>      Update a parcel's status

Project note:
This is a local academic demonstration. It does not connect to courier-company systems
or provide real-world GPS tracking. Parcel records and status changes are stored in SQLite.
The Flask debug server is for development only, not public production deployment.
