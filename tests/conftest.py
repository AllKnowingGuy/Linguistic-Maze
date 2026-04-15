import os
import sys
import pytest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def change_test_dir():
    """Меняет рабочую директорию, если нужно для тестов (в текущем состоянии проекта не нужно)"""
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    os.chdir(src_dir)
    yield

@pytest.fixture(autouse=True)
def init_pygame():
    """Инициализирует pygame, нужно для некоторых тестов"""
    pygame.init()
    yield
