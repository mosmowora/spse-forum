import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyDjrfvE8FPIq1Zu8gFzJChdz_y7hwcTf3E",
  "authDomain": "spse-adventure.firebaseapp.com",
  "databaseURL": "https://spse-adventure-default-rtdb.firebaseio.com",
  "projectId": "spse-adventure",
  "storageBucket": "spse-adventure.appspot.com",
  "messagingSenderId": "880192570755",
  "appId": "1:880192570755:web:ef31a8d4f721549754a2b6",
  "measurementId": "G-EF9NM3SH3Q"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()  
    
def retrieve_data(name=""):
    '''
    Retrieves the data from the server
    '''
    users = db.get()
    if users.each() is not None:
        if name != "":
            for user in users.each():
                if user.val()["name"] == name: return user.val()
        
        else:
            name_ending: list[tuple] = []

            for player in range(len(users.each())): 
                if 'endings' not in users[player].val().keys(): users[player].val()['endings'] = []
                name_ending.append((len(users[player].val()['endings']), users[player].val()['name']))
            name_ending.sort(reverse=True)

            return {name_ending[user] : name_ending[user] for user in range(len(name_ending))}
    
    return []