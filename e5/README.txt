00726104, FABIAN PECHSTEIN
e5 - NETWORK

# some notes
* setup_client.py & setup_server.py connect via an existing wifi and install required libraries using upip
* installing uuid via upip yields an empty file for whatever reason ... just copy the content from here: https://github.com/pfalcon/pycopy-lib/blob/master/uuid/uuid.py
* the client creates a new token (using uuid) during each boot.
* every request needs a Bearer Token to identify the client -> HTTP 401 otherwise
	* multiple clients are supported in theory
* server_init.py creates the  network, server.py holds the server's logic
* server listens to "/state"
	* GET and PUT only -> HTTP 405 otherwise
	* PUT: parameters are mandatory, but are not further validated otherwise
* server flashes a LED everytime a request is processed

# see attached screenshots for json responses, HTTP Status codes etc.