#! python

"""Загрузка видео и аудио с youtube."""

import re

import subprocess
import time
import os
import pytube  # pip install pytube
from pytube.cli import on_progress  # для статус-бара загрузки

directories = ("video", "audio")

# url = "https://www.youtube.com/watch?v=l9nh1l8ZIJQ&ab_channel=JimTV"
url = "https://www.youtube.com/watch?v=rrwjymZMLdM&ab_channel=JimTV"

playlist_url = "https://www.youtube.com/playlist?list=PLUja9J5M1XReqoBal5IKog_PWz2Q_hZ7Y"


def create_directory() -> None:
    """Создание служебных каталогов в текущей директории"""
    global directories
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"Создали каталог: {directory}")
            except Exception as err:
                print(err)


def clean_filename(name: str) -> str:
    """Убираем лишние символы из файла и обрезаем его"""
    clean_name = re.sub(
        " +",
        " ",
        "".join(char for char in name if char.isalpha() or char.isdigit() or char == " ").strip(),
    )
    if len(clean_name) >= 125:
        clean_name = clean_name[:121]
    return clean_name


def get_info(url: str) -> dict:
    """Взять информацию о видео по ссылке и вернуть словарь с данными"""
    yt = pytube.YouTube(url)
    info_dict = {
        "Название": yt.title,
        "Автор": yt.author,
        "Опубликовано": yt.publish_date.strftime("%Y-%m-%d"),
        "Количество просмотров": yt.views,
        "Длина видео": yt.length,
        "Описание": yt.description,
        "Ключевые слова": yt.keywords,
        "Метадата": yt.metadata,
        "Рейтинг": yt.rating,
        "URL миниатюры": yt.thumbnail_url,
    }
    return info_dict


def download_video(url: str) -> None:
    """Загрузить одно видео"""
    global video_dir
    print(f"Запуск загрузки видео из: {url}")
    yt = pytube.YouTube(url, on_progress_callback=on_progress)
    filename = clean_filename(yt.title) + ".mp4"
    print(f"Загрузка {filename}")
    try:
        yt.streams.get_highest_resolution().download(filename=filename, output_path=video_dir)
        print("Успешно!")
        print(f"Длина загруженного видео: {yt.length // 60} мин {yt.length % 60} сек")
    except Exception as err:
        print(err)


def download_playlist(playlist_url: str) -> None:
    """Загрузить плейлист"""
    global video_dir
    print(f"Запуск загрузки видео из плейлиста: {playlist_url}")
    yt_playlist = pytube.Playlist(playlist_url)
    indx = 1
    for video in yt_playlist.videos:
        filename = clean_filename(video.title) + ".mp4"
        print(f"{indx} / {len(yt_playlist.videos)} | Загрузка {filename}")
        video.register_on_progress_callback(on_progress)
        try:
            video.streams.get_highest_resolution().download(
                filename=filename, output_path=video_dir
            )
            print("Успешно!")
            print(f"Длина загруженного видео: {video.length // 60} мин {video.length % 60} сек")
        except Exception as err:
            print(err)
            continue
        indx += 1


def convert_video_to_audio(video_filename: str) -> None:
    """Конвертируем видео в аудио с помощью ffmpeg"""
    global video_dir, audio_dir
    print(f"Конвертируется файл {video_filename}")
    try:
        base, _ = os.path.splitext(video_filename)
        audio_filename = base + ".mp3"
        subprocess.run(
            [
                "ffmpeg.exe",
                "-i",
                os.path.join(video_dir, video_filename),
                os.path.join(audio_dir, audio_filename),
            ]
        )
    except Exception as err:
        print(err)


if __name__ == "__main__":
    ti = time.time()

    create_directory()  # создаём служебные директории

    video_dir = os.sep.join((os.getcwd(), directories[0]))
    audio_dir = os.sep.join((os.getcwd(), directories[1]))

    download_video(url)  # загружаем одно видео
    # download_playlist(playlist_url)  # загружаем видео из плейлиста

    # Для каждого скачанного видео файла
    for _, _, videos in os.walk(video_dir):
        for video in videos:
            # выполним конвертацию в mp3
            convert_video_to_audio(video)

    print(f"Времени прошло: {time.time() - ti:0.2f} секунд")
