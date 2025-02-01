## What is re-cloud?

re-cloud is a software package that enables to spin up a private cloud on your own bare-metal hardware within minutes. 

Fundamentally, re-cloud provides you an unlimitedly scalable compute units (VMs), storage and networking capabilities including security.
In addition, it provides Kubernetes as a high availability application runtime, for your productive applications with persistent storage.
These capabilities enable organisations to run their own compute infrastructure, either on data-center or on-premise hardware.

## Minimum Requirements

We call bare metal hardware "**nodes**".
You will need at least 3 nodes with the following minimum configuration to get re-cloud initially set up. After that, you can add nodes as your needs scale.

- 8 core CPU
- 64 GB RAM
- 1 TiB SSD or NVMe

We develop for, and hence recommend, Ubuntu Linux latest stable. 
You will need root access with SSH to all your nodes.

## What can you do with re-cloud?

Depending on the type of organisation you are, you can use your private cloud for specific functions.
To support you as much as possible out of the box, we provide "**Stacks**" of software applications. These help you get productive with your re-cloud fast, in the best cases within an hour or two.

We support following Stacks:

- AI Stack
- Office Stack
- IoT Stack
- SaaS and Software

Lists of software packages available in Stacks are documented in [stacks.md](https://).

Depending on your high-availability needs, Stacks are installed on your private-cloud as Docker containers, either on VMs on re-cloud, or the optional Kubernetes cluster running on it.

# Architecture

## Controllers and Workers

To manage your private cloud, it's compute, storage, networking, security and application resources, one (or in larger deployments more) node is dedicated as a **Controller**. Think of this machine as an administration machine, and maintain it as such.

The actual compute, storage and other such functional resources of your private cloud are settled on **Worker** nodes.
Worker nodes are designed to be scaled almost infinitely, baring physical limits.

Together Controllers and Workers ensure a high availability of resources to your organisation, scalable by its needs.

## Storage

re-cloud differentiates between hot and cold storage in terms of a) provisioning disk resoures and b) latency of accessing data.

### Hot Storage

H-Storage is mounted initially on the same hardware that the compute-VM is running, hence offering rapid access to disk-space.
It is mounted at boot-time and carries on it essential operating system components and directories.

### Cold Storage

C-Storage can be attached to (and detached from) any compute-VM as an additional resource. Sometimes, these resources are referred to as Volumes.

Usually some of your hardware nodes are dedicated to storage. 
Such nodes are used to create and expand storage Volumes, hence offering software developers the necessary resources according to their applications' needs.
