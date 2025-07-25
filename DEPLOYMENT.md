# Deploying to Render with GitHub Actions

This guide provides instructions for deploying the ElevateCV application to Render using GitHub Actions for continuous deployment.

## Prerequisites

1.  **Render Account:** Create a new account on [Render](https://render.com/).
2.  **Create a Web Service:** Create a new web service in your Render account and link it to your GitHub repository.
3.  **GitHub Repository:** Create a new GitHub repository and push your application code to it.

## Deployment Steps

1.  **Add Secrets to GitHub:**

    In your GitHub repository, go to **Settings > Secrets > Actions** and add the following secrets:

    *   `RENDER_SERVICE_ID`: Your Render service ID.
    *   `RENDER_API_KEY`: Your Render API key.
    *   `GOOGLE_API_KEY`: Your Google AI API key.
    *   `SECRET_KEY`: A strong, randomly generated secret key.

2.  **Push to `main`:**

    Push your changes to the `main` branch of your GitHub repository. This will trigger the GitHub Actions workflow and deploy your application to Render.

## Accessing the Application

Once the deployment is complete, you can find the URL for your service in your Render dashboard.
