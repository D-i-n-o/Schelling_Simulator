# Interactive Schelling Simulator
A schelling simulator with a build-in visual representation, very much like "The Parable of the Polygons".
It features an interactive setting panel, where the utility function can be changed on the fly. The `>=Tau and <1` utility function is like the standard tau model, except that any agent f_i = 1 has a utility of zero. To choose a custom utility function, select the type `Custom` and enter the formula that converts the fraction of same type agents `frac` to a utility in the custom function line. For example, we can write `abs(frac - 0.5)`.

Agents are activated in a random order and evaluate the potential jump targets in a random order as well (they take the first improving jump). 

To start the simulator, run `python main.py`.
 

# Requirements
- pygame
- pygame-gui

# Credits
- Graphics from "The Parable of the Polygons" by Vi Hart and Nicky Case (public domain) https://github.com/ncase/polygons
- Lars Seifert, who wrote the simulator for his master thesis on [Single-peaked Schelling Games](https://hpi.de/friedrich/publications/2023/Document/puma-friedrich/2302.12107.pdf/1d7f23e9b0503577203b37e9eca62e2e.html?tx_extbibsonomycsl_publicationlist%5Baction%5D=download&cHash=cb031c483e0161814a3de4c1b3302b3a)
