# Volume Backup and Restore Guide

This guide provides step-by-step instructions for backing up and restoring volumes using Longhorn in a Kubernetes cluster. Whether you prefer manual backups or automated cron jobs, this document covers all necessary procedures to ensure your data is safely backed up and can be restored efficiently when needed.

## Table of Contents

1. [Backup Volume](#backup-volume)
   - [Manual Backup](#manual-backup)
   - [Automated Backup with Cron Job](#automated-backup-with-cron-job)
2. [Restore Volume from Backup](#restore-volume-from-backup)
   - [Create Volume from Backup](#1-create-volume-from-backup)
   - [Scale Down Odoo Replicas](#2-scale-down-odoo-replicas-to-0)
   - [Create PV/PVC from Longhorn Volume](#3-create-pvpvc-from-longhorn-volume)
   - [Scale Out the Odoo Deployment](#4-scale-out-the-deployment-odoo)

---

## Backup Volume

Ensuring regular backups of your volumes is crucial for data safety and recovery. You can perform backups manually or set up automated backups using cron jobs.

### Manual Backup

Follow these steps to create a manual backup of your volume:

1. **Create a Backup:**
   - Navigate to the volume details page.
   - Click on **Create Backup**.

   ![Create Backup](volume-doc-images/create-backup-manual.png)

2. **Check Backup Status:**
   - After initiating the backup, monitor its status to ensure it's completed successfully.

   ![Backup Status](volume-doc-images/backup-status.png)

### Automated Backup with Cron Job

Automating backups ensures that your data is backed up at regular intervals without manual intervention.

1. **Create a Recurring Backup Job:**
   - Set up a cron job to perform backups at your desired schedule.

   ![Recurring Backup](volume-doc-images/recurring.png)

2. **Change Working Group:**
   - Modify the working group settings as needed to accommodate the backup process.

   ![Working Group](volume-doc-images/working-group.png)

3. **Assign Volume to the Group:**
   - Assign the specific volume to the working group responsible for applying the recurring backup job.

   ![Volume Groups](volume-doc-images/volume-groups.png)

---

## Restore Volume from Backup

In the event of data loss or corruption, restoring your volume from a backup ensures minimal downtime and data integrity.

### 1. Create Volume from Backup

Start by creating a new volume using the latest backup.

- **Use the UI to Create Volume:**
  - Navigate to the backup section.
  - Select **Create Volume from Latest Backup**.

  ![Create Volume from Backup](volume-doc-images/image.png)
  ![Volume Creation](volume-doc-images/image-1.png)

- **Verify the New Volume:**
  - Ensure the new volume has been successfully created.

  ![New Volume](volume-doc-images/volume.png)

### 2. Scale Down Application's persistent volume to 0

Before restoring, it's essential to scale down the Odoo deployment to prevent conflicts.

- **Edit Deployment YAML:**
  - Open the Odoo deployment YAML file.
  - Set `replicas` to `0`.

- **Apply Changes:**
  ```bash:recipes/backup-and-restore.md
  kubectl apply -f deployment.yaml
  # Or scale down using the command
  kubectl scale deploy -n <namespace_odoo> <odoo_deployment_name> --replicas=0
  ```

### 3. Create PV/PVC from Longhorn Volume

Next, set up the Persistent Volume (PV) and Persistent Volume Claim (PVC) using the restored Longhorn volume.

- **Use UI to Create PV/PVC:**
  - Navigate to the Longhorn UI.
  - Create PV/PVC from the restored volume.

  ![PV/PVC Creation](volume-doc-images/pv-pvc.png)

- **Verify PVC Creation:**
  - Ensure the PVC is created and bound to the restored Longhorn volume.

  ```bash:recipes/backup-and-restore.md
  kubectl get pvc -n v18e-ha v18e-ha-pvc -o yaml
  ```

  **Output:**
  ```yaml
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    annotations:
      pv.kubernetes.io/bind-completed: "yes"
    name: v18e-ha-pvc
    namespace: v18e-ha
    ...
  spec:
    accessModes:
      - ReadWriteMany
    resources:
      requests:
        storage: 5Gi
    storageClassName: longhorn
    volumeMode: Filesystem
    volumeName: odoo-ha-restore-from-backup
  status:
    phase: Bound
  ```

### 4. Scale Out the Odoo Deployment

After setting up the restored volume, scale the Odoo deployment back to its original state.

- **Edit Deployment YAML:**
  - Open the Odoo deployment YAML file.
  - Set `replicas` to `2`.

- **Apply Changes:**
  ```bash:recipes/backup-and-restore.md
  kubectl apply -f deployment.yaml
  # Or scale up using the command
  kubectl scale deploy -n <namespace_odoo> <odoo_deployment_name> --replicas=2
  ```

- **Verify Pod Status:**
  - Ensure all Odoo pods are running correctly.

  ```bash:recipes/backup-and-restore.md
  kubectl get pods -n <namespace_odoo>
  ```

  ![Check App Status](volume-doc-images/check-app.png)

---

## Summary

By following this guide, you can effectively manage backups and restorations of your Kubernetes volumes using Longhorn. Regular backups, whether manual or automated, ensure data security and facilitate quick recovery in case of unexpected issues.

For any further assistance or advanced configurations, refer to the [Longhorn Documentation](https://longhorn.io/docs/) or contact your system administrator.
