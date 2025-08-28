import json
import re
import yaml
import os
import inspect
class DynamyqueObject:
    def __init__(self):
        pass
class Config:

    def __init__(self,file_name):
        caller_frame = inspect.stack()[1]
        caller_file = caller_frame.filename
        self.__base_dir = os.path.dirname(os.path.abspath(caller_file))
        self.__file_name = file_name
        self.__file_path = os.path.join(self.__base_dir,self.__file_name)
        self.__extensions = self.__find_good_extensions()

        match self.__extensions :
            case "json":
                self.__data = self.__get_env_data()
            case "env" :
                self.__data = self.__get_env_from_dot_env()
            case "yaml":
                self.__data = self.__get_env_data()
            case _ :
                self.__data = {}
        self.__set_attribute(self, self.__data)

    def __set_attribute(self,obj, data):
        for key, value in data.items():
            if isinstance(value, dict):
                sub_object = DynamyqueObject()
                setattr(obj, key, sub_object)
                self.__set_attribute(sub_object, value)
            else:
                setattr(obj, key, value)

    def __get_env_data(self):
        with open(self.__file_path, 'r') as f:
            if self.__extensions == "json":
                return json.loads(f.read())
            elif self.__extensions == "yaml":
                return yaml.safe_load(f)



    def __find_good_extensions(self):
        extensions = re.findall(r"\.[a-zA-Z]+$", self.__file_name)[0].split(".")[1]
        match extensions:
            case "env":
                return "env"
            case "json":
                return "json"
            case "yaml":
                return "yaml"
            case _:
                return False

    def __get_env_from_dot_env(self):
        dico = {}
        with open(self.__file_path, "r") as f:
            data = f.readlines()
            cleanData = [line.replace("\n", "") for line in data]
            for line in cleanData:
                if re.match(r"^\s*#", line):
                    continue
                match = re.match(r"^\.?([a-zA-Z0-9_.-]+)=(.+)$", line)
                if match:
                    dico[match.group(1)] = match.group(2)
        return dico