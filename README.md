# Title: TypeX

# Description:
TypeX is an application that measures how fast and accurately a user can type a given text. It can track typing speed (words per minute), accuracy, and past performance over time. Using a database allows storing user scores, high scores, and historical progress for analysis.

## features

-   **Interactive Typing Area** – Type the given text in a user-friendly interface.

-   **Dynamic Text Generator** – Get new sentences or paragraphs every time.

-   **Real-Time Timer** – Track typing duration instantly.

-   **Speed Measurement (WPM)** – Calculates words per minute accurately.

-   **Accuracy Tracker** – Shows mistakes and correct typing percentage.

-   **Progress Bar** – Visual indicator of text completion.

-   **Start/Restart Test** – Easily begin or reset the test.

-   **Difficulty Modes** – Choose between easy, medium, and hard levels.

-   **Custom Text Input** – Paste your own text for practice.

-   **History & Stats** – Save and review past typing performances.

-   **Leaderboard** – Compare scores with other users.

-   **Responsive Design** – Works on desktop and mobile devices.

# Project Structure

    TypeX/
    |
    |---src/          #core application logic
    |   |---logic.py. #Business logic and tasks
    operations
    |.  |__db.py.     #Database operations
    |
    |---API/          #Backend API
    |   |__main.py    #FASTAPI endpoints
    |
    |---frontend/     #Frontend Application
    |   |__app.py     #Streamlit web interface
    |
    |___requirements.txt    #python Dependencies
    |
    |___README.md     #Project Documentation
    |
    |___.env        #python variables

## Quick Start

### Prerequisites

    -Python 3.8 or higher
    -A supabase Account
    -Git(push,cloning)

### 1.clone or Download the project
    # option 1.clone with Git
    git clone <repositorty-url>

# option 2. Install Dependencies

# install all required python packages
    pip install -r requirements.txt

# 3. set up supabase database

    1.create a supabase projects:

    2.create the task tables:

    -Go to the sql editor in your supabase dashboard
    -run this sql command:

    ```sql
    CREATE TABLE users (
    user_id serial PRIMARY KEY,
    name text NOT NULL,
    email text UNIQUE NOT NULL,
    join_date timestamptz DEFAULT NOW()
    );

    CREATE TABLE typing_tests (
    test_id serial PRIMARY KEY,
    user_id int REFERENCES users(user_id),
    wpm decimal(5,2) NOT NULL,
    accuracy decimal(5,2) NOT NULL,
    test_date timestamptz DEFAULT NOW()
    );

    CREATE VIEW leaderboard AS
    SELECT user_id, MAX(wpm) AS max_wpm, MAX(accuracy) AS best_accuracy
    FROM typing_tests
    GROUP BY user_id
    ORDER BY max_wpm DESC;
    ```
    3.Get your credentials:

### 4.Configure Envinorment Varialbles

    1. create a `.env` file in project root

    2. add supabase credentials to `.env`:
        SUPABASE_URL="https://zgggkafzipfhbjahthql.supabase.co"
        SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpnZ2drYWZ6aXBmaGJqYWh0aHFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2OTkxNTEsImV4cCI6MjA3NDI3NTE1MX0.8wOtfDSIb9XrdVqmiu_1o8UrAWNwWH0JSPTz8sWtGcY"

### 5.Run the application

## Streamlit Frontend
Streamlit run frontend/app.py

This app will open in your browser at `http://localhost:8501`

# FastAPI Backend

cd API
uvicorn API.main:app --reload
this app will be available at `http://localhost:8000`

## How to use

## technical details

## Technoligies used

- **Frontend**: Streamlit (Python web framework)

- **Backend**: FastAPI (Python REST API framework)

- **Database**: Supabase (PostgreSQL-based backend-as-a-service)

- **Language**: Python 3.8+

## Key Components

1. **`src/db.py`**: Database operations

-   Handles all CRUD operations with Supabase

2. **`src/logic.py`**: Business logic

-   Task validation and processing

## Trobleshooting

## common issues
- make sure you have installed all dependencies:`pip install -r requirements.txt`
    -Check that you are running from correct directory

- ImportError: email-validator is not installed
    - We now use a simple string email with basic validation in `API/main.py` (no extra dependency needed).
    - If you prefer strict RFC validation, install the extra:
      
      ```bash
      pip install 'pydantic[email]'
      ```

## Future Enhancement

- **Real-Time Error Highlighting** – Highlight mistakes as the user types and provide instant corrections.

- **Adaptive Difficulty** – Adjust text complexity and suggest exercises based on user performance.

- **Multiplayer Typing Races** – Compete with friends or global users with leaderboards.

- **Advanced Analytics** – Show WPM, accuracy trends, keystroke dynamics, and error heatmaps.

- **Mobile-Friendly Support** – Optimize the app for mobile devices and offline practice.

## support

if you are having any queries:

- **contact**:9391544253

- **email**:dhanaushyadav0099@gmail.com

