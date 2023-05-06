import subprocess

def check_dependency_installed(dependency_name, version_arg):
    try:
        output = subprocess.check_output([dependency_name, version_arg], stderr=subprocess.STDOUT, universal_newlines=True)
        print(f"{dependency_name} is installed:")
        print(output)
        return True
    except FileNotFoundError:
        print(f"{dependency_name} is not installed.")
        return False