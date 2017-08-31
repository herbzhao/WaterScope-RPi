## Streaming - Antoine's research


### A few streaming technologies I found

#### 'Hacky' solutions
*	Motion JPEG: encode the video as a stream of images, sent individually.  
	*	Can be done using Flask - cf [Miguel Grinberg blog](https://blog.miguelgrinberg.com/post/video-streaming-with-flask)
	*	Or mjpeg-streamer - cf [Miguel Grinberg blog](https://blog.miguelgrinberg.com/post/stream-video-from-the-raspberry-pi-camera-to-web-browsers-even-on-ios-and-android)
	*	Or RPi-Cam-Web-Interface (choice of apache/nginx/lighttpd) - cf [elinux website](http://elinux.org/RPi-Cam-Web-Interface)
		*	Is said to work beautifully, with good resolution and low latency. However there seems to be latency before capturing photo or video. 
		*	We could reuse many parts of their project!

*	Netcat a raw H.264 stream and read it from a compatible media player e.g. MPlayer- see [the RPi blog](https://www.raspberrypi.org/blog/camera-board-available-for-sale/)  
	*	Any browser support? Is it possible to embed an open source media player plugin in a browser? -> here it's a raw TCP stream, can we make it HTTP so a browser can receive it?
	* 	Might need some complicated setup
	*	Not sure it'll recover from errors well either.

#### State-of-the art streaming standards
It seems there are 3 commonly-used standards for adaptive streaming i.e. changing the bitrate to adapt to fluctuating network conditions: HLS (HTTP Live Streaming), MPEG-Dash and RTMP - see [this report](https://developer.jwplayer.com/articles/html5-report/#adaptive-streaming). HLS and MPEG-Dash are natively supported by HTML5 whereas RTMP requires a Flash plugin which is becoming deprecated (and isn't open source). 

*	HTTP Live Streaming - made by Apple  
	*	This [gist](https://gist.github.com/chrislavender/cad26500c9655627544f) explains
	*	Browser support table [from JWPlayer website](https://developer.jwplayer.com/articles/html5-report/adaptive-streaming/hls.html)

*	MPEG-Dash
	*	[Wikipedia article](https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP)

#### Ready-made solutions that implement these technologies

*	HTML5 video streaming  
	*	[StackOverflow](http://stackoverflow.com/questions/40045857/live-video-streaming-with-html-5) it mentions that two ways to stream the video are MPEG-Dash and HLS (HTTP Live Streaming). Also provides some useful links. 
	*	W3CSchools documentation for [HTML](https://www.w3schools.com/html/html5_video.asp) and [JavaScript](https://www.w3schools.com/tags/ref_av_dom.asp)

*	WebRTC - Open Source APIs for streaming media from server to browser  
	*	This was the library we were recommended to use at the company hackathon during my internship last summer.
	*	cf [official website](https://webrtc.org/)
	*	and [tutorial](https://codelabs.developers.google.com/codelabs/webrtc-web)


### How should we compare the technologies?
*	Latency (average and maximum)
*	Resolution
*	Can it stream well for a long time (i.e. not error-prone)?
	*	What would be an acceptable frequency of error?
*	Robustness - can it recover gracefully from errors?
	*	Ideally just reloading the webpage would solve the problem, or not even having to. 


### Notes on implementing streaming

Ok. So for streaming to happen we need 2 things:
*	Signaling: At the most basic level, it's telling the server to start/stop sending data. But it could also involve exchanging information such as addresses and media capabilities.
*	Media: Server-side, we need to take the video from the RPi camera, encode it, payload it into chunks, send those chunks over the network (this doesn't need to be done by an actual server if we have a signaling server to control the media flow on-the-fly.) Client-side, we need to receive those chunks, reconstruct and decode the video, and display it. 
	*	For signaling, we can probably do away with any kind of web server, though preferably one that talks the same language as the client's signaling side. Also we want the signaling server to configure the media flow so a way to have live configuration would be awesome. This seems to be possible using [GStreamer's Python bindings](http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.pdf)
	*	For media, we need something that can take the video from the RPi camera, encode it into some sort of codec, payload it and send it via RTP. Ideally it would be easily configured on-the-fly i.e. without restarting the whole pipeline. And then we need the media stream to be decoded by the client. 
		*	The obvious candidate for this is GStreamer. Here are 2 tutorials explaining the server-side picture (but not the web-client side): [this](http://www.einarsundgren.se/gstreamer-basic-real-time-streaming-tutorial/) and [this](http://www.z25.org/static/_rd_/videostreaming_intro_plab/) and finally [this tutorial explaining how to combine with raspivid](http://www.raspberry-projects.com/pi/pi-hardware/raspberry-pi-camera/streaming-video-using-gstreamer)
		*	Apparently there are resolution problems when attempting to access Pi camera video from a browser, see [this thread](https://www.raspberrypi.org/forums/viewtopic.php?f=43&t=137549). So using getUserMedia() to obtain video is precluded. 
		*	Another option is to use HTTP instead of RTP - does that increase latency and complexity though? 2 articles explain this: [using a custom HTTP server](https://coaxion.net/blog/2013/10/streaming-gstreamer-pipelines-via-http/) and [using icecast](https://schneide.wordpress.com/2015/03/03/streaming-images-from-your-application-to-the-web-with-gstreamer-and-icecast-part-1/)


### Compte-rendu: Why I decide to abandon using GStreamer

GStreamer seemed a compelling choice for streaming video to a webpage, because it is inherently fast, being written in C, and has a modular pipeline architecture that makes it easy to take video from the camera, encode it, chunk it and send it through a network interface. However, the encoding algorithms I was considering to use are designed to reduce bandwidth at the cost of latency, and are hence not adapted to our use-case, where bandwidth on the WiFi network between the Raspberry Pi and the external device is more than sufficient, and latency is at a premium. When trying to implement sending video to a webpage using GStreamer, I indeed found that the received video intermittently paused. Hence, it makes sense to stick with the Motion-JPEG streaming option that Kai Song has been implementing. 


