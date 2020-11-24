from pyffmpeg import FFmpeg
import os

ffmpeg = FFmpeg()
def convert_audio(file_name):
    directory_path = './temp/'+file_name+'/'
    output_directory = './output/'+file_name+'/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for file in os.listdir(directory_path):
        try:
            if file.startswith('camera') and file.endswith('.flv'):
                print('converting '+ directory_path + file)
                ffmpeg.convert(directory_path + file, output_directory + file.split('.')[0] + '.ogg')
        except:
            pass
def convert_video(file_name):
    directory_path = './temp/'+file_name+'/'
    output_directory = './output/'+file_name+'/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for file in os.listdir(directory_path):
        try:
            if file.startswith('screen') and file.endswith('.flv'):
                print('converting '+ directory_path + file)
                ffmpeg.options('-i ' + directory_path + file +' -c copy ' + output_directory + file.split('.')[0] + '.mkv')
        except:
            pass
