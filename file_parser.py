import glob
import os
from os.path import exists
from os import makedirs
from pathlib import Path
import soundfile as sf
from pydub import AudioSegment
import librosa


class AudioFileConverter:

    @classmethod
    def convert_to_wav(cls, src_file_path, dst_path):
        """
        converting audio file to wav five
        :param src_file_path: file to convert
        :type src_file_path: string
        :param dst_path: file path and name to save converted file to
        :type dst_path: string
        :return: none
        :rtype:
        """
        data, sample_rate = sf.read(src_file_path)
        sf.write(dst_path, data, sample_rate, format="wav")

    @classmethod
    def folder_flac_to_wav(cls, audio_files_path, destination_path):
        """
        convert folder tree to same tree, but change each .flac with .wav
        :param audio_files_path: root tree path
        :type audio_files_path: string
        :param destination_path: new tree path
        :type destination_path: string
        :return: none
        :rtype:
        """

        for root, dirs, files in os.walk(audio_files_path):
            for file in files:
                if not file.endswith('.flac'):
                    continue

                audio_flac_path = os.path.join(root, file)
                dst_path_current = destination_path + audio_flac_path.replace(audio_files_path, "")
                # create path if not exists
                Path(dst_path_current.replace(file, "")).mkdir(parents=True, exist_ok=True)
                # create wav file path
                dst_path_current = dst_path_current.replace("flac", "wav")
                # convert to wav
                AudioFileConverter.convert_to_wav(audio_flac_path, dst_path_current)

    @classmethod
    def delete_wav_files(cls, path, delete_root=True):
        """
        safely delete all wav files
        :param path: root folder
        :type path: basestring
        :param delete_root: indicates if delete the folder, in addition to files
        :type delete_root: bool
        :return: none
        :rtype:
        """
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.wav'):
                    os.remove(os.path.join(root, file))
        if delete_root:
            import shutil
            shutil.rmtree(path)


