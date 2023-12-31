# Overview

This project aims to help with language learning by utilizing Optical Character Recognition to extract the subtitles from the "Easy Languages" YouTube channel. The extracted
information is stored and organized, allowing users to easily search for specific words and understand the context through English translations.

# How it Works

**Subtitle Extraction:**

The videos which we want to extract the subtitles from are downloaded as mp4 files and moved to the folder "videos". OCR is later applied to extract the subtitles.

**Word Information Storage:**

From the extracted subtitles the individual words are read. Each word stores information about the word itself and the timestamps of all its occurrences across all videos.

**Search Functionality:**

After all videos have been processed and the subtitles extracted, the system stores all unique words on a map. Since each word saves information about all its appearances
across all videos, we can access any appearance by going to the exact video and frame in which it appears. That frame will show a sentence in which the word is used and
also the translated sentence below.

# Example

https://github.com/XaviMV/easy-french-practice/assets/70759474/a6efad7f-2655-49c6-998e-079e4f125c5c

I have only processed French videos but this code should work with any language as long as it is supported by paddleOCR.

The total processing time for about 180 videos, each from 5 to 10 minutes long, with multithreading enabled, was about 16 hours on a Ryzen 5 2600x CPU. But this process
only needs to run once to collect all the information needed and store it in a way that can later be read much faster.

Since all the videos are about 12GB in size I can't upload them to github. They would need to be downloaded and each put in a numbered folder inside the folder "videos".

# Requirements

To run the processing of the videos the following libraries are required: cv2, numpy, os, multiprocessing, paddleocr.

To simply use the word finding functionality the libraries needed are: os, cv2, streamlit.
