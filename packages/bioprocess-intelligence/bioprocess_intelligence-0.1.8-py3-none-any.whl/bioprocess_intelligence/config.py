from typing import Optional

class Config:
    def __init__(self):
        # GraphQL endpoint
        self.api_url: str = ''
        
        # Authentication
        self.username: str = ''
        self.password: str = ''
        
        # JWT token (will be set after authentication)
        self.token: Optional[str] = None

# Global config instance - only used if not overridden by client
config = Config()
