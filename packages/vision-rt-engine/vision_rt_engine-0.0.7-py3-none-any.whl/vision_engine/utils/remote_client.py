#!/usr/bin/env python

import io
import requests
import click

from PIL import Image


@click.command()
@click.option('--text', type=str, default=None)
@click.option('--image', type=str, default=None)
@click.option('--url', default='http://127.0.0.1:8080/chat')
def main(text, image, url):
    args = {}
    if text:
        args['data'] = {'text': text}

    if image is not None:
        with Image.open(image) as image:
            im_buffer = io.BytesIO()
            image.save(im_buffer, format='JPEG')
            im_buffer.seek(0)

        args['files'] = {'image': ('image.jpg', im_buffer, 'image/jpeg')}

    assert len(args) > 0
    print(args)
    response = requests.post(url, **args)

    if response.status_code == 200:
        print("Server reply:", response.json().get('response'))
    else:
        print("Failed to contact server:", response.status_code)
    
    
if __name__ == '__main__':
    main()
