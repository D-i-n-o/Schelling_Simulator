from collections import defaultdict
import pygame
import pygame_gui
import sys
from fractions import Fraction
from game import *
from utilities import *
from ui import *

import random
import numpy as np 
import argparse


def select_mode_popup(manager, screen, clock, w_width, w_height):

    mode_selection_window = pygame_gui.elements.UIWindow(
        pygame.Rect((w_width//4, w_height//4), (w_width//2, w_height//2)),
        manager=manager,
        window_display_title="Select Mode",
        object_id="#mode_selection_window"
    )

    button_layout_rect = pygame.Rect(0, 0, 100, 50)
    jump_button = pygame_gui.elements.UIButton(
        relative_rect=button_layout_rect.copy().move(50, 50),
        text='Jump',
        manager=manager,
        container=mode_selection_window,
        object_id="#jump_button"
    )

    swap_button = pygame_gui.elements.UIButton(
        relative_rect=button_layout_rect.copy().move(200, 50),
        text='Swap',
        manager=manager,
        container=mode_selection_window,
        object_id="#swap_button"
    )

    is_running = True
    mode = None
    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == jump_button:
                    mode = "Jump"
                    is_running = False
                elif event.ui_element == swap_button:
                    mode = "Swap"
                    is_running = False

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill((0, 0, 0))
        manager.draw_ui(screen)

        pygame.display.update()

    mode_selection_window.kill()
    return mode


def main():
    pygame.init()
    infoObject = pygame.display.Info()
    w_width, w_height = infoObject.current_w, infoObject.current_h
    screen = pygame.display.set_mode((w_width, w_height), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font(), 12)


    manager = pygame_gui.UIManager((w_width, w_height))

    mode = select_mode_popup(manager, screen, clock, w_width, w_height)

    utility = SinglePeakedUtility(Fraction(1, 2))

    if mode == "Jump":
        game = JumpGame(25, 25, utility)
    elif mode == "Swap":
        game = SwapGame(15, 15, utility)
    else:
        error_message = "No mode selected"
        print(error_message)
        exit(1) 


    pygame.display.set_caption(f'{mode} Schelling Simulator')



    game.adapt_to_windowsize(w_width, w_height)
        
    ui_window_width, ui_window_height = 640, 640
    ui_window_x = (w_width - ui_window_width)
    ui_window_y = (w_height - ui_window_height + 100)
    ui_window_rect = pygame.Rect((ui_window_x, ui_window_y), (ui_window_width, ui_window_height))

    graph_window_width, graph_window_height = 300, 150
    graph_window_margin_top, graph_window_margin_right = 10, 10
    graph_window_x = w_width - graph_window_width - graph_window_margin_right
    graph_window_y = graph_window_margin_top
    graph_window_rect = pygame.Rect((graph_window_x, graph_window_y), (graph_window_width, graph_window_height))

    ui_window = SettingsWindow(ui_window_rect, manager, game)
    utility_window = GraphWindow(graph_window_rect, manager, game)
    
    
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
     