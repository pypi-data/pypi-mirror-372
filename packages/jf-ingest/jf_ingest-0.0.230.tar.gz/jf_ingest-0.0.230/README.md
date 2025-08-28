# Jellyfish Ingest

## Description

This is a Pypi Project that is shared between Agent and Managed Ingest (our self hosted prefect tasks) that is responsible for downloading Jira and Git code, and uploading it to our S3 bucket, where it can than be ingested to our database via the import tasks.

## Current State of Project

The current state of this project is 'In Development'. Only parts of this module are live in production. We plan on doing a big Jira Cutover sometime in Q4 of 2023, hopefully. After a successful Jira Launch we will begin rolling out our git ingestion to use this module

## Documentation for local development

https://jelly-ai.atlassian.net/wiki/spaces/JEL/pages/2963210264/Working+with+Jellyfish+Ingest
