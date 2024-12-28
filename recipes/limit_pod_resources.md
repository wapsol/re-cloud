
We used to have a discussion about limit resouces and seperate the customer with namespace k8s (tenancy)

I think we should comeback and here is my thought about that requirement:

#### Resources: 

limit resouces (CPU,Memory) that the Odoo application and Postgresql could use according to our customer, 
we define this in the deployment yaml file => avoid the application from a customer overhead other app from other customer 

#### Apply resources limit in namespace: 

defind quota => cannot increase the resources over this limit (https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/quota-memory-cpu-namespace/) 

#### Network: 

apply k8s networkpolicy so that only the container inside network namespace able to connect with each other => prevent cross connection between pod from different namespaces