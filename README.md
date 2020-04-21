## SOCIAL NETWORK PLATFORM

##### + Features Built-in this social-network platform:
    - Authentification & Authorization
    - Email Registration Confirmation
    - Change Password & Forgot
    - Forms Data Validations
    - Account Reconfirmation when Changing Email
    - CRUD Ops on Models(User, Relationship, Feed)
    - Image Uploads
    - Social Network Standard Features:

        + Post with multiple Images
        + Like
        + Profile
        + Friendship
        + Wall
        + Feed (Fan-out Pattern)
    - 90% Tested Features
    - Mongodb configuration

##### + run Mongodb From the conf file (mongod.conf):
    - cd social-network-platform
    - mkdir data
    - mkdir log
    - touch mongod.conf
```
    systemLog:
        destination: file
        path: "/Users/MDRAHALI/Desktop/Learning_Roadmap/social-network-platform/log/mongod.log"
        logAppend: true
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

##### + Amazon Configuration:
    # Amazon simple Email Service:
        !- mkdir ~/.aws
        !- vi ~/.aws/credentials
        !- add Secret Keys:
                aws_access_key_id = AKI*******************
                aws_secret_access_key = XMF8v*************
        !- vi ~/.aws/config
                    [default]
                    region = us-west-2






##### + Tech Stack And Tools used to build the app :
    - AMAZON Simple Email Service (Mailing Service)
    - Flask (Web Framework)
    - Mongodb (NoSQL Database)
    - AMAZON S3 (Image Upload)
    - Unittest (Unitesting)

##### + CORS configuration editor ARN: arn:aws:s3:::social-network-image-upload

    <?xml version="1.0" encoding="UTF-8"?>
        <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <CORSRule>
                <AllowedOrigin>*</AllowedOrigin>
                <AllowedOrigin>http://*</AllowedOrigin>
                <AllowedOrigin>https://*</AllowedOrigin>
                <AllowedMethod>GET</AllowedMethod>
                <MaxAgeSeconds>3000</MaxAgeSeconds>
                <AllowedHeader>Authorization</AllowedHeader>
            </CORSRule>
        </CORSConfiguration>

##### + Install Some Dependencies :
   - [ImageMagick](https://imagemagick.org/script/download.php)
