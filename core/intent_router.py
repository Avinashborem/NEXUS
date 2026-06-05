# core/intent_router.py
from core.brain import ask_brain

def route(command):
    return ask_brain(command)