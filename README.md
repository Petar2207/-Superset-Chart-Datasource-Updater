# Superset Chart Datasource Updater

This script connects to a Superset instance, retrieves all charts from a specified dashboard, and updates each chart's datasource to a new dataset using Superset's REST API.

## 📌 Features

- Authenticates with Superset using the REST API
- Handles CSRF protection using a session
- Fetches chart metadata from a dashboard
- Updates chart `datasource_id` and `datasource_type`
- Cleans and sends valid payloads (removes read-only fields)
- Prints update results for each chart

## 🚀 Requirements

- Python 3.7+
- [requests]

  ## Also included simple html, css, and js(not tested) prepared for flask conection with python code.