class FileParser:
    files_dict = {}

    def __init__(self, vowels=None):
        if not vowels:
            self.vowels = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'OW', 'OY', 'UH', 'UW', 'IH', 'IY']
        else:
            self.vowels = vowels

    @classmethod
    def wav_splitter(cls, original_wav, start, end, destination_file):
        """
        split wav file by given times
        :param original_wav: audio file path
        :type original_wav: basestring
        :param start: start time for cut in milli seconds
        :type start: int
        :param end: end time for cut in milli seconds
        :type end: int
        :param destination_file: new file
        :type destination_file: basestring
        :return: none
        :rtype:
        """
        audio_file = AudioSegment.from_file(original_wav)
        audio_file = audio_file[start:end]
        audio_file.export(destination_file, format="wav")  # Exports to a wav file in the current path.

    @classmethod
    def silence_padding(cls, original_wav, start, end, padding, destination_file):
        """
        split wav file from start to end time and add silence after
        :param original_wav: file to cut
        :type original_wav: basestring
        :param start: start time from original wav - in milli seconds
        :type start: int
        :param end: end time from original wav - in milli seconds
        :type end: int
        :param padding: additional silence required - in milli seconds
        :type padding: float
        :param destination_file: path to destination file
        :type destination_file: basestring
        :return: none
        :rtype:
        """
        audio_file = AudioSegment.from_file(original_wav)
        audio_file = audio_file[start:end]  # cut from start to end
        silence = AudioSegment.silent(duration=padding)
        audio_file = audio_file + silence  # add silence after end
        audio_file.export(destination_file, format="wav")  # Exports to a wav file in the current path.

    @classmethod
    def file_path_generator(cls, dst_folder, phoneme, extension=""):
        """
        This function generates the next file name, according to numeric increasing order
        :param dst_folder: root folder to generate new file name at
        :type dst_folder: basestring
        :param phoneme: sub folder name
        :type phoneme: basestring
        :param extension: get the last numeric name in the folder sorting by file type
        :type extension: basestring
        :return: file path
        :rtype: basestring
        """

        new_index = 0
        folder_path = dst_folder + "\\" + phoneme  # get folder path

        if not exists(folder_path):  # case folder doesn't exists
            makedirs(folder_path)  # create new folder path
            cls.files_dict[folder_path] = 0  # create new key in the dictionary
            return folder_path + "\\" + str(0) + extension  # return path and file name zero
        else:
            if folder_path in cls.files_dict:  # check if folder is in the dictionary
                val = cls.files_dict[folder_path]  # get last index
                val += 1  # increase
                cls.files_dict[folder_path] = val  # update dictionary
                return folder_path + "\\" + str(val) + extension  # return path and new file name
            else:
                # folder not in the dictionary - goes to file system
                list_of_files = glob.glob(folder_path + "\\*" + extension)  # * means all if need specific format
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)  # check largest number of file names
                    import ntpath
                    latest_file = ntpath.basename(latest_file).split(".")[0]
                    if latest_file.isdigit():
                        new_index = int(latest_file) + 1
                cls.files_dict[folder_path] = new_index  # add folder to dictionary
                return folder_path + "\\" + str(new_index) + extension  # return folder path and new index file name

    @classmethod
    def write_to_wrd(cls, phonemes_list, wrd_file):
        """
        write phonemes to wrd format file line by line
        :param phonemes_list: to write to file
        :type phonemes_list: list
        :param wrd_file: destination file
        :type wrd_file: basestring
        :return: none
        :rtype:
        """

        file = open(wrd_file, "w")
        lines = []
        for item in phonemes_list:
            # sample rate 16000 (milli sec to sr)
            start_wrd = item['start'] * 16
            end_wrd = item['end'] * 16
            start_wrd = round(start_wrd)
            end_wrd = round(end_wrd)
            # create string
            str_to_file = str(start_wrd) + " " + str(end_wrd) + " " + item['phoneme'] + "\n"
            # write to file
            lines.append(str_to_file)

        file.writelines(lines)
        file.close()

    @classmethod
    def get_phonemes_in_interval(cls, phonemes_list, start, end):
        """
        This function get sub list from given list which contains phonemes in specified interval.
        If half or more from the phoneme in the given interval, will return it.
        :param phonemes_list: list of phonemes in different times
        :type phonemes_list: list
        :param start: start of interval in milli seconds
        :type start: int
        :param end: end of interval in milli seconds
        :type end: int
        :return: sub list of phonemes
        :rtype: list
        """

        sub_list = []

        for item in phonemes_list:

            if item['start'] > end:  # out of range
                return sub_list

            if item['start'] >= start and item['end'] <= end:  # in range
                sub_list.append(item)
                continue

            duration = item['end'] - item['start']
            # check case in which ends out of range, but most of the phoneme in range
            if item['start'] >= start and item['start'] + 0.5 * duration <= end:
                sub_list.append(item)

            # check case in which starts out of range, but most of the phoneme in range
            if item['end'] <= end and item['end'] - 0.5 * duration >= start:
                sub_list.append(item)

        return sub_list

    def extract_phonemes(self, text_grid_file):
        """
        Extracting phonemes from text grid
        :param text_grid_file: text grid file (librispeech alignment format)
        :type text_grid_file: basestring
        :return: list of items: start phoneme time, end phoneme time, phoneme name
        :rtype: list
        """
        text = open(text_grid_file, 'r')
        extracted_list = []

        # read until get to phonemes section
        while True:
            line = text.readline()
            if line.__contains__("phones"):
                break
        # read until get to size section
        while True:
            line = text.readline()
            if line.__contains__("size"):
                break
        # get size
        size = int(line.split("size = ")[1])

        for interval in range(size):
            # read one interval
            text.readline()
            x_min = float(text.readline().split("xmin = ")[1]) * 1000  # milli sec
            x_max = float(text.readline().split("xmax = ")[1]) * 1000  # milli sec
            txt = text.readline().split("text = ")[1].split('"')[1]

            # combine phonemes with same name and different number
            if txt.endswith("1") or txt.endswith("2") or txt.endswith("0"):
                txt = txt[:-1]
            # remove phonemes not specified
            if txt not in self.vowels:
                continue

            current = {'start': x_min, 'end': x_max, 'phoneme': txt}  # create item
            extracted_list.append(current)  # add to list

        return extracted_list

    def cut_file_by_phonemes(self, audio_file, txt_file, destination_folder):
        """
        Divide wav file with text grid alignment to multiple files according to phonemes.
        :param audio_file: audio file to extract data from
        :type audio_file: str
        :param txt_file: Text grid file to extract data from
        :type txt_file: str
        :param destination_folder: root folder for output files
        :type destination_folder: str
        :return: none
        :rtype:
        """

        # get phonemes list from Text Grid file
        extracted = self.extract_phonemes(txt_file)

        for item in extracted:
            start_time = item['start']  # Works in milliseconds
            end_time = item['end']
            phoneme = item['phoneme']

            # generate file name for phoneme, create sub only containing the phoneme
            destination_file = FileParser.file_path_generator(destination_folder, phoneme, '.wav')
            FileParser.wav_splitter(audio_file, start_time, end_time, destination_file)

    def cut_file_by_interval(self, audio_file, txt_file, dst_folder, interval=500):
        """
        create from given audio file and it's alignment text file sub files:
        each audio sub file in give interval length,
        add for each audio file: wrd file with phonemes in it's interval.
        :param audio_file: original audio file
        :type audio_file: str
        :param txt_file: Text grid alignment to the audio file
        :type txt_file: str
        :param dst_folder: root folder to save files to
        :type dst_folder: str
        :param interval: time in milli seconds
        :type interval: int
        :return: none
        :rtype:
        """
        # get phonemes from text grid file
        phoneme_list = self.extract_phonemes(txt_file)
        # get end of file time in milli seconds
        end_of_file = librosa.get_duration(filename=audio_file) * 1000

        # set interval
        start_interval = 0
        end_interval = interval
        silence_padding = 0

        while start_interval < end_of_file:  # each loop running deals with single interval

            # get phonemes in current interval
            sub_list = FileParser.get_phonemes_in_interval(phoneme_list, start_interval, end_interval)

            # check phoneme for file saving
            if not sub_list:
                common_phoneme = "none"
            else:
                common_phoneme = max(set([item['phoneme'] for item in sub_list]))

            # generate file destination for current interval
            dst_file = FileParser.file_path_generator(dst_folder, common_phoneme, '.wav')

            # check if silence need to be added (to that each output will be length of interval)
            if silence_padding <= 0:
                # get sub- audio file
                FileParser.wav_splitter(audio_file, start_interval, end_interval, dst_file)
            else:
                # get sub audio file
                FileParser.silence_padding(audio_file, start_interval, end_of_file, silence_padding, dst_file)

            # create corresponding wrd file
            wrd_dst = dst_file.replace(".wav", ".wrd")

            # remove phonemes so that each phoneme will appear only in single interval
            [phoneme_list.remove(item) for item in sub_list]
            for item in sub_list:
                # arrange times related to new file times (the new file length is interval)
                item['start'] -= start_interval
                item['start'] = max(0, item['start'])
                item['end'] -= start_interval
                item['end'] = min(interval, item['end'])

            FileParser.write_to_wrd(sub_list, wrd_dst)  # write to wrd

            # promote to next interval
            start_interval += interval
            end_interval += interval

            silence_padding = end_interval - end_of_file

    def cut_file_by_count_phonemes_interval(self, audio_file, txt_file, dst_folder, interval=500):
        """
        create from given audio file and it's alignment text file sub files:
        each audio sub file in give interval length,
        will be added to folder according to it's vowels count.
        :param audio_file: original audio file
        :type audio_file: str
        :param txt_file: Text grid alignment to the audio file
        :type txt_file: str
        :param dst_folder: root folder to save files to
        :type dst_folder: str
        :param interval: time in milli seconds
        :type interval: int
        :return: none
        :rtype:
        """
        # get phonemes from text grid file
        phoneme_list = self.extract_phonemes(txt_file)
        # get end of file time in milli seconds
        end_of_file = librosa.get_duration(filename=audio_file) * 1000

        # set interval
        start_interval = 0
        end_interval = interval
        silence_padding = 0

        while start_interval < end_of_file:  # each loop running deals with single interval

            # get phonemes in current interval
            sub_list = FileParser.get_phonemes_in_interval(phoneme_list, start_interval, end_interval)

            # check count for file saving
            count_phonemes = len(sub_list)

            # generate file destination for current interval
            dst_file = FileParser.file_path_generator(dst_folder, str(count_phonemes), '.wav')

            # check if silence need to be added (to that each output will be length of interval)
            if silence_padding <= 0:
                # get sub- audio file
                FileParser.wav_splitter(audio_file, start_interval, end_interval, dst_file)
            else:
                # get sub audio file
                FileParser.silence_padding(audio_file, start_interval, end_of_file, silence_padding, dst_file)

            # promote to next interval
            start_interval += interval
            end_interval += interval

            silence_padding = end_interval - end_of_file

    @classmethod
    def parse_folder_data(cls, audio_path, txt_path, dst_folder, parser, args=None, count_total=0):
        """
        parse all files in given root folder
        :param audio_path: audio root path folder
        :type audio_path: str
        :param txt_path: text grid alignment root path folder.
                        each audio file related path to root audio path,
                        should have alignment text grid file at same related to txt path, same name different extension
        :type txt_path: str
        :param dst_folder: folder to output parser files to
        :type dst_folder: str
        :param parser: function to apply on each pair: audio wav file, text grid file
        :type parser: function pointer
        :param args: if any needed to parse
        :type args:
        :param count_total: total file counter, for progress printing
        :type count_total: int
        :return: none
        :rtype:
        """
        count = 0
        for root, dirs, files in os.walk(audio_path):  # go over root folder
            for file in files:
                if not file.endswith('.wav'):
                    continue

                # get audio and text file
                audio_file = os.path.join(root, file)
                txt_file = txt_path + audio_file.replace(audio_path, "")
                txt_file = txt_file.replace('.wav', '.TextGrid')
                if not os.path.exists(txt_file):
                    continue

                # apply parser
                if args:
                    parser(audio_file, txt_file, dst_folder, args)
                else:
                    parser(audio_file, txt_file, dst_folder)

            if count_total != 0:  # print progress for user
                count += len(files)
                if files:
                    print(f"{count} out of {count_total} files were parsed")

    def parse_data_by_phonemes(self, path_for_audio, path_for_txt, path_dst, count_total=0):
        """
        apply cut by phonemes parser on files
        """
        self.parse_folder_data(path_for_audio, path_for_txt, path_dst,
                               self.cut_file_by_phonemes, None, count_total)

    def parse_data_by_interval(self, path_for_audio, path_for_txt, path_dst, interval=500, count_total=0):
        """
        apply cut by interval parser on files
        """
        self.parse_folder_data(path_for_audio, path_for_txt, path_dst,
                               self.cut_file_by_interval, interval, count_total)

    def parse_data_by_phonemes_count(self, path_for_audio, path_for_txt, path_dst, interval=500, count_total=0):
        """
            apply cut by interval and count of phonemes parser on files
        """
        self.parse_folder_data(path_for_audio, path_for_txt, path_dst,
                               self.cut_file_by_count_phonemes_interval, interval, count_total)


