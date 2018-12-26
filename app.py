import json
import os
import re
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


def _download_images_and_replace_links_in_content(content, title, site_uri, save_dir=_SAVE_DIR):
    """Download images in each post to ./save_dir/title/ directory, replace image markdown links "![]()" in content.
     Return content after replace."""
    image_markdown_links = re.findall(r'!\[.+?\]\(.+?\)', content)
    if image_markdown_links:
        images_save_dir = f'{save_dir}/{str(title).replace("/", "／")}'
        os.makedirs(images_save_dir, exist_ok=True)
        for index, image_link in enumerate(image_markdown_links):
            search = re.search(r'(\(.+)\.(.+\))', image_link)
            image_uri, image_ext = search.group(0)[2:-1], search.group(2)[0:-1]
            # todo multiprocess
            request.urlretrieve(f'{site_uri}/{image_uri}', filename=f'{images_save_dir}/{index}.{image_ext}')
            content = content.replace(image_uri, f'{index}.{image_ext}')
    return content


def download(_site_uri, ghost_api, token, save_dir=_SAVE_DIR):
    """Download your Ghost blog's all post articles and images belonging to each article to ./save_dir directory.
    Accessing ghost_api url with token.
    Then you can execute linux command "cp -r ./save_dir/* hexo/source/_post/path; hexo generate -d"
    to migrate download files"""
    posts = _posts_from(_site_uri + ghost_api, token)
    os.makedirs(save_dir, exist_ok=True)
    for post in posts:
        title, date, tags, categories, content = _title_date_tags_categories_content_from(post)
        content = _download_images_and_replace_links_in_content(content, title, _site_uri, save_dir)
        with open(f'{save_dir}/{str(title).replace("/", "／")}.md', 'wt+') as f:
            f.write(_hexo_content_header(title, date, tags, categories) + content)


if __name__ == '__main__':
    _site_uri = 'https://s1mple.xyz'
    _ghost_api = '/ghost/api/v0.1/posts/?limit=9999&page=1&status=alll&formats=mobiledoc&include=tags'
    _token = 'jXwRER4QirDVKSkzE7VGeyuqG40sur8obwCFpGXjZYDjItTP157wZ96b7MbACN8uexbkw9f7VZ9EemX6H1YhbmSnfxYW0R3Acr0gPPnOWzoVKr8pXbp1EAX39BsJOZxCugFdlW2yxeGSJEa6EDW2SSeZ7IShVD7QE5iGH9cI6cV0jABwG6YfgXNHdDXpp4E'
    download(_site_uri, _ghost_api, _token)
