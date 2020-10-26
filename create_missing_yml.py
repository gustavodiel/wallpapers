import os
from PIL import Image


def process_file(root, file):
  file_name = ''.join(file.split('.')[:-1])
  file_yml = "{}/{}.yml".format(root, file_name)
  original_file = "{}/{}".format(root, file)
  
  if not os.path.isfile(file_yml):
    print("Created {}!".format(file_yml))
    generate_default_yml(file_yml, original_file)


def default_info(file):
  file_format = file.split('.')[-1]
  with Image.open(file) as img:
    width, height = img.size
  return "Size: ({} x {})\\n\\nFormat: {}".format(width, height, file_format)


def generate_default_yml(file, original_file):
  with open(file, 'w') as f:
    f.write(
"""name: {}
source:
author:
author_page:
image_path: {}
info: \"{}\"""".format(original_file, original_file[2:], default_info(original_file)))


def invalid_root(root):
  return '.git' in root or root == '.' or '.idea' in root or '.cache' in root


def ignore_file(file):
  return file == '.DS_Store' or '.yml' in file or '.md' in file


def process_images(folder):
  for root, _, files in os.walk(folder):
    if invalid_root(root): continue
    for file in files:
      if ignore_file(file): continue
      process_file(root, file)


if __name__ == '__main__':
  process_images('.')
