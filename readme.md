## Instructions

---

### Configuration:

##### [.env](.env)

    
    MONGO_INITDB_ROOT_USERNAME=VAL - Username to use for connection to database
    MONGO_INITDB_ROOT_PASSWORD=VAL - Password to user for connection to database


##### [app/config.py](app/config.py)
    
    DATABASE_NAME - Name of database to create
    TABLE_NAME - Name of table in database to create
    RESULT_PLOT_PATH - Path to file with image of result plot
    TIME_RECORD_PATH = Path to file with load time record
    

---

### Start the application:

1. Start `Docker Engine`.


2. Download/unpack project into desire folder.  


3. Open console in the same folder as project.  


4. Run following command to build application:

        $ docker-compose build
    

5. Run following command to *start* application:
   
       $ docker-compose up
   

**Note**: Command to *stop* application:

    $ docker-compose down


---