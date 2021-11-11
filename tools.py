import datetime
import subprocess
import shlex
import os
# Https://Github.com/Miladshakerdn

def removefile(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        
def mSeconds_Timedelta(milliseconds):
    return str(datetime.timedelta(seconds=int(milliseconds)//1000)) #milliseconds=milliseconds

def run_command(command):
    print('running command: {0}'.format(command))
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        print(output.strip())
        if output == b'' and process.poll() is not None:
            print('Done running the command.')
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc

def audioCut(targetAudio, outputAudio, cFrom, cTo):
    conversion_command = 'ffmpeg -loglevel quiet -hide_banner -i "{0}" -ss {1}ms -to {2}ms -c copy "{3}"'.format(targetAudio, cFrom, cTo, outputAudio)
    run_command(conversion_command)

def videoAddAudio(targetAudio, targetVideo, output_path):
    output_VideoName = targetVideo + "_(VC)"
    output_path = output_path.replace("\\","/")
    output_VideoName=output_VideoName.replace(".flv","")
    targetAudio = output_path + targetAudio
    targetVideo = output_path + targetVideo
    conversion_command = 'ffmpeg -loglevel quiet -hide_banner -i "{0}" -i "{1}" -c copy -map 0:a:0 -map 1:v:0 -shortest -y "{3}{2}.flv"'.format(targetAudio, targetVideo, output_VideoName, output_path)
    run_command(conversion_command)
    removefile(targetAudio)
    removefile(targetVideo)


def timeLine(time_table, time_Lines, meeting = "sample"):
    time_screen = {}
    time_temp = []
    time_slice = {}
    for item in time_table:
        if str(item).startswith('screenshare'):
            if time_table[item][1] >= time_Lines :
                time_table[item][1] = time_Lines
            time_screen[time_table[item][1]]= list()
            txt = 'Video({})'.format(item.replace(".flv",""))
            time_screen[time_table[item][1]].append(txt)
            time_temp.append(time_table[item][0])
            time_temp.append(time_table[item][1])
    time_temp.append(time_Lines)
    time_temp = list(set(time_temp)) # remove duplicate time
    time_temp.sort()
    temp=0
    if time_temp[0] == 0 : time_temp.remove(0)
    for index, item in enumerate(time_temp):
        meeting_type = time_screen[time_temp[index]][0] if time_temp[index] in time_screen else "Audio_Only"
        name = '{0}_{1}_{2}'.format(meeting, meeting_type, index)
        if not name in time_slice:
            time_slice[name] = list()
        time_slice[name].append([temp,time_temp[index]])
        temp = time_temp[index]
    return time_slice

def audios_splitter(targetAudio,time_box,output_path,format=".mp3"):
    output_path = output_path.replace("\\","/")
    for audio in time_box:
        outputAudio = output_path + audio + format
        cFrom = time_box[audio][0][0]
        cTo = time_box[audio][0][1]
        audioCut(targetAudio, outputAudio, cFrom, cTo)

def audio_webcam_extract(target,output):
    print("sub process for audio")
    conversion_command = 'ffmpeg -loglevel quiet -hide_banner -i "{0}" -vn -acodec copy "{1}"'.format(target,output)
    run_command(conversion_command)