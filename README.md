# Chick Coop Door
A project to control a chicken coop door based on a regular schedule (sunrise / sunset) or as required.
<img src="https://raw.githubusercontent.com/strangesast/chicken-cam/master/media/coop_door_in.png" height="300"/>
<img src="https://giant.gfycat.com/LonelyBreakableGoldenmantledgroundsquirrel.gif" height="300"/>

# Project Structure
## `arduino/`
Code to accept commands & report state of door based on polling 3 switches and L298N motor driver.  Configured for [ino](http://inotool.org/).
## `client/`
Angular project.  Schedule open/close and view history.
## `server/`
Python asyncio (aiohttp & aiosqlite) http server and polling loop.  Checks for requests and handles serial read / writes via ser2net.  Can be configured to schedule (via cron) open / close based on seasonal sunrise / sunset.  Main loop configured as systemctl service.
## `temp-monitor/`
Old temperature monitoring and graphing code
