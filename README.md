# OpenCV-projects
This Repository Consists of various python projects utilizing OpenCV

# Files

**FaceRecognition**: face detection used to track attendence for a class

When run for the first time will create the subsequent files:
* Faces: Folder for storing faces
* data.npy: numpy array for storing encoded facial features
* MarkTime.csv: storing the marked time and face upon first recognition
* NameList.txt: store the name associated with the facial features in data.npy

**VirtualMouse**: hand tracking and certain gesture detection

HandTrackingModule.py implements the following functions:
* virtual mouse: moving, selecting, clicking
* Hide desktop
* Take a screen shot and store it as a PNG file
* Control volume 

**Jarvis**: Onging virtual Assistant

On going project that seeks to combine the above functions and others to create a virtual assistant
Currently able to implement the following functions through incorporating various apis:
* Speech to text commands and text to speech replies
* Open and search for websites 
* Get the latest news from https://news.google.com/news/rss
* Wikipedia information
* Tell terrible jokes
* Tell the weather
* Analysis user sentiment
* Return answers for basic user arithmetic
