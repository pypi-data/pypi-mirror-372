import time
import sys

class runtime_error:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:runtime_error \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info()
    
class out_of_range:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:out_of_range \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info
    
class logic_error:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:logic_error \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info

class domain_error:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:domain_error \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info

class invalid_arguments:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:invalid_arguments \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info

class length_error:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:length_error \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info

class range_error:
    def __init__(self,info:str):
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called an instance of:range_error \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info

class custom_error:
    def __init__(self,name:str,info:str):
        self.instance_name=name
        self.what_info=info
        self.terminal()
        time.sleep(2)
        sys.exit()
    def terminal(self):
        print('Terminal called after custom_error an instance of:'+self.instance_name+' \n')
        print('     what(): '+self.what_info+'\n')
    def what(self) -> str:
        return self.what_info