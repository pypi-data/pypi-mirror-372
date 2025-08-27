import aiohttp
import asyncio
import json
import re

try:
    from user_agents import parse
except ImportError:
    parse = None


class AsyncClient:
    """
    Asynchronous client for solving riddles using repixify.com
    
    Usage example:
        async def main():
            client = AsyncClient(key="a1b2c3d4e5f6789012345678901234567890abcdef")
            answer = await client.solve(riddle="2+2")
            print(answer)
            await client.close()
        
        asyncio.run(main())
    """
    
    def __init__(self, key, user_agent=None):
        """
        Initialize the asynchronous client
        
        Args:
            key (str): Next-Action key for API
            user_agent (str, optional): Custom User-Agent string
        """
        self.key = key
        self.url = "https://www.repixify.com/tools/riddle-solver"
        self.user_agent = user_agent or self._generate_user_agent()
        self._session = None
        
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/x-component",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Next-Action": self.key,
        }
    
    async def _get_session(self):
        """Create or return existing session"""
        if self._session is None:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self._session
    
    async def solve(self, riddle):
        """
        Asynchronously solve a riddle
        
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
        
        session = await self._get_session()
        
        try:
            async with session.post(
                self.url,
                headers=self.headers,
                data=json.dumps(body_data)
            ) as response:
                
                content_type = response.headers.get('content-type', '')
                
                if 'text/html' in content_type:
                    return None
                elif 'application/json' in content_type:
                    try:
                        json_response = await response.json()
                        return self._extract_answer(json_response)
                    except:
                        return None
                else:
                    text = await response.text()
                    match = re.search(r'"riddle"\s*:\s*"([^"]+)"', text)
                    if match:
                        return match.group(1)
                    return None
                    
        except Exception:
            return None
    
    async def solve_batch(self, riddles):
        """
        Asynchronously solve multiple riddles in parallel
        
        Args:
            riddles (list): List of riddles
            
        Returns:
            list: List of answers (or None for failed requests)
        """
        tasks = [self.solve(riddle) for riddle in riddles]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
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
    
    async def close(self):
        """Close the session"""
        if self._session:
            try:
                await self._session.close()
                await asyncio.sleep(0.1)
            except Exception:
                pass
            finally:
                self._session = None
    
    async def __aenter__(self):
        """Support for async context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager"""
        await self.close()
        try:
            await asyncio.sleep(0.01)
        except Exception:
            pass
    
    def __del__(self):
        """Destructor for guaranteed session closure"""
        if self._session and not self._session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except Exception:
                pass
