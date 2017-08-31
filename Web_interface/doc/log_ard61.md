# GM2 log - Antoine

### Thursday 11 May

Morning meeting - met with all the participants. Understood - more or less - what the current hardware and software does. 

Currently, there is:
* A Raspberry Pi 3, with software and a GUI that can scan the whole microscope table
* A custom motors board to control the motors
* An Arduino to control sensors and LEDs

Discussed what we would be working on: there was a multitude of proposals - sigh ... cf my notes for all of that

We finally did converge - I think? - to streaming the camera output to a web-page, and being able to control the microscope through a web-interface (hence not worrying anymore about the internal workings inside the Raspberry Pi).

And agreed to a further meeting on Saturday 3:30pm BST. Not sure what we will discuss there: we're expecting a demo of the current kit, and an introduction to the software? It would be helpful if we could finalise in broad terms what we will be working on. 


### Monday 15 May

Converged on the features we'll want at the end of the project, and fleshed out the different components we'll need to achieve them. We decided that our end-goal, to be able to control the microscope and view its output from an external device, can be split off into two groups, one focusing on the interface between the Raspberry Pi and the motors & sensors, the other focusing on the interface between the Raspberry Pi and the external device. 

The precise goals were documented in [here](https://docs.google.com/document/d/1QzkXOdFrkiqjfj2YdRiPwxmbORR5bd-4i0nzOWeweW4)

Since the project proposal is due on Thursday, we have also discussed how we would proceed for that presentation. After consulting with Alexandre Kabla, the only written document will be on costing and parts needed - all the other items on the list will be delivered orally. 

Fergus gave us a Raspberry Pi camera we'll use - many thanks to him!

Followed the tutorial [here](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/) and configured the Raspberry Pi as a WiFi hotspot.

We agreed on how to split off the project proposal presentation. 

*	Kai Song and William will present the context, the problem that we're solving, and describe the solution that we plan to deliver, and it's meant to be used. 

*	Akhass will give a presentation of the technical plans to build the hardware - RPi interface.

*	I'll be explaining the design of the Raspberry Pi - External Device interface, as a step towards our feature of being able to view and control the microscope from the external device (also including contingency plans such as what happens if there are latency/bandwidth issues with streaming video). 

	Definitely I want to talk about our AGILE approach to getting features out, and also propose a rough design based on my internship experience last year (things might turn out slightly different as I investigate Flask/streaming). 

	I will also present a mockup of the website which will help us get feedback for our design - which I've started [here](https://app.moqups.com/ard61/7ybYBf96FC/view). 

	I'm planning to do all of this before we meet on Wednesday to rehearse for our Thursday presentation and gather feedback.


William's done the risk assessment sheet, awesome! And he'll do the costing sheet too. 
Kai Song got the Raspberry Pi camera to work, using the raspistill and raspivid tools. 

#### So, the next things to do for me are:

Prepare my part of the project proposal:
*	get familiar with the different intermediate targets / maybe flesh them out a bit more, think where they could fail, think about the time each would take.


### Wednesday 17 May

Morning: Created a Trello board for our project to help with AGILE project management. In the 'backlog' list, I broke out intermediate steps that I'd like to achieve to go towards the project goals. 
Afternoon: Met with the team to prepare the project proposal document and presentation. 


### Thursday 18 May

Morning pitch to Alexandre Kabla and Lara Allen. Feedback consisted of three items:
*	Be more precise about the project timeline and explicitly explain that since we are following an AGILE project management technique, we have not set out a detailed roadmap that will bring us to the end-result, given that we cannot predict all the contingencies right now. Rather, we will focus on short-term features. 
*	Make clear who the intended user is, and describe his activity
*	In the risk assessment, evaluate the risk that the components/libraries we use might become obsolete.

Afternoon:

Discussed with Kai Song what our next target would be and organised ourselves on Trello (tasks and time estimate). We decided that we'll focus on getting streaming working for the interim presentation. Our first step is to investigate different streaming methods, and then shortlist with 2 solutions. We will then implement and compare the 2 solutions in the next week. 

I documented my research in [doc/streaming_research_ard61.md](https://github.com/ard61/gm2-waterscope/blob/master/doc/streaming_research_ard61.md) The two solutions we shortlisted are Motion JPEG and WebRTC. 

Next steps would be to do further research into these two solutions, maybe try some tutorials - I'll definitely follow the WebRTC tutorial. And then it would be nice to write a document comparing the two. 

Although we clearly have split off work individually, I'm thinking it would still be nice to work together, for morale :) and also to give each other help and discuss difficult decisions.


### Monday 22 May

Morning and afternoon: 

Continued work on implementing streaming to a webpage using GStreamer. After searching for tutorials throughout the internet, I finally found [this](https://schneide.wordpress.com/2015/03/03/streaming-images-from-your-application-to-the-web-with-gstreamer-and-icecast-part-1/) which describes how to send video from GStreamer to an HTTP streaming server called Icecast. I tried implementing what they described, and hooray, I can stream video from GStreamer's testvideosrc to a webpage. Unfortunately, once I try streaming from my webcam, v4l2src, the video is really choppy, takes ages to load, and crashes after a few seconds. Seems that HTTP streaming is a pretty bad option. 

In fact, I'm having doubts on the whole idea of taking video from the Pi Camera, piping it to GStreamer and displaying it on a web page. GStreamer - if I can get it to work - will only handle the media side. I would then need to integrate this myself with some form of signaling, that controls GStreamer, telling it to start/stop, recover from errors, etc. If I had two weeks full-time to work on this I'm fairly confident that I could get it working. But it's just not going to happen before next Tuesday.

We'll meet on Thursday and this will be a good time to discuss how we follow on. 


Kai Song got the Motion-JPEG solution working! It has a latency of ~1s and a frame rate of ~2fps which is definitely not very comfortable to look at. We'll need to discuss what to aim for. 


### Thursday 25 May

Morning: 

Alexandre explained in detail what he's looking for in the interim presentation. Here are my notes:
*	It should be 10-15 minutes of technically-focused presentation - no context needed.
*	Present a working prototype
*	Describe technical choices, explaining what worked and what didn't work, and why. 
*	Reflect on the timeline: how we envisaged it and what unexpected things made us change our plan
*	Referring to the first presentation, explain which technical and 'soft' skills we learnt.

Also, Lara gave advice on presenting: talking slower, and making sure not to trail off at the end of a sentence.


We then discussed with Alexandre, Lara and Fergus the intermediate and long-term goals for our project. 

The first subject was the motors and motor boards. Up to now, Akhass and William had been working on transforming unipolar motors to become bipolar ones. Alexandre was a bit concerned because he saw this transformation as 'hacky' and perhaps not sustainable in an actual production context. From the discussion, I understood that the CNC shield software and/or hardware does not support unipolar motors. 

There seem to be several alternatives to me, each with its pros and cons:
*	Transforming the unipolar motors to bipolar motors (i.e. rewiring them) and connecting them via the CNC shield and Arduino. This is what Akhass and William have been working on up to now. Pros: it means we can use GRBL, and the motors are ideal for our application (good form factor, low power, high speed). Cons: this transformation needs to be done manually, depends on the internals of the motors (which are susceptible to change without notice), and hence is likely not sustainable in a production context.
*	Reverting to use the 'fergboard' to control the motors. Pros: Tried and tested. We get all the advantages of the motors without having to transform them. Cons: the 'fergboard' is less configurable - and would also need to be mass-produced for deployement: would that cost more or less than rewiring the motors? Also, an Arduino is needed anyway for sensor interfacing and the incubator, so using the 'fergboard' wouldn't eliminate the Arduino.
*	Changing the motors: using bipolar motors with the CNC shield and Arduino. It seems to me this option has been slightly overlooked. Pros: Uses 100% off-the-shelf components and (in principle) shouldn't need much tweaking. Cons: Fergus says the available bipolar motors are unsuited to our application (this might warrant some research).
*	Finally, another potential option I can think of is to use the CNC shield and Arduino with the unipolar motors, but using another software to control them than GRBL. Pros: Use the good motors with the good board. Cons: Is there any such software that works? If not, it is probably unfeasable to adapt one ourselves. 

For the interim presentation I understand that Akhass and William will look into implementing options 1 and 2 and evaluating their feasibility.

The second subject was on the web interface. 

For our interim presentation, we will be focusing first on demonstating streaming from the Raspberry Pi to an web-page on an external device. If possible, Alexandre would also like a demonstration of controlling behaviour on the Raspberry Pi from the website. 

I raised the question of whether it makes sense to set as a target to have a beautiful and user-friendly UI. Lara and Alexandre's response was mixed: the main aim of the project is first of all to develop the technology and explain the methodology to reuse it. On the other hand, it also is clear to all of us that a crucial factor in the adoption of a product is its ease of use: hence, if we create a beautiful and user-friendly UI, it might have a great impact, both as something WaterScope can demonstrate, and something they can reuse when they launch their product. 

In the end, this is something that we need to discuss with WaterScope:
*	How useful a UI would be for them and what sort of UI they would be looking for
*	If we are to build a UI, they need to describe precisely who the user will be.


Finally, I discussed with Kai Song our work for the next few days. 
*	Kai Song will be extremely busy until tomorrow (Friday).
*	We agreed to continue forward with streaming using Motion-JPEG only. 
*	I will briefly describe what I tried with GStreamer during the interim presentation, and why we have decided not to go forward with it.
*	We want to improve the latency and framerate of the Motion-JPEG solution.
	*	For this we need to find bottlenecks and solve them.
	*	We also need to work with specifications: say what latency and frame rate is good enough, and say 'done' when we've got that. For this, we need to ask WaterScope what they need; the acceptable latency is likely linked to the motor speed in the final product (if the user spends his time waiting for motors to move, it doesn't matter if he waits for 0.5 seconds extra). 
*	We also want to proof-of-concept sending an instruction from the webpage to the server, and perhaps controlling a LED with it. Kai Song has proposed figuring out how to control a LED on the Arduino from the Raspberry Pi. I have the feeling that's effort spent on something unnecessary; just displaying something in a terminal when an instruction arrives would be good enough for me.

One thing that I'm wondering but I forgot to bring up is whether she has documented her work setting up Motion-JPEG. 

So, the next things for me are:
*	Documenting my efforts with GStreamer
*	Sending an instruction from a webpage to a webserver using Flask (i.e. getting back in the bath with Flask).
*	Start work on the interim presentation.
*	Then, I'll look into what I can do about Motion-JPEG.
