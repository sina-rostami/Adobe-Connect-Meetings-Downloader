import ffmpeg
import os


def convert_audio(file_name):
    directory_path = './temp/'+file_name+'/'
    output_directory = './output/'+file_name+'/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for file in os.listdir(directory_path):
        if file.startswith('camera') and file.endswith('.flv'):
            print('converting '+ directory_path + file)
            audio = ffmpeg.input(directory_path + file).audio
            ffmpeg.output(audio, output_directory + file.split('.')[0] + '.ogg', loglevel='quiet').run()
def convert_video(file_name):
    ffmpeg.loglevel = 'info'
    directory_path = './temp/'+file_name+'/'
    output_directory = './output/'+file_name+'/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for file in os.listdir(directory_path):
        if file.startswith('screen') and file.endswith('.flv'):
            print('converting '+ directory_path + file)
            video = ffmpeg.input(directory_path + file).video
            ffmpeg.output(video, output_directory + file.split('.')[0] + '.mkv', codec='copy', loglevel='quiet').run()