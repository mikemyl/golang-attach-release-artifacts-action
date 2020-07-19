#!/usr/bin/env python

import os
import subprocess
import tarfile
import json
import requests


def get_env_or_die(var_name):
    val = os.getenv(var_name)
    if not val:
        raise EnvironmentError("{} environment variable is not set".format(var_name))
    return val


# Environment dependencies
input_go_files = get_env_or_die("INPUT_GO_FILES")
input_binaries = get_env_or_die("INPUT_BINARIES")
input_linux_build_variants = get_env_or_die("INPUT_LINUX_BUILD_VARIANTS")
input_darwin_build_variants = get_env_or_die("INPUT_DARWIN_BUILD_VARIANTS")
github_workspace = get_env_or_die("GITHUB_WORKSPACE")
github_event_path = get_env_or_die("GITHUB_EVENT_PATH")

print("Github workspace: {}".format(github_workspace))
print(os.listdir(github_workspace))

with open(github_event_path) as f:
    github_event_data = json.load(f)
tag_name = github_event_data['ref'].replace("refs/tags/", "")
repo_owner, repo_name = github_event_data['repository']['full_name'].split('/')

print("Tag name: {}\nRepo oewner: {}\nRepo Name: {}".format(tag_name, repo_owner, repo_name))

go_files = input_go_files.split(" ")
binaries = input_binaries.split(" ")
linux_build_variants = input_linux_build_variants.split(" ") if input_linux_build_variants else []
darwin_build_variants = input_darwin_build_variants.split(" ") if input_darwin_build_variants else []

if not len(go_files) == len(binaries):
    raise AssertionError('Number of GO_FILES ({}) and BINARIES ({}) should be the same'.format(len(go_files), len(binaries)))

build_variants = {'linux': linux_build_variants, 'darwin': darwin_build_variants}

archives_to_upload = []
for op_sys, architectures in build_variants.items():
    for arch in architectures:
        archive_file_name = "{}-{}-{}.tar.gz".format(repo_name, op_sys, arch)
        env = os.environ
        env.update({'GOOS': op_sys, 'GOARCH': arch})
        target_dir = os.path.join('target')
        try:
            os.mkdir(target_dir)
        except OSError:
            print("Failed to create {} directory".format(target_dir))
        archive = os.path.join(target_dir, archive_file_name)
        with tarfile.open(archive, "w:gz") as tar:
            for i, file in enumerate(go_files):
                print(subprocess.check_output(["go", "build", "-v", "-o", os.path.join('target', binaries[i]), file], cwd=github_workspace, env=env).decode())
                tar.add(os.path.join(github_workspace, "target", binaries[i]), arcname=os.path.basename(os.path.join(target_dir, binaries[i])))
        archives_to_upload.append(archive)


headers = {'Authorization': "Bearer {}".format(os.getenv("INPUT_GITHUB_TOKEN"))}

create_release_url = "https://api.github.com/repos/{owner}/{repo}/releases".format(owner=repo_owner, repo=repo_name)
create_release_data = {'tag_name': tag_name}

ret = requests.post(create_release_url, json=create_release_data, headers=headers).json()
print("Post request to create release url returned: {}".format(ret))

upload_url = ret['upload_url'].replace('{?name,label}', "")
headers.update({'Content-Type': 'application/octet-stream'})
for archive in archives_to_upload:
    filename = os.path.basename(archive)
    print(upload_url + '?name=' + filename)
    ret = requests.post(upload_url + '?name=' + filename, headers=headers, data=open(archive, 'rb').read())

