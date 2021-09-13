import requests
import json
import time

def automate_vm_creation(form_data):

    token = "Bearer NH9QW60oD9Ijfh3luE06RVtcmq82f7qWWHlGcnTND2Ov0gnyXBEbl0WRCsQ9Y44o"
    snapshot_image =  "47744853"

    # Provision a new server using a snapshot image:

    input_data = {"server_type": "cx11", "image": snapshot_image, "name": "api-test-server"}

    try:
        response = requests.post(
            url='https://api.hetzner.cloud/v1/servers',
            headers={"Content-Type": "application/json", "Authorization": token},
            data=json.dumps(input_data)
        )

    except requests.exceptions.HTTPError as e:
        print(e)
    except requests.exceptions.ConnectionError as e:
        print(e)
    except requests.exceptions.Timeout as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)

    print(response.status_code)
    if (response.status_code == 201):

        dict_response = json.loads(response.text)

        new_vm = {
            "root_password": dict_response['root_password'],
            "server_id": dict_response['server']['id'],
            "name": dict_response['server']['name'],
            "primary_disk_size": dict_response['server']['primary_disk_size'],
            "ipv4": dict_response['server']['public_net']['ipv4']['ip'],
            "ipv6": dict_response['server']['public_net']['ipv6']['ip'],
            "server_type": dict_response['server']['server_type']
        }

        status = "initializing"
        start = time.time()
        while(status != "running"):
            response = requests.get(
                url='https://api.hetzner.cloud/v1/servers',
                headers={"Content-Type": "application/json", "Authorization": token},
                params={"name": new_vm['name']}
            )

            dict_response = json.loads(response.text) 
            status = dict_response['servers'][0]['status']
            end = time.time()
            dt = end - start
            print(status, "time elapsed:", dt, "sec")

        new_vm["success"] = True

    else:
        print(json.dumps(response.json(), indent=4))
        new_vm = {"success": False}

    return new_vm

# Main program:
new_user_data = {
    "firstname": "Elena",
    "lastname": "Kusevska",
    "e-mail": "elena.kusevska@gmail.com",
    "password": "password"
}

new_vm = automate_vm_creation(new_user_data)
print(new_vm)
print(" ")

