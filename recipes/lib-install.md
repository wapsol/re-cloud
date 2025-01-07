# Guide for installing libraries inside k*s pod (for developers)

## NOTE: Only do this for internal testing purpose. At the time of writing, your sysadmin has probably built an image with neccessary libraries.

Assuming you have access to k*s cluster, run the command ```k9s``` and you will have this:

![image](https://github.com/user-attachments/assets/5f2b0ef7-37f3-4af3-8213-092b74d7d630)

This is the list of pods running in the entire k*s cluster. 

Suppose you want to get inside the odoo pod of ```kj``` as shown above, press d.

![image](https://github.com/user-attachments/assets/7062c147-32f0-4495-8655-d8855eee16af)

Don't be afraid! You only need to take a look at ```Container ID```:

![image](https://github.com/user-attachments/assets/b6ce1a73-9195-4ce1-97b5-bd35a6926300)

Your account might have access to sudo command. If not, ask your admin

Now, remember the container ID, and execute this command

``` sudo runc --root /run/containerd/runc/k8s.io exec -t -u 0 [ContainerID] bash ``` where ContainerID is shown above (but exclude the containerd://)
Tada, you're inside the pod as root. 
![image](https://github.com/user-attachments/assets/369f6a9d-7fab-4ed0-b141-85449ec577f7)

Depends on Odoo version of the pod, you can just ```pip install {} ``` whichever libraries are missing in your case, or you need to ```apt update``` and ```apt install python3-[your-lib]```
