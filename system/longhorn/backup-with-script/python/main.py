import argparse
from kubernetes import client, config
import time
from kubernetes.client.rest import ApiException

# Configure Kubernetes client
def configure_k8s():
    try:
        config.load_kube_config()  # For local development
    except Exception:
        config.load_incluster_config()  # For in-cluster execution
    return client.CustomObjectsApi()

def configure_k8s_v1core():
    try:
        config.load_kube_config()  # For local development
    except Exception:
        config.load_incluster_config()  # For in-cluster execution
    return client.CoreV1Api()


# Create a VolumeSnapshot
def create_volume_snapshot(api_instance, namespace, pvc_name, snapshot_name, snapshot_class_name, timeout=300, interval=5):
    """
    Create a VolumeSnapshot and wait for it to become ready to use.

    Parameters:
    - api_instance: The Kubernetes API client instance.
    - namespace: The namespace where the snapshot should be created.
    - pvc_name: The name of the PersistentVolumeClaim to snapshot.
    - snapshot_name: The name of the VolumeSnapshot.
    - snapshot_class_name: The name of the VolumeSnapshotClass to use.
    - timeout: Maximum time to wait for the snapshot to be ready (seconds).
    - interval: Time between status checks (seconds).
    """
    snapshot_body = {
        "apiVersion": "snapshot.storage.k8s.io/v1",
        "kind": "VolumeSnapshot",
        "metadata": {
            "name": snapshot_name,
            "namespace": namespace,
        },
        "spec": {
            "source": {
                "persistentVolumeClaimName": pvc_name
            },
            "volumeSnapshotClassName": snapshot_class_name,
        }
    }
    
    # Create the VolumeSnapshot
    api_instance.create_namespaced_custom_object(
        group="snapshot.storage.k8s.io",
        version="v1",
        namespace=namespace,
        plural="volumesnapshots",
        body=snapshot_body
    )
    print(f"VolumeSnapshot '{snapshot_name}' created for PVC '{pvc_name}' in namespace '{namespace}'.")

    # Wait for the VolumeSnapshot to become ReadyToUse
    start_time = time.time()
    while True:
        try:
            snapshot = api_instance.get_namespaced_custom_object(
                group="snapshot.storage.k8s.io",
                version="v1",
                namespace=namespace,
                plural="volumesnapshots",
                name=snapshot_name
            )
            status = snapshot.get("status", {})
            ready_to_use = status.get("readyToUse", False)
            error = status.get("error", "")
            if error:
                raise Exception(f"Error creating VolumeSnapshot '{snapshot_name}': {error}")
            if ready_to_use:
                print(f"VolumeSnapshot '{snapshot_name}' is ReadyToUse.")
                return snapshot
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"Timed out waiting for VolumeSnapshot '{snapshot_name}' to become ReadyToUse.")
        except ApiException as e:
            print(f"Error fetching VolumeSnapshot status: {e}")

        print(f"Waiting for VolumeSnapshot '{snapshot_name}' to become ReadyToUse...")
        time.sleep(interval)

# Delete a VolumeSnapshot
def delete_volume_snapshot(api_instance, namespace, snapshot_name):
    api_instance.delete_namespaced_custom_object(
        group="snapshot.storage.k8s.io",
        version="v1",
        namespace=namespace,
        plural="volumesnapshots",
        name=snapshot_name
    )
    print(f"VolumeSnapshot '{snapshot_name}' deleted in namespace '{namespace}'.")

def create_pvc_from_snapshot(api_instance, snapshot_name, pvc_name, storage_size , storage_class_name, access_mode="ReadWriteOnce", namespace="default",timeout=300, interval=5):
    """
    Create a PersistentVolumeClaim from a VolumeSnapshot.

    Parameters:
    - api_instance: The Kubernetes API client instance.
    - snapshot_name: The name of the VolumeSnapshot to use.
    - pvc_name: The name of the PersistentVolumeClaim to create.
    - storage_class_name: The StorageClass to associate with the PersistentVolumeClaim.
    - access_mode: The access mode for the PVC. Default is "ReadWriteOnce".
    - namespace: The namespace where the PVC and Snapshot exist. Default is "default".

    Returns:
    - PersistentVolumeClaim details if created successfully, else an error message.
    """
    pvc_body = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {
            "name": pvc_name,
            "namespace": namespace,
        },
        "spec": {
            "storageClassName": storage_class_name,
            "dataSource": {
                "name": snapshot_name,
                "kind": "VolumeSnapshot",
                "apiGroup": "snapshot.storage.k8s.io"
            },
            "accessModes": [access_mode],
            "resources": {
                "requests": {
                    "storage": storage_size  # Adjust storage size as required.
                }
            }
        }
    }

    start_time = time.time()

    created_pvc = api_instance.create_namespaced_persistent_volume_claim(
        namespace=namespace,
        body=pvc_body
    )
    print(f"PersistentVolumeClaim '{pvc_name}' created in namespace '{namespace}'")

    while True:
        try:
            pvc = api_instance.read_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=namespace
            )
            # status = pvc.get("status", {})
            status_phase = pvc.status.phase
            if status_phase == "Bound":
                print(f"PersistentVolumeClaim '{pvc_name}' created successfully.")
                return created_pvc
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"Timed out waiting for PVC '{pvc_name}' change to phase Bound.")
        except ApiException as e:
            print(f"Failed to create PersistentVolumeClaim: {e}")
            return None
        print(f"Waiting for PVC '{pvc_name}' to change to phase Bound...")

        time.sleep(interval)

