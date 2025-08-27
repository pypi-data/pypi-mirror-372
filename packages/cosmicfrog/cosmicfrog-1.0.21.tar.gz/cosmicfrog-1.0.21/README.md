# README #

This library contains helper code for working with Cosmic Frog Anura supply chain models

# What is this repository for?

Include this library in your code to simplify interactions with Cosmic Frog models when integrating with external systems

# How do I get set up? #

include cosmic_frog
see examples folder for example code for common operations
see tests folder for tests and example files

## running the tests with pytest
The tests and associated files are located in the ./cosmicfrog/cosmicfrog/tests directory. In order to run these tests with pytest you will need to run them from the ./cosmicfrog directory. This is necessary so the project can be properly imported without having to do a full build of the component.  
```
/mnt/c/code/cosmicfrog/cosmicfrog-cosmicfrog/cosmicfrog (feature/excel-sheet1)$ python -m pytest cosmicfrog/tests/unit_test.py -v
```
In order to have the component be able to import from the local source code and find all the directories, depencies, files, etc. you will need to run the command as shown above. It needs to be in the project directory (/mnt/c/code/cosmicfrog/cosmicfrog-cosmicfrog or below) in order to be able to import the directory in the python path when the tests start

Also note the use of the `Path(__file__).with_name('customers.csv')` pattern in unit_test.py. This ensures that dependent files in the tests that are in the same directory as the tests will be open.

# Publishing

This library is published on pypi, via the script in the cosmicfrog folder, e.g. 

./publish_pypi./sh

The username is __token__ , and the pypi app key is also required.

The version number in setup.py should be increases before pushing a new version with this script.  

the installation script uses twine to update pypi. Here are the steps you will need to follow.  

*  Install twine if you do not have it already. Be sure you are installing the twine utility for publishing to pypi and not the twine editor.  
    *  ```pip install twine```
*  run the script
    *  ```./publish_pypi.sh```
*  you will be prompted to enter your api token
    *  then token is over 200 characters long. You will want to copy and paste it.
    *  This is currently in a file (pypi.txt) that can be gotten from Mike Surel or Gordon Hart. The token will have a copy available in azure keyvault in the near future.
*  if the installation is successful you will get a prompt telling you where to view the package
    *  e.g. View at:
https://pypi.org/project/cosmicfrog/0.3.60/



# Configuration
A number of environment variables are used to configure this application  


**ADMIN_APP_KEY** - app key for an administrative user that can perform actions in the API on behalf of other users or at the system level.  
**APPLICATIONINSIGHTS_CONNECTION_STRING** - connection string to application insights for metrics, logging and monitoring.  
**ATLAS_API_BASE_URL** - The base url used for the platform. This is usually https://api.optilogic.app/v0/.  
**ATLAS_SERVICE_URL** - url for atlas service. Usually https://service.optilogic.app/appkey/authenticate.  
**AUTH_MAX_RETRIES** - number of retries for authorization call when getting an app key on the user's behalf. Defaults to 3.  
**CF_ACTIVITY_URL** - url for the activitiy service, barking frog.  
**CFLIB_CONNECT_TIMEOUT** - timeout for database connections. This is in seconds. Defaults to 15.   
**CFLIB_DEFAULT_MAX_RETRIES** - number of times to retry database connections. Defaults to 5.  
**CFLIB_DEFAULT_RETRY_DELAY** - delay between database connection attempts in the case a connection cannot be made. this is seconds. Default is 5.  
**CFLIB_IDLE_TRANSACTION_TIMEOUT** - timeout for idle transactions. Unit? Defaults to 1800.  
**CFLIB_STATEMENT_TIMEOUT** - timeout for database statement execution. This is in milliseconds  Defaults to 1800000, which is 30 minutes.  
**FROG_LOG_LEVEL** - Log level for debugging. This corresponds to the definitions of log levels in the logging library. This is an integer. 10 is DBUG, 20 is INFO, 30 is WARN, 40 is ERROR and 50 is CRITICAL.  
**OPTILOGIC_API_URL** - the base of platform api as defined by the optilogic python library. If the platform client needs to point at a different set of services set this variable (e.g. penetration testing or dev environments). Note that setting this will override **ATLAS_API_BASE_URL**.  
**SECURITY_TIMEOUT** - timeout for connections to **ATLAS_SERVICE_URL**.    
# Who do I talk to? #

* cosmicfrog.com
* support@optilogic.com
