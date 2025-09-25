import os
from supabase import create_client
from dotenv import load_dotenv

# Load env variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------- USERS -------------------

def add_user(name, email):
    response = supabase.table("users").insert({
        "name": name,
        "email": email
    }).execute()
    return response.data

def get_all_users():
    response = supabase.table("users").select("*").execute()
    return response.data

def get_user_by_id(user_id: int):
    response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    return response.data

def update_user(user_id: int, name=None, email=None):
    data = {}
    if name: data["name"] = name
    if email: data["email"] = email
    response = supabase.table("users").update(data).eq("user_id", user_id).execute()
    return response.data

def delete_user(user_id: int):
    response = supabase.table("users").delete().eq("user_id", user_id).execute()
    return response.data

# ------------------- TYPING TESTS -------------------

def add_typing_test(user_id: int, wpm: float, accuracy: float, duration_seconds: int, difficulty: str, completed: bool = True):
    response = supabase.table("typing_tests").insert({
        "user_id": user_id,
        "wpm": wpm,
        "accuracy": accuracy,
        "duration_seconds": duration_seconds,
        "difficulty": difficulty,
        "completed": completed
    }).execute()
    return response.data

def get_all_typing_tests():
    response = supabase.table("typing_tests").select("*").execute()
    return response.data

def get_tests_by_user(user_id: int):
    response = supabase.table("typing_tests").select("*").eq("user_id", user_id).execute()
    return response.data

def update_typing_test(test_id: int, wpm=None, accuracy=None, completed=None):
    data = {}
    if wpm is not None: data["wpm"] = wpm
    if accuracy is not None: data["accuracy"] = accuracy
    if completed is not None: data["completed"] = completed
    response = supabase.table("typing_tests").update(data).eq("id", test_id).execute()
    return response.data

def delete_typing_test(test_id: int):
    response = supabase.table("typing_tests").delete().eq("id", test_id).execute()
    return response.data

# ----------------Leaderboard-------------------

def create_leaderboard_view():
    """
    Creates or replaces the leaderboard view in Supabase.
    """
    sql = """
    CREATE OR REPLACE VIEW leaderboard AS
    SELECT user_id,
           MAX(wpm) AS max_wpm,
           MAX(accuracy) AS best_accuracy
    FROM typing_tests
    GROUP BY user_id
    ORDER BY max_wpm DESC;
    """

def get_leaderboard():
    
    response = supabase.table("leaderboard").select("*").execute()
    if response.data:
        return response.data
    else:
        return []  # Return empty list if no data

