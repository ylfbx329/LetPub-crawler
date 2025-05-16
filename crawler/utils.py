import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from crawler.journal import Journal


def get_page(driver, url):
    driver.get(url)
    time.sleep(2)

    close_popups(driver)
    # 解析渲染后页面
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    return soup


def close_popups(driver, timeout=0.5):
    """
    在任意时刻尝试关闭 LetPub 弹窗（广告和注册提示），不抛错
    :param driver:
    :param timeout:
    :return:
    """
    for class_name in ["layui-layer-close1", "layui-layer-close2"]:
        try:
            wait = WebDriverWait(driver, timeout)
            # btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
            btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            driver.execute_script("arguments[0].click();", btn)
        except:
            pass  # 没有弹窗就跳过


def parse_journal_info(soup):
    journal = Journal()

    # 期刊信息表格
    table_tag = soup.select_one('#yxyz_content > table:nth-of-type(3)')

    # 遍历所有 tr 行
    for tr in table_tag.tbody.find_all('tr', recursive=False):
        tds = tr.find_all('td')
        if not tds:
            continue  # 跳过空行或无 td 的行

        first_cell_text = tds[0].get_text(strip=True)

        if '期刊名字' in first_cell_text:
            # 期刊名
            name_tag = tr.select_one('td:nth-child(2) > span:nth-child(1) > a')
            journal.name = name_tag.get_text(strip=True)
            # 简称
            shortname_tag = tr.select_one('td:nth-child(2) > span:nth-child(1) > font')
            journal.shortname = shortname_tag.get_text(strip=True)
            # letpub评分
            letpub_score_tag = tr.select_one('td:nth-child(2) > span:nth-child(2) > span:nth-child(2) > div:nth-child(1)')
            journal.letpub_score = letpub_score_tag.get_text(strip=True)
            # letpub打分人数
            score_people_tag = tr.select_one('td:nth-child(2) > span:nth-child(2) > span:nth-child(2) > div:nth-child(3)')
            journal.score_people = score_people_tag.get_text(strip=True).split('人')[0]
            # 声誉分
            reputation_score_tag = tr.select_one('td:nth-child(2) > span:nth-child(2) > div:nth-child(6)')
            journal.reputation_score = reputation_score_tag.get_text(strip=True)
            # 影响力分
            influence_score_tag = tr.select_one('td:nth-child(2) > span:nth-child(2) > div:nth-child(10)')
            journal.influence_score = influence_score_tag.get_text(strip=True)
            # 速度分
            speed_score_tag = tr.select_one('td:nth-child(2) > span:nth-child(2) > div:nth-child(14)')
            journal.speed_score = speed_score_tag.get_text(strip=True)
        elif '期刊ISSN' in first_cell_text:
            # 期刊ISSN
            ISSN_tag = tr.select_one('td:nth-child(2)')
            journal.issn = ISSN_tag.get_text(strip=True)
        elif 'P-ISSN' in first_cell_text:
            # P-ISSN
            P_ISSN_tag = tr.select_one('td:nth-child(2)')
            journal.p_issn = P_ISSN_tag.get_text(strip=True)
        elif 'E-ISSN' in first_cell_text:
            # E-ISSN
            E_ISSN_tag = tr.select_one('td:nth-child(2)')
            journal.e_issn = E_ISSN_tag.get_text(strip=True)
        elif '2023-2024最新影响因子' in first_cell_text:
            # 2023-2024最新影响因子
            if_tag = tr.select_one('td:nth-child(2)')
            journal.impact_factor = if_tag.text.split('点击')[0].strip()
        elif '实时影响因子' in first_cell_text:
            # 实时影响因子
            real_time_if_tag = tr.select_one('td:nth-child(2)')
            journal.real_time_if = real_time_if_tag.get_text(strip=True).split('：')[-1]
        elif '2023-2024自引率' in first_cell_text:
            # 2023-2024自引率
            self_cite_rate_tag = tr.select_one('td:nth-child(2)')
            journal.self_cite_rate = self_cite_rate_tag.text.split('点击')[0].strip()
        elif '五年影响因子' in first_cell_text:
            # 五年影响因子
            five_year_if_tag = tr.select_one('td:nth-child(2)')
            journal.five_year_if = five_year_if_tag.get_text(strip=True)
        elif 'JCI期刊引文指标' in first_cell_text:
            # JCI期刊引文指标
            jci_tag = tr.select_one('td:nth-child(2)')
            journal.jci = jci_tag.get_text(strip=True)
        elif 'h-index' in first_cell_text:
            # h-index
            h_index_tag = tr.select_one('td:nth-child(2)')
            journal.h_index = h_index_tag.get_text(strip=True)
        elif 'CiteScore' in first_cell_text:
            tr_tr = tr.select_one('td:nth-child(2) > table > tbody > tr:nth-child(2)')
            if tr_tr:
                cite_score_tag = tr_tr.select_one('td:nth-child(1)')
                journal.cite_score = cite_score_tag.get_text(strip=True)

                sjr_tag = tr_tr.select_one('td:nth-child(2)')
                journal.sjr = sjr_tag.get_text(strip=True)

                snip_tag = tr_tr.select_one('td:nth-child(3)')
                journal.snip = snip_tag.get_text(strip=True)

                tab_tag = tr_tr.select_one('td:nth-child(4) > table')
                tr_tr_tr = tab_tag.find_all('tr')[1:]
                rank_dict = {'学科': '', '分区': '', '排名': '', '百分位': ''}
                for tmp_tr in tr_tr_tr:
                    subject_tag = tmp_tr.select_one('td:nth-child(1)')
                    subject = subject_tag.get_text(strip=True)
                    major = subject.split("大类：")[1].split("小类：")[0].strip()
                    minor = subject.split("小类：")[1].strip()
                    rank_dict['学科'] = major + '-' + minor

                    part_tag = tmp_tr.select_one('td:nth-child(2)')
                    rank_dict['分区'] = part_tag.get_text(strip=True)

                    rank_tag = tmp_tr.select_one('td:nth-child(3)')
                    rank_dict['排名'] = rank_tag.get_text(strip=True)

                    percentage_tag = tmp_tr.select_one('td:nth-child(4)')
                    rank_dict['百分位'] = percentage_tag.get_text(strip=True)

                    journal.cite_score_rank.append(rank_dict)

        elif '期刊简介' in first_cell_text:
            # 期刊简介
            intro_tag = tr.select_one('#readmore_content')
            journal.intro = intro_tag.get_text(strip=True)
        elif '期刊官方网站' in first_cell_text:
            # 期刊官方网站
            website_tag = tr.select_one('td:nth-child(2) > a')
            journal.website = website_tag.get_text(strip=True)
        elif '期刊投稿格式模板' in first_cell_text:
            # 会员信息，不做处理
            pass
        elif '期刊投稿网址' in first_cell_text:
            # 期刊投稿网址
            submission_url_tag = tr.select_one('td:nth-child(2) > a')
            journal.submission_url = submission_url_tag.get_text(strip=True)
        elif '作者指南网址' in first_cell_text:
            # 作者指南网址
            guidelines_url_tag = tr.select_one('td:nth-child(2) > a')
            journal.guidelines_url = guidelines_url_tag.get_text(strip=True)
        elif '期刊语言要求' in first_cell_text:
            language_require_tag = tr.select_one('td:nth-child(2)')
            journal.language_require = language_require_tag.get_text(strip=True).split('经LetPub语言')[0].strip()
        elif '是否OA开放访问' in first_cell_text:
            # 是否OA开放访问
            open_access_tag = tr.select_one('td:nth-child(2)')
            journal.open_access = open_access_tag.get_text(strip=True) == 'Yes'
        elif 'OA期刊相关信息' in first_cell_text:
            oa_info_tag = tr.select_one('td:nth-child(2)')
            match = re.search(r'USD\s?(\d+)', oa_info_tag.get_text(strip=True))
            journal.oa_price = int(match.group(1)) if match else None
        elif '通讯方式' in first_cell_text:
            # 通讯方式
            communication_tag = tr.select_one('td:nth-child(2)')
            journal.communication = communication_tag.get_text(strip=True)
        elif '出版商' in first_cell_text:
            # 出版商
            publisher_tag = tr.select_one('td:nth-child(2)')
            journal.publisher = publisher_tag.get_text(strip=True)
        elif '涉及的研究方向' in first_cell_text:
            # 涉及的研究方向
            field_tag = tr.select_one('td:nth-child(2)')
            journal.field = field_tag.get_text(strip=True)
        elif '出版国家或地区' in first_cell_text:
            # 出版国家或地区
            country_tag = tr.select_one('td:nth-child(2)')
            journal.country = country_tag.get_text(strip=True)
        elif '出版语言' in first_cell_text:
            # 出版语言
            language_tag = tr.select_one('td:nth-child(2)')
            journal.language = language_tag.get_text(strip=True)
        elif '出版周期' in first_cell_text:
            # 出版周期
            period_tag = tr.select_one('td:nth-child(2)')
            journal.period = period_tag.get_text(strip=True)
        elif '出版年份' in first_cell_text:
            # 出版年份
            start_year_tag = tr.select_one('td:nth-child(2)')
            journal.start_year = start_year_tag.get_text(strip=True)
        elif '年文章数' in first_cell_text:
            # 年文章数
            year_paper_tag = tr.select_one('td:nth-child(2)')
            journal.year_paper = year_paper_tag.text.split('点击')[0].strip()
        elif 'Gold OA文章占比' in first_cell_text:
            # Gold OA文章占比
            gold_oa_tag = tr.select_one('td:nth-child(2)')
            journal.gold_oa = gold_oa_tag.get_text(strip=True)
        elif '研究类文章占比' in first_cell_text:
            # 研究类文章占比
            research_ratio_tag = tr.select_one('td:nth-child(2)')
            journal.research_ratio = research_ratio_tag.get_text(strip=True)
        elif 'WOS期刊SCI分区' in first_cell_text:
            sci_part_tag = tr.select_one('td:nth-child(2) > span')
            journal.sci_part = sci_part_tag.get_text(strip=True)

            tab_tags = tr.find_all('table')
            if tab_tags:
                rank_dict = {'学科': '', '收录子集': '', '分区': '', '排名': '', '百分位': ''}
                for tab_tag in tab_tags:
                    tr_tr = tab_tag.select_one('tbody > tr:nth-child(2)')
                    subject_tag = tr_tr.select_one('td:nth-child(1)')
                    rank_dict['学科'] = subject_tag.get_text(strip=True).split('学科：')[1].strip()

                    subset_tag = tr_tr.select_one('td:nth-child(2)')
                    rank_dict['收录子集'] = subset_tag.get_text(strip=True)

                    part_tag = tr_tr.select_one('td:nth-child(3)')
                    rank_dict['分区'] = part_tag.get_text(strip=True)

                    rank_tag = tr_tr.select_one('td:nth-child(4)')
                    rank_dict['排名'] = rank_tag.get_text(strip=True)

                    percentage_tag = tr_tr.select_one('td:nth-child(5)')
                    rank_dict['百分位'] = percentage_tag.get_text(strip=True)

                    tmp_td_tag = tab_tag.select_one('tbody > tr:nth-child(1) > td:nth-child(1)')
                    if '按JIF指标学科分区' in tmp_td_tag.get_text(strip=True):
                        journal.jif_sci_rank = rank_dict
                    elif '按JCI指标学科分区' in tmp_td_tag.get_text(strip=True):
                        journal.jci_sci_rank = rank_dict

        elif '中国科学院《国际期刊预警名单（试行）》名单' in first_cell_text:
            warning_tag = tr.select_one('td:nth-child(2)')
            # 匹配每一年的状态（每段格式必须有“：XXX”结尾）
            pattern = r'\d{4}年\d{2}月发布的\d{4}版：(.*?)\s*(?=\d{4}年|\Z)'
            matches = re.findall(pattern, warning_tag.get_text(strip=True))
            journal.warning = not all(s.strip() == '不在预警名单中' for s in matches)
        elif '中国科学院SCI期刊分区' in first_cell_text and '2025年3月最新升级版' in first_cell_text:
            tab_tags = tr.select_one('table')
            if tab_tags:
                part_dict = {'大类学科': '', '小类学科': '', 'Top期刊': False, '综述期刊': False, '分区': ''}
                major_subject_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(1)')
                part_dict['大类学科'] = major_subject_tag.find(text=True, recursive=False).strip()

                minor_subject_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td:nth-child(1)')
                part_dict['小类学科'] = minor_subject_tag.get_text(strip=True)

                top_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(3)')
                part_dict['Top期刊'] = top_tag.get_text(strip=True) == '是'

                review_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(4)')
                part_dict['综述期刊'] = review_tag.get_text(strip=True) == '是'

                part_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(1) > span:nth-child(2)')
                part_dict['分区'] = part_tag.get_text(strip=True)

                journal.ch_sci_2025 = part_dict
        elif '中国科学院SCI期刊分区' in first_cell_text and '2023年12月升级版' in first_cell_text:
            tab_tags = tr.select_one('table')
            if tab_tags:
                part_dict = {'大类学科': '', '小类学科': '', 'Top期刊': False, '综述期刊': False, '分区': ''}
                major_subject_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(1)')
                part_dict['大类学科'] = major_subject_tag.find(text=True, recursive=False).strip()

                minor_subject_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td:nth-child(1)')
                part_dict['小类学科'] = minor_subject_tag.get_text(strip=True)

                top_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(3)')
                part_dict['Top期刊'] = top_tag.get_text(strip=True) == '是'

                review_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(4)')
                part_dict['综述期刊'] = review_tag.get_text(strip=True) == '是'

                part_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(1) > span:nth-child(2)')
                part_dict['分区'] = part_tag.get_text(strip=True)

                journal.ch_sci_2023 = part_dict
        elif '中国科学院SCI期刊分区' in first_cell_text and '2022年12月旧的升级版' in first_cell_text:
            tab_tags = tr.select_one('table')
            if tab_tags:
                part_dict = {'大类学科': '', '小类学科': '', 'Top期刊': False, '综述期刊': False, '分区': ''}
                major_subject_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(1)')
                part_dict['大类学科'] = major_subject_tag.find(text=True, recursive=False).strip()

                minor_subject_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td:nth-child(1)')
                part_dict['小类学科'] = minor_subject_tag.get_text(strip=True)

                top_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(3)')
                part_dict['Top期刊'] = top_tag.get_text(strip=True) == '是'

                review_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(4)')
                part_dict['综述期刊'] = review_tag.get_text(strip=True) == '是'

                part_tag = tab_tags.select_one('tbody > tr:nth-child(2) > td:nth-child(1) > span:nth-child(2)')
                part_dict['分区'] = part_tag.get_text(strip=True)

                journal.ch_sci_2022 = part_dict
        elif 'SCI期刊收录coverage' in first_cell_text:
            sci_tag = tr.select_one('td:nth-child(2)')
            text = sci_tag.get_text(strip=True)
            journal.sci = 'Science Citation Index Expanded (SCIE)' in text
            journal.scopus = 'Scopus (CiteScore)' in text
        elif 'PubMed Central (PMC)链接' in first_cell_text:
            # PubMed Central (PMC)链接
            pmc_url_tag = tr.select_one('td:nth-child(2) > a')
            journal.pmc_url = pmc_url_tag.get_text(strip=True)
        elif '平均审稿速度' in first_cell_text:
            speed_tag = tr.select_one('td:nth-child(2)')
            journal.speed = speed_tag.get_text(strip=True).split('经验：')[1]
        elif '平均录用比例' in first_cell_text:
            accept_tag = tr.select_one('td:nth-child(2)')
            journal.accept = accept_tag.get_text(strip=True).split('经验：')[1]
        elif 'APC文章处理费信息' in first_cell_text:
            apc_tag = tr.select_one('td:nth-child(2)')
            match = re.search(r'USD\s?(\d+)', apc_tag.get_text(strip=True))
            journal.apc_price = int(match.group(1)) if match else None
        elif 'LetPub助力发表' in first_cell_text:
            # 广告，不做处理
            pass
        elif '收稿范围' in first_cell_text:
            range_tag = tr.select_one('td:nth-child(2)')
            journal.range = range_tag.get_text(strip=True).split('数据：')[1]
        elif '收录体裁' in first_cell_text:
            type_tag = tr.select_one('td:nth-child(2)')
            journal.type = type_tag.get_text(strip=True).split('数据：')[1]
        elif '编辑信息' in first_cell_text:
            editor_tag = tr.select_one('td:nth-child(2)')
            journal.editor = editor_tag.get_text(strip=True)
        elif '期刊常用信息链接' in first_cell_text:
            # 无关信息，不做处理
            pass
        else:
            print(first_cell_text)
    return journal
