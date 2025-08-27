#!/usr/bin/env python3
"""
CLI utility for getting Next-Action keys
"""

import sys
from .key_extractor import get_key


def main():
    """
    Main CLI function
    """
    print("🔑 Getting Next-Action key...")
    
    try:
        key = get_key()
        
        if key:
            print(f"✅ Key obtained: {key}")
            return key
        else:
            print("❌ Failed to get key")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
