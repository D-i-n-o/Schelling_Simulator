# Interactive Schelling Simulator
A schelling simulator with a build-in visual representation, very much like "The Parable of the Polygons".
It features an interactive setting panel, where the utility function can be changed on the fly. The `>=Tau and <1` utility function is like the standard tau model, except that any agent f_i = 1 has a utility of zero. To choose a custom utility function, select the type `Custom` and enter the formula that converts the fraction of same type agents `frac` to a utility in the custom function line. For example, we can write `abs(frac - 0.5)`.

Agents are activated in a random order and evaluate the potential jump targets in a random order as well (they take the first improving jump). 

To start the simulator, run `python main.py`.
 

# Requirements
- pygame
- pygame-gui

# Credits
Graphics from "The Parable of the Polygons" by Vi Hart and Nicky Case (public domain) https://github.com/ncase/polygons