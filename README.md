## SOCIAL NETWORK PLATFORM

##### + run Mongodb From the conf file (mongod.conf):
    - cd social-network-platform
    - mkdir data
    - mkdir log
    - touch mongod.conf
```
    systemLog:
        destination: file
        path: "/Users/MDRAHALI/Desktop/Learning_Roadmap/social-network-platform/log/mongod.log"
        logAppend: t`rue
    storage:
        journal:
            enabled: false
        dbPath: "/Users/MDRAHALI/Desktop/Learning_Roadmap/social-network-platform/data"
    processManagement:
           fork: true
    net:
        bindIp: 0.0.0.0
        port: 27017
```

    - mongod -f mongod.conf


##### + to restart mongodb server:

    - sudo rm /usr/local/var/mongodb/mongod.lock
    - mongod -f mongod.conf
        or use this command
    - chmod -R 755 mongo_restart

##### + if you got this error `` Failed to set up listener: SocketException: Address already in use `` :

    1- sudo lsof -iTCP -sTCP:LISTEN -n -P

    2- sudo kill 37885

    3- mongod -f mongod.conf

##### + Launch The App :
    - export environment='testing'
    => echo $environment # check

    -> python manage.py runserver


##### + database ops:
    1- source ./venv/bin/activate
    2- (venv) MACBOOK-ELRAHALI:social-network-platform mdrahali$ python manage.py shell

##### + running tests:

    -> python tests.py

##### + Mongodb Queries :

    -> db.collection.getIndexes() # find queries
    -> db.users.dropIndex( "userIdx" ) # delete an index by name
    -> db.users.dropIndex( { "username" : -1 } ) # delete an index by key


##### + Indexation Technique:
    # Indexation in mongodb tend to speed-up the read operations from O(n) -> O(1)

    -> db.users.find( { "username" : "mdrahali" } ).explain() # indexed search == we have an index by `username`
    -> db.users.find( "first_name" : "Mohamed" ).explain() # no indexed search
