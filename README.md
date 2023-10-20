This repository is dedicated to the editing of Psalter hymns, including their original intros 
and outros, with the ability to specify the desired number of verses. All the Psalter hymns 
available here are those used by the Reformed Protestant Church in their worship services every 
Lord's day.


To run this application, simply clone this repository, navigate to the 'dist' folder, then access
the 'box' folder and execute the 'box.exe' file located on your desktop. All the files within that 
folder are essential for the proper functioning of the application.

If necessary, you have the flexibility to adjust the main code within 'box.py' for configuration 
changes.

I uploaded the 'segments.ipynb' and 'scrape.py' so you can see how I scraped the audio data from the 
website. Inside 'scrape.py,' you'll find functions that split the audio to extract segments for the 
intro sound, outro sound, and verses.

I have input all the necessary data into the 'stanzas.db' database, which is required to determine 
the maximum number of verses that can be combined for a specific psalter hymn.
