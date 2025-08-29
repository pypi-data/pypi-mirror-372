"""
Configuration file for ROS Chatbot CLI
"""

import os
from typing import Optional
from typing import List
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import platform
import shutil

from rich.console import Console
console = Console()


# Load .env file from multiple locations
possible_paths = [
    Path(__file__).parent.parent / ".env",  # Project root
    Path(__file__).parent / ".env",         # cli directory  
    Path.cwd() / ".env"                     # Current directory
]

for env_path in possible_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break
else:
    # Try auto-discovery
    from dotenv import find_dotenv
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file, override=True)
        print(f"Auto-discovered .env at: {env_file}")

# API Keys - get them after all loading attempts
AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")

# Default configurations
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OLLAMA_MODEL = "qwen3:1.7b"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_ROS_VERSION = "both"
SUPPORTED_ROS_VERSIONS = ["ros1", "ros2", "both"]

# ROS Distro configurations
DEFAULT_ROS_DISTRO = None  # Auto-detect by default
SUPPORTED_ROS_DISTROS = [
    # ROS2 Distros
    "humble", "iron", "jazzy", "rolling", 
    # ROS1 Distros (legacy)
    "noetic", "melodic"
]
# Allow user override via environment variable
USER_ROS_DISTRO = os.getenv("OORB_ROS_DISTRO")

# Available models
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant", 
    "gemma2-9b-it"
]

OLLAMA_MODELS = [
    "qwen3:1.7b",
]

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4-turbo", 
    "gpt-3.5-turbo",
    "gpt-4.1",
    "gpt-4o-mini"
]

# Azure OpenAI Configuration (preferred)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Available Azure OpenAI models (deployment names in Azure)
AZURE_OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4",
    "gpt-4-turbo", 
    "gpt-35-turbo",
    "gpt-4o",
    "gpt-4o-mini"
]

# Add retrieval API base URL configuration
RETRIEVAL_API_BASE_URL = os.getenv("RETRIEVAL_API_BASE_URL", "http://localhost:8000")
DEFAULT_RETRIEVAL_ENDPOINT = "http://localhost:8000"

# Allow user override for retrieval endpoint
USER_RETRIEVAL_ENDPOINT = os.getenv("OORB_RETRIEVAL_ENDPOINT")

# Helper functions

def get_available_backends() -> List[str]:
    backends = []
    if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
        backends.append("azure")
    if OPENAI_API_KEY:
        backends.append("openai")
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            backends.append("ollama")
    except:
        pass
    return backends

def get_best_available_backend() -> Optional[str]:
    for backend in ["azure", "openai", "ollama"]:
        if backend in get_available_backends():
            return backend
    return None

def get_default_model_for_backend(backend: str) -> Optional[str]:
    if backend == "azure" and AZURE_OPENAI_MODELS:
        return AZURE_OPENAI_MODELS[0]
    if backend == "openai" and OPENAI_MODELS:
        return OPENAI_MODELS[0]
    if backend == "ollama" and OLLAMA_MODELS:
        return OLLAMA_MODELS[0]
    return None

def check_backend_availability(backend: str) -> tuple[bool, str]:
    """Check if a specific backend is available"""
    backend = backend.lower()
    
    if backend == "azure" or backend == "openai":
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
            return True, "Azure OpenAI API available"
        elif OPENAI_API_KEY:
            return True, "OpenAI API available"
        else:
            return False, "Neither AZURE_OPENAI_API_KEY nor OPENAI_API_KEY set"
    
    elif backend == "ollama":
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return True, "Ollama service running"
            else:
                return False, "Ollama service not responding"
        except:
            return False, "Ollama service not running"
    else:
        return False, f"Unknown backend: {backend}"

def validate_config():
    """Validate configuration"""
    errors = []
    warnings = []
    
    if not AZURE_OPENAI_API_KEY and not OPENAI_API_KEY:
        warnings.append("No API keys found. Set AZURE_OPENAI_API_KEY or OPENAI_API_KEY or use Ollama.")
    
    if DEFAULT_TEMPERATURE < 0 or DEFAULT_TEMPERATURE > 1:
        errors.append("DEFAULT_TEMPERATURE must be between 0 and 1")
    
    return {"errors": errors, "warnings": warnings}


def get_ubuntu_version():
    try:
        version = platform.linux_distribution()[1]
    except AttributeError:
        import distro
        version = distro.version()
    return version

def ROS_Distro(user_override: str = None):
    """
    Get ROS distro with user override capability
    Priority: user_override > OORB_ROS_DISTRO env var > ROS_DISTRO env var > auto-detect
    """
    # 1. Check user override parameter
    if user_override and user_override.lower() in SUPPORTED_ROS_DISTROS:
        return user_override.lower()
    
    # 2. Check OORB-specific environment variable
    if USER_ROS_DISTRO and USER_ROS_DISTRO.lower() in SUPPORTED_ROS_DISTROS:
        return USER_ROS_DISTRO.lower()
    
    # 3. Check standard ROS environment variable
    ros_distro = os.environ.get("ROS_DISTRO")
    if ros_distro and ros_distro.lower() in SUPPORTED_ROS_DISTROS:
        return ros_distro.lower()
    
    # 4. Try to auto-detect from sourced environment
    try:
        # Try to detect from common ROS setup paths
        setup_paths = [
            f"/opt/ros/{distro}/setup.bash" for distro in SUPPORTED_ROS_DISTROS
        ]
        for path in setup_paths:
            if os.path.exists(path):
                distro = path.split('/')[-2]
                return distro
    except:
        pass
    
    return None

