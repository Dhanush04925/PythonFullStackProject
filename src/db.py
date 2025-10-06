"""
Database operations for Typing Speed Tester
Handles all CRUD operations with Supabase
"""

import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class TypingDB:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, name: str, email: str) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            response = self.client.table("users").insert({
                "name": name,
                "email": email
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            error_msg = str(e)
            # Check for specific error types
            if "duplicate key" in error_msg.lower() or "unique" in error_msg.lower():
                print(f"User with email {email} already exists")
                return None
            elif "connection" in error_msg.lower():
                print(f"Database connection error: {e}")
                raise Exception("Cannot connect to database. Check your .env file.")
            else:
                print(f"Error creating user: {e}")
                return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.client.table("users").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            response = self.client.table("users").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    # ==================== TYPING TEST OPERATIONS ====================
    
    def save_typing_test(self, user_id: int, wpm: float, accuracy: float) -> Optional[Dict[str, Any]]:
        """Save a typing test result"""
        try:
            response = self.client.table("typing_tests").insert({
                "user_id": user_id,
                "wpm": wpm,
                "accuracy": accuracy
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving typing test: {e}")
            return None
    
    def get_user_tests(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get typing tests for a specific user"""
        try:
            response = self.client.table("typing_tests")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("test_date", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting user tests: {e}")
            return []
    
    def get_user_best_score(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's best WPM score"""
        try:
            response = self.client.table("typing_tests")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("wpm", desc=True)\
                .limit(1)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting best score: {e}")
            return None
    
    def get_user_average_stats(self, user_id: int) -> Dict[str, float]:
        """Calculate user's average WPM and accuracy"""
        try:
            tests = self.get_user_tests(user_id, limit=1000)
            if not tests:
                return {"avg_wpm": 0.0, "avg_accuracy": 0.0, "total_tests": 0}
            
            total_wpm = sum(test["wpm"] for test in tests)
            total_accuracy = sum(test["accuracy"] for test in tests)
            count = len(tests)
            
            return {
                "avg_wpm": round(total_wpm / count, 2),
                "avg_accuracy": round(total_accuracy / count, 2),
                "total_tests": count
            }
        except Exception as e:
            print(f"Error calculating averages: {e}")
            return {"avg_wpm": 0.0, "avg_accuracy": 0.0, "total_tests": 0}
    
    # ==================== LEADERBOARD OPERATIONS ====================
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the top `limit` individual test scores by WPM (duplicate users allowed).
        Priority order:
        1) top_tests view (if created in DB),
        2) direct typing_tests ordered by wpm,
        3) fallback to aggregated leaderboard view (per-user best).
        """
        # 1) Try security-definer view if it exists
        try:
            tv_resp = self.client.table("top_tests") \
                .select("user_id,wpm,accuracy,test_date") \
                .order("wpm", desc=True) \
                .limit(limit) \
                .execute()
            if tv_resp.data:
                results: List[Dict[str, Any]] = []
                for row in tv_resp.data:
                    user = self.get_user_by_id(row["user_id"])
                    results.append({
                        "user_id": row["user_id"],
                        "name": user["name"] if user else "Unknown",
                        "wpm": row.get("wpm", 0),
                        "accuracy": row.get("accuracy", 0),
                        "test_date": row.get("test_date")
                    })
                return results
        except Exception:
            pass

        # 2) Primary: top individual tests
        try:
            tests_resp = self.client.table("typing_tests") \
                .select("user_id,wpm,accuracy,test_date") \
                .order("wpm", desc=True) \
                .limit(limit) \
                .execute()

            if tests_resp.data:
                results: List[Dict[str, Any]] = []
                for row in tests_resp.data:
                    user = self.get_user_by_id(row["user_id"])
                    results.append({
                        "user_id": row["user_id"],
                        "name": user["name"] if user else "Unknown",
                        "wpm": row.get("wpm", 0),
                        "accuracy": row.get("accuracy", 0),
                        "test_date": row.get("test_date")
                    })
                return results
        except Exception as e:
            print(f"Error getting individual-scores leaderboard (tests): {e}")

        # 3) Fallback: aggregated per-user best from view
        try:
            view_resp = self.client.table("leaderboard") \
                .select("user_id,max_wpm,best_accuracy") \
                .order("max_wpm", desc=True) \
                .limit(limit) \
                .execute()

            if not view_resp.data:
                return []

            results: List[Dict[str, Any]] = []
            for row in view_resp.data:
                user = self.get_user_by_id(row["user_id"])
                results.append({
                    "user_id": row["user_id"],
                    "name": user["name"] if user else "Unknown",
                    "wpm": row.get("max_wpm", 0),
                    "accuracy": row.get("best_accuracy", 0)
                })
            return results
        except Exception as e:
            print(f"Error getting leaderboard view fallback: {e}")
            return []
    
    def get_user_rank(self, user_id: int) -> Optional[int]:
        """Get user's rank on leaderboard"""
        try:
            leaderboard = self.get_leaderboard(limit=1000)
            for idx, entry in enumerate(leaderboard, 1):
                if entry["user_id"] == user_id:
                    return idx
            return None
        except Exception as e:
            print(f"Error getting user rank: {e}")
            return None
    
    # ==================== STATISTICS ====================
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics"""
        try:
            # Get all tests
            response = self.client.table("typing_tests").select("*").execute()
            tests = response.data if response.data else []
            
            if not tests:
                return {
                    "total_tests": 0,
                    "avg_wpm": 0.0,
                    "highest_wpm": 0.0,
                    "avg_accuracy": 0.0
                }
            
            total_wpm = sum(test["wpm"] for test in tests)
            total_accuracy = sum(test["accuracy"] for test in tests)
            highest_wpm = max(test["wpm"] for test in tests)
            
            return {
                "total_tests": len(tests),
                "avg_wpm": round(total_wpm / len(tests), 2),
                "highest_wpm": round(highest_wpm, 2),
                "avg_accuracy": round(total_accuracy / len(tests), 2)
            }
        except Exception as e:
            print(f"Error getting global stats: {e}")
            return {
                "total_tests": 0,
                "avg_wpm": 0.0,
                "highest_wpm": 0.0,
                "avg_accuracy": 0.0
            }