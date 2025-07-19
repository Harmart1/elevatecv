# Deploying to Google Cloud Run

This guide provides instructions for deploying the ElevateCV application to Google Cloud Run.

## Prerequisites

1.  **Google Cloud SDK:** Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured on your local machine.
2.  **Google Cloud Project:** Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
3.  **Enable APIs:** Enable the Cloud Build, Cloud Run, and Artifact Registry APIs for your project.
4.  **Docker:** Make sure you have [Docker](https://docs.docker.com/get-docker/) installed on your local machine.

## Deployment Steps

1.  **Authenticate with Google Cloud:**

    ```bash
    gcloud auth login
    gcloud config set project [YOUR_PROJECT_ID]
    ```

2.  **Create an Artifact Registry Repository:**

    ```bash
    gcloud artifacts repositories create elevatecv-repo --repository-format=docker --location=us-central1
    ```

3.  **Build the Docker Image:**

    Build the Docker image using Cloud Build. This will build the image and push it to your Artifact Registry repository.

    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/elevatecv-repo/elevatecv
    ```

4.  **Deploy to Cloud Run:**

    Deploy the container image to Cloud Run. This command will create a new service and deploy the image to it.

    ```bash
    gcloud run deploy elevatecv --image us-central1-docker.pkg.dev/[YOUR_PROJECT_ID]/elevatecv-repo/elevatecv --platform managed --region us-central1 --allow-unauthenticated
    ```

    *   `--platform managed`: Specifies the fully managed version of Cloud Run.
    *   `--region us-central1`: Specifies the region where the service will be deployed.
    *   `--allow-unauthenticated`: Allows public access to the service.

5.  **Set Environment Variables:**

    You need to set the `GOOGLE_API_KEY` and `SECRET_KEY` environment variables in your Cloud Run service.

    ```bash
    gcloud run services update elevatecv --update-env-vars=GOOGLE_API_KEY=[YOUR_GOOGLE_API_KEY],SECRET_KEY=[YOUR_SECRET_KEY] --region=us-central1
    ```

    *   Replace `[YOUR_GOOGLE_API_KEY]` with your actual Google AI API key.
    *   Replace `[YOUR_SECRET_KEY]` with a strong, randomly generated secret key.

## Accessing the Application

Once the deployment is complete, you will see a URL for your service in the output. You can use this URL to access your application.

## Continuous Deployment (Optional)

You can set up a Cloud Build trigger to automatically build and deploy your application whenever you push changes to your Git repository. See the [Cloud Build documentation](https://cloud.google.com/build/docs/automating-builds/create-trigger) for more information.
