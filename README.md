# Celestial Navigator for X-Plane

The aim of this project is to wholeheartedly bring celestial navigation into x-plane.
It aims to do this a number of ways:

1. provide an automatic connection between [x-plane](http://www.x-plane.com/desktop/home/) and [Stellarium](http://www.stellarium.org/)
   + provide plugin for Stellarium to do this
   + provide plugin for x-plane to do this
2. provide a sextant like tool as a plugin for Stellarium
3. provide an automated navigator, who can take sights, dead reckon, and is affected by the weather conditions.
   Idea is very much based on the fantastic navigation mods for Silent Hunter 5
4. provide weather effects for stellarium
5. provide a java libgdx application with:
   + map plotting tools
   + navaids from x-plane database
   + an easily accesible almanac
   + automatic connection with Stellarium's sextant plugin

The basis for network communication with stellarium is a protocol buffer, and udp sockets. 
his should allow other simulators such as fsx, p3d, silent hunter or any other game
or simulator to easily implement their own input into stellarium.

## Project Status

### Done:
+ Basic Plugin for x-plane
+ Basic Static Plugin for stellarium
+ Communication is working, and x-plane can successfully update Stellarium position and times

### Partial:
+ Libgdx application, have basic map working

### Todo:
+ automatic periodic position/time updates
+ Configuration files for x-plane
+ Configuration files for stellarium
+ Configuration ui for stellarium
+ make dynamic version of plugin and provide windows and mac builds
+ Sextant plugin for stellarium
+ automated navigator for x-plane
+ weather effects for stellarium
+ java application

## Credits
+ Heavily based on Joan Perez's Ground Services plugin.
+ Thanks to Sandy Barbour for his fantastic python interface for x-plane