import os.path

class FileUtils:
    @staticmethod
    def create_paths(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def read_file(path):
        content = ''
        with open(path,'r',encoding='utf-8') as file:
            content = file.read()
        return content

    @staticmethod
    def del_file(file_path):
        # 尝试删除文件
        try:
            os.remove(file_path)
            print(f"文件 '{file_path}' 已成功删除")
        except FileNotFoundError:
            print(f"文件 '{file_path}' 不存在")
        except PermissionError:
            print(f"没有权限删除文件 '{file_path}'")
        except Exception as e:
            print(f"删除文件时发生错误: {e}")