def get_ros_distro_info(distro: str = None) -> dict:
    """Get detailed information about a ROS distro"""
    current_distro = distro or ROS_Distro()
    
    distro_info = {
        # ROS2 Distros
        "humble": {"version": "ROS2", "lts": True, "eol": "2027-05", "ubuntu": ["20.04", "22.04"]},
        "iron": {"version": "ROS2", "lts": False, "eol": "2024-11", "ubuntu": ["22.04"]},
        "jazzy": {"version": "ROS2", "lts": True, "eol": "2029-05", "ubuntu": ["24.04"]},
        "rolling": {"version": "ROS2", "lts": False, "eol": "Rolling", "ubuntu": ["22.04", "24.04"]},
        # ROS1 Distros
        "noetic": {"version": "ROS1", "lts": True, "eol": "2025-05", "ubuntu": ["20.04"]},
        "melodic": {"version": "ROS1", "lts": True, "eol": "2023-05", "ubuntu": ["18.04"]},
    }
    
    if current_distro and current_distro in distro_info:
        info = distro_info[current_distro].copy()
        info["name"] = current_distro
        info["detected"] = True
        return info
    
    return {"name": "unknown", "version": "unknown", "detected": False}

def get_retrieval_endpoint(user_override: str = None) -> str:
    """
    Get retrieval API endpoint with user override capability
    Priority: user_override > OORB_RETRIEVAL_ENDPOINT env var > RETRIEVAL_API_BASE_URL env var > default
    """
    # 1. Check user override parameter
    if user_override:
        return user_override.strip()
    
    # 2. Check OORB-specific environment variable
    if USER_RETRIEVAL_ENDPOINT:
        return USER_RETRIEVAL_ENDPOINT.strip()
    
    # 3. Check standard RETRIEVAL_API_BASE_URL environment variable
    if RETRIEVAL_API_BASE_URL:
        return RETRIEVAL_API_BASE_URL.strip()
    
    # 4. Default fallback
    return DEFAULT_RETRIEVAL_ENDPOINT

def validate_retrieval_endpoint(endpoint: str) -> tuple[bool, str]:
    """Validate if a retrieval endpoint is accessible"""
    if not endpoint:
        return False, "No endpoint specified"
    
    try:
        import requests
        from urllib.parse import urlparse
        
        # Basic URL validation
        parsed = urlparse(endpoint)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format. Use http://host:port or https://host:port"
        
        # Test connectivity
        test_url = endpoint.rstrip('/') + '/health' if not endpoint.endswith('/') else endpoint + 'health'
        response = requests.get(test_url, timeout=5)
        
        if response.status_code == 200:
            return True, "Endpoint is accessible"
        elif response.status_code == 404:
            # /health endpoint might not exist, try base endpoint
            response = requests.get(endpoint, timeout=5)
            if response.status_code in [200, 404, 405]:  # 404/405 are acceptable for API endpoints
                return True, "Endpoint is accessible (no /health endpoint)"
            else:
                return False, f"Endpoint returned status {response.status_code}"
        else:
            return False, f"Endpoint returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to endpoint - check if service is running"
    except requests.exceptions.Timeout:
        return False, "Connection timeout - endpoint may be slow or unreachable"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def get_retrieval_endpoint_info(endpoint: str = None) -> dict:
    """Get detailed information about a retrieval endpoint"""
    current_endpoint = endpoint or get_retrieval_endpoint()
    
    info = {
        "endpoint": current_endpoint,
        "accessible": False,
        "status_code": None,
        "error": None,
        "features": []
    }
    
    try:
        import requests
        
        # Test base endpoint
        response = requests.get(current_endpoint, timeout=5)
        info["status_code"] = response.status_code
        info["accessible"] = response.status_code in [200, 404, 405]
        
        # Test common retrieval endpoints
        test_endpoints = [
            "/retrieve", "/search", "/query", "/health", "/docs"
        ]
        
        for test_path in test_endpoints:
            try:
                test_url = current_endpoint.rstrip('/') + test_path
                test_response = requests.get(test_url, timeout=2)
                if test_response.status_code in [200, 405]:  # 405 = Method Not Allowed (POST might be required)
                    info["features"].append(test_path)
            except:
                continue
                
    except Exception as e:
        info["error"] = str(e)
    
    return info

def validate_ros_distro(distro: str) -> tuple[bool, str]:
    """Validate if a ROS distro is supported"""
    if not distro:
        return False, "No distro specified"
    
    distro = distro.lower().strip()
    if distro in SUPPORTED_ROS_DISTROS:
        info = get_ros_distro_info(distro)
        return True, f"Valid {info['version']} distro"
    
    return False, f"Unsupported distro. Supported: {', '.join(SUPPORTED_ROS_DISTROS)}"
    """Validate if a ROS distro is supported"""
    if not distro:
        return False, "No distro specified"
    
    distro = distro.lower().strip()
    if distro in SUPPORTED_ROS_DISTROS:
        info = get_ros_distro_info(distro)
        return True, f"Valid {info['version']} distro"
    
    return False, f"Unsupported distro. Supported: {', '.join(SUPPORTED_ROS_DISTROS)}"



def is_ros_installed(ros_version):
        if ros_version == "ros1":
            return shutil.which("roscore") is not None
        elif ros_version == "ros2":
            return shutil.which("ros2") is not None
        elif ros_version == "both":
            return shutil.which("roscore") is not None and shutil.which("ros2") is not None
        return False
