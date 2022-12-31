import zipfile, os
from typing import overload

class DriverException(Exception):
    def __init__(self,message):
        super(DriverException, self).__init__(message)

class FileNotDefinedException(Exception):
    def __init__(self,message):
        super(FileNotDefinedException, self).__init__(message)

class ZipUtility:
    @overload
    def __init__(self, zip_file: str): ...
    @overload
    def __init__(self, zip_file: str, password: str): ...
    @overload
    def __init__(self, zip_file: str, to_path: str): ...
    @overload
    def __init__(self, zip_file: str, password: str, to_path: str): ...
    
    def __init__(self, zip_file: str, password: str = "", to_path: str = "./") -> None:  # type: ignore
        # assert zipfile.is_zipfile(zip_file)
        self.zip_file = zip_file
        self.password = password.encode("ascii")
        self.to_path = to_path
        
    @staticmethod
    def is_all_defined(files:list)->bool:
        return set(os.listdir()) & set(files) == set(files)


class ZipExtrator(ZipUtility):
    """
    # 解壓縮壓縮檔
    1. 支援解密壓縮檔
    2. 可選擇解壓縮檔案存放路徑
    """
    def unzip(self,create_folder_by_extension:bool=False)->None:
        """
        create_folder_by_extension若為True則會在to_path底下創建該檔案副檔名的資料夾 並將檔案放置在這底下 若為False會直接依照to_path放置在該路徑
        """
        with zipfile.ZipFile(self.zip_file, "r", zipfile.ZIP_DEFLATED) as zip_reader:
            file_extension = ""
            for file in zip_reader.namelist():
                if create_folder_by_extension:
                    file_extension:str = os.path.splitext(file)[1][1:]
                    if os.path.exists(os.path.join(self.to_path, file_extension)) is not True:
                        os.mkdir(file_extension)
                        
                path_args:list = list(filter(lambda x: x != "", [self.to_path, file_extension]))
                zip_reader.extract(file, path=fr".\{os.path.join(*path_args)}", pwd=self.password if self.password != b"" else None)
    
class ZipCreator(ZipUtility):
    """
    # 建立壓縮檔
    1. 支援加密壓縮 
    2. 支援多個檔案、資料夾，單個檔案、資料夾壓縮成壓縮檔
    """
    def __init__(self, zip_file: str, password: str = "", to_path: str = "./", zip_filename:str = os.path.basename(os.getcwd()), zip_driver:str = "./7z.exe"):
        if os.path.isfile(zip_driver) is False:
            raise DriverException("Zip driver not found")
        
        super().__init__(zip_file, password, to_path)
        self.zip_filename = zip_filename
        self.zip_driver = zip_driver


    def compress_files(self,src_path:str, files:list):
        if self.is_all_defined(files) is False:
            raise FileNotDefinedException("File not defined")
        
        import subprocess
        command = [self.zip_driver, 'a', '-p{}'.format(self.password), f"{self.zip_filename}"] + [os.path.join(src_path, file) for file in files]
        result = subprocess.run(command)
        return result.returncode == 0
    
if __name__ == "__main__":
    # 解壓縮檔案
    zip_file = ZipExtrator("aio.zip", password="1234", to_path="./") # V
    print(zip_file.unzip())
    
    # 檔案壓縮成壓縮檔
    create_zip = ZipCreator(zip_file = "123", password = "1234", zip_filename = "aio加密.zip")
    create_zip.compress_files(src_path="./", files= ["123.txt","1234.txt"])

        