import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, List
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

    def get_user_threads(self, limit: int = 25) -> Optional[List[Dict]]:
        """
        Fetch the authenticated user's recent threads with pagination support
        
        Args:
            limit: Maximum number of threads to fetch (default: 25)
            
        Returns:
            List of thread dictionaries with text content, or None if failed
        """
        user_id = self.get_user_id()
        if not user_id:
            print("❌ Could not get user ID")
            return None
        
        url = f"{self.base_url}/{user_id}/threads"
        all_threads = []
        
        params = {
            "fields": "id,text,thread_id,timestamp",
            "limit": min(limit, 100)  # API might have max limit per request
        }
        
        try:
            while len(all_threads) < limit:
                response = requests.get(url, headers=self._get_headers(), params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    threads = data.get("data", [])
                    
                    if not threads:
                        break  # No more posts available
                    
                    all_threads.extend(threads)
                    
                    # Check for pagination
                    paging = data.get("paging", {})
                    next_cursor = paging.get("cursors", {}).get("after")
                    
                    if next_cursor and len(all_threads) < limit:
                        params["after"] = next_cursor
                    else:
                        break  # No more pages or reached limit
                else:
                    if len(all_threads) == 0:
                        # First request failed
                        print(f"❌ Error fetching threads: {response.status_code}")
                        print(f"Response: {response.text}")
                        
                        if response.status_code == 403:
                            print("💡 Tip: You may need 'threads_basic' permission in your access token")
                        elif response.status_code == 404:
                            print("💡 Tip: This endpoint may not be available in the current API version")
                        
                        return None
                    else:
                        # Partial success - return what we have
                        print(f"⚠️  Pagination stopped at {len(all_threads)} posts")
                        break
            
            # Trim to exact limit if needed
            if len(all_threads) > limit:
                all_threads = all_threads[:limit]
            
            if all_threads:
                print(f"✅ Fetched {len(all_threads)} posts from Threads")
            else:
                print(f"⚠️  No posts found")
            
            return all_threads
            
        except Exception as e:
            print(f"❌ Exception while fetching threads: {e}")
            return None if len(all_threads) == 0 else all_threads

    def post_thread(self, text: str, auto_publish: bool = True) -> Optional[Dict]:
        """
        Post a text thread to Threads
        
        Args:
            text (str): The text content to post (max 500 characters)
            auto_publish (bool): If True, automatically publish after creation (default: True)
            
        Returns:
            dict: Response containing thread ID if successful, or error dict if failed
        """
        if len(text) > 500:
            error_msg = "Thread text cannot exceed 500 characters"
            print(f"❌ Error: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'status_code': 400
            }
        
        user_id = self.get_user_id()
        if not user_id:
            error_msg = "Could not get user ID from Threads API"
            print(f"❌ Error: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'status_code': 401
            }
        
        # Step 1: Create the thread container
        url = f"{self.base_url}/{user_id}/threads"
        
        payload = {
            "media_type": "TEXT",
            "text": text
        }
        
        # If auto_publish is True, add the parameter to publish automatically
        if auto_publish:
            payload["auto_publish_text"] = True
        
        print(f"📤 Creating thread with auto_publish={auto_publish}...")
        print(f"📝 Post text ({len(text)} chars): {text[:100]}...")
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
        except Exception as e:
            error_msg = f"Network error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'status_code': 0
            }
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Thread created successfully!")
            print(f"📋 Full API Response: {result}")
            
            # The API returns 'creation_id' when creating, 'id' when published
            creation_id = result.get('creation_id') or result.get('id')
            
            if auto_publish:
                # If auto_publish was used, the thread should already be published
                if creation_id:
                    print(f"✅ Thread published automatically!")
                    print(f"🆔 Thread ID: {creation_id}")
                    return {
                        'success': True,
                        'id': creation_id,
                        'thread_id': creation_id,
                        'creation_id': creation_id,
                        'response': result
                    }
                else:
                    # No ID in response - might need manual publish
                    print(f"⚠️ No thread ID in auto-publish response, trying manual publish...")
                    # Fall through to manual publish logic
            else:
                # Step 2: Publish the thread using creation_id
                if creation_id:
                    publish_url = f"{self.base_url}/{user_id}/threads_publish"
                    publish_payload = {"creation_id": creation_id}
                    print(f"📤 Publishing thread with creation_id: {creation_id}...")
                    
                    try:
                        publish_response = requests.post(
                            publish_url, 
                            headers=self._get_headers(), 
                            json=publish_payload
                        )
                    except Exception as e:
                        error_msg = f"Network error during publish: {str(e)}"
                        print(f"❌ {error_msg}")
                        return {
                            'success': False,
                            'error': error_msg,
                            'creation_id': creation_id,
                            'status_code': 0
                        }
                    
                    if publish_response.status_code == 200:
                        publish_result = publish_response.json()
                        print(f"✅ Thread published successfully!")
                        print(f"📋 Publish Response: {publish_result}")
                        # The publish response contains the actual thread ID
                        thread_id = publish_result.get('id')
                        if thread_id:
                            return {
                                'success': True,
                                'id': thread_id,
                                'thread_id': thread_id,
                                'creation_id': creation_id,
                                'response': publish_result
                            }
                        else:
                            error_msg = "Publish succeeded but no thread ID in response"
                            print(f"⚠️ {error_msg}")
                            return {
                                'success': False,
                                'error': error_msg,
                                'creation_id': creation_id,
                                'response': publish_result
                            }
                    else:
                        error_msg = f"Error publishing thread: HTTP {publish_response.status_code}"
                        print(f"❌ {error_msg}")
                        print(f"📋 Publish response: {publish_response.text}")
                        return {
                            'success': False,
                            'error': error_msg,
                            'detail': publish_response.text,
                            'creation_id': creation_id,
                            'status_code': publish_response.status_code
                        }
                else:
                    error_msg = "No creation_id returned from thread creation"
                    print(f"❌ {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'response': result
                    }
            
            # If we get here with auto_publish but no ID, return what we have
            if creation_id:
                return {
                    'success': True,
                    'id': creation_id,
                    'thread_id': creation_id,
                    'creation_id': creation_id,
                    'response': result
                }
            
            # No ID at all
            error_msg = "Thread created but no ID returned"
            print(f"⚠️ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'response': result
            }
        else:
            error_msg = f"Error creating thread: HTTP {response.status_code}"
            print(f"❌ {error_msg}")
            print(f"📋 Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                error_detail = error_data.get('error', {}).get('message', response.text)
            except:
                error_detail = response.text
            
            return {
                'success': False,
                'error': error_msg,
                'detail': error_detail,
                'status_code': response.status_code,
                'response': response.text
            }
    
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