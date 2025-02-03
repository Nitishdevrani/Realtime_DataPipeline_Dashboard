# Data Engineering Final Project
A realtime data processing pipeline for the redset dataset providing workload analysis to the user.

## Setup Guide

### 1. Download Parquet Files
- Download the required `.parquet` files from [Amazon Science Redset GitHub](https://github.com/amazon-science/redset).
- Place the `provisioned_full.parquet` file in `data/provisioned/`.
- Place the `serverless_full.parquet` file in `data/serverless/`.

### 2. Install Dependencies
- Create a Python virtual environment (optional):
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Linux/MacOS
  .venv\Scripts\activate    # On Windows
  ```
- Install the required Python packages:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Start Kafka
- Ensure Docker is installed and running on your system.
- Start Kafka using the provided shell script (Linux only):
  ```bash
  ./start_kafka.sh
  ```

### 4. Run the Application
- Start the data processing pipeline:
  ```bash
  python main.py
  ```

### 5. Start the Dashboard
- Navigate to the `dashboard` directory:
  ```bash
  cd dashboard
  ```
- Install Node.js dependencies:
  ```bash
  npm install
  ```
- Start the dashboard:
  ```bash
  npm run dev
  ```
- Open the dashboard in your browser at `http://localhost:3000`.
### 6. Check the README.md of /dashboard directory for more details.


| **Date**       | **Day**   | **Tasks**                                                                                                                                                 |
| -------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **23.01.2025** | Thursday  | Think of possible implementations, tools for each part of the project.                                                                                    |
| **24.01.2025** | Friday    | Discuss actual implementation details, detailed responsibilities, and interfaces between *replay -> cleaning -> processing -> dashboard* **Zoom Meeting** |
| **25.01.2025** | Saturday  | Start initial work: dashboard wireframes, data cleaning / storage setup, pipeline setup, data processing strategy.                                        |
| **26.01.2025** | Sunday    | Develop core features: dashboard components, basic clean data validation, initial pipeline and basic processing                                           |
| **27.01.2025** | Monday    | Continue dashboard and pipeline development; test initial data integration; prepare presentation. **Zoom Meeting?**                                       |
| **28.01.2025** | Tuesday   | **Midterm Project Presentation**, some buffer in case we have problems during weekend                                                                     |
| **29.01.2025** | Wednesday | Implement advanced features (query metrics, cost analysis, prediction); debug pipeline and refine dashboards.                                             |
| **30.01.2025** | Thursday  | Testing of complete pipeline. **Meet before or after ML?**                                                                                                |
| **31.01.2025** | Friday    | Final iteration: Add features like suggestions/alerts; polish dashboards and finalize integration.                                                        |
| **01.02.2025** | Saturday  | Comprehensive testing and validation of all project components. Discuss presentation structure **Zoom Meeting around lunch?**                             |
| **02.02.2025** | Sunday    | Finalize project documentation, presentation and ensure Github repository is complete and well-commented.                                                 |
| **03.02.2025** | Monday    | Create Video, write report (individual) and submit everything.                                                                                            |
| **04.02.2025** | Tuesday   | **Final Presentation + Group Interview**                                                                                                                  |
