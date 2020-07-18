
import time
import argparse
import urllib.parse
import subprocess
import json
import collections
import pathlib
import uuid

from selenium.webdriver.common.action_chains import ActionChains
import requests
import tqdm

import lib


def until_timeout(timeout, wait=1):
    t0 = time.time()
    while time.time() - t0 < timeout:
        yield
        time.sleep(wait)
    raise Exception("Connection timeout")


def click_center(driver, element):
    x, y = element.location["x"] + element.size["width"] / 2, element.location["y"] + element.size["height"] / 2
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), 0, 0)
    actions.move_by_offset(int(x), int(y)).click().perform()


def get_network_urls(driver):
    return driver.execute_script("""
        var network = performance.getEntries() || {};
        return network.map((elem) => elem.name);
    """)


def get_video_streams(urls):
    found = set()
    for url_str in urls:
        try:
            url = urllib.parse.urlparse(url_str)
        except ValueError:
            continue
        if url.path.endswith('mp4'):
            queries = urllib.parse.parse_qs(url.query)
            del queries["bytestart"]
            del queries["byteend"]
            new_url = url._replace(query=urllib.parse.urlencode(queries, doseq=True))
            found.add(new_url.geturl())
    return found


def get_shortened_name(filename, max_length=12):
    name = pathlib.Path(filename).name
    if len(name) > 12:
        start = int((max_length - 2) / 2)
        return name[:start] + ".." + name[-start:]


def download_file(url, filename: pathlib.Path):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(str(filename), 'wb') as file, tqdm.tqdm(
            desc=get_shortened_name(filename, 30),
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def download_header(url, filename, min_size=2048):
    resp = requests.get(url, stream=True)
    size = 0
    with open(filename, 'wb') as file:
        for data in resp.iter_content(chunk_size=1024):
            size += file.write(data)
            if size >= min_size:
                break


MediaType = collections.namedtuple("MediaType", ["codec_type", "area"])


def get_media_type(filename) -> MediaType:
    p = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format",
                        "-show_streams", str(filename)], capture_output=True)
    info = json.loads(p.stdout)
    assert len(info['streams']) == 1
    stream = info['streams'][0]
    try:
        area = int(stream["width"]) * int(stream["height"])
    except KeyError:
        area = None
    return MediaType(stream['codec_type'], area)


def get_filename(url, folder):
    filename = pathlib.PurePath(urllib.parse.urlparse(url).path).name
    return pathlib.Path(folder) / filename


def combine_audio_video(audio_file, video_file, output_file):
    subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(audio_file), "-i", str(video_file),
                    "-c:v", "copy", "-c:a", "copy", str(output_file)])


def download_facebook_video(driver, fb_url, timeout=30, folder="downloads", out_name=''):
    driver.get(fb_url)

    # wait until page loaded
    videos = []
    for _ in until_timeout(timeout):
        videos = driver.find_elements_by_tag_name("video")
        if len(videos) > 0:
            break

    # start video
    click_center(driver, videos[0])

    # parse network streams
    streams = []
    for _ in until_timeout(timeout):
        network = get_network_urls(driver)
        streams = get_video_streams(network)
        if len(streams) >= 2:
            break

    # stop video
    click_center(driver, videos[0])

    # analyze media formats
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    audio = None
    video = None
    video_area = 0
    for url in streams:
        filename = get_filename(url, folder)
        download_header(url, filename)
        media_type = get_media_type(filename)
        if media_type.codec_type == "audio":
            audio = url
        elif media_type.codec_type == "video":
            if media_type.area > video_area:
                video = url
                video_area = media_type.area
        else:
            raise Exception("Unknown codec type '{}' encountered in {}".format(media_type.codec_type, url))

    if not audio:
        raise Exception("Could not find audio stream")
    if not video:
        raise Exception("Could not find video stream")

    # download files
    print("Downloading audio:")
    audio_file = get_filename(audio, folder)
    download_file(audio, audio_file)
    print("Downloading video:")
    video_file = get_filename(video, folder)
    download_file(video, video_file)

    # combine audio & video
    if not out_name:
        out_name = uuid.uuid4().hex
    out_file = pathlib.Path(folder) / (out_name + ".mp4")
    combine_audio_video(audio_file, video_file, out_file)
    print("Combined output:")
    print(out_file)

    # delete temporary files
    for url in streams:
        get_filename(url, folder).unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="video post url")
    parser.add_argument("--name", type=str, help="name of output video", default="")
    parser.add_argument("--no-headless", help="run chrome not in headless mode", action="store_true")
    parser.add_argument("--profile-path", type=str, help="chrome profile to use (default ~/.selenium)",
                        default="~/.selenium")
    parser.add_argument("--download-folder", type=str, help="download folder (default ~/Desktop/download)",
                        default="~/Desktop/download")
    args = parser.parse_args()

    print("Opening Facebook", end="")
    profile_path = pathlib.Path(args.profile_path).expanduser()
    driver = lib.create_driver(headless=not args.no_headless, profile_path=profile_path,
                               open_devtools=False, log_level=3)
    try:
        lib.login_facebook(driver)
        folder = pathlib.Path(args.download_folder).expanduser()
        download_facebook_video(driver, args.url, folder=folder, out_name=args.name)
    finally:
        driver.close()

    print("Done...")


if __name__ == "__main__":
    main()
