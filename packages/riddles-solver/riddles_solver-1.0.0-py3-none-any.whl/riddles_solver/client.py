import requests
import json
import re

try:
    from user_agents import parse
except ImportError:
    parse = None


class Client:
    """
    Client for solving riddles using repixify.com
    
    Usage example:
        client = Client(key="a1b2c3d4e5f6789012345678901234567890abcdef")
        answer = client.solve(riddle="2+2")
        print(answer)
    """
    
    def __init__(self, key, user_agent=None):
        """
        Initialize the client
        
        Args:
            key (str): Next-Action key for API
            user_agent (str, optional): Custom User-Agent string
        """
        self.key = key
        self.url = "https://www.repixify.com/tools/riddle-solver"
        self.session = requests.Session()
        self.user_agent = user_agent or self._generate_user_agent()
        
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/x-component",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Next-Action": self.key,
        }
    
    def solve(self, riddle):
        """
        Solve a riddle
        
        Args:
            riddle (str): The riddle text
            
        Returns:
            str: Answer to the riddle or None if error occurred
        """
        body_data = [
            f"What is an answer to the following riddle: {riddle}",
            {
                "items": {
                    "riddle": {
                        "type": "string",
                        "description": "The answer to the riddle"
                    }
                }
            }
        ]
        
        try:
            response = self.session.post(
                self.url,
                headers=self.headers,
                data=json.dumps(body_data),
                timeout=30
            )
            
            response.encoding = 'utf-8'
            
            content_type = response.headers.get('content-type', '')
            
            if 'text/html' in content_type:
                return None
            elif 'application/json' in content_type:
                try:
                    json_response = response.json()
                    return self._extract_answer(json_response)
                except json.JSONDecodeError:
                    return None
            else:
                match = re.search(r'"riddle"\s*:\s*"([^"]+)"', response.text)
                if match:
                    return match.group(1)
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def _extract_answer(self, json_response):
        """
        Extract answer from JSON response
        
        Args:
            json_response: JSON response from server
            
        Returns:
            str: Extracted answer or JSON as string
        """
        if isinstance(json_response, dict):
            if "riddle" in json_response:
                return json_response["riddle"]
            for v in json_response.values():
                if isinstance(v, dict) and "riddle" in v:
                    return v["riddle"]
        
        if isinstance(json_response, list):
            for item in json_response:
                if isinstance(item, dict) and "riddle" in item:
                    return item["riddle"]
        
        return json.dumps(json_response, ensure_ascii=False)
    
    def _generate_user_agent(self):
        """
        Generate random User-Agent
        
        Returns:
            str: User-Agent string
        """
        if parse:
            from user_agents import UserAgent
            ua = UserAgent()
            return str(ua.random)
        else:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"