# List VolumeSnapshots
def list_volume_snapshots(api_instance, namespace):
    snapshots = api_instance.list_namespaced_custom_object(
        group="snapshot.storage.k8s.io",
        version="v1",
        namespace=namespace,
        plural="volumesnapshots"
    )
    print(f"Listing VolumeSnapshots in namespace '{namespace}':")
    for snapshot in snapshots.get("items", []):
        print(f"  - Name: {snapshot['metadata']['name']}")

def associate_volume_snapshot_and_content(api_instance, snapshot_name, snapshot_content_name, snapshot_class_name, snapshot_source_handle):
    """
    Create VolumeSnapshot and VolumeSnapshotContent resources.

    Parameters:
    - api_instance: The Kubernetes API client instance.
    - snapshot_name: The name of the VolumeSnapshot.
    - snapshot_content_name: The name of the VolumeSnapshotContent.
    - snapshot_class_name: The VolumeSnapshotClass name.
    - snapshot_source_handle: The snapshot handle pointing to the existing backup.

    Returns:
    - Tuple of VolumeSnapshot and VolumeSnapshotContent details if created successfully, else None.
    """
    # VolumeSnapshotContent definition
    snapshot_content_body = {
        "apiVersion": "snapshot.storage.k8s.io/v1",
        "kind": "VolumeSnapshotContent",
        "metadata": {
            "name": snapshot_content_name
        },
        "spec": {
            "volumeSnapshotClassName": snapshot_class_name,
            "driver": "driver.longhorn.io",
            "deletionPolicy": "Delete",
            "source": {
                "snapshotHandle": snapshot_source_handle
            },
            "volumeSnapshotRef": {
                "name": snapshot_name,
                "namespace": "default"
            }
        }
    }

    # Create VolumeSnapshotContent
    try:
        created_content = api_instance.create_namespaced_custom_object(
            group="snapshot.storage.k8s.io",
            version="v1",
            namespace="default",
            plural="volumesnapshotcontents",
            body=snapshot_content_body
        )
        print(f"VolumeSnapshotContent '{snapshot_content_name}' created successfully.")
    except ApiException as e:
        print(f"Failed to create VolumeSnapshotContent: {e}")
        return None, None

    # VolumeSnapshot definition
    snapshot_body = {
        "apiVersion": "snapshot.storage.k8s.io/v1",
        "kind": "VolumeSnapshot",
        "metadata": {
            "name": snapshot_name,
            "namespace": "default"
        },
        "spec": {
            "volumeSnapshotClassName": snapshot_class_name,
            "source": {
                "volumeSnapshotContentName": snapshot_content_name
            }
        }
    }

    # Create VolumeSnapshot
    try:
        created_snapshot = api_instance.create_namespaced_custom_object(
            group="snapshot.storage.k8s.io",
            version="v1",
            namespace="default",
            plural="volumesnapshots",
            body=snapshot_body
        )
        print(f"VolumeSnapshot '{snapshot_name}' created successfully.")
        return created_snapshot, created_content
    except ApiException as e:
        print(f"Failed to create VolumeSnapshot: {e}")
        return None, None

# def create_pvc_from_backup():


# Main function with argument parsing
def main():
    parser = argparse.ArgumentParser(description="Manage Kubernetes CSI Snapshots using the Snapshot Controller.")
    parser.add_argument("action", choices=["create-snapshot", "delete-snapshot", "list-snapshots", "create-pvc-from-snapshot"],
                        help="Action to perform: create-snapshot, delete-snapshot, create-pvc-from-snapshot ,or list-snapshots")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--pvc-name", help="Name of the PersistentVolumeClaim (required for create-snapshot)")
    parser.add_argument("--snapshot-name", help="Name of the VolumeSnapshot")
    parser.add_argument("--snapshot-class-name", help="Name of the VolumeSnapshotClass (required for create-snapshot)", default="longhorn-backup-vsc")
    parser.add_argument("--access-mode", help="Name of the PVC access-mode (ReadWriteOnce, ReadWriteMany)")
    parser.add_argument("--storage-size", help="PVC storage size (default 5Gi)", default="5Gi" )
    parser.add_argument("--storage-class-name", help="Name of the VolumeSnapshotClass (required for create-snapshot)", default="longhorn")
    parser.add_argument("--backup-id", help="Longhorn backup id")


    args = parser.parse_args()

    # Configure Kubernetes API client
    api_instance = configure_k8s()

    # Perform actions based on the specified action
    if args.action == "create-snapshot":
        if not args.pvc_name or not args.snapshot_name:
            raise ValueError("PVC name, and snapshot name are required for create-snapshot action.")
        create_volume_snapshot(api_instance, args.namespace, args.pvc_name, args.snapshot_name, args.snapshot_class_name)

    elif args.action == "delete-snapshot":
        if not args.snapshot_name:
            raise ValueError("Snapshot name is required for delete-snapshot action.")
        delete_volume_snapshot(api_instance, args.namespace, args.snapshot_name)

    elif args.action == "list-snapshots":
        if not args.namespace:
            raise ValueError("namespace are required for list-snapshot action.") 
        list_volume_snapshots(api_instance, args.namespace)
        
    elif args.action == "create-pvc-from-snapshot":
        if not args.pvc_name or not args.snapshot_name or not args.namespace:
            raise ValueError("PVC name, namespace and snapshot name are required for create-pvc-from-snapshot action.")
        api_instance = configure_k8s_v1core()
        create_pvc_from_snapshot(api_instance, args.snapshot_name, args.pvc_name, args.storage_size, args.storage_class_name, args.access_mode, args.namespace)



if __name__ == "__main__":
    main()
