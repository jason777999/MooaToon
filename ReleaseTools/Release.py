import os
import sys
import subprocess
import datetime
import github_release as ghr
import github3 as gh
from dotenv import load_dotenv
import winreg


# ================= Defines =================
engine_version = "5.2"
repo_name = "JasonMa0012/MooaToon"
mooatoon_root_path = r"X:\MooaToon"
if len(sys.argv) > 1:
    mooatoon_root_path = sys.argv[1]

# Debug
argv = [
    '--Release'
]

if len(sys.argv) > 2:
    argv = sys.argv[2:]

current_date = datetime.date.today().strftime("%Y.%m.%d")
release_name = engine_version + "-" + current_date

bandizip_path = mooatoon_root_path + r"\InstallTools\BANDIZIP-PORTABLE\Bandizip.x64.exe"
zip_path = mooatoon_root_path + r"\ReleaseTools\Zip"
engine_path = mooatoon_root_path + r"\MooaToon-Engine"
project_path = mooatoon_root_path + r"\MooaToon-Project"
engine_zip_path = zip_path + r"\MooaToon-Engine-Precompiled-" + release_name + ".zip"
project_zip_path = zip_path + r"\MooaToon-Project-Precompiled-" + release_name + ".zip"

engine_user = 'Jason-Ma-0012'
engine_repo = 'MooaToon-Engine'


# ============ Functions ==============
def get_onedrive_env_path():
    # 打开 OneDrive 注册表项
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\OneDrive", 0, winreg.KEY_READ) as key:
        # 获取 OneDrive 安装路径的值
        envPath, _ = winreg.QueryValueEx(key, "UserFolder")

    return os.path.join(envPath, '_Data', 'envs', 'MooaToon.env')


def get_release_comment(last_release_date = '2023-06-23'):
    g = gh.login(token=os.getenv('MOOATOON_ENGINE_TOKEN'))
    repo : gh.github.repo.Repository = g.repository(engine_user, engine_repo)
    comment = ''
    for commit in repo.commits(since=last_release_date):
        comment += f'\n[[{commit.sha[0:7]}]({commit.html_url})]\n'
        comment += commit.message
        comment += '\n'
    return comment


def async_run(args):
    # 使用 subprocess.Popen() 函数异步执行 bat 文件，并获取 stdout 和 stderr 输出
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    return process.poll()


# ================= Main ==================
load_dotenv(dotenv_path=get_onedrive_env_path())

if '--Clean' in argv:
    print("======Clean======")
    for file_name in os.listdir(zip_path):
        file_path = os.path.join(zip_path, file_name)
        os.remove(file_path)
        print(file_path)

if '--BuildEngine' in argv:
    print("======Build Engine======")
    os.chdir(engine_path)
    async_run([engine_path + r"\_build.bat"])

if '--CleanEngine' in argv:
    print("======Clean Engine======")
    async_run([engine_path + r"\_clean.bat"])

if '--ZipEngine' in argv:
    print("======Zip Engine======")
    args = [bandizip_path, "a", "-l:9", "-y", "-v:2000MB", "-t:60", engine_zip_path, engine_path + r"\LocalBuilds\Engine", ]
    async_run(args)

if '--ZipProject' in argv:
    print("======Zip Project======")
    args = [bandizip_path, "a", "-l:9", "-y", "-v:2000MB", "-t:60", project_zip_path,
            project_path + r"\Art",
            project_path + r"\Config",
            project_path + r"\Content",
            project_path + r"\MooaToon_Project.uproject", ]
    async_run(args)

file_paths = []
for file_name in os.listdir(zip_path):
    file_path = os.path.join(zip_path, file_name)
    file_paths.append(file_path)

last_release_info = None
for release in ghr.get_releases(repo_name):
    if (not release['draft']) and (release['tag_name'].startswith(engine_version)):
        last_release_info = release
        break

if '--Release' in argv:
    print("======Release======")
    comment = get_release_comment(last_release_info['published_at'][0:10])
    # print('\n' + comment + '\n')
    ghr.gh_release_create(
        repo_name,
        release_name,
        publish=False,
        body=comment,
        name=release_name,
        asset_pattern=file_paths,
    )
    ghr.gh_release_publish(repo_name, release_name)

if '--Reupload' in argv:
    print("======Reupload======")
    current_release_info = ghr.get_release(repo_name, release_name)
    tag_name = current_release_info['tag_name']

    # 仅上传失败的文件
    for asset in current_release_info['assets']:
        for file_path in file_paths:
            if file_path.endswith(asset['name']):
                file_paths.remove(file_path)

    ghr.gh_asset_upload(repo_name, tag_name, file_paths)
    ghr.gh_release_publish(repo_name, tag_name)


input("\nPress Enter to continue...")