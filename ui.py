from collections import defaultdict
import pygame
import pygame_gui
from fractions import Fraction
from game import *
from pygame_gui.elements import UIWindow
from pygame_gui.elements import UIButton
from pygame_gui.elements import UIHorizontalSlider
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.elements import UILabel
import numpy as np 

from utilities import *

class UICallbackManager:
    def __init__(self):
        self.callbacks = defaultdict(lambda: defaultdict(list))
        
    def add_callback(self, event_type, obj, callback):
        self.callbacks[event_type][obj].append(callback)
    
    def handle_event(self,event):
        if not hasattr(event, "ui_element"):
            return
        for function in self.callbacks[event.type][event.ui_element]:
            function(event)
def clip(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


class GraphWindow(UIWindow):
    def __init__(self, rect, ui_manager, game, title = "Utility Function", id = '#utility_graph'):
        super().__init__(rect, ui_manager,
                            window_display_title=title,
                            object_id=id,
                            resizable=True)
        self.game = game
    def update(self, time_delta):
        
        self.image.fill((50,50,50))
        super().update(time_delta)
        step_size = 0.01
        points = []
        for i, f_i in enumerate(np.arange(0.0, 1.0+step_size, step_size)):
            h = self.rect.height - 75
            points.append((i*step_size*self.rect.width*0.8 + self.rect.width*0.1, h-(self.game.utility_function(f_i)*h*0.8) - h*0.1+35))
        pygame.draw.lines(self.image, (200,200,200), False, points, width=2)
    def on_close_window_button_pressed(self):
        self.hide()


class UISliderProperty:
    def __init__(self, window, name, start_value, value_range, click_increment = 1,**kwargs):
        self.name = name
        self.value_range = value_range
        self.slider = window.make(UIHorizontalSlider, start_value = start_value, value_range = value_range, click_increment = click_increment, **kwargs)
        self.label = window.make(UILabel, text = name)
        self.value_text = window.make(UITextEntryLine)
        self.value_text.set_text(str(self.slider.get_current_value()))
        self.value_text.set_allowed_characters([str(i) for i in range(10)] + ['.', '-'])
        
        def value_text_changed(event):
            try:
                val = float(self.value_text.get_text())

                if self.value_range is not None:
                    val = clip(val, self.value_range[0], self.value_range[1])
                self.slider.set_current_value(val)
            except:
                pass
            
        window.callback_manager.add_callback(pygame_gui.UI_TEXT_ENTRY_CHANGED, self.value_text, value_text_changed)
        window.callback_manager.add_callback(pygame_gui.UI_HORIZONTAL_SLIDER_MOVED, self.slider, 
                                           lambda event: self.value_text.set_text(str(self.slider.get_current_value())))
    def get_value(self):
        return self.slider.get_current_value()
    def update(self):
        pass
    def ui_elements(self):
        return [self.label, self.slider, self.value_text]
    

class UIDropDownProperty:
    def __init__(self, window, name, options_list, starting_option, **kwargs):
        self.name = name
        self.value = starting_option
        self.label = window.make(UILabel, text = name)
        def set_value(event):
            self.value = event.text
        self.dropdown = window.make(UIDropDownMenu, options_list = options_list, starting_option = starting_option, **kwargs)
        window.callback_manager.add_callback(pygame_gui.UI_DROP_DOWN_MENU_CHANGED, self.dropdown, set_value)
    def update(self):
        pass
    def get_value(self):
        return self.value
    
    def ui_elements(self):
        return [self.label, self.dropdown]
    

class UITextProperty:
    def __init__(self, window, name, text):
        self.name = name
        self.value_text = window.make(UITextEntryLine)
        self.value_text.set_text(text)
        self.label = window.make(UILabel, text = name)
        self.value = text
        def value_text_changed(event):
            self.value = event.text
            
        window.callback_manager.add_callback(pygame_gui.UI_TEXT_ENTRY_CHANGED, self.value_text, value_text_changed)
    def update(self):
        pass
    def get_value(self):
        return self.value
    
    def ui_elements(self):
        return [self.label, self.value_text]

class UIDisplayValue:
    def __init__(self, window, name, update_func):
        self.name = name
        self.value_label = window.make(UILabel, text = "")
        self.label = window.make(UILabel, text = name)
        self.update_func = update_func
        
    def update(self):
        self.value_label.set_text(self.update_func())
    
    def ui_elements(self):
        return [self.label, self.value_label]

class SettingsWindow(UIWindow):
    def add_ui_property(self, prop):
        self.properties[prop.name] = prop
        
        
    def make_row(self, *elements):
        first_element_width = 0.33
        width_per_element = self.rect.width * 0.9*(1-first_element_width) / (len(elements)-1)
        start_x = 0
        for i, element in enumerate(elements):
            if i == 0:
                element.set_relative_position((start_x, self.current_row * self.row_y*1.5))
                element.set_dimensions((first_element_width * self.rect.width, self.row_y))
                start_x += first_element_width * self.rect.width
            else:
                element.set_relative_position((start_x, self.current_row * self.row_y*1.5))
                element.set_dimensions((width_per_element, self.row_y))
                start_x +=width_per_element
        self.current_row += 1
    def make(self, cls, **kwargs):
        callbacks = kwargs.get("callbacks", [])
        if "callbacks" in kwargs:
            kwargs.pop("callbacks")
        obj = cls(relative_rect = self.default_rect, manager = self.ui_manager, container = self, **kwargs)
        for event_type, callback in callbacks:
            self.callback_manager.add_callback(event_type, obj, callback)
        return obj
    
    def rebuild_ui(self):
        self.current_row = 0.25
        for name, prop in self.properties.items():
            self.make_row(*prop.ui_elements())
            
    def __init__(self, rect, ui_manager, game):
        super().__init__(rect, ui_manager,
                         window_display_title='Settings',
                         object_id='#settings',
                         resizable=True)
        self.properties = {}
        self.display_values = {}
        
        self.game = game
        self.row_y = 25
        self.settings = {}
        self.enable_close_button = False
        self.rebuild()
        self.default_rect = pygame.Rect((0,0), (100, self.row_y))
        self.callback_manager = UICallbackManager()
        
        
        
        self.add_ui_property(UISliderProperty(self, "Simulation Speed", start_value = 1, value_range=(0, 100), click_increment = 1))
        self.add_ui_property(UISliderProperty(self, "Width", start_value  = 20, value_range=(1, 100), click_increment = 1))
        self.add_ui_property(UISliderProperty(self, "Height", start_value = 20, value_range=(1, 100), click_increment = 1))
        self.add_ui_property(UIDropDownProperty(self, "Torus Type", starting_option = "8-Torus", options_list = ["8-Torus", "4-Torus"]))
        self.add_ui_property(UIDropDownProperty(self, "Neighborhood", starting_option = "Self-Inclusive", options_list = ["Self-Inclusive", "Self-Exclusive"]))
        
        self.add_ui_property(UISliderProperty(self, "All Agents", start_value = 0.8, value_range=(0.0, 0.999), click_increment = 0.005))
        self.add_ui_property(UISliderProperty(self, "Blue Agents", start_value = 0.5, value_range=(0.0, 1.0), click_increment = 0.01))

        self.add_ui_property(UIDropDownProperty(self, "Game Type", starting_option = "Single-Peaked", options_list =  ["Single-Peaked", ">=Tau",">=Tau and <1", "Custom"]))
        self.add_ui_property(UISliderProperty(self, "Peak", start_value = 0.0, value_range=(0.01, 0.99), click_increment = 0.01))
        self.add_ui_property(UISliderProperty(self, "Tau", start_value = 0.0, value_range=(0.0, 1.0), click_increment = 0.01))
        self.add_ui_property(UITextProperty(self, "Custom U_i(frac) = ", text = "min(frac, 0.5)"))
        
        self.add_ui_property(UIDisplayValue(self, "Nash Equilibrium", lambda : "True" if self.game.NE else "False"))
        self.add_ui_property(UIDisplayValue(self, "Yellow", lambda : str(self.game.r)))
        self.add_ui_property(UIDisplayValue(self, "Blue", lambda : str(self.game.b)))
        self.add_ui_property(UIDisplayValue(self, "Empty", lambda : str(self.game.width*self.game.height - self.game.b - self.game.r)))
        
        
        self.game_type = "Single-Peaked"
        self.rebuild_ui()
    def update(self, time_delta):
        super().update(time_delta)
        self.rebuild_ui()
        for name, prop in self.properties.items():
            prop.update()
    
        self.game.set_grid_size(self.properties["Width"].get_value(), self.properties["Height"].get_value())
        self.game.set_torus_type(self.properties["Torus Type"].get_value())
        self.game.set_self_inclusive(self.properties["Neighborhood"].get_value() == "Self-Inclusive")
        self.game.set_agents(self.properties["All Agents"].get_value())
        self.game.set_blue_agents(self.properties["Blue Agents"].get_value())
        
        if self.game_type != self.properties["Game Type"].get_value():
            self.game_type = self.properties["Game Type"].get_value()
            if self.game_type == ">=Tau":
                self.game.set_utility_function(TauUtility(Fraction(self.properties["Tau"].get_value())))
            if self.game_type == ">=Tau and <1":
                self.game.set_utility_function(TauNoSegUtility(Fraction(self.properties["Tau"].get_value())))
            if self.game_type == "Single-Peaked":
                self.game.set_utility_function(SinglePeakedUtility(Fraction(self.properties["Peak"].get_value())))
            if self.game_type == "Custom":
                self.game.set_utility_function(CustomUtility(self.properties["Custom U_i(frac) = "].get_value()))
        
        if self.game_type == ">=Tau":
            if self.game.utility_function.tau != Fraction(self.properties["Tau"].get_value()):
                self.game.NE = False    
            self.game.utility_function.tau = Fraction(self.properties["Tau"].get_value())
        if self.game_type == ">=Tau and <1":
            if self.game.utility_function.tau != Fraction(self.properties["Tau"].get_value()):
                self.game.NE = False    
            self.game.utility_function.tau = Fraction(self.properties["Tau"].get_value())
        if self.game_type == "Single-Peaked":
            if self.game.utility_function.peak != Fraction(self.properties["Peak"].get_value()):
                self.game.NE = False    
            self.game.utility_function.peak = Fraction(self.properties["Peak"].get_value())
        if self.game_type == "Custom":
            if self.game.utility_function.code != self.properties["Custom U_i(frac) = "].get_value():
                self.game.NE = False    
            self.game.utility_function.code = self.properties["Custom U_i(frac) = "].get_value()
        
