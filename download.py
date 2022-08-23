# Author: Elham Sharifia

import os
import urllib

import requests
from bs4 import BeautifulSoup

from progress_bar import MyProgressBar

def get_file_name(episode):
    title = episode.find("a", {"class": "episode_link"}).text
    lesson_counter = episode.find("p", {"class": "episode_counter"}).text
    if len(lesson_counter) == 1:
        lesson_counter = '0' + lesson_counter
    file_name = f'{lesson_counter} - {title}.mp4'
    return file_name

def get_lesson_link(episode):
    lesson_url = episode.find("a", {"class": "episode_link"}, href=True)
    return lesson_url['href']


class Course:
    main_url  = 'https://www.mongard.ir/'
    login_url = f'{main_url}accounts/login/'
    email = '<your email>'
    password = '<your password>'

    def __init__(self, course_url):
        self.url = course_url

    def download_lessons(self, soup, full_filename):
        download_link = soup.find("a", {"class": "video_download_link"}, href=True)
        print(download_link['href'])
        urllib.request.urlretrieve(download_link['href'], full_filename, MyProgressBar())


    def get_lessons(self, soup, path):
        episodes = soup.find_all("div", {"class": "episode_container"})
        for episode in episodes:
            if 'course_time_container' not in episode.attrs['class']:
                file_name = get_file_name(episode)
                lesson_link = get_lesson_link(episode)
                final_url = self.main_url + lesson_link
                lesson_page = session.get(final_url)
                soup = BeautifulSoup(lesson_page.text, "html.parser")

                full_filename = os.path.join(path, file_name)
                if os.path.exists(full_filename):
                    print(f'{full_filename} is downloaded before. skip this')

                else:
                    self.download_lessons(soup, full_filename)
            print('all episodes downloaded completely')



    def get_course_name(self, session):
        page = session.get(self.url)
        soup = BeautifulSoup(page.text, "html.parser")
        course_name = soup.find("h1", {"class": "course_top_title"}).text
        return soup, course_name


def login(course):
    session = requests.Session()
    login_page = session.get(course.login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    payload = {'email': course.email,
               'password': course.password,
               'csrfmiddlewaretoken': csrf
               }

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

    response = session.post(course.login_url, headers=header, data=payload)
    if response.status_code == 200:
        return session
    print('Login failed!')
    raise Exception

def course_directory(course_name, default_path='g://mongard'):
    current_path = os.path.abspath(default_path)
    path = f'{current_path}/{course_name}'
    is_exists = os.path.exists(path)
    if not is_exists:
        os.makedirs(path)

    return path






c = Course('https://www.mongard.ir/courses/django-cbv/')

session = login(c)

soup, course_name = c.get_course_name(session)
path = course_directory(course_name)
c.get_lessons(soup, path)

