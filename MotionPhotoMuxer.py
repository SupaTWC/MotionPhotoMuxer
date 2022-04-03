import argparse
import logging
import os
import sys
from os.path import exists, basename

import pyexiv2


def validate_inputs(photo_path, video_path):
    """
    Checks if the files provided are valid inputs. Currently the only supported inputs are MP4/MOV and JPEG filetypes.
    Currently it only checks file extensions instead of actually checking file formats via file signature bytes.
    :param photo_path: path to the photo file
    :param video_path: path to the video file
    :return: True if photo and video files are valid, else False
    """
    if not exists(photo_path):
        logging.error("Photo does not exist: {}".format(photo_path))
    if not exists(video_path):
        logging.error("Video does not exist: {}".format(video_path))
    if not photo_path.lower().endswith(('.jpg', '.jpeg')):
        logging.error("Photo isn't a JPEG: {}".format(photo_path))
    if not video_path.lower().endswith(('.mov', '.mp4')):
        logging.error("Video isn't a MOV or MP4: {}".format(photo_path))


def merge_files(photo_path, video_path):
    """Merges the photo and video file together by concatenating the video at the end of the photo. Writes the output to
    a temporary folder.
    :param photo_path: Path to the photo
    :param video_path: Path to the video
    :return: File name of the merged output file
    """
    logging.info("Merging {} and {}.".format(photo_path, video_path))
    out_path = "output/{}".format(basename(photo_path))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as outfile, open(photo_path, "rb") as photo, open(video_path, "rb") as video:
        outfile.write(photo.read())
        outfile.write(video.read())
    logging.info("Merged photo and video.")
    return out_path


def add_xmp_metadata(merged_file, offset):
    """Adds XMP metadata to the merged image indicating the byte offset in the file where the video begins.
    :param merged_file: The path to the file that has the photo and video merged together.
    :param offset: The number of bytes from EOF to the beginning of the video.
    :return: None
    """
    metadata = pyexiv2.Image(merged_file)
    logging.info("Reading existing metadata from file.")
    metadata.read_xmp() 
    logging.info("Found XMP keys: " + str(metadata.read_xmp()))
    if len(metadata.read_xmp()) > 0:
        logging.warning("Found existing XMP keys. They *may* be affected after this process.")
    # (py)exiv2 raises an exception here on basically all my 'test' iPhone 13 photos -- I'm not sure why,
    # but it seems safe to ignore so far. It's logged anyways just in case.
    try:
        pyexiv2.registerNs('http://ns.google.com/photos/1.0/camera/', 'GCamera')
    except KeyError:
        logging.warning("exiv2 detected that the GCamera namespace already exists.".format(merged_file))

    xmpData = {'Xmp.GCamera.Microvideo': 1, 
               'Xmp.GCamera.MicroVideoVersion': 1, 
               'Xmp.GCamera.MicroVideoOffset': offset, 
               'Xmp.GCamera.MicroVideoPresentationTimestampUs':1500000} # in Apple Live Photos, the chosen photo is 1.5s after the start of the video, so 1500000 microseconds
    metadata.modify_xmp(xmpData)


def convert(photo_path, video_path):
    """
    Performs the conversion process to mux the files together into a Google Motion Photo.
    :param photo_path: path to the photo to merge
    :param video_path: path to the video to merge
    :return: None
    """
    validate_inputs(photo_path, video_path)

    merged = merge_files(photo_path, video_path)
    photo_filesize = os.path.getsize(photo_path)
    merged_filesize = os.path.getsize(merged)

    # The 'offset' field in the XMP metadata should be the offset (in bytes) from the end of the file to the part
    # where the video portion of the merged file begins. In other words, merged size - photo_only_size = offset.
    offset = merged_filesize - photo_filesize
    add_xmp_metadata(merged, offset)


def matching_video(photo_path):
    base = os.path.splitext(photo_path)[0]
    logging.info("Looking for videos named: {}".format(base))
    if os.path.exists(base + ".mov"):
        return base + ".mov"
    if os.path.exists(base + ".mp4"):
        return base + ".mp4"
    if os.path.exists(base + ".MOV"):
        return base + ".MOV"
    if os.path.exists(base + ".MP4"):
        return base + ".MP4"
    else:
        return ""


def process_directory(file_dir, recurse):
    """
    Loops through files in the specified directory and generates a list of (photo, video) path tuples that can
    be converted
    :TODO: Implement recursive scan
    :param file_dir: directory to look for photos/videos to convert
    :param recurse: if true, subdirectories will recursively be processes
    :return: a list of tuples containing matched photo/video pairs.
    """
    logging.info("Processing dir: {}".format(file_dir))
    if recurse:
        logging.error("Recursive traversal is not implemented yet.")
        exit(1)

    file_pairs = []
    for file in os.listdir(file_dir):
        file_fullpath = os.path.join(file_dir, file)
        if os.path.isfile(file_fullpath) and file.lower().endswith(('.jpg', '.jpeg')) and matching_video(
                file_fullpath) != "":
            file_pairs.append((file_fullpath, matching_video(file_fullpath)))

    logging.info("Found {} pairs.".format(len(file_pairs)))
    logging.info("subset of found image/video pairs: {}".format(str(file_pairs[0:9])))
    return file_pairs


def main(args):
    logging_level = logging.INFO if args.verbose else logging.ERROR
    logging.basicConfig(level=logging_level, stream=sys.stdout)
    logging.info("Enabled verbose logging")
    if args.dir:
        pairs = process_directory(args.dir, args.recurse)
        for pair in pairs:
            pass
            convert(pair[0], pair[1])
    else:
        photo_path = args.photo
        video_path = args.video
        convert(photo_path, video_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Merges a photo and video into a Microvideo-formatted Google Motion Photo')
    parser.add_argument('--verbose', help='Show logging messages.', action='store_true')
    parser.add_argument('--dir', type=str, help='Process a directory for photos/videos. Takes precedence over '
                                                '--photo/--video')
    parser.add_argument('--recurse', help='Recursively process a directory. Only applies if --dir is also provided',
                        action='store_true')
    parser.add_argument('--photo', type=str, help='Path to the JPEG photo to add.')
    parser.add_argument('--video', type=str, help='Path to the MOV video to add.')
    main(parser.parse_args())
