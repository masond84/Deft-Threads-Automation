import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

class ThreadsAPI:
    def __init__(self):
        self.access_token = os.getenv("THREADS_ACCESS_TOKEN")
        self.app_id = os.getenv("THREADS_APP_ID")
        self.api_version = "v1.0"
        self.base_url = f"https://graph.threads.net/{self.api_version}"
        
        if not self.access_token:
            raise ValueError("THREADS_ACCESS_TOKEN not found in .env file")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_user_id(self) -> Optional[str]:
        """Get the current user's Threads user ID"""
        url = f"{self.base_url}/me"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            data = response.json()
            return data.get("id")
        else:
            print(f"Error getting user ID: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get information about the authenticated user/profile"""
        # Remove threads_count - it's not a valid field
        url = f"{self.base_url}/me?fields=id,username"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting user info: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def post_thread(self, text: str, auto_publish: bool = True) -> Optional[Dict]:
        """
        Post a text thread to Threads
        
        Args:
            text (str): The text content to post (max 500 characters)
            auto_publish (bool): If True, automatically publish after creation (default: True)
            
        Returns:
            dict: Response containing thread ID if successful, None otherwise
        """
        if len(text) > 500:
            print("Error: Thread text cannot exceed 500 characters")
            return None
        
        user_id = self.get_user_id()
        if not user_id:
            return None
        
        # Step 1: Create the thread container
        url = f"{self.base_url}/{user_id}/threads"
        
        payload = {
            "media_type": "TEXT",
            "text": text
        }
        
        # If auto_publish is True, add the parameter to publish automatically
        if auto_publish:
            payload["auto_publish_text"] = True
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Thread created successfully!")
            print(f"Full API Response: {result}")
            
            # The API returns 'creation_id' when creating, 'id' when published
            creation_id = result.get('creation_id') or result.get('id')
            
            if auto_publish:
                # If auto_publish was used, the thread should already be published
                if creation_id:
                    print(f"✅ Thread published automatically!")
                    print(f"Thread ID: {creation_id}")
                    result['thread_id'] = creation_id
                    return result
            else:
                # Step 2: Publish the thread using creation_id
                if creation_id:
                    publish_url = f"{self.base_url}/{user_id}/threads_publish"
                    publish_payload = {"creation_id": creation_id}
                    publish_response = requests.post(
                        publish_url, 
                        headers=self._get_headers(), 
                        json=publish_payload
                    )
                    
                    if publish_response.status_code == 200:
                        publish_result = publish_response.json()
                        print(f"✅ Thread published successfully!")
                        print(f"Publish Response: {publish_result}")
                        # The publish response contains the actual thread ID
                        thread_id = publish_result.get('id')
                        if thread_id:
                            result['thread_id'] = thread_id
                            result['creation_id'] = creation_id
                        return result
                    else:
                        print(f"❌ Error publishing thread: {publish_response.status_code}")
                        print(f"Publish response: {publish_response.text}")
                        return None
            
            return result
        else:
            print(f"❌ Error creating thread: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def reply_to_thread(self, thread_id: str, text: str) -> Optional[Dict]:
        """
        Reply to an existing thread
        
        Args:
            thread_id (str): The ID of the thread to reply to
            text (str): The reply text
            
        Returns:
            dict: Response containing reply ID if successful
        """
        if len(text) > 500:
            print("Error: Reply text cannot exceed 500 characters")
            return None
        
        user_id = self.get_user_id()
        if not user_id:
            return None
        
        url = f"{self.base_url}/{user_id}/threads"
        
        payload = {
            "media_type": "TEXT",
            "text": text,
            "reply_control": "FOLLOWERS",  # or "MENTIONED" or "OFF"
            "reply_to": thread_id
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Reply posted!")
            return result
        else:
            print(f"❌ Error posting reply: {response.status_code}")
            print(f"Response: {response.text}")
            return None