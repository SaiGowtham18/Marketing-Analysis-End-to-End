# ETL-Marketing Analysis-data-pipeline Project

## Overview

This project is a comprehensive end-to-end pipeline for analyzing marketing and sales data to derive actionable insights. The goal is to enable data-driven decision-making for marketing and sales teams by integrating data engineering, ETL, and visualization techniques. The pipeline is designed to identify the most-viewed items, sales success rates, platform preferences, and provide a foundation for investment decisions in mobile applications.

## Objectives

Analyze Customer Behavior: Understand user interactions with digital shop items.

Measure Sales Performance: Compare item views against sales data.

Platform Analysis: Assess user preferences for mobile vs. web platforms.

Actionable Insights: Equip the sales and marketing teams with dashboards for strategic decision-making.


## Tools & Technologies

### Data Engineering & Storage

Cloud Storage: AWS S3

ETL Orchestration: Apache Airflow

Data Warehouse: Snowflake

### Data Analysis & Visualization

Programming Languages: Python, SQL

Visualization Tools: Power BI

### Frameworks & Libraries

Pandas, PySpark, Statsmodels

Snowflake Connector, SQLAlchemy


## Project Workflow

1. Data Ingestion (AWS S3)

Raw marketing and sales data is uploaded to an S3 bucket.

Data includes item views, sales logs, and user interactions.

2. ETL Process (Apache Airflow)

Extract: Data is retrieved from S3.

Transform: Data is cleaned, enriched, and transformed using Python and PySpark.

Load: Transformed data is stored in Snowflake as a structured data mart.

3. Data Analysis

Key Performance Indicators (KPIs) such as total sales, view-to-sale ratios, and platform preferences are calculated using SQL and Python.

4. Data Visualization (Power BI)

An interactive Power BI dashboard visualizes:

Top viewed items vs. sales success rates.

User platform preferences (mobile vs. web).

Monthly sales trends.
