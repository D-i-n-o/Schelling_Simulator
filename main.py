import random
from collections import defaultdict
import pygame
import pygame_gui
import sys
from fractions import Fraction
from game import *
from utilities import *
from ui import *
import numpy as np 



def main():
    random.seed()
    
    pygame.init()
    w_width, w_height = 1400, 800
    screen = pygame.display.set_mode((w_width, w_height), pygame.RESIZABLE)
    
    pygame.display.set_caption('Schelling Simulator')
    clock = pygame.time.Clock()
    
    manager = pygame_gui.UIManager((w_width, w_height))
    

    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    
    game = Game(25, 25, peak = Fraction(1,2))
    game.adapt_to_windowsize(w_width, w_height)
    
    
    ui_window = SettingsWindow(pygame.Rect((800, 170), (640, 640)), manager, game)
    utility_window = GraphWindow(pygame.Rect((1000, 10), (300, 150)), manager, game)
    
    
    running = True
    paused = False
    simulation_speed = 1 # simulation ticks per second.
    ms_per_simulation_tick = 1000/simulation_speed
    elapsed_time_since_last_sim = 0.0
    while running:
        time_delta_ms = clock.tick(60)
        time_delta_s = time_delta_ms/1000.0
        if not paused:
            elapsed_time_since_last_sim += time_delta_ms
        simulate = False
        if elapsed_time_since_last_sim >= ms_per_simulation_tick:
            elapsed_time_since_last_sim -= ms_per_simulation_tick
            simulate = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                w_width, w_height = event.dict["size"]
                screen = pygame.display.set_mode((w_width, w_height), pygame.RESIZABLE)
                game.adapt_to_windowsize(w_width, w_height)
                manager.set_window_resolution((w_width, w_height))
            
            ui_window.callback_manager.handle_event(event)
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == ui_window.properties["Simulation Speed"].slider:                
                    simulation_speed = ui_window.properties["Simulation Speed"].get_value()
                    paused = (simulation_speed == 0)
                    if not paused:
                        ms_per_simulation_tick = 1000/simulation_speed
                    elapsed_time_since_last_sim = 0.0
            manager.process_events(event)

        manager.update(time_delta_s)
        if simulate:
            game.update_simulation()
        game.draw_on(screen, font)
        
        manager.draw_ui(screen)
        
        pygame.display.update()
        
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
    