import pygame
import time
import json
import pandas as pd
import numpy as np
from classes import *

game = App(population_size=200, apple_population=35, kids_amount=2, apple_max=200)
game.game_running()