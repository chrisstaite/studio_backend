import pytube


def import_video(url: str, location: str) -> str:
    """
    Download the audio from a YouTube video
    :param url:  The YouTube URL to download from
    :param location:  The directory to download it to
    :return:  The name of the file that was downloaded
    """
    yt = pytube.YouTube(url)
    file = yt.streams. \
        filter(only_audio=True, subtype='mp4'). \
        first(). \
        download(location)
    return file
