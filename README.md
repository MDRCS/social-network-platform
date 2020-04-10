# social-network-platform
SOCIAL NETWORK PLATFORM

+ Launch The App :
-> export environment='testing'
=> echo $environment # check

-> python manage.py runserver

+ database ops:
1- source ./venv/bin/activate
2- (venv) MACBOOK-ELRAHALI:social-network-platform mdrahali$ python manage.py shell


+ Mongodb Queries :

-> db.collection.getIndexes() # find queries
-> db.users.dropIndex( "userIdx" ) # delete an index by name
db.users.dropIndex( { "username" : -1 } ) # delete an index by key


+ Indexation Technique:
    - Indexation in mongodb tend to speed-up the read operations from O(n) -> O(1)

-> db.users.find( { "username" : "mdrahali" } ).explain() # indexed search == we have an index by `username`
-> db.users.find(  "first_name" : "Mohamed" ).explain() # no indexed search
