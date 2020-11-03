# Libri Speech Files Parser

This is part of speech rate measure project.

This code can be used to parse libri-speech data for speech measure project.

This code allows to separate each audio file according to vowels mentioned in it's
corresponding alignment file.

## Installation instructions

* Python 3.6+
* librosa
* pydub
* soundfile
* pathlib
* shutil
* Download the code:
```
	git clone https://github.com/Jenny-Smolensky/LibriSpeechFilesParser.git
```


## Data

You should specify two folder paths: folder for audio files, and folder for alignment
TextGrid.files.

Both folders should contain same structure, each .flac/.wav file should have
.TextGrid file in same relative path in alignment folder.


All files were downloaded from: LibriSpeech ASR corpus- http://www.openslr.org/12/

Example provided: 
```
sample_data_libriSpeech
├───alignment
│   ├───4088
│   │   ├───158077
│   │   │       4088-158077-0000.TextGrid
│   │   │       4088-158077-0001.TextGrid
│   │   │       4088-158077-0002.TextGrid
│   │   │
│   │   └───158079
│   │           4088-158079-0000.TextGrid
│   │           4088-158079-0001.TextGrid
│   │           4088-158079-0002.TextGrid
│   ├───4406
│   │   ├───16882
│   │   │       4406-16882-0000.TextGrid
│   │   │       4406-16882-0001.TextGrid
│   │   │       4406-16882-0002.TextGrid
│   │   │
│   │   └───16883
│   │           4406-16883-0000.TextGrid
│   │           4406-16883-0001.TextGrid
│   │           4406-16883-0002.TextGrid
└───audio
    ├───4088
    │   ├───158077
    │   │       4088-158077-0000.flac
    │   │       4088-158077-0001.flac
    │   │       4088-158077-0002.flac
    │   │
    │   └───158079
    │           4088-158079-0000.flac
    │           4088-158079-0001.flac
    │           4088-158079-0002.flac
    │
    ├───4406
    │   ├───16882
    │   │       4406-16882-0000.flac
    │   │       4406-16882-0001.flac
    │   │       4406-16882-0002.flac
    │   │
    │   └───16883
    │           4406-16883-0000.flac
    │           4406-16883-0001.flac
    │           4406-16883-0002.flac


```

## Params

In the main function there are options to choose audio and alignment paths.

In the main function choose one of three options to parse files by:

* by_phoneme -  the files will be created in a way in which each file contains
	one vowel only.
	A created file will be in folder named as the vowel in it.

* by_interval - the files will be created in a way in which each file will be 
	0.5 second long (you can change this parameter).
	Each .wav file will be created with .wrd file that mentions the vowels in the audio
	and relative time in frames. 
	The audio files will be in folders, so that the most common vowel in the audio file 
	is the name of the folder.
	(for training model2 - yolo hybrid)
	
* by_counter -  the files will be created in a way in which each file will be 
	0.5 second long (you can change this parameter).
	The audio files will be in folders, so that each folder name will point the number
	of vowels in the audio files in it.
	(for training model1- multiclass)


do this by changing "extract_method_chosen" to one of above.

## dataToFolders
```
This code divides parsed files in given structure:

├───path
    │   ├───folder1
    │   │       file (wav / wav + wrd)	
    |   ├───folder2
    │   │       file (wav / wav + wrd)
    |   ├───....
    │   │       

into structure:

├───test
│   ├───folder1
│   │       407.wav (wav / wav + wrd)	
│   │
│   ├───folder2
│   │       858.wav (wav / wav + wrd)	
│
├───train
│   ├───folder1
│   │       1023.wav (wav / wav + wrd)	
│   │       1059.wav
│   │
│   ├───folder2
│   │       1148.wav
│   │       1314.wav
│   │       1523.wav
│   │       1597.wav
│
└───valid
    ├───folder1
    │       682.wav
    │       746.wav
    │
    ├───folder2
    │       1496.wav
    │       394.wav
```
You can specify source_path and destination path.

The folder with the smallest amount of files (source_path) defines the size of
all destination folders. 
Train will contain 80% of files, valid and test 10%.
The split is random.

## Authors

**Almog Gueta** ,  **Jenny Smolensky** 

