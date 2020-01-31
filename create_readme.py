import yaml
import os


def invalid_root(root):
    return '.git' in root or root == '.'


def ignore_file(file):
    return file == '.DS_Store' or '.yml' not in file


def write_title(file, name, source, author, author_page):
    full_title = name
    if source:
        full_title = "[{}]({})".format(full_title, source)
    if author:
        if author_page:
            full_title = "{} by [{}]({})".format(full_title, author, author_page)
        else:
            full_title = "{} by {}".format(full_title, author)
    else:
        full_title = "{} (unkown source)".format(full_title)

    file.write("### {}\n".format(full_title))


def write_image(file, root, filename, local=False):
    full_path = "{}/{}".format(root, filename)
    with open(full_path) as yml_file:
        content = yaml.load(yml_file, Loader=yaml.FullLoader)
        name = content['name'].strip()
        source = content['source']
        author = content['author']
        author_page = content['author_page']
        image_path = content['image_path']
        info = content['info']
        if local:
            image_path = image_path.split('/')[-1]
        write_title(file, name, source, author, author_page)
        file.write("![{}]({})\n".format(name, image_path))
        if info:
            file.write("{}\n".format(info))
        file.write("\n")


def write_root_content(file, root, title, images, collapse=True):
    if collapse:
        file.write("## {}\n".format(title))
        file.write("""
<details><summary>{} Wallpapers</summary>
<p>\n\n""".format(title))

    for image in images:
        write_image(file, root, image, local=not collapse)

    if collapse:
        file.write("""
</p>
</details>\n\n\n""")


def process_root(file, root, images):
    title = root.split('/')[1].title()
    write_root_content(file, root, title, images)

    sub_readme_name = "{}/README.md".format(root)
    with open(sub_readme_name, 'w') as sub_readme:
        sub_readme.write("# {}\n\n".format(title))
        write_root_content(sub_readme, root, title, images, collapse=False)



def write_images_to_file(file, folder):
    images = {}
    for root, _, files in os.walk(folder):
        if invalid_root(root): continue

        images[root] = []

        for filename in files:
            if ignore_file(filename): continue
            images[root].append(filename.lower())
        images[root].sort()
    for root in sorted(images.keys()):
        process_root(file, root, images[root])


with open('config.yml') as config:
    configurations = yaml.load(config, Loader=yaml.FullLoader)

    filename = configurations['filename']
    with open(filename, 'w') as file:
        file.write("# {}\n\n".format(configurations['title']))
        file.write("{}\n\n".format(configurations['description']))

        for section_name in configurations['sections']:
            section = configurations['sections'][section_name]

            file.write("## {}\n\n".format(section['title']))
            file.write("{}\n\n".format(section['info']))

        write_images_to_file(file, '.')
