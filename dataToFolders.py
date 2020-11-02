import random
from pathlib import Path
import os
from shutil import copyfile
import ntpath


class DataToFolders:

    @staticmethod
    def create_sub_folder(root, sub_folder):
        """
        create sub folder in specified folder
        :param root: root folder path
        :type root: str
        :param sub_folder: name
        :type sub_folder: str
        :return: new combined path
        :rtype: str
        """
        new_path = root + "\\" + sub_folder
        Path(new_path).mkdir(parents=True, exist_ok=True)
        return new_path

    @staticmethod
    def create_folders_for_net(root):
        """
        create in given root folder three sub folders: train, valid, test
        :param root: folder path
        :type root: str
        :return: list of three combined folders
        :rtype: list of str
        """
        train_path = DataToFolders.create_sub_folder(root, "train")
        valid_path = DataToFolders.create_sub_folder(root, "valid")
        test_path = DataToFolders.create_sub_folder(root, "test")
        return [train_path, valid_path, test_path]

    @staticmethod
    def get_files(root_folder, extension, extension_second=None):
        """
        get files with extension from given folder
        or paired files with same name and both given extensions
        :param root_folder: folder path
        :type root_folder: str
        :param extension: first extension to search by
        :type extension: str
        :param extension_second: second extension to search paired file
        :type extension_second: str
        :return: files list
        :rtype: list
        """
        file_list = []
        for root, dirs, files in os.walk(root_folder):  # go over root folder
            file_list.extend([os.path.join(root, file) for file in files if file.endswith(extension)])

        if not extension_second:
            return file_list

        paired_list = []
        for file in file_list:
            # search for same name file in same path, which has second type
            paired = file.replace(extension, extension_second)
            if os.path.exists(paired):
                paired_list.append([file, paired])

        return paired_list

    @staticmethod
    def get_min_count_files(root_folder, extension):
        """
        check in root folder for the folder with smallest amount of files type as extension
        :param root_folder: folder to search in sub folders
        :type root_folder: str
        :param extension: file type
        :type extension: str
        :return: number indicated the smallest folder len
        :rtype: int
        """
        import sys
        min_count = sys.maxsize

        for sub_folder in os.listdir(root_folder):
            full_path = os.path.join(source_path, sub_folder)
            if os.path.isdir(full_path):
                # get amount of files
                total = len(DataToFolders.get_files(full_path, extension))
                # update smallest
                min_count = min(total, min_count)
        return min_count

    @staticmethod
    def copy_files_paired(paired_file_list, dst_folder):
        """
        copy paired items
        :param paired_file_list: list of paired paths
        :type paired_file_list: list of lists of str
        :param dst_folder: destination path
        :type dst_folder: str
        :return: none
        :rtype:
        """

        for paired in paired_file_list:
            # get two files
            first_src = paired[0]
            second_src = paired[1]

            # create destination file path + name
            first_dst = dst_folder + "\\" + ntpath.basename(first_src)
            second_dst = dst_folder + "\\" + ntpath.basename(second_src)

            # copy the files
            copyfile(first_src, first_dst)
            copyfile(second_src, second_dst)

    @staticmethod
    def copy_files(file_list, dst_folder):
        """
        copy list of files to given folder
        :param file_list: list of file paths
        :type file_list: list of str
        :param dst_folder: folder to copy files to
        :type dst_folder: str
        :return: none
        :rtype:
        """

        for file in file_list:
            # create destination file path = path + file name
            file_dst = dst_folder + "\\" + ntpath.basename(file)
            copyfile(file, file_dst)

    @staticmethod
    def split_to_folders(source_root, dst_root_list,
                                first_split=0.8, second_split=0.1, is_balanced=True,
                                extension=".wav", second_extension=None):
        """
        This function splits files in root to three destinations, while saving folders hierarchy
        :param source_root: root folder
        :type source_root: str
        :param dst_root_list: list on three destination folders
        :type dst_root_list: str
        :param first_split: first part fraction size
        :type first_split: float < 1
        :param second_split: second part fraction size
        :type second_split: float < 1
        :param is_balanced:indicates if to split files so that in destination each folder will
                have same count of files (uses smallest folder count of files)
        :type is_balanced: bool
        :param extension: file type to move
        :type extension: str
        :param second_extension: second type to move (same name needed different extension)
        :type second_extension: str
        :return: none
        :rtype:
        """

        # create balanced division
        if is_balanced:
            # get smallest folder count of files
            min_count = DataToFolders.get_min_count_files(source_root, extension)
            # set split intervals
            first_split = round(min_count * first_split)
            second_split = first_split + round(min_count * second_split)
            third_split = min_count

        # check if needed to copy one or two type of files
        copy_method = DataToFolders.copy_files
        if second_extension:
            copy_method = DataToFolders.copy_files_paired

        for path in os.listdir(source_root):

            full_path = os.path.join(source_path, path)
            if os.path.isdir(full_path):

                # get files
                file_list = DataToFolders.get_files(full_path, extension, second_extension)
                random.shuffle(file_list)

                if not is_balanced:
                    # get intervals according to count of files in current folder
                    current_count = len(file_list)
                    first_split = round(current_count * first_split)
                    second_split = first_split + round(current_count * second_split)
                    third_split = current_count

                # divide file list according to intervals
                # train
                first_part = file_list[0: first_split]
                # validation
                second_part = file_list[first_split: second_split]
                # test
                third_part = file_list[second_split: third_split]

                # create in each folder sub folder with current name to keep hierarchy
                dst_first_part = DataToFolders.create_sub_folder(dst_root_list[0], path)
                dst_second_part = DataToFolders.create_sub_folder(dst_root_list[1], path)
                dst_third_part = DataToFolders.create_sub_folder(dst_root_list[2], path)

                # copy each files interval to suitable destination
                copy_method(first_part, dst_first_part)
                copy_method(second_part, dst_second_part)
                copy_method(third_part, dst_third_part)


source_path = "sample_data_libriSpeech/parsed-by-interval"
dst_path = "sample_data_libriSpeech/parsed-by-interval-div"

dst_list = DataToFolders.create_folders_for_net(dst_path)
DataToFolders.split_to_folders(source_path, dst_list, second_extension='.wrd')
# if no wrd - un comment this:
#DataToFolders.split_to_folders(source_path, dst_list)
