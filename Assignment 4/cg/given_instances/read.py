with open('square.col', 'r') as f:
    file = f.readlines()
    for index in range(len(file)):
        if index == 0:
            continue
        else:
            content = file[index][: -1]
            print(content.split(' '))