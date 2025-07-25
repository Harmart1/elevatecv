# Deploying to Google Cloud Run with GitHub Actions

This guide provides instructions for deploying the ElevateCV application to Google Cloud Run using GitHub Actions for continuous deployment.

## Prerequisites

1.  **Google Cloud Project:** Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enable APIs:** Enable the Cloud Build, Cloud Run, and Artifact Registry APIs for your project.
3.  **Create a Service Account:** Create a service account in your Google Cloud project and grant it the following roles:
    *   Cloud Build Editor
    *   Cloud Run Admin
    *   Storage Admin
    *   Service Account User
4.  **Create a Service Account Key:** Create a JSON key for the service account and download it to your local machine.
5.  **GitHub Repository:** Create a new GitHub repository and push your application code to it.

## Deployment Steps

1.  **Add Secrets to GitHub:**

    In your GitHub repository, go to **Settings > Secrets > Actions** and add the following secrets:

    *   `GCP_PROJECT_ID`: Your Google Cloud project ID.
    *   `GCP_SA_KEY`: The contents of the JSON key file that you downloaded in the previous step.
    *   `GOOGLE_API_KEY`: Your Google AI API key.
    *   `SECRET_KEY`: A strong, randomly generated secret key.

2.  **Push to `main`:**

    Push your changes to the `main` branch of your GitHub repository. This will trigger the GitHub Actions workflow and deploy your application to Google Cloud Run.

## Accessing the Application

Once the deployment is complete, you can find the URL for your service in the output of the GitHub Actions workflow. You can also find it in the [Google Cloud Console](https://console.cloud.google.com/run).
