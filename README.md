# portainer_listing

This component was created by GPT-4 over 3 2-hour sessions.
The component does exactly what I needed/wanted and it is quite likely to fall far short of what you were hoping for - so take it, extend it - and then re-share it!  This was just an experiment for me to see if I could convince GPT-4 to create a basic custom component that works without having to write a single line of code.  It's not something that I plan to support, extend or develop further - but if it is useful to you, take it and do with it as you will.

A very simple Home Assistant custom component to query a portainer server for a list of containers

I have Portainer running on my NAS, 2 Raspberry Pi's and 2 Debian VM's and I was finding it hard to remember what containers were running on which servers - so I searched for a Portainer integration.  I found one that seemed pretty robust but looked like it was only intended to interact with a single Portainer server co-existing with Home Assistant - and I think it was also marked as deprecated?

In any case, I needed something simpler, but that could work with multiple servers.  All I really wanted was to see what containers were on each server and if they were running or stopped, but I didn't have the first clue as to how to build a custom integration - so I reached out to GPT4 and explained what I wanted - and after 2.5 days of testing auto-generated code and going back and forth with GPT-4, it finally provided an __init__.py, a manifest.json and a sensor.py file that do what I need!

This may not be useful to anyone other than me - and I don't have time to make it more robust or document it - but on the off chance that someone else wants to take it further, I'll attach my files here.

This post isn't so much a "look at the great component I created", but more of a "Holy Crap! I used GPT-4 to build a working custom component without having to write a single line of code!!!"

I don't need any credit or attribution for this.  If it's useful to you - take it.  If not, ignore it.  

But just know that it **IS** possible to get GPT-4 to create a working custom component if you have the patience to go back and forth with it for a day or two.  I've also used ChatGPT3.5 to configure some Lovelace multi-entity cards for me since I was too lazy to look up the documentation for it.

When you're trying to understand some of the Home Assistant documentation - that doesn't have any examples - just paste it in to ChatGPT and ask it to generate some examples for you!  I've only been doing it for a couple of days so far - but I already find it a huge time saver.

It's configured by adding
sensor:
    - platform: portainer
      url: http://192.168.1.15:9000
      name:  nas15
      username: !secret port_user
      password: !secret port_pass
    - platform: portainer
      url: http://192.168.1.10:9000
      name: pi10
      username: !secret port_user
      password: !secret port_pass

And it creates a sensor for the server itself, named sensor.portainer_server_<servername> and then a sensor for each container on the server, named sensor.portainer_<servername>_<containername>.  Each sensor has several extra attributes such as how long it's been running, what image it's running, and the url to quickly get to that server.

The Dashboard was created usign the auto-entities card from HACS.  I included my dashboard code in a file named dashboard.yaml but it won't work unless you first install the auto-entities component.  https://github.com/thomasloven/lovelace-auto-entities

<img width="1409" alt="Screen Shot PortainerServers" src="https://user-images.githubusercontent.com/33942031/229692431-ba636ff8-bb5c-4f0e-a6cb-523efbc81619.png">
<img width="1072" alt="Screen Shot Portainer Server" src="https://user-images.githubusercontent.com/33942031/229692468-cc57ecb0-b47c-4546-8496-883fd7b76cdf.png">
<img width="1073" alt="Screen Shot Portainer Container" src="https://user-images.githubusercontent.com/33942031/229692495-32fc7b0d-2ad6-41cc-aa0c-9f7846790dd1.png">

There are only 3 files required.  
Copy them into a folder named 'portainer' under your 'custom_components' folder, restart Home Assistant and then add the settings into configuration.yaml 
- I've only tested this with HTTP.  It may need some tweaking to work with HTTPS portainer servers.

