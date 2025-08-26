# core_engine

Modular core engine for Python-based microservices.  
This package provides reusable components such as authentication, caching, database connectivity, queue management, and external integrations.

---

## 📦 Features

- **Authentication (`auth`)**  
  Handle user authentication logic and services.

- **Bridges (`bridges`)**  
  Communication logic between internal modules.  
  - `module`: Handles system integration logic.  
  - `user_management`: Manages user access control.

- **Caching (`caches`)**  
  Redis-based caching services.

- **Database Connectivity (`connectivity`)**  
  Abstractions for building and running database queries.

- **Custom Query (`custom_query`)**  
  Contains raw SQL files and custom database queries.

- **External Integration (`external_integration`)**  
  Handles API and service communication with external systems.

- **Queueing (`queueing`)**  
  RabbitMQ or similar queue implementations.

- **Utilities (`utilities`)**  
  Helper functions such as validation, pagination, etc.

- **Connection Modules**  
  Shared connection helpers:
  - `connection.py`: DB or external service connection.
  - `constants.py`: Shared constant values.

---

## 🛠️ Installation

Make sure you have Python 3.8+ and `pip`.

Url https://pypi.org/project/ebesha-core-engine/0.1.2/

```bash
# Install as package
pip install ebesha-core-engine

# Update to Pypi Public
pip install twine
twine upload dist/*
