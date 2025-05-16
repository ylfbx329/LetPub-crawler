import json
import time
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.edge.options import Options

from crawler.utils import get_page, parse_journal_info

base_url = r'https://www.letpub.com.cn'
result_file = Path(r'journals.ndjson')
proxy = '127.0.0.1:7891'

edge_options = Options()
edge_options.add_argument(f'--proxy-server=http://{proxy}')
driver = webdriver.Edge(options=edge_options)


def main():
    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        id_list = [item['id'] for item in data]
    else:
        id_list = []

    max_journal_id = 44587

    for i in range(1, max_journal_id + 1):
        if i in id_list:
            continue
        url = f'https://www.letpub.com.cn/index.php?journalid={i}&page=journalapp&view=detail'
        soup = get_page(driver, url)
        journal = parse_journal_info(soup)
        journal.id = i
        journal.letpub_link = url

        journal_dict = vars(journal)
        print(i)

        with open(result_file, 'a', encoding="utf-8") as f:
            f.write(json.dumps(journal_dict, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except Exception:
            traceback.print_exc()  # 打印完整错误堆栈
            print(f"出错了，60秒后重试...")
            time.sleep(60)
    print(f"已全部保存为 csv 文件：journals.csv")
