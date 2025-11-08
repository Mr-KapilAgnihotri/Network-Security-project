from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    """_summary_
        This function will return list of requirements
    """
    requirements_list:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            lines=file.readlines()
            for line in lines:
                requirements=line.strip()
                #ignore empty line and -e.
                if requirements and requirements!='-e .':
                    requirements_list.append(requirements)
    except FileNotFoundError:
        print("Requirements.txt file not found")                
    return requirements_list    
        
        
setup(
    name="Network Security Project",
    version="0.0.1",
    author="Kapil Agnihotri",
    author_email="Kapilagnihotri123ka@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()   
)        