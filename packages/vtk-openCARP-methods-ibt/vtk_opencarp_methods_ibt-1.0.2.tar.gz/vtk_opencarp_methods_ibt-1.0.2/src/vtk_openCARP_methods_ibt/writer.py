def write_to_dat(filename, data):
    if not filename.endswith('.dat'):
        raise ValueError(f'Filename must end with .dat extension but was {filename}')
    f = open(filename, 'w')
    for i in data:
        f.write(f"{i:.4f}\n")
    f.close()
