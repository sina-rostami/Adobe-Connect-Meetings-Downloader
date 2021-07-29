import zipfile
import media_converter


def unzip(name):
    print('extracting zip file...')
    path = './temp/' + name + '.zip'
    zipfile.ZipFile(path, 'r').extractall('./temp/' + name)
    print('extracted!')


def convert(name):
    print('converting and merging media....')
    if not media_converter.convert_media(name):
        print('An error occurred during conversion...')
        return
    print('converted!')


def export(name):
    unzip(name)
    convert(name)
