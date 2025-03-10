Flask-AppBuilder With Keycloak and JWT
=======================================
--------------------------------------------------------------

- Clone the project::

	git clone https://github.com/applerdotxyz/keycloak-fab-demo.git
---------------------------------------------------------------

- Install virtual enviroment::
	
	pip install virtualenv
- Make a virtual enviroment::

	virtaulenv env
- Launch the virtual enviroment::

	./env/Scripts/activate.ps1
- Install dependencies::

	pip install -r Requirement.txt

    
----------------------------------------------------------------

- Run the project through pytest code with SeleniumBase::

	pytest pytest-Keycloak.py --html=report.html 
- Go to browser at http://localhost:8080/ and login with the credentials::
	
	Username: admin
	Password: admin
- Click on the dropdown menu next to realm name and select the realm name::
	
	Realm Name: myrealm (or whatever realm name you choose )
- Click on Realm Settings in the left menu and then click on Keys tab:
	
- Click on the Public Key in front of Algorithms RS256 and copy the key and paste it in the .env in the PUBLIC_KEY variable (in the given format)
	
- Run the FAB app with the command::
	
	pytest pytest-fab.py --html=report.html 
- Run and check api's through ::

	pytest pytest-api.py -v
	
SeleniumBase does have timing errors, so if you get any error, please run the command again.
if you want to change the name of the realm user client, you can change it in the .env file.

----------------------------------------------------------------
- commands to run the keycloak and fab app just for debugging is ::
	
	1. Run the keycloak server::
	
		docker compose up --build
	
	2. Run the FAB app::
			
		flask run --host=0.0.0.0 --port=5000

That's it!!


