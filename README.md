# Chemical-PFD Web Desktop

## Overview

**Chemical-PFD Web Desktop** is a cross-platform system designed to create, edit, and manage **Chemical Process Flow Diagrams (PFDs)**.
The project provides both **Web** and **Desktop applications**, powered by a **shared backend**, ensuring consistency, scalability, and flexibility across different user workflows.

The system is intended for **chemical engineering visualization**, **academic use**, and **industrial process modeling**, with a unified data model across platforms.

---

## Platform Breakdown

### 🌐 Web Application

* **Technology:** React.js
* Browser-based interface for quick access and collaboration
* Dashboard-driven workflow for creating and managing diagrams
* Ideal for lightweight usage, demonstrations, and remote access

### 🖥️ Desktop Application

* **Technology:** PyQt5
* High-performance native desktop editor
* Designed for detailed diagram editing and advanced interactions
* Suitable for offline usage and heavy engineering workflows

### 🔗 Backend Service (Common for Web & Desktop)

* **Technology:** Python + Django REST Framework
* Acts as a centralized API layer
* Handles:

  * User authentication
  * Diagram creation, storage, and retrieval
  * Component management
  * Validation of diagram data

Both Web and Desktop applications communicate with the backend using **REST APIs**, enabling seamless data sharing between platforms.

---

## System Architecture

The project is structured into three main modules:

* **Web Application**
  Browser-based interface focused on accessibility, dashboard-driven workflows, and quick diagram interactions.

* **Desktop Application**
  High-performance, offline-capable editor designed for detailed engineering workflows.

* **Backend Service**
  Centralized service responsible for authentication, diagram persistence, and data validation.

All modules operate on a **shared JSON-based diagram schema**, ensuring consistency across platforms.

---

## Repository Structure

```
Chemical-PFD-Web-Desktop/
 ├── web-frontend/        # Web Application
 ├── desktop-frontend/    # Desktop Application
 ├── backend/             # Backend Service
```

---

## Getting Started

1. Clone the repository
2. Navigate to the required module
3. Follow setup instructions in the module-specific README

* Web App: `web-frontend/README.md`
* Desktop App: `desktop-frontend/README.md`
* Backend: `backend/README.md`

---

## Project Status

🚧 Under active development

---

## Ownership & Contribution

This project is maintained as part of an **academic/industrial development initiative**.
Contributions follow defined **module-level guidelines**.
