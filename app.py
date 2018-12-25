import json
import os
import re
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


def _download_images_and_replace_content_links(content, title, save_dir=_SAVE_DIR):
    """Download images in each post to _SAVE_DIR/title directories, replace image links in content.
     Return content after replace.
    """
    p = re.compile(r'!\[.+?\]\(.+?\)')
    image_links = p.findall(content)
    if image_links:
        # print(len(image_links), title, image_links)
        save_images_dir = f'{save_dir}/{str(title).replace("/", "／")}'
        os.makedirs(save_images_dir, exist_ok=True)
        for index, image_link in enumerate(image_links):
            p2 = re.compile(r'(\(.+)\.(.+\))')
            search = p2.search(image_link)
            if search:
                uri, ext = search.group(0)[2:-1], search.group(2)[0:-1]
                request.urlretrieve(f'https://s1mple.xyz/{uri}', filename=f'{save_images_dir}/{index}.{ext}')
                content = content.replace(uri, f'{index}.{ext}')
            else:
                print(image_link)  # todo logger

    return content


def _copy_downloads_files_to(hexo_post_dir):  # todo
    """cp -r ./downloads/* hexo/source/_post/path"""
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
        content = _download_images_and_replace_content_links(content, title)
        _write_to_file(_hexo_content_header(title, date, tags, categories) + content,
                       f'{save_dir}/{str(title).replace("/", "／")}.md')
    # _copy_downloads_files_to('./a')


if __name__ == '__main__':
    _ghost_api = 'https://s1mple.xyz/ghost/api/v0.1/posts/?limit=9999&page=1&status=alll&formats=mobiledoc&include=tags'
    _token = 'nRgAovALPGOVCiY5UlgOiqQYs6E2vT4UXNjesgweM5mlVaok24ENrzzg2R3rdfRufXYthR0Qdnp7MvjGWJlsj8XbiStHUqpJxYv5LwiNJuLaeqmgMQK6KfRaN5JtbfImkWZBnzOp8bA9rfYX2vEL6lHWvHzB2NNfo8su1HLuY8VoLzTfySLU9pnQm4h2NUu'
    run(_ghost_api, _token)
