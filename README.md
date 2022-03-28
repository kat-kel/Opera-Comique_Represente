# Projet Python

## Requirements
* python 3 --> [installation instructions](https://realpython.com/installing-python/)
* virtualenv --> [installation instructions](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
* git

## Instructions for mac, linux

1. Open a terminal.

2. Change directories (aka move) with the command `cd` to wherever you want the folder `Opera-Comique_Represente` to be downloaded. 

3. Clone the project from Github: ```git clone https://github.com/kat-kel/Opera-Comique_Represente.git```

4. Change to the downloaded directory: ```cd Opera-Comique_Represente```

5. Create a virtual environment: ```python3 -m venv env-opera```

6. Activate the virtual environment: ```source env-opera/bin/activate```

7. In your virtual environment, download the required Python extensions: ```pip install -r requirements.txt```

8. Run the Flask web application: ```flask run```

9. Load this URL in a browser (not Internet Explorer): http://127.0.0.1:5000/.

10. To immediately explore the user features, without creating an account, feel free to sign in as Cinderella.
    * username: `Cendrillon`
    * password: `password?Cendrillon`