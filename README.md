# Task Management System

![Python](https://img.shields.io/badge/python-3.13.0-blue)

Backend system for **Task Management System** (TMS) supporting functionalities required for Task management, Project management, user requests handling, and user authentication and authorization. The application will have different user roles and functionalities based on those roles.

---

## Features

- **Role-Based Access Control** - Restrict actions based in user roles (Admin, PM, Lead, Developer, Client)
- **CRUD Operations** - Create, Read, Update and Delete APIs for users, projects, tasks and comments.
- **Authentication and Authorization** - Token-based login, registration, and secured access to resources.
- **User and Task Assignment** - Assign users to projects and tasks to projects as well as users.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/mrityuanjayagupta/DjangoRestFramework-Assignment.git
cd DjangoRestFramework-Assignment

# (Optional) Create a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt