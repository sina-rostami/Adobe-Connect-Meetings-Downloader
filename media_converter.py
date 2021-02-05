from typing import DefaultDict
from pyffmpeg import FFmpeg
import xmltodict
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
                print('converting ' + directory_path + file)
                ffmpeg.convert(directory_path + file,
                               output_directory + file.split('.')[0] + '.ogg')
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
                print('converting ' + directory_path + file)
                ffmpeg.options('-i ' + directory_path + file + ' -c copy ' +
                               output_directory + file.split('.')[0] + '.mkv')
        except:
            pass


def print_events_time_table(file_name):
    mainstream_path = './temp/'+file_name+'/mainstream.xml'
    with open(mainstream_path) as file:
        mainstream = xmltodict.parse(file.read())
    time_table = {}
    for event in mainstream['root']['Message']:
        if event.get('Method') and event.get('String') and event.get('Array') and event.get('Array').get('Object'):
            if event.get('String') != "streamAdded" and event.get('String') != "streamRemoved":
                continue
            event_name = event['Array']['Object']['streamName'].replace('/', '') + '.flv'
            if event.get('String') == "streamAdded":
                if not event_name in time_table:
                    time_table[event_name] = list()
                time_table[event_name].append(int(event['@time']))
            elif event.get('String') == "streamRemoved":
                time_table[event_name].append(int(event['@time']))
    # for debug mode comment return line
    return time_table

    for ev in time_table:
        print(ev + ':')
        for e in time_table[ev]:
            print(e)


if __name__ == "__main__":
    print_events_time_table(input()) # meeting id e.g.: 8830285