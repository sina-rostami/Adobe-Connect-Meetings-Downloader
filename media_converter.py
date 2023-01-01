import ffmpeg
import xmltodict
import os
import re


def does_camera_voip_have_attribute(file_name, name, attribute):
    xml_path = f'./temp/{file_name}/{name[:-4]}.xml'
    with open(xml_path) as file:
        camera_voip = xmltodict.parse(file.read())

    return attribute in camera_voip['root']['Flag']

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
        if str(item).startswith('screenshare') or not does_camera_voip_have_attribute(meeting_id, item, "video"):
            vid = ffmpeg.input(meeting_temp_path + item).video
            try:
                ffmpeg.run(ffmpeg.output(vid, output_path + item.split('.')[0] + '.mp4', f='flv', c='copy', loglevel=log_level), overwrite_output=True)
            except:
                pass

    audios = []
    camera_voips = [f for f in os.listdir(meeting_temp_path) if re.match('cameraVoip.+\.flv', f)]
    for camera_voip in camera_voips:
        if camera_voip in time_table and does_camera_voip_have_attribute(meeting_id, camera_voip, "audio"):
            aud = ffmpeg.input(meeting_temp_path + camera_voip).audio
            audios.append(ffmpeg.filter(aud, 'adelay', '{}ms'.format(time_table[camera_voip][0])))

    if len(audios) > 1:
        aud_out = ffmpeg.filter(audios, 'amix', inputs=len(audios))
    else:
        aud_out = audios[0]

    stream = ffmpeg.output(aud_out, output_path + 'meeting_audio.mp3', loglevel=log_level)
    try:
        ffmpeg.run(stream, overwrite_output=True)
        return True
    except Exception as e:
        return False


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
                end_time = int(event['@time'])
                if end_time > time_table[event_name][0]:
                    time_table[event_name].append(end_time)
                else:
                    time_table.pop(event_name)

    for ev in time_table:
        time_table[ev][0] = time_table[ev][0] - time_table[first_stream][0]
        if len(time_table[ev]) == 2:
            time_table[ev][1] = time_table[ev][1] - time_table[first_stream][0]

    return time_table


if __name__ == "__main__":
    convert_media(input())