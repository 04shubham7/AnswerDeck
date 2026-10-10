# AnswerDeck - RAG-Powered Semantic Chat

[![Backend CI](https://github.com/04shubham7/AnswerDeck/workflows/Backend%20CI%20Pipeline/badge.svg)](https://github.com/04shubham7/AnswerDeck/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/04shubham7/AnswerDeck/workflows/Frontend%20CI%20Pipeline/badge.svg)](https://github.com/04shubham7/AnswerDeck/actions/workflows/frontend-ci.yml)
[![codecov](https://codecov.io/gh/04shubham7/AnswerDeck/branch/master/graph/badge.svg)](https://codecov.io/gh/04shubham7/AnswerDeck)

AnswerDeck is a full-stack Retrieval-Augmented Generation (RAG) application that combines semantic search with AI-powered chat to answer questions based on document context.

## Features

🔍 **Semantic Search** - Find relevant content using vector embeddings  
💬 **AI Chat** - Get intelligent responses augmented with retrieved context  
⚡ **Fast & Scalable** - Built with modern async frameworks  
🎨 **Beautiful UI** - Responsive React frontend with real-time updates  
🔒 **Production Ready** - Comprehensive testing, error handling, and monitoring  
📦 **Containerized** - Easy deployment with Docker and Docker Compose  

## User Interface & Dashboard

AnswerDeck features a premium dark-themed, glassmorphic dashboard divided into two functional columns:

- **Left Control Panel**: Displays the live operational status of the RAG engine, environment configuration, Qdrant node endpoint, and active collections. It hosts the ingestion hub supporting **Local PDF Drag-and-Drop** upload and **Amazon S3 Document Ingestion** configuration.
- **Right Chat Panel**: Interactive AI Assistant showing streaming thinking levels (`Analyse`, `Retrieve`, `Execute`, `Validation`) and retrieved source snippets in real-time.


#### 1. System Dashboard Overview
#### 2. Ingestion Hub (Local PDF & Amazon S3 Settings)
#### 3. Real-Time Streaming Chat & Reasoning Timeline
<img width="1919" height="875" alt="image" src="https://github.com/user-attachments/assets/be5871a0-1c3d-4555-a71f-e538e4323a7d" />
<img width="1919" height="873" alt="image" src="https://github.com/user-attachments/assets/6d84bae9-1a0c-459b-b7cb-ea4104cf130f" />



## System Architecture & Flow

### 1. Document Ingestion Flow

The document ingestion pipeline processes documents to generate vector embeddings and index them in the Qdrant cluster:

```mermaid
graph TD
    A[Start: PDF Document] --> B{Ingestion Method}
    B -->|Local Upload| C[Drag & Drop / Select PDF]
    B -->|Amazon S3| D[Enter Bucket, Key & Credentials]
