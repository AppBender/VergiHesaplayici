import os
import shutil


class FileManager:
    def __init__(self):
        pass

    def clear_directory(self, dir_path):
        if not os.path.exists(dir_path):
            print(f'Directory {dir_path} does not exist.')
            return

        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    def create_file(self, file_path, content=''):
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
