def read_config(file):
    config = []
    with open(file, 'r') as file:
        config = file.readlines()
    return config