def audio_preparation(audio_files_path, destination_path):
    """
    This function will check if audio files in flac format, then convert them to wav
    :param audio_files_path: root folder for audio files
    :type audio_files_path: str
    :param destination_path: path to save converted files if necessary
    :type  destination_path: str
    :return: count of files, path for files
    :rtype: int, str
    """

    # create destination path
    Path(destination_path).mkdir(parents=True, exist_ok=True)

    # get total count of flac files
    count = 0
    for root, dirs, files in os.walk(audio_files_path):
        count += len([file for file in files if file.endswith('.flac')])

    print(f"found {count} audio files in format flac")

    # convert flac files to wav files
    if count != 0:
        destination_path_wav = destination_path + "\\converted_wav"
        AudioFileConverter.folder_flac_to_wav(audio_files_path, destination_path_wav)
        audio_files_path = destination_path_wav
        print("files converted to .wav format")

    # get total count of wav files
    count = 0
    for root, dirs, files in os.walk(audio_files_path):
        count += len([file for file in files if file.endswith('.wav')])

    print(f"found {count} audio files in format wav")

    return count, audio_files_path


def main(audio_files_path, text_files_path, destination_path, delete_wav_when_done=False, extract_method="by_phoneme"):
    # check input
    if not os.path.isdir(audio_files_path) or not os.path.isdir(text_files_path):
        raise Exception("path not exists")
    # convert to wav if needed
    count, audio_files_path = audio_preparation(audio_files_path, destination_path)
    # check input
    if count == 0:
        return -1

    file_parser = FileParser()

    # # create parser with less phonemes if needed here
    # short_phonemes = ['AA', 'AE', 'AH', 'EY', 'IH', 'IY', 'OW', 'UW']
    # file_parser_8_phonemes = FileParser(short_phonemes)
    # file_parser = file_parser_8_phonemes

    if extract_method == "by_phoneme":
        file_parser.parse_data_by_phonemes(audio_files_path, text_files_path,
                                           destination_path, count)
    else:
        if extract_method == "by_interval":
            file_parser.parse_data_by_interval(audio_files_path, text_files_path,
                                               destination_path, 500, count)
        else:
            if extract_method == "by_count":
                file_parser.parse_data_by_phonemes_count(audio_files_path, text_files_path,
                                                         destination_path, 500, count)

    if delete_wav_when_done:
        destination_path_wav = files_save_destination + "\\converted_wav"
        AudioFileConverter.delete_wav_files(destination_path_wav)
        print("created wav files deleted")


if __name__ == '__main__':
    audio_base_path = "sample_data_libriSpeech\\audio"
    text_path = "sample_data_libriSpeech\\alignment"

    files_save_destination = "sample_data_libriSpeech\\parsed-by-interval"

    by_phoneme = "by_phoneme"  # meaning cut each the phoneme
    by_interval = "by_interval"  # meaning cut by 0.5 sec interval (tag as most common phoneme)
    # this option was used for yolo model
    by_counter = "by_count"  # meaning cut by 0.5 sec interval and tag as counter

    extract_method_chosen = by_interval

    main(audio_base_path, text_path, files_save_destination,
         delete_wav_when_done=True, extract_method=extract_method_chosen)
