import pickle
import sys
from time import sleep
import re

import lxml
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from game import gameno

url = f"https://minesweeper.online/game/{gameno}"
print(url)


if sys.argv[1] == "1":
    driver_path = "./data/chromedriver-linux64/chromedriver"
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    sleep(5)
    resp = driver.page_source
    driver.quit()
    pickle.dump(resp, open("data/response.dump", 'wb'))
else:
    resp = pickle.load(open("data/response.dump", 'rb'))

soup = bs(resp, 'lxml')


def get_board():
    cells = soup.find_all('div', {"id": "AreaBlock"})[0].find_all(class_="cell")
    
    cells_new = []
    for cell in cells:
        cellclasses = cell["class"]
        if len(cellclasses)  == 3:
            celltype = "hdd_closed"
        else:
            celltype = cellclasses[3]
    
        cellpos = int(cell.get("data-x")), int(cell.get("data-y"))
        cells_new.append((celltype, cellpos))
    
    n = max(x[1][1] for x in cells_new) + 1
    m = max(x[1][0] for x in cells_new) + 1
    
    board = [[None for _ in range(m)] for _ in range(n)]
    for celltype, cellpos in cells_new:
        char = ""
        if celltype == "hdd_closed":
            char = "#"
        elif celltype == "hdd_flag":
            char = "b"
        else:
            char = celltype[len("hdd_type"):]
        board[cellpos[1]][cellpos[0]] = char
    
    return "\n".join("".join(x) for x in board)

def get_nbombs():
    top_10 = soup.find('div', {"id": "top_area_mines_10"})["class"]
    top_1 = soup.find('div', {"id": "top_area_mines_1"})["class"]

    for top in top_10, top_1:
        del top[top.index("zoomable")]
        del top[top.index("top-area-num")]
        del top[top.index("pull-left")]

    top_10 = top_10[0][len("hdd_top-area-num"):]
    top_1 = top_1[0][len("hdd_top-area-num"):]
    return int(top_10 + top_1)


board_str = get_board()
bombs_left = get_nbombs()
log = 0

with open("myboard.py", 'wt') as f:
    f.write(f"{bombs_left, log = }\n")
    f.write("board_str = '''\n")
    for line in board_str.split('\n'):
        f.write(line + "\n")
    f.write("'''")

