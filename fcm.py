from google.auth.transport import requests
from google.oauth2 import service_account
import subprocess
import json



def send_push_notification():
    def generate_access_token(service_account_file):

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

        request = requests.Request()
        credentials.refresh(request)

        return credentials.token

    access_token = generate_access_token('hochwasserwarnapp-4b01ebd06065.json')
    url = 'https://fcm.googleapis.com/v1/projects/hochwasserwarnapp/messages:send'
    device_token = "fz6xutdktw6urasit8wk5q:apa91bgn8zuztxsyy7eygfs5pkqxqg6fsgzoynox_e7b-6ywqrm6h7vfyeiocicm7vvwj1zbohr-1d5ljnraaewwffkbzxcbgfsg1mpf_h-3mz6bxrk8kifizycd9a393e6clxzntpr-"

    data = {
        "message": {
            #"token": "fz6xutdktw6urasit8wk5q:apa91bgn8zuztxsyy7eygfs5pkqxqg6fsgzoynox_e7b-6ywqrm6h7vfyeiocicm7vvwj1zbohr-1d5ljnraaewwffkbzxcbgfsg1mpf_h-3mz6bxrk8kifizycd9a393e6clxzntpr-",
            "topic":"nah",
            "notification": {
                "title": "warnung",
                "body": "test",
            },
            "android": {
                "notification": {
                    "sound": "default", 
                    "sticky": "true",
                    "vibrate_timings" : ["10.5s"],
                    "notification_count": 2
                }
            }
        }
    }

    # convert data to a json string
    data_json = json.dumps(data)

    # build the curl command as a list
    curl_command = [
        'curl',
        '-X', 'POST',
        url,
        '-H', 'content-type: application/json',
        '-H', f'authorization: Bearer {access_token}',
        '-d', data_json
    ]

    # execute the curl command
    process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # print the response
    print(output.decode('utf-8'))
    print(error.decode('utf-8'))
send_push_notification()
