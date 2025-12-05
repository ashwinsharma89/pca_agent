import reflex as rx
import requests
from .base import BaseState

API_URL = "http://localhost:8001"

class AuthState(BaseState):
    """State for Authentication."""
    
    token: str = rx.Cookie(name="token")
    user_authenticated: bool = False
    username: str = ""
    
    def check_auth(self):
        """Check if user is authenticated via token."""
        if self.token:
            self.user_authenticated = True
            self.username = "User" 
        else:
            self.user_authenticated = False

    def login(self, form_data: dict):
        """Handle login."""
        self.log(f"Login attempt for user: {form_data.get('username')}")
        try:
            data = {
                "username": form_data["username"],
                "password": form_data["password"]
            }
            response = requests.post(f"{API_URL}/api/v1/auth/login", json=data)
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.user_authenticated = True
                self.username = form_data["username"]
                self.log(f"Login successful for user: {self.username}")
                return rx.redirect("/")
            else:
                self.log(f"Login failed for user: {form_data.get('username')} - {response.text}", level="warning")
                return rx.window_alert("Login failed: Invalid credentials")
        except Exception as e:
            self.log(f"Login error: {e}", level="error")
            return rx.window_alert(f"Login error: {str(e)}")

    def logout(self):
        """Handle logout."""
        self.log(f"User {self.username} logging out")
        self.token = ""
        self.user_authenticated = False
        return rx.redirect("/")
