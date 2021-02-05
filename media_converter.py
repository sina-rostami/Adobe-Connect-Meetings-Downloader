import ffmpeg
import xmltodict
import os
import re


def convert_media(meeting_id):
    # for debugging change from 'quiet' to 'info'
    log_level = 'quiet'

    meeting_temp_path = './temp/' + meeting_id + '/'
    output_path = './output/' + meeting_id + '/'

    if not os.path.exists('./output/' + meeting_id):
        os.makedirs(output_path)

    time_table = get_events_time_table(meeting_id)
    videos = []
    prev_scrnshr = ""
    for item in time_table:
        # iterating over time_table because it's sorted already
        if str(item).startswith('screenshare'):
            vid = ffmpeg.input(meeting_temp_path + item).video
            if prev_scrnshr:
                start_duration = time_table[item][0] - time_table[prev_scrnshr][1]
                if start_duration < 0:
                    other_file_input = ffmpeg.input(meeting_temp_path + prev_scrnshr).video
                    other_file_stream = ffmpeg.output(other_file_input, output_path + item, loglevel=log_level)
                    ffmpeg.run(other_file_stream)
            else:
                prev_scrnshr = item
                start_duration = time_table[item][0]
            videos.append(ffmpeg.filter(vid, 'tpad', start_duration='{}ms'.format(start_duration)))

    audios = []
    camera_voips = [f for f in os.listdir(meeting_temp_path) if re.match('cameraVoip.+\.flv', f)]
    for camera_voip in camera_voips:
        aud = ffmpeg.input(meeting_temp_path + camera_voip).audio
        audios.append(ffmpeg.filter(aud, 'adelay', '{}ms'.format(time_table[camera_voip][0])))

    if len(audios) > 1:
        aud_out = ffmpeg.filter(audios, 'amix', inputs=len(audios))
    else:
        aud_out = audios[0]

    if len(videos) == 0:
        vid_out = None
    elif len(videos) == 1:
        vid_out = videos[0]
    else:
        vid_out = ffmpeg.filter(videos, 'concat', n=str(len(videos)), v=1, a=0)

    if vid_out:
        stream = ffmpeg.output(aud_out, vid_out, output_path + 'output.mp4', loglevel=log_level)
    else:
        stream = ffmpeg.output(aud_out, output_path + 'output.mp3', loglevel=log_level)

    ffmpeg.run(stream, overwrite_output=True)


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
            event_name = event['Array']['Object']['streamName'].replace('/', '') + '.flv'
            if not first_stream:
                first_stream = event_name
            if event.get('String') == "streamAdded":
                if not event_name in time_table:
                    time_table[event_name] = list()
                time_table[event_name].append(int(event['@time']))
            elif event.get('String') == "streamRemoved":
                time_table[event_name].append(int(event['@time']))

    for ev in time_table:
        time_table[ev][0] = time_table[ev][0] - time_table[first_stream][0]
        time_table[ev][1] = time_table[ev][1] - time_table[first_stream][0]

    return time_table
