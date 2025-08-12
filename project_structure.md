
# AI Predictive Maintenance Recommendation System - Project Structure

AI_Predictive_Maintenance_System/
│
├── 1_Documentation/
│   ├── Abstract.md
│   ├── Requirements_Specification.md
│   ├── CRISP_DM_Phases.md
│   ├── System_Architecture_Diagram.png
│   └── Data_Dictionary.xlsx
│
├── 2_Backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── random_forest.pkl
│   │   │   ├── svm_model.pkl
│   │   │   └── gradient_boosting.pkl
│   │   ├── routes/
│   │   │   ├── tenants.py
│   │   │   ├── predictions.py
│   │   │   ├── tasks.py
│   │   │   ├── admin.py
│   │   │   └── feedback.py
│   │   ├── services/
│   │   │   ├── prediction_service.py
│   │   │   ├── scheduling_service.py
│   │   │   └── data_import_export.py
│   │   ├── database/
│   │   │   ├── models.py
│   │   │   └── seed_data.py
│   │   └── utils/
│   │       ├── preprocess.py
│   │       ├── validation.py
│   │       └── config.py
│   ├── tests/
│   │   ├── test_prediction.py
│   │   ├── test_tenant_reporting.py
│   │   └── test_scheduling.py
│   ├── requirements.txt
│   └── run.py
│
├── 3_Frontend/
│   ├── tenant_portal/
│   │   ├── index.html
│   │   ├── report_issue.html
│   │   ├── track_status.html
│   │   ├── feedback.html
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── admin_dashboard/
│   │   ├── dashboard.html
│   │   ├── reports.html
│   │   ├── manage_tasks.html
│   │   ├── css/
│   │   ├── js/
│   │   └── charts/
│   └── package.json
│
├── 4_ML_Model_Development/
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── environmental_factors.csv
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_model_training.ipynb
│   │   ├── 04_model_evaluation.ipynb
│   │   └── 05_prediction_pipeline.ipynb
│   ├── scripts/
│   │   ├── train_random_forest.py
│   │   ├── train_svm.py
│   │   ├── train_gradient_boosting.py
│   │   └── evaluate_models.py
│   └── models/
│       └── saved_models/
│
├── 5_Database/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── maintenance_db.sqlite
│
├── 6_Deployment/
│   ├── docker-compose.yml
│   ├── Dockerfile_backend
│   ├── Dockerfile_frontend
│   ├── nginx.conf
│   └── deployment_guide.md
│
└── README.md
