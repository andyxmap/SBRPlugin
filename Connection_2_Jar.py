
import subprocess
from sys import platform
import os
from pathlib import WindowsPath, PosixPath, Path



class Connection:
    def __init__(self,path):
        self.path_2_jar = str(path)
        self.platform = platform

        self._jvm_installed()
        self.check_is_Jar()


    def check_is_Jar(self):
           if self.platform == 'win32':
               self.path_2_jar = WindowsPath(self.path_2_jar)
               if self.path_2_jar.suffix != '.jar' or not self.path_2_jar.exists():
                   raise Exception("The path not is a jar file")

           elif self.platform == 'linux':
               pass



    def _jvm_installed(self):

           if self.platform == "win32":
              env_data = os.environ["PROGRAMDATA"]
              env_jar =  "\Oracle\Java\javapath"

              os.environ["PATH"] += ";"+ env_data + env_jar

              if os.system('java -version') != 0:
                  raise NotImplementedError("Java Virtual Machine is not found")

           elif self.platform == 'linux':
             pass





    def run_jar(self,string_args):

        start = subprocess.STARTUPINFO()
        start.wShowWindow = subprocess.SW_HIDE

        java_popen = subprocess.Popen("java -jar "+ str(self.path_2_jar) + 
                                                        " " + string_args,
                                      startupinfo=start,
                                      stdout=subprocess.DEVNULL,
                                      creationflags=subprocess.CREATE_NO_WINDOW)

        java_popen.communicate()
        
