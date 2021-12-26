from __future__ import annotations
import abc
import atexit
from datetime import datetime
import logging
import os
import io

class IFileAppender(abc.ABC):
    @abc.abstractclassmethod
    def openStream(self) -> IFileAppender:
        pass
    
    @abc.abstractclassmethod
    def closeStream(self) -> None:
        pass
    
    @abc.abstractclassmethod
    def write(self, string:str):
        pass
    
    def __enter__(self):
        return self

    @abc.abstractclassmethod
    def __exit__(self, exc_type, exc_value, traceback):
        self.closeStream()
        


class DummyFileAppender(IFileAppender):
    def __init__(self, logname:str) -> None:
        self._fileName = f'../data/url_pioneer_{logname}.txt'
        atexit.register(self.closeStream)
    
    def openStream(self):
        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        print(f'FileOpenEvent: ({timestamp})')
        print(f'DummyFileNamedEvent: ({self._fileName})')
        return self
        

    def closeStream(self):
        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        print(f'FileCloseEvent: ({timestamp})')
        
    def write(self, string:str):
        print(f'DummyFileWriteEvent: {string}')
            
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeStream()

class FileAppender(IFileAppender):
    def __init__(self, logname:str) -> None:
        parent_dir = os.getcwd()
        if os.path.basename(parent_dir) == 'notebooks':
            parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        
        self._fileName = os.path.join(parent_dir, f'data/url_pioneer_{logname}.txt')
        if not os.path.exists(self._fileName):
            with open(self._fileName, 'w') as f:
                pass
        self._file:io.TextIOWrapper = None
        atexit.register(self.closeStream)
    
    def openStream(self):
        self._file = open(self._fileName, 'a+')
        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        self._file.write(f'FileOpenEvent: ({timestamp})\n')
        return self
    
    def write(self, string:str):
        if self._file.writable:
            self._file.write(string)
    
    def closeStream(self):
        if self._file is not None:
            try:
                timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
                self._file.write(f'FileCloseEvent: ({timestamp})\n')
            except Exception as e:
                logging.error(e)
            self._file.close()
            self._file = None
            
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            self.closeStream()
            
            # Line below to delete the file:
            # os.unlink(self._file)