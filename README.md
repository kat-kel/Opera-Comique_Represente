# Projet Python

## Requirements
- Python, version 3 --> [installation instructions](https://realpython.com/installing-python/)
- virtualenv

## Instructions (fr)

1. Open a terminal.

2. Change directories (aka move) with the command `cd` to wherever you want the folder `Opera-Comique_Represente` to be downloaded. 

3. Clone the project from Github: ```git clone https://github.com/kat-kel/Opera-Comique_Represente.git```

4. Change to the downloaded directory: ```cd Opera-Comique_Represente```

5. Create a virtual environment.
   * mac, linux: ```python3 -m venv venv-opera```
   * windows: ```py -m venv venv-opera```

6. Activate the virtual environment.
   * mac, linux: ```source venv-opera/bin/activate```
   * windows: ```.\venv-opera\Scripts\activate```

7. In your virtual environment, download the required Python extensions.
   * mac, linux: ```pip install -r requirements.txt```
   * windows: ```-m pip install requirements.txt```

8. Run the Flask web application: ```flask run```

9. Load this URL in a browser (not Internet Explorer): http://127.0.0.1:5000/.