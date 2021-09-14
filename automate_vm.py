import requests
import json
import time

def provision_new_server(new_user_data):

    # To do: set up as environment variables
    token = "Bearer lyhhUacDJNH19LxVujGooKoCiaTsCHPboY0NEhGxLrsQcXjlE25uNWySw98m6P2d"
    snapshot_image_id =  "47744853"

    # Provision a new server using a snapshot image:
    input_data = {"server_type": "cx11", "image": snapshot_image_id, "name": "api-test-server"}

    try:
        response = requests.post(
            url='https://api.hetzner.cloud/v1/servers',
            headers={"Content-Type": "application/json", "Authorization": token},
            data=json.dumps(input_data)
        )

    except requests.exceptions.HTTPError as e:
        new_server = {"provisioned": False, "error": "encountered HTTPError exception", "exception": e}
        return new_server
    except requests.exceptions.ConnectionError as e:
        new_server = {"provisioned": False, "error": "encountered ConnectionError exception", "exception": e}
        return new_server
    except requests.exceptions.Timeout as e:
        new_server = {"provisioned": False, "error": "encountered Timeot exception", "exception": e}
        return new_sever
    except requests.exceptions.RequestException as e:
        new_server = {"provisioned": False, "error": "encountered Other exception", "exception": e}
        return new_server

    # If provisioning of new server was successful:
    if (response.status_code == 201):

        dict_response = json.loads(response.text)

        # Store data about new server:
        new_vm = {
            "root_password": dict_response['root_password'],
            "server_id": dict_response['server']['id'],
            "name": dict_response['server']['name'],
            "primary_disk_size": dict_response['server']['primary_disk_size'],
            "ipv4": dict_response['server']['public_net']['ipv4']['ip'],
            "ipv6": dict_response['server']['public_net']['ipv6']['ip'],
            "server_type": dict_response['server']['server_type']
        }

        # Once the new server is running:
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

            # To do: set up a timeout for the loop

        # Set the status of the provisioning as success:
        new_server["provisioned"] = True

    else:
        new_server = {"provisioned": False, 
            "error": "status code of response not 201", 
            "error description": json.loads(response.text) }

    return new_server

def set_up_A_record(new_server):
    a_record = {"set up": True}
    return a_record

def ssl(new_user_data, new_server, a_record):
    ssl_certificate = {"set up": True}
    return a_record

def nginx_port_mapping(new_server):
    nginx = {"port mapped": True}
    return nginx

def send_email_to_client(new_user_data, new_server, a_record, ssl_certificate, nginx):
    e_mail_to_client = {"sent": True}
    return e_mail_to_client

def automate_vm_creation(new_user_data):
    new_vm = {}
    new_server = provision_new_server(new_user_data)

    if (new_server['provisioned']):
        new_vm["new server"] = new_server
        print("step 1:", new_vm)
        a_record = set_up_A_record(new_user_data, new_server)
    else:
        # Send e-mail to admin
        print("step 1 error", new_server)
        return{"success": False}

    if (a_record['set up']):
        ssl_certificate = ssl(new_user_data, new_server, a_record)
    else:
        # send e-mail to admin
        return{"success": False}

    if (ssl_certificate['set up']):
        nginx = nginx_port_mapping(new_server)
    else:
        # send e-mail to admin
        return{"success": False}

    if (nginx['port_mapped']):
        e_mail_to_client = send_email_to_client(new_user_data, new_server, a_record, ssl_certificate, nginx)
    else:
        # Send e-mail to admin
        return {"success": False}

    if (e_mail_to_client['sent']):
        new_vm['success'] = True 
        return new_vm
    else:
        # Send e-mail to admin
        return {"success": False}


def main():
    new_user_data = {
        "firstname": "Elena",
        "lastname": "Kusevska",
        "e-mail": "elena.kusevska@gmail.com",
        "password": "password"
    }

    new_vm = automate_vm_creation(new_user_data)

    print(new_vm)
    print(" ")

if __name__ == "__main__":
    main()
