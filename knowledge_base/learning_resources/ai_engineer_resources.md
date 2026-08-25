# AI Engineer Learning Resources and Projects

## Core Resources

- Python documentation: use the official tutorial to practice syntax, modules, exceptions, classes, and virtual environments.
- SQL practice: solve exercises involving filtering, joins, grouping, subqueries, and window functions.
- NumPy and pandas: practice array operations, data cleaning, missing values, grouping, and feature preparation.
- scikit-learn documentation: study pipelines, preprocessing, model selection, cross-validation, and evaluation metrics.
- PyTorch tutorials: learn tensors, datasets, neural networks, training, saving models, and inference.
- FastAPI documentation: practice request validation, dependency injection, authentication, error handling, and testing.
- Docker documentation: learn images, containers, Dockerfiles, volumes, networks, and multi-stage builds.

## Recommended Projects

### 1. Resume Skill Extractor
Extract skills from resumes, normalize skill names, and return structured JSON. Add tests for PDF and DOCX inputs.

### 2. Job Matching API
Compare a resume with job descriptions, calculate an explainable match score, and expose the result through FastAPI.

### 3. End-to-End ML Service
Train a classification model, save the model artifact, create a prediction API, add input validation, and run it in Docker.

### 4. Retrieval Augmented Career Advisor
Load Markdown documents, split them into chunks, create embeddings, retrieve relevant context, generate answers, and cite sources.

### 5. Model Evaluation Dashboard
Track accuracy, precision, recall, latency, failed requests, and examples where the model is uncertain.

## Project Quality Checklist

- Include a clear README with setup and usage instructions.
- Keep secrets in environment variables and never commit API keys.
- Add unit and integration tests for important paths.
- Use type hints and meaningful error messages.
- Explain tradeoffs and limitations.
- Include sample input and output.
