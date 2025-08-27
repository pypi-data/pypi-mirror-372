from pathlib import Path
from configset import configset
import json
# from pydebugger.debug import debug
import os
from rich.theme import Theme
from rich.console import Console

class ClassMethodMeta(type):
    def __new__(mcs, name, bases, attrs):
        # print(f"mcs: {mcs} --> type: {type(mcs)}")
        # print(f"name: {name} --> type: {type(name)}")
        # print(f"bases: {bases} --> type: {type(bases)}")
        # print(f"attrs: {attrs} --> type: {type(attrs)}")
        # Buat instance internal untuk configset
        # config_file = str(Path.cwd() / 'debug.ini') if (Path.cwd() / 'debug.ini').is_file() else str(Path(__file__).parent / "debug.ini")
        attrs['_config_instance'] = configset(attrs.get('_config_ini_file'))


        # Fungsi pembungkus untuk mengubah method menjadi classmethod
        def make_classmethod(method):
            @wraps(method)
            def classmethod_wrapper(cls, *args, **kwargs):
                # Panggil method pada instance internal
                return method(cls._config_instance, *args, **kwargs)
            return classmethod(classmethod_wrapper)

        # Ambil semua method dari base class dan attrs, lalu jadikan classmethod
        for base in bases:
            for attr_name, attr_value in base.__dict__.items():
                if callable(attr_value) and not attr_name.startswith('__'):
                    attrs[attr_name] = make_classmethod(attr_value)
        for attr_name, attr_value in attrs.copy().items():
            if callable(attr_value) and not attr_name.startswith('__'):
                attrs[attr_name] = make_classmethod(attr_value)

        return super().__new__(mcs, name, bases, attrs)
    
    def __getattr__(cls, name):
        # Ambil dari instance internal
        # print(f"cls._config_instance: {cls._config_instance} --> type: {type(cls._config_instance)}")
        # print(f"name: {name} --> type: {type(name)}")

        if hasattr(cls._config_instance, name):
            return getattr(cls._config_instance, name)
        # Cek di _data jika ada
        # if hasattr(cls._config_instance, '_data') and name in cls._config_instance._data:
        if hasattr(cls, '_data') and name in cls._data:
            return cls._data[name]
        raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

    def __setattr__(cls, name, value):
        # Set ke instance internal jika ada di _data
        if hasattr(cls, '_config_instance') and hasattr(cls._config_instance, '_data') and name in cls._config_instance._data:
            cls._config_instance._data[name] = value
            # Simpan ke file jika perlu
            if hasattr(cls._config_instance, '_config_file'):
                with open(cls._config_instance._config_file, "w") as f:
                    json.dump(cls._config_instance._data, f, indent=4)
        else:
            super().__setattr__(name, value)


class CONFIG(metaclass=ClassMethodMeta):
    _name = 'config'
    _config_file = Path.cwd() / f'{_name}.json' if (Path.cwd() / f'{_name}.json').is_file() else '' or Path(__file__).parent / f"{_name}.json"
    _config_ini_file = str(Path.cwd() / f'{_name}.ini') if (Path.cwd() / f'{_name}.ini').is_file() else "" or str(Path(__file__).parent / f"{_name}.ini")
    config = configset(_config_ini_file)
    
    _data = {
        'args' : config.get_config('colors', 'args', "bold #FFFF00") or "bold #FFFF00",
        'groups' : config.get_config('colors', 'groups', "#AA55FF") or "#AA55FF",
        'help' : config.get_config('colors', 'help', "bold #00FFFF") or "bold #00FFFF",
        'metavar' : config.get_config('colors', 'metavar, "bold #FF55FF"') or "bold #FF55FF",
        'syntax' : config.get_config('colors', 'syntax', "underline") or "underline",
        'text' : config.get_config('colors', 'text', "white") or "white",
        'prog' : config.get_config('colors', 'prog', "bold #00AAFF italic") or "bold #00AAFF italic",
        'default'  : config.get_config('colors', 'default', 'bold') or "bold",
    }

    #debug(_data = _data)

    _data_default = _data

    def __init__(self):
        # Load existing configuration if the file exists
        if self._config_file.exists():
            with open(self._config_file, "r") as f:
                self._data = json.load(f)

    def __getattr__(self, name):
        # Retrieve a value from the configuration data
        if name in self._data:
            return self._data[name]
        elif self._config_file.exists() and not name in self._data and name in self._data_default:
            self.__setattr__(name, '')
            return self._data[name]
            
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @classmethod
    def get_config(cls, section, option):
        return cls.config.get_config(section, option)
    
    @classmethod
    def write_config(cls, section, option):
        return cls.config.write_config(section, option)

    @classmethod
    def set(cls, key, value):
        key = str(key).upper()  
        cls.console.print(f"[bold #FFFF00]Write/Set config[/] [bold #00FFFF]{key}[/] [bold #FFAAFF]-->[/] [bold ##00AAFF]{value if value else ''}[/]")
        if str(value).isdigit(): value = int(value)
        return CONFIG().__setattr__(key, value)
    
    def __setattr__(self, name, value):
        if name in {"_config_file", "_data"}:  # Allow setting internal attributes
            super().__setattr__(name, value)
        else:
            # Update the configuration data and save to the file
            self._data[name] = value
            with open(self._config_file, "w") as f:
                json.dump(self._data, f, indent=4)

