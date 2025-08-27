from playwright.sync_api import sync_playwright
import json


def get_key():
    """
    Get Next-Action key from repixify.com website
    
    Returns:
        str: Next-Action key or None if error occurred
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        next_action_value = None
        
        def handle_response(response):
            nonlocal next_action_value
            if (response.request.method == "POST" and 
                "riddle-solver" in response.url):
                
                request_headers = response.request.headers
                
                if "next-action" in request_headers:
                    next_action_value = request_headers["next-action"]
                
                try:
                    post_data = response.request.post_data
                    if post_data:
                        try:
                            json_data = json.loads(post_data)
                            if "Next-Action" in json_data:
                                next_action_value = json_data["Next-Action"]
                        except:
                            pass
                            
                except Exception as e:
                    pass
        
        page.on("response", handle_response)
        
        try:
            page.goto("https://www.repixify.com/tools/riddle-solver")
            
            page.wait_for_load_state("networkidle")
            
            textarea_xpath = "/html/body/main/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[2]/div/div[1]/textarea"
            
            page.wait_for_selector(f"xpath={textarea_xpath}", timeout=10000)
            
            page.fill(f"xpath={textarea_xpath}", "2+2")
            
            button_xpath = "/html/body/main/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[2]/div/div[2]/button"
            
            page.wait_for_selector(f"xpath={button_xpath}", timeout=10000)
            
            page.click(f"xpath={button_xpath}")
            
            page.wait_for_timeout(1000)
            
            if not next_action_value:
                page.wait_for_timeout(1000)
                
        except Exception as e:
            pass
        
        finally:
            browser.close()
            
        return next_action_value
