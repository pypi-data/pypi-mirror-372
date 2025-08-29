"""
Email Template API Client

Handles authentication and API calls to the email template system.
"""

import requests
from typing import Dict, Any, Optional
import logging
import re
import json
import base64
from urllib.parse import unquote


class EmailTemplateClient:
    """Client for email template management API."""
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        if not base_url:
            raise ValueError("base_url is required")
        if not username:
            raise ValueError("username is required")  
        if not password:
            raise ValueError("password is required")
            
        self.base_url = base_url
        self.session = requests.Session()
        self.username = username
        self.password = password
        self._authenticated = False
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self) -> bool:
        """
        Authenticate with the email template system.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Step 1: Get initial cookies (XSRF-TOKEN, laravel_session)
            self.logger.info("Step 1: Getting initial cookies...")
            login_url = f"{self.base_url}/users/login"
            
            response = self.session.get(login_url)
            response.raise_for_status()
            
            self.logger.info(f"Initial cookies: {list(self.session.cookies.keys())}")
            
            # Verify we got the required cookies
            if 'XSRF-TOKEN' not in self.session.cookies:
                self.logger.error("Missing XSRF-TOKEN cookie")
                return False
            
            if 'laravel_session' not in self.session.cookies:
                self.logger.error("Missing laravel_session cookie")
                return False
            
            # Step 2: URL decode XSRF-TOKEN for X-XSRF-TOKEN header
            xsrf_cookie = self.session.cookies['XSRF-TOKEN']
            self.logger.debug(f"Raw XSRF-TOKEN: {xsrf_cookie[:50]}...")
            
            # URL decode the cookie value - this is what goes in X-XSRF-TOKEN header
            xsrf_token_value = unquote(xsrf_cookie)
            self.logger.debug(f"URL decoded XSRF-TOKEN: {xsrf_token_value[:50]}...")
            
            self.logger.info("XSRF token URL decoded successfully")
            
            # Step 3: Perform login POST with initial cookies and X-XSRF-TOKEN header
            self.logger.info("Step 2: Performing login with cookies and X-XSRF-TOKEN header...")
            
            login_data = {
                'email': self.username,
                'password': self.password
            }
            
            # Headers for login request
            headers = {
                'X-XSRF-TOKEN': xsrf_token_value,  # Decoded token value in header
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            self.logger.debug(f"Login cookies: {dict(self.session.cookies)}")
            self.logger.debug(f"X-XSRF-TOKEN: {xsrf_token_value[:30]}...")
            
            # POST login request (session will automatically include cookies)
            response = self.session.post(login_url, data=login_data, headers=headers, allow_redirects=False)
            
            self.logger.info(f"Login response: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Step 4: Handle login response
            if response.status_code == 302:
                # Success - login redirects
                redirect_url = response.headers.get('Location', '')
                self.logger.info(f"Login successful! Redirecting to: {redirect_url}")
                
                # Get new cookies after successful login
                self.logger.info(f"New cookies: {list(self.session.cookies.keys())}")
                
                # Follow redirect to complete the login process
                if redirect_url and not redirect_url.startswith('http'):
                    redirect_url = self.base_url + redirect_url
                
                if redirect_url:
                    redirect_response = self.session.get(redirect_url)
                    self.logger.info(f"Redirect completed: {redirect_response.status_code}")
                
                self._authenticated = True
                return True
                
            elif response.status_code == 200:
                # May still be successful, test with an API call
                self.logger.info("Got 200 response, testing authentication...")
                return self._test_authentication()
                
            else:
                self.logger.error(f"Login failed with status: {response.status_code}")
                if response.status_code == 419:
                    self.logger.error("CSRF token mismatch - check token extraction")
                self.logger.debug(f"Response: {response.text[:300]}...")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Authentication request failed: {e}")
            return False
    
    def _test_authentication(self) -> bool:
        """Test if authentication was successful by calling an authenticated endpoint."""
        try:
            test_url = f"{self.base_url}/email-templates/1"
            test_response = self.session.get(test_url, headers={'Accept': 'application/json'})
            
            self.logger.info(f"Auth test: {test_response.status_code}")
            
            if test_response.status_code in [200, 404]:  # 404 = authenticated but resource not found
                self._authenticated = True
                self.logger.info("Authentication verified!")
                return True
            elif test_response.status_code == 401:
                self.logger.error("Authentication test failed - still unauthorized")
                return False
            else:
                self.logger.warning(f"Unexpected auth test response: {test_response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Auth test failed: {e}")
            return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure the client is authenticated, authenticate if not."""
        if not self._authenticated:
            return self.authenticate()
        return True
    
    def get_email_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get email template by ID.
        
        Args:
            template_id: The email template ID
            
        Returns:
            Dict containing template information or None if error
        """
        if not self.ensure_authenticated():
            return None
            
        try:
            url = f"{self.base_url}/email-templates/{template_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching template {template_id}: {e}")
            return None
    
    def update_email_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Update email template.
        
        Args:
            template_data: Dictionary containing template update data
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if not self.ensure_authenticated():
            return False
            
        try:
            url = f"{self.base_url}/email-templates/update"
            
            # Get current XSRF token for the update request
            headers = {}
            if 'XSRF-TOKEN' in self.session.cookies:
                xsrf_cookie = self.session.cookies['XSRF-TOKEN']
                xsrf_token_value = unquote(xsrf_cookie)
                headers['X-XSRF-TOKEN'] = xsrf_token_value
                self.logger.debug(f"Using X-XSRF-TOKEN for update: {xsrf_token_value[:30]}...")
            
            response = self.session.post(url, data=template_data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if "ok" in result:
                self.logger.info(f"Template update successful: {result['ok']}")
                return True
            else:
                self.logger.error(f"Template update failed: {result}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Error updating template: {e}")
            return False