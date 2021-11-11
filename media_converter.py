import ffmpeg
import xmltodict
import os
import re
import tools as milad # Miladshakerdn => Github

def convert_media(meeting_id):
    # for debugging change from 'quiet' to 'info'
    log_level = 'quiet'

    meeting_temp_path = './temp/' + meeting_id + '/'
    output_path = './output/' + meeting_id + '/'
    targetAudio = output_path + 'meeting_audio.mp3'
    
    if not os.path.exists('./output/' + meeting_id):
        os.makedirs(output_path)

    time_table,time_Line = get_events_time_table(meeting_id)
    time_box = milad.timeLine(time_table,time_Line,meeting_id)

    audios = []
    camera_voips = [f for f in os.listdir(meeting_temp_path) if re.match('cameraVoip.+\.flv', f)]
    for camera_voip in camera_voips:
        if camera_voip in time_table:
            target_audio_path = meeting_temp_path + camera_voip
            prop = len(ffmpeg.probe(meeting_temp_path + camera_voip)['streams'])

            if prop == 2: # check is audio have data
                aud = ffmpeg.input(target_audio_path).audio
                audios.append(ffmpeg.filter(aud, 'adelay', '{}ms'.format(time_table[camera_voip][0])))
            
            if prop > 2 : # voice from web cam
                output_audio_path = meeting_temp_path + 'audio' + camera_voip
                milad.audio_webcam_extract(target_audio_path,output_audio_path)
                aud = ffmpeg.input(output_audio_path).audio
                audios.append(ffmpeg.filter(aud, 'adelay', '{}ms'.format(time_table[camera_voip][0])))
            
    if len(audios) > 1:
        aud_out = ffmpeg.filter(audios, 'amix', inputs=len(audios))
    else:
        aud_out = audios[0]

    stream = ffmpeg.output(aud_out, targetAudio, loglevel=log_level)
    try:
        ffmpeg.run(stream, overwrite_output=True)
    except:
        pass
    # Split audios
    milad.audios_splitter(targetAudio, time_box, output_path)

    videos = []
    prev_scrnshr = ""
    for item in time_table:
        # iterating over time_table because it's sorted already
        if str(item).startswith('screenshare'):
            vid = ffmpeg.input(meeting_temp_path + item).video
            vTemp = '{0}_Video({1})_'.format(meeting_id,item.replace(".flv",""))
            video_name = ""
            for iname in time_box:
                if str(iname).startswith(vTemp):
                    video_name = iname
            targetAudioV = video_name + ".mp3"
            targetVideo = video_name + ".flv"
            try:
                ffmpeg.run(ffmpeg.output(vid, output_path + video_name + '.flv', f='flv', c='copy', loglevel=log_level), overwrite_output=True)
                milad.videoAddAudio(targetAudioV, targetVideo, output_path)
                # milad.removefile(targetAudio) # keep all
            except:
                return False
    return True


def get_events_time_table(file_name):
    mainstream_path = './temp/' + file_name + '/mainstream.xml'
    with open(mainstream_path) as file:
        mainstream = xmltodict.parse(file.read())
    first_stream = None
    time_table = {}
    for event in mainstream['root']['Message']:
        if event.get('Method') and event.get('String') and event.get('Array') and event.get('Array').get('Object'):
            if event.get('String') != "streamAdded" and event.get('String') != "streamRemoved":
                continue
            event_name = event['Array']['Object']['streamName'].replace('/', '') + '.flv' # dump =>  ['/screenshare_6_15', 'screenshare_6_15.flv']
            if not first_stream:
                first_stream = event_name #dump only=>  cameraVoip_0_3.flv
            if event.get('String') == "streamAdded":
                if not event_name in time_table:
                    time_table[event_name] = list()
                time_table[event_name].append(int(event['@time']))
            elif event.get('String') == "streamRemoved":
                end_time = int(event['@time'])
                if end_time > time_table[event_name][0]:
                    time_table[event_name].append(end_time)
                else:
                    time_table.pop(event_name)
    time_line = 0
    for ev in time_table:
        time_table[ev][0] = time_table[ev][0] - time_table[first_stream][0]
        if len(time_table[ev]) == 2:
            time_table[ev][1] = time_table[ev][1] - time_table[first_stream][0]
            time_line = int(time_table[ev][1]) if time_line < int(time_table[ev][1]) else time_line
    return [time_table,time_line]


if __name__ == "__main__":
    convert_media(input())
