# Import the Libraries
from pydrive.auth import GoogleAuth
import streamlit as st
from pydrive.drive import GoogleDrive
import os

st.set_page_config(layout="wide", page_title='York Archive')
row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((3, .2, 0.55, .1))
row0_1.title('York Data Archive')
with row0_2:
    st.write('')

st.subheader("")
with st.form("my_form"):
    place = st.text_input("Target", "Polaris")
    parent_folder_id = st.text_input("Parent ID (exp. 14bMWZWJeLGoZR-UaksDX5gFGaNzB8c6C)", "")
    parent_folder_dir = st.text_input("Parent Directory (exp. /home/toby/Downloads)", "")
    submit = st.form_submit_button(label="Submit")

# A browser window will open. login using the appropriate account.
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Set the id of the Google Drive folder. You can find it in the URL of the google drive folder.
#   parent_folder_id = '14bMWZWJeLGoZR-UaksDX5gFGaNzB8c6C'
# Set the parent folder, where you want to store the contents of the google drive folder
#   parent_folder_dir = '/home/toby/Downloads/Data/XXCyg'

if parent_folder_dir[-1] != '/':
    parent_folder_dir = parent_folder_dir + '/'

# This is the base wget command that we will use. This might change in the future due to changes in Google drive
wget_text = '"wget "https://docs.google.com/uc?export=download&amp;confirm=$(wget --quiet --keep-session-cookies --no-check-certificate \'https://docs.google.com/uc?export=download&amp;id=FILEID\' -O- | sed -rn \'s/.*confirm=([0-9A-Za-z_]+).*/\\1\\n/p\')&id=FILEID" -O FILENAME"'.replace('&amp;', '&')
# Get the folder structure

file_dict = dict()
folder_queue = [parent_folder_id]
dir_queue = [parent_folder_dir]
cnt = 0

while len(folder_queue) != 0:
    current_folder_id = folder_queue.pop(0)
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(current_folder_id)}).GetList()

    current_parent = dir_queue.pop(0)
    st.caption(current_parent + current_folder_id)
    for file1 in file_list:
        file_dict[cnt] = dict()
        file_dict[cnt]['id'] = file1['id']
        file_dict[cnt]['title'] = file1['title']
        file_dict[cnt]['dir'] = current_parent + file1['title']

        if file1['mimeType'] == 'application/vnd.google-apps.folder':
            file_dict[cnt]['type'] = 'folder'
            file_dict[cnt]['dir'] += '/'
            folder_queue.append(file1['id'])
            dir_queue.append(file_dict[cnt]['dir'])
        else:
            file_dict[cnt]['type'] = 'file'

        cnt += 1


# /home/toby/Data/Exposures -20/0.1s/domeBlue_FlatField00000012.fit -------------> /home/toby/Data/Blue 15s/domeBlue_FlatField00000008.fit
def absolutePath(directory):
    path_list = directory.split(os.sep)
    last = len(path_list) - 1
    sec_last = len(path_list) - 2
    absolute_path = str(parent_folder_dir) + '/' + str(path_list[sec_last]) + '/' + str(path_list[last])

    return absolute_path


def script_run():
    download = input("DOWNLOAD(Y/N): ")
    if download == 'y' or download == 'Y':
        os.system('chmod 777 script.sh')
        os.system('./script.sh')


# Write the bash script
def script():
    os.system('chmod 777 script.sh')
    os.system('sh script.sh')
    f = open('script.sh', 'w')

    # Write the bash script
    file_dict.keys()
    for file_iter in file_dict.keys():
        if file_dict[file_iter]['type'] == 'file':
            if "polaris" in str(file_dict[file_iter]['title']) or "Polaris" in str(file_dict[file_iter]['title']):
                path_list = file_dict[file_iter]['dir'].split(os.sep)
                sec_last = len(path_list) - 2
                space_path = str(path_list[sec_last])
                if ' ' in str(space_path):
                    absolute_path2 = space_path.replace(' ', '-')
                    f.write('mkdir ' + str(parent_folder_dir) + str(absolute_path2) + '\n')
                else:
                    f.write('mkdir ' + str(parent_folder_dir) + str(path_list[sec_last]) + '\n')
                filename = absolutePath(file_dict[file_iter]['dir'])
                filename2 = absolutePath(file_dict[file_iter]['dir']).split(os.sep)
                sec_last = len(filename2) - 2
                last = len(filename2) - 1
                filename3 = filename2[sec_last]
                if ' ' in str(filename2[sec_last]):
                    filename3 = str(filename3).replace(' ', '-')
                    wget_filename = str(parent_folder_dir) + '/' + str(filename3) + '/' + str(filename2[last])
                    f.write(wget_text[1:-1].replace('FILEID', file_dict[file_iter]['id']).replace('FILENAME',
                                                                                                  str(wget_filename) + '\n'))
                else:
                    f.write(wget_text[1:-1].replace('FILEID', file_dict[file_iter]['id']).replace('FILENAME',
                                                                                                  str(filename) + '\n'))

    f.close()

    '''
    download = input("DOWNLOAD(Y/N): ")
    if download == 'y' or download == 'Y':
        os.system('./script.sh')
    '''


script()
