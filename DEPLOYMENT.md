# Deployment Instructions

This document provides instructions on how to deploy the application to Google Cloud.

## Prerequisites

- A Google Cloud project
- The `gcloud` command-line tool installed and configured
- A Cloud SQL for PostgreSQL instance

## 1. Set up Cloud SQL

1.  **Create a Cloud SQL for PostgreSQL instance:**
    ```bash
    gcloud sql instances create resume-analyzer-db --database-version=POSTGRES_13 --region=us-central1
    ```

2.  **Create a database:**
    ```bash
    gcloud sql databases create resume-analyzer --instance=resume-analyzer-db
    ```

3.  **Create a user:**
    ```bash
    gcloud sql users create <your-db-user> --instance=resume-analyzer-db --password=<your-db-password>
    ```

## 2. Configure Environment Variables

1.  **Enable the Cloud SQL Admin API:**
    ```bash
    gcloud services enable sqladmin.googleapis.com
    ```

2.  **Create a service account:**
    ```bash
    gcloud iam service-accounts create resume-analyzer-sa
    ```

3.  **Grant the service account the Cloud SQL Client role:**
    ```bash
    gcloud projects add-iam-policy-binding <your-project-id> \
        --member="serviceAccount:resume-analyzer-sa@<your-project-id>.iam.gserviceaccount.com" \
        --role="roles/cloudsql.client"
    ```

4.  **Create a service account key:**
    ```bash
    gcloud iam service-accounts keys create credentials.json \
        --iam-account="resume-analyzer-sa@<your-project-id>.iam.gserviceaccount.com"
    ```

5.  **Set the `DATABASE_URL` environment variable in `cloudbuild.yaml`:**
    Replace `<your-project-id>`, `<your-db-user>`, `<your-db-password>`, and `<your-db-name>` with your actual values.
    ```yaml
    ...
      - '--set-env-vars'
      - 'DATABASE_URL=postgresql+pg8000://<your-db-user>:<your-db-password>@/<your-db-name>?unix_sock=/cloudsql/<your-project-id>:<your-region>:<your-instance-name>/.s.PGSQL.5432'
    ...
    ```

## 3. Deploy the Application

1.  **Enable the Cloud Build and Cloud Run APIs:**
    ```bash
    gcloud services enable cloudbuild.googleapis.com run.googleapis.com
    ```

2.  **Submit the build:**
    ```bash
    gcloud builds submit --config cloudbuild.yaml .
    ```

## 4. (Optional) Set up a Custom Domain

1.  **Map a custom domain to your Cloud Run service:**
    ```bash
    gcloud run services map-domain resume-analyzer --domain=<your-domain>
    ```

2.  **Update your DNS records with the values provided by Google.**
