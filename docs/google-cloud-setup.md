# Google Cloud Setup

## Enable APIs

gcloud services enable run.googleapis.com

gcloud services enable artifactregistry.googleapis.com

gcloud services enable cloudbuild.googleapis.com

## Create Artifact Registry

gcloud artifacts repositories create worldcup-repo \
  --repository-format=docker \
  --location=us-central1

## Create Service Account

gcloud iam service-accounts create github-deployer

## Grant Roles

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-deployer@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-deployer@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
