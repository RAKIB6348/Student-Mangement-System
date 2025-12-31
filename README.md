# Student Management System (Django)

This is a Student Management System built with **Django**.  
The project manages students, teachers, academic information, and notifications.

## Project Description
The application provides a role-aware portal for admins, teachers, and students. Admins can register new users, broadcast notifications, and review teacher leave requests from a central dashboard backed by real-time counts of classes, subjects, and enrollments. Teachers receive notifications, submit leave requests, and maintain their profiles, while students have comprehensive records covering academic placement, guardianship details, and contact information. Behind the scenes, each module exposes CRUD interfaces, auto-generates human-friendly IDs, and enforces relationships between the custom `User` model and the academic catalog of classes, sessions, sections, and subjects.

## 🚀 Features
- Student management
- Teacher management
- Academic modules
- Teacher notifications
- Authentication & authorization
- Media and static file handling

## 🛠️ Tech Stack
- Python
- Django
- SQLite
- HTML, CSS, Bootstrap
