import yaml
import os
import shutil
from PIL import Image

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


def invalid_root(root):
    return '.git' in root or '.idea' in root or root == '.' or '.cache' in root


def ignore_file(file):
    return file == '.DS_Store' or '.yml' not in file


def write_title(file, name, source, author, author_page):
    full_title = name
    if source:
        full_title = f"[{full_title}]({source})"
    if author:
        if author_page:
            full_title = f"{full_title} by [{author}]({author_page})"
        else:
            full_title = f"{full_title} by {author}"
    else:
        full_title = f"{full_title} (unkown source)"

    file.write(f"### {full_title}\n")


def cached_image_path(path):
    root, filename = path.split('/')
    cache_path = f"{root}/.cache/{filename}"
    if os.path.isfile(cache_path):
        return cache_path
    thumbnail_size = 512, 512
    im = Image.open(path)
    im.thumbnail(thumbnail_size, Image.ANTIALIAS)
    im.save(cache_path)
    return cache_path


def write_image(file, root, filename, local=False):
    full_path = f"{root}/{filename}"
    with open(full_path) as yml_file:
        content = yaml.load(yml_file, Loader=yaml.FullLoader)
        name = content['name'].strip()
        source = content['source']
        author = content['author']
        author_page = content['author_page']
        original_image_path = content['image_path']
        image_path = cached_image_path(original_image_path)
        info = content['info']
        if local:
            image_path = '/'.join(image_path.split('/')[1:])
            original_image_path = '/'.join(original_image_path.split('/')[1:])
        write_title(file, name, source, author, author_page)
        file.write(f"[![{name}]({image_path})]({original_image_path})\n")
        if info:
            file.write(f"{info}\n")
        file.write("\n")


def write_root_content(file, root, title, images, collapse=True):
    if collapse:
        file.write(f"## [{title}]({root})\n")
        file.write("""
<details><summary>{} Wallpapers</summary>
<p>\n\n""".format(title))

    for image in images:
        write_image(file, root, image, local=not collapse)

    if collapse:
        file.write("""
</p>
</details>\n\n\n""")


def cache_path_for_path(root):
    return f"{root}/.cache"


def create_cache_folder(path):
    cache_path = cache_path_for_path(path)
    if not os.path.isdir(cache_path):
        os.makedirs(cache_path)


def process_root(file, root, images):
    print(f"Processing {root}")
    create_cache_folder(root)
    title = root.split('/')[1].title()
    write_root_content(file, root, title, images)

    sub_readme_name = f"{root}/README.md"
    with open(sub_readme_name, 'w') as sub_readme:
        sub_readme.write(f"# {title}\n\n")
        write_root_content(sub_readme, root, title, images, collapse=False)


def write_images_to_file(file, folder):
    images = {}
    for root, _, files in os.walk(folder):
        if invalid_root(root): continue

        images[root] = [filename for filename in files if not ignore_file(filename)]

        images[root].sort(key=str.lower)
    for root in sorted(images.keys()):
        process_root(file, root, images[root])


with open('config.yml') as config:
    configurations = yaml.load(config, Loader=yaml.FullLoader)

    filename = configurations['filename']
    with open(filename, 'w') as file:
        file.write(f"# {configurations['title']}\n\n")
        file.write(f"{configurations['description']}\n\n")

        for section_name in sorted(configurations['sections']):
            section = configurations['sections'][section_name]

            file.write(f"## {section['title']}\n\n")
            file.write(f"{section['info']}\n\n")

        write_images_to_file(file, '.')
