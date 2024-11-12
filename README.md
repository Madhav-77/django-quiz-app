# Django Quiz Application

## Project Overview

This project is a full-stack quiz application designed to showcase my proficiency in both front-end and back-end technologies. It features a frontend built using Angular 18, using standalone components for maintainable and lightweight architecture. The backend is in Django, with SQLite as the database. The application uses JWT for authentication.

[![Version](https://img.shields.io/badge/version-1.0.0.alpha.1-blue.svg)](https://semver.org)

### Key Features:
**User Registration & Authentication:** Users can register, log in, and receive a JWT token for secure access. The token must be included in the headers of API requests to access restricted resources such as quiz results.

**Quizzes & Answers:** Users can view available quizzes, submit their answers, and view their results upon completion.

**Results:** Once the quiz is completed, users can view their scores and correct/incorrect answers.

**Super Admin Access:** The super admin has privileges to manage users, quizzes, and results. For managing the application and its users, a super admin account is required. The admin can log into the Django admin panel to manage all the quizzes, results, and user data.

- URL for Admin Panel: /admin/
- Username: madhavtrivedi
- Password: Admin@123

**Authentication Flow:**
- Login: The user provides their credentials (username, password) via the frontend.
- JWT Token Generation: Upon successful login, the backend (Django) generates a JWT token, which is sent to the frontend.
- Accessing Protected Routes: The token is sent in the HTTP headers for each request that requires authentication. The backend verifies the token to authorize access.
- Secure User Interaction: With JWT authentication, users can safely interact with quiz data, submit answers, and view their results without the need for traditional session-based authentication.

## Table of Contents
[Project Overview](#project-overview)

[Setting Up the Project](#setting-up-the-project)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
[API Endpoints](#api-endpoints)
   - [Endpoint Overview](#overview)
   - [Request and Response Details](#request-and-response-details)
[Testing Documentation](#testing-documentation)
   - [Running Tests](#running-tests)
   - [Writing Tests](#writing-tests)
[Database Information](#database-information)
   - [Database Schema](#database-schema)
   - [Database Setup](#database-setup)
[Additional Notes](#additional-notes)
[Conclusion](#conclusion)

---

## Setting Up the Project

### Prerequisites
To run this project, ensure you have the following installed:
- **Python 3.8+**
- **Django 5.x**

### Installation
**Clone the Repository**:

    git clone https://github.com/Madhav-77/django-quiz-app.git
    cd project_quiz_app
    
**Create a Virtual Environment**:
    
    python3 -m venv venv
    use venv\Scripts\activate # For Windows
    
**Install Dependencies**:

    pip install -r requirements.txt

**Apply Database Migrations**:

    python manage.py migrate

**Run the Development Server**:

    python manage.py runserver
---
## API Endpoints

| Method | Endpoint                                     | Description                                    | Example Request                           |
|--------|----------------------------------------------|------------------------------------------------|------------------------------------------|
| GET    | `/api/quizzes/`                              | Retrieve all quizzes                           | `GET /api/quizzes/`                      |
| POST   | `/api/quizzes/create/`                       | Create a new quiz                              | `POST /api/quizzes/create/`              |
| GET    | `/api/quizzes/<quiz_id>/`                    | Retrieve details of a specific quiz by ID      | `GET /api/quizzes/1/`                    |
| POST   | `/api/quizzes/submit/`                       | Submit answers for a quiz                      | `POST /api/quizzes/submit/`              |
| GET    | `/api/quizzes/<quiz_id>/users/<user_id>/results/` | Retrieve a user’s result for a specific quiz | `GET /api/quizzes/1/users/123/results/`  |
| DELETE | `/api/quizzes/<quiz_id>/users/<user_id>/delete/`  | Delete a user's results and answers for a quiz | `DELETE /api/quizzes/1/users/123/delete/` |

### Request and Response Details

#### 1. Retrieve All Quizzes (GET `/api/quizzes/`)
- **Request Example**:
    ```bash
    GET /api/quizzes/
    ```
- **Response Example**:
    ```json
    [
      {
        "id": 13,
        "title": "Test  123"
      },
      {
        "id": 14,
        "title": "Test"
      }
    ]
    ```

#### 2. Create a new quiz (POST `/api/quizzes/create/`)
- **Request Example**:
    ```bash
    POST /api/quizzes/1/answers/
    Content-Type: application/json

    {
      "title": "Test", 
      "questions": [
        {
          "text": "Test que 123", 
          "options": [1, 2, 3, 4], 
          "correct_option": 2
        }
      ]
    }
    ```
- **Response Example**:
    ```json
    {
      "message": "Quiz created successfully.",
      "quiz_id": 14
    }
    ```
#### 3. Retrieve details of a specific quiz by ID (GET `/api/quizzes/<quiz_id>/`)
- **Response Example**:
    ```json
    {
      "title": "Test  123",
      "questions": 
      [
        {
          "id": 6,
          "text": "New que",
          "options": ["1", "2", "3", "4"]
        },
        {
          "id": 7,
          "text": "New que 1",
          "options": ["1", "2", "3", "4"]
        }
      ]
    }
    ```
#### 4. Submit answers for a quiz (POST `/api/quizzes/submit/`)
- **Request Example**:
    ```bash
    POST /api/quizzes/submit/
    Content-Type: application/json

    {
      "question_id": 3,
      "selected_option": 3
    }
    ```
- **Response Example**:
    ```json
    {
      "is_correct": true,
      "correct_option": 1,
      "message": "Correct answer!"
    }
    ```
#### 5. Retrieve a user’s result for a specific quiz (GET `/api/quizzes/<quiz_id>/users/<user_id>/results/`)
- **Response Example**:
    ```json
    {
      "quiz_id": 14,
      "user_id": 2,
      "total_score": 3,
      "answers": [
          {
              "question_id": 7,
              "selected_option": 3,
              "correct_option": 2,
              "is_correct": false
          },
          {
              "question_id": 4,
              "selected_option": 3,
              "correct_option": 2,
              "is_correct": true
          },
          {
              "question_id": 17,
              "selected_option": 3,
              "correct_option": 2,
              "is_correct": true
          },
          {
              "question_id": 42,
              "selected_option": 3,
              "correct_option": 2,
              "is_correct": true
          }
      ]
    }
    ```
#### 6. Delete a user's results and answers for a quiz (DELETE `/api/quizzes/<quiz_id>/users/<user_id>/delete/`)
- **Response Example**:
    ```json
    {"message": "Result and Answers deleted successfully."}
    ```
---

## Testing Documentation
Running Unit Tests, enter following command:
    
    python manage.py test

## Database Information

### Database Schema

The following tables are defined in the database schema for the Quiz API application:

- **Quiz Table**: Stores quiz metadata.
    - `id` (Primary Key): Unique identifier for each quiz.
    - `title` (CharField): The name/title of the quiz.

- **Answer Table**: Stores answers submitted by users for specific quiz questions.
    - `id` (Primary Key): Unique identifier for each answer entry.
    - `question` (ForeignKey to Question): The question associated with the answer.
    - `user` (ForeignKey to User): The user who submitted the answer.
    - `selected_option` (PositiveIntegerField): The option selected by the user for the question.
    - `is_correct` (BooleanField): Indicates if the selected answer is correct.

- **Question Table**: Stores questions create with quiz.
    - `id` (Primary Key): Unique identifier for each question entry.
    - `quiz` (ForeignKey to Quiz): The quiz associated with the question.
    - `text` (CharField): The text of the question.
    - `correct_option` (PositiveIntegerField): The index of correct option from the 4 options.
    - `options` (Json): Stores the list of 4 options/answers.

- **Result Table**: Stores the results of users' attempts at quizzes.
    - `id` (Primary Key): Unique identifier for each result entry.
    - `quiz` (ForeignKey to Quiz): The quiz for which the result was recorded.
    - `user` (ForeignKey to User): The user whose result is recorded.
    - `score` (PositiveIntegerField): The total score achieved by the user in the quiz.
    - `answers` (ManyToManyField to Answer): A collection of all answers associated with this result entry, allowing linkage of multiple answers to each result.

## Limitation of the current version
Any quiz can be given only once per any user, to give the quiz again, entries for that quiz & user must be deleted using ```/api/quizzes/<quiz_id>/users/<user_id>/delete/``` api, it will require ```quiz_id``` & ```user_id``` parameters.

## Contributors

- [@madhavtrivedi](https://www.madhavtrivedi.com/)