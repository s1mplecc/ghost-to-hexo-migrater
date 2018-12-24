import json
import os
import shutil
from urllib import request

_SAVE_DIR = './downloads'


def _response_from(url, token):
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Authorization', f'Bearer {token}')
    with request.urlopen(req) as res:
        return res.read()


def _posts_from(url, token):
    return json.loads(_response_from(url, token)).get('posts')


def _title_date_tags_categories_content_from(post):
    title = post['title']
    date = post['created_at']
    tags = [tag['name'] for tag in post['tags']]
    categories = []
    content = json.loads(post['mobiledoc'])['cards'][0][1]['markdown']
    return title, date, tags, categories, content


def _hexo_content_header(title, date, tags, categories):
    return f'''---\ntitle: {title}\ndate: {date}\ntags: {tags}\ncategories: {categories}\n---\n'''


def _write_to_file(content, path):
    with open(path, 'wt+') as f:
        f.write(content)


def _copy_downloads_files_to(hexo_post_dir):  # todo
    files = [os.path.join(top, f) for top, dirs, fs in os.walk(_SAVE_DIR) for f in fs]
    print(files)
    print(len(files))
    for file in files:
        shutil.copy2(file, f'{hexo_post_dir}/{file[12:]}')


def run(ghost_api, token, save_dir=_SAVE_DIR):
    posts = _posts_from(ghost_api, token)
    os.makedirs(save_dir, exist_ok=True)
    for post in posts:
        title, date, tags, categories, content = _title_date_tags_categories_content_from(post)
        _write_to_file(_hexo_content_header(title, date, tags, categories) + content,
                       f'{_SAVE_DIR}/{str(title).replace("/", "／")}.md')
    # _copy_downloads_files_to('./a')


if __name__ == '__main__':
    _ghost_api = 'https://s1mple.xyz/ghost/api/v0.1/posts/?limit=9999&page=1&status=alll&formats=mobiledoc&include=tags'
    _token = 'ZX6Lp0BC2lmlG1dhlRg8PoVBvAUolEEtcThCZLE8CmhTOtWxPji0hsRwn80BDcW0K7AaKiAEd7LEiVpaicvzOJXFFQwm9zBv3UdNW37uo9Tw4LeV97SnpXhuEIzgOq1hjxs1xE5X97dVXuhI3GOAGheN2QELvRPhbut5UFwDL17akupgRKbUxYHitWtyJYm'
    run(_ghost_api, _token)
