import os
import exporter


def export_only():
    for meeting in [x for x in os.listdir('./temp/') if x.endswith('.zip')]:
        meeting_name = meeting[:len(meeting) - 4]
        exporter.export(meeting_name)


if __name__ == '__main__':
    export_only()
