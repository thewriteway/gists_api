#!/usr/bin/python3

import argparse
import http.client
import json
import os.path
import re
import shlex
import subprocess
import sys
import urllib
import urllib.parse
import urllib.request

# TODO: think of what to do with the TOKEN
with open('TOKEN', 'r') as t:
    TOKEN = t.read()

BASE_URL = 'https://api.github.com'
GIST_URL = 'https://gist.github.com'

def str2bool(v):
    """
    Function to convert posible bool values to Pythonic bools.
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# ====== Get a single gist ======
# https://developer.github.com/v3/gists/#get-a-single-gist
def getSingleGist(GIST_ID):
    """Print gist content to STDOUT.

    Args:
        GIST_ID (str): gist_id.

    Examples:
        >>> ./gist_api.py gist 0ba2b2a39f8f66caa5630549239f35a2
        VSCode: Open directory from integrated terminal.

        `code -r .`
    """

    # TODO: finalize output

    try:
        r = urllib.request.urlopen(f'{BASE_URL}/gists/{GIST_ID}').read()
    except urllib.error.HTTPError:
        print('ERROR: GIST_ID IS BAD')
        return

    cont = json.loads(r.decode('utf-8'))

    gist_id = cont.get('id')
    gist_url = cont.get('html_url')
    gist_files = list(cont.get('files'))
    gist_description = cont.get('description')
    gist_content = list(cont.get('files').values())[0].get('content')

    print(gist_content)


# ====== List a user's gists ======
# https://developer.github.com/v3/gists/#list-a-users-gists
def getAllGists(USERNAME):
    """Print gists information of given user.

    Args:
        USERNAME (str): owner of gists.

    Examples:
        >>> ./gist_api.py list snowmanunderwater
        === 1 of 5 ===
        Name:        Tips.md
        Description: Tips
        URL:         https://gist.github.com/0ba2b2a39f8f66caa5630549239f35a2
        ID:          0ba2b2a39f8f66caa5630549239f35a2
    """

    # TODO: finalize output

    try:
        r = urllib.request.urlopen(f'{BASE_URL}/users/{USERNAME}/gists').read()
    except urllib.error.HTTPError:
        print('ERROR: USERNAME IS BAD')
        return

    cont = json.loads(r.decode('utf-8'))
    all_gists = len(cont)
    count = 1
    for item in cont:
        name = list(item.get('files').keys())[0]
        gist_id = item.get('id')
        html_url = item.get('html_url')
        raw_url = item.get('files').get(name).get('raw_url')
        gist_description = item.get('description')
        print(f'=== {count} of {all_gists} ===')
        print(
            f'Name:        {name}\nDescription: {gist_description}\nURL:         {html_url}\nID:          {gist_id}'
        )
        count += 1


# ====== Create a gist ======
# https://developer.github.com/v3/gists/#create-a-gist
def createGist(files, desc, public):
    """Create gist.

    Args:
        files (list): files into gist
        desc (str): gist description
        public (bool): True for public, False for private

    Examples:
        >>> ./gist_api.py create -f file1 file2 -d 'Lalala' -b no
    """

    url = 'https://api.github.com/gists'

    files_dict = {}

    # FIXME: Possible problems in file parsing
    for file in files:
        filename = file.split('/')[-1]
        fileContent = open(file, 'r').read()
        files_dict[filename] = {'content': fileContent}

    json_dict = {
        'files': files_dict,
        'description': desc,
        'public': str2bool(public)
    }

    # convert json_dict to JSON
    json_data = json.dumps(json_dict)
    # convert str to bytes (ensure encoding is OK)
    post_data = json_data.encode('utf-8')

    # we should also say the JSON content type header
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'token ' + TOKEN
    }

    # now do the request for a url
    req = urllib.request.Request(url, post_data, headers, method='POST')

    # send the request
    res = urllib.request.urlopen(req)

    if res.code == 201:
        print('Gist created!')


# ====== Edit a gist ======
# https://developer.github.com/v3/gists/#edit-a-gist
def editGist(id, desc, files):
    url = f'https://api.github.com/gists/{id}'

    files_dict = {}

    # FIXME: Possible problems in file parsing
    for file in files:
        filename = file.split('/')[-1]
        fileContent = open(file, 'r').read()
        files_dict[filename] = {'content': fileContent, 'filename': filename}

    json_dict = {
        'description': desc,
        'files': files_dict,
    }

    # convert json_dict to JSON
    json_data = json.dumps(json_dict)
    # convert str to bytes (ensure encoding is OK)
    post_data = json_data.encode('utf-8')

    # we should also say the JSON content type header
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'token ' + TOKEN
    }

    # now do the request for a url
    req = urllib.request.Request(url, post_data, headers, method='PATCH')

    # send the request
    res = urllib.request.urlopen(req)

    if res.code == 200:
        print('Gist edited!')



if __name__ == '__main__':

    # TODO: refactor argparse

    parser = argparse.ArgumentParser(description='Github Gists CLI')
    parser.add_argument('name', type=str, help='Name of method')
    parser.add_argument('-id', '--gist_id', type=str, help='Gist ID')
    parser.add_argument('-u', '--username', type=str, help='Name of user')
    parser.add_argument('-f', '--files', nargs='*', help='Path to files')
    parser.add_argument('-d', '--description', type=str, default='', help='A descriptive name for this gist.')
    parser.add_argument('-p', '--public', type=str, default='yes', help='Gist status(public or private). Default is Public')

    args = parser.parse_args()


    # ====== Get a single gist ======
    # https://developer.github.com/v3/gists/#get-a-single-gist
    if args.name == 'gist':
        getSingleGist(args.gist_id)

    # ====== List a user's gists ======
    # https://developer.github.com/v3/gists/#list-a-users-gists
    if args.name == 'list':
        getAllGists(args.username)

    # ====== Create a gist ======
    # https://developer.github.com/v3/gists/#create-a-gist
    if args.name == 'create':
        for file in args.files:
            if not os.path.isfile(file):
                raise Exception(f"{file} IS NOT A FILE")
        createGist(args.files, args.description, args.public)
    
    # ====== Edit a gist ======
    # https://developer.github.com/v3/gists/#edit-a-gist
    if args.name == 'edit':
        for file in args.files:
            if not os.path.isfile(file):
                raise Exception(f"{file} IS NOT A FILE")
        editGist(args.gist_id, args.description, args.files)


    else:
        print(
            f"""gist_api: {args.name} is not a gist_api command. See 'gist_api --help'."""
        )



