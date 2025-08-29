"""
ROS Chatbot CLI Package

A command-line interface for interacting with a ROS/ROS2 specialized chatbot
that can answer questions about Robot Operating System development and usage.
"""

__version__ = "1.0.0"
__author__ = "OORB Chatbot Team"
__description__ = "Intelligent assistant for ROS and ROS2 questions"

from .oorb_qa_system import ROSQASystem
from .config import *

__all__ = [
    "ROSQASystem",
    "OLLAMA_MODELS",
    "OPENAI_MODELS"
]