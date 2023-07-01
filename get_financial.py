import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


def get_snapshot_soup(gicode) :
    # URL 설정
    url = f'http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{str(gicode)}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=&strResearchYN='

    # URL에서 HTML 가져오기
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return soup

# 연결재무제표 (연간) 추출
def get_year_fh(soup) :
    # ID가 'highlight_D_A'인 div 찾기
    div = soup.find('div', {'id': 'highlight_D_A'})

    # div 안의 table 태그 찾기
    table = div.find('table')

    # 각 tr 찾기
    rows = table.find('tbody').find_all('tr')

    # 결과를 저장할 dict 생성 (재무제표)
    result = {}

    # 각 tr에 대해
    for row in rows:
        # th의 텍스트 추출
        th_text = row.th.get_text(strip=True)

        # 괄호가 있다면 괄호를 포함한 괄호안의 텍스트 제거
        th_text = re.sub(r'\(.*?\)', '', th_text)

        # 띄어쓰기로 split하고 index가 0번째의 값만 추출
        key = th_text.split()[0]

        # DPSDPS는 DPS로 수정되게 추가
        if key == 'DPSDPS' :
            key = 'DPS'

        # 중복 텍스트
        cnt = 0
        while key in result :
            cnt += 1
            key = '%s_%d'%(key.split('_')[0], cnt)
        
        # 각 td에서 index가 0~3까지의 텍스트 추출
        values = [td.get_text(strip=True) for td in row.find_all('td')[:4]]

        # 추출한 각 td의 텍스트가 만약 빈값('')이면 None으로 변환
        values = [value if value != '' else None for value in values]

        # 추출한 td의 값을 list로 묶어줌
        result[key] = values

    # 결과 dict의 values를 None을 제외하고 모두 정수 또는 소수로 변환
    for key, values in result.items():
        new_values = []
        for value in values:
            if value is not None:
                # 쉼표 제거
                value = value.replace(',', '')
                
                # N/A 에러 케이스 발견
                if value != 'N/A':
                    # 소수점이 있는지 확인
                    if '.' in value:
                        # 소수로 변환
                        new_values.append(float(value))
                    else:
                        # 정수로 변환
                        new_values.append(int(value))
                else:
                    new_values.append(None)
                
            else:
                new_values.append(None)
        result[key] = new_values
        
    # 각 value를 ['3_years_ago', '2_years_ago', '1_years_ago', 'estimated']와 매칭
    years = ['c1', 'c2', 'c3', 'c4']

    for key, values in result.items():
        result[key] = dict(zip(years, values))


    theads = table.find('thead').find_all('tr')[1].find_all('th')[:4]
    years_text = []

    for th in theads :
        chk_a = th.find('a')
        if chk_a == None :
            years_text.append(th.get_text(strip=True))
        else :
            years_text.append(chk_a.get_text(strip=True))

    result['year_chk'] = dict(zip(years, years_text))

    return result


# 연결재무제표 (분기) 추출
def get_quarter_fh(soup) :
    # ID가 'highlight_D_Q'인 div 찾기
    div = soup.find('div', {'id': 'highlight_D_Q'})

    # div 안의 table 태그 찾기
    table = div.find('table')

    # 각 tr 찾기
    rows = table.find('tbody').find_all('tr')

    # 결과를 저장할 dict 생성 (재무제표)
    result = {}

    # 각 tr에 대해
    for row in rows:
        # th의 텍스트 추출
        th_text = row.th.get_text(strip=True)

        # 괄호가 있다면 괄호를 포함한 괄호안의 텍스트 제거
        th_text = re.sub(r'\(.*?\)', '', th_text)

        # 띄어쓰기로 split하고 index가 0번째의 값만 추출
        key = th_text.split()[0]

        # DPSDPS는 DPS로 수정되게 추가
        if key == 'DPSDPS' :
            key = 'DPS'
        
        # 중복 텍스트
        cnt = 0
        while key in result :
            cnt += 1
            key = '%s_%d'%(key.split('_')[0], cnt)
        
        # 각 td에서 index가 4~까지의 텍스트 추출
        values = [td.get_text(strip=True) for td in row.find_all('td')[4:]]

        # 추출한 각 td의 텍스트가 만약 빈값('')이면 None으로 변환
        values = [value if value != '' else None for value in values]

        # 추출한 td의 값을 list로 묶어줌
        result[key] = values

    # 결과 dict의 values를 None을 제외하고 모두 정수 또는 소수로 변환
    for key, values in result.items():
        new_values = []
        for value in values:
            if value is not None:
                # 쉼표 제거
                value = value.replace(',', '')
                
                # N/A 에러 케이스 발견
                if value != 'N/A':
                    # 소수점이 있는지 확인
                    if '.' in value:
                        # 소수로 변환
                        new_values.append(float(value))
                    else:
                        # 정수로 변환
                        new_values.append(int(value))
                else:
                    new_values.append(None)
                
            else:
                new_values.append(None)
        result[key] = new_values
        
    # 각 value를 ['y1', 'y2', 'y3', 'y4']와 매칭
    qts = ['c1', 'c2', 'c3', 'c4']

    for key, values in result.items():
        result[key] = dict(zip(qts, values))
    

    theads = table.find('thead').find_all('tr')[1].find_all('th')[4:]
    qts_text = []

    for th in theads :
        chk_a = th.find('a')
        if chk_a == None :
            qts_text.append(th.get_text(strip=True))
        else :
            qts_text.append(chk_a.get_text(strip=True))

    result['year_chk'] = dict(zip(qts, qts_text))

    return result

# Summary 추출
def get_summary(soup) :
    # ID가 'bizSummaryContent'인 div 찾기
    div = soup.find('ul', {'id': 'bizSummaryContent'})
    
    # summary li 추출
    lis = div.find_all('li')
    
    summary = [li.get_text(strip=True).replace('\xa0', ' ') for li in lis]
    
    return summary

# 발행주식수 추출
def get_common_stock(soup) :
    # ID가 'svdMainGrid1'인 div 찾기
    div = soup.find('div', {'id': 'svdMainGrid1'})
    
    # table > last tr
    tr = div.find('table').find_all('tr')[-1]
    
    # last td
    td = tr.find_all('td')[0].get_text(strip=True)
    
    # split td
    sp_td = [i.strip() for i in td.split('/')]
    
    # 발행 주식수 숫자 변환
    common_stock = int(sp_td[0].replace(',', ''))
    

    # 시가 총액 추출
    capa_tr = div.find('table').find_all('tr')[-3]
    capa = int(capa_tr.find('td', {'class': 'r'}).get_text(strip=True).replace(',', ''))*100000000
    

    return {
        'common_stock': common_stock,
        'market_capa': capa
    }


# 자사주 추출
def get_treasury_stock(soup) :
    # ID가 'svdMainGrid4'인 div 찾기
    div = soup.find('div', {'id': 'svdMainGrid4'})
    
    # find all tr
    trs = div.find_all('tr')
    
    # find treasury tr
    flag_text = ['자사주']
    
    treasury_td = 0
    
    for tr in trs :
        # th에 '자사주', '우리사주' 텍스트 포함 검색
        th = tr.find('th').get_text(strip=True).replace('\xa0', ' ')
        
        if any(flag in th for flag in flag_text) :
            treasury_td = int(tr.find_all('td')[0].get_text(strip=True).replace(',', ''))
            break
    
    return treasury_td


# 종목 이름/업종 추출
def get_stock_info(soup) :
    h1 = soup.find('h1', {'id': 'giName'})
    name = h1.get_text(strip=True).replace('&nbsp', ' ').replace('\xa0', ' ')

    p = soup.find('p', {'class': 'stxt_group'})
    stxt = [i.get_text(strip=True).replace('&nbsp', ' ').replace('\xa0', ' ') for i in p.find_all('span', {'class': 'stxt'})]

    return {
        'name': name,
        'stxt': stxt
    }


# 재무비율 추출
def get_stock_rate(gicode) :
    # URL 설정
    url = f'http://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode=A{str(gicode)}&cID=&MenuYn=Y&ReportGB=&NewMenuID=104&stkGb=701'

    # URL에서 HTML 가져오기
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # class 'um_table' div index 0
    div = soup.find_all('div', {'class': 'um_table'})[0]

    # thead
    thead = div.find('thead')
    ths = thead.find_all('th')[2:] # 최근 3년 & 현재 기준
    dates = [t.get_text(strip=True) for t in ths]

    # tbody
    tbody = div.find('tbody')
    trs = tbody.find_all('tr')

    # return rate
    rate = {}

    for t in trs :
        tr_th = t.find('th')
        th_a = tr_th.find('a')
        if not th_a == None :
            a_tx = th_a.get_text(strip=True).replace('&nbsp', '').replace('\xa0', ' ')
            if a_tx in ['유동비율', '당좌비율', '부채비율', '유보율'] :
                tds = [t.get_text(strip=True).replace(',', '') for t in t.find_all('td')[1:]]
                tds = [float(td) if '.' in td else int(td) for td in tds]
                rate[a_tx] = list(zip(dates, tds))

    return rate

# 재무상태표/현금흐름표 추출
def get_cash_table(gicode) :
    # URL 설정
    url = f'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{str(gicode)}&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701'

    # URL에서 HTML 가져오기
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 현금흐름표
    # id가 divCashY인 div
    div = soup.find('div', {'id': 'divCashY'})

    # thead
    thead = div.find('thead')
    ths = thead.find_all('th')[1:] # 최근 3년 & 현재 기준
    dates = [t.get_text(strip=True) for t in ths]

    # tbody
    tbody = div.find('tbody')
    trs = tbody.find_all('tr', {'class', 'rowBold'})[:-1]

    cash_table = {}
    for tr in trs :
        th = tr.find('th').get_text(strip=True)
        tds = [int(i.get_text(strip=True).replace(',' ,'')) for i in tr.find_all('td')]
        cash_table[th] = list(zip(dates, tds))

    # 재무상태표
    # id가 divDaechaY인 div 
    daecha_div = soup.find('div', {'id': 'divDaechaY'})

    daecha_thead = daecha_div.find('thead')
    daecha_ths = daecha_thead.find_all('th')[1:] # 최근 3년 & 현재 기준
    daecha_dates = [t.get_text(strip=True) for t in daecha_ths]

    row_bold = daecha_div.find_all('tr', {'class': 'rowBold'})
    
    daecha_table = {}
    for tr in row_bold :
        th = tr.find('th').get_text(strip=True)
        tds = [int(i.get_text(strip=True).replace(',' ,'')) for i in tr.find_all('td')]
        daecha_table[th] = list(zip(daecha_dates, tds))


    return {
        'cash_table': cash_table,
        'daecha_table': daecha_table
    }


# 현재가 추출 (NAVER 금융)
def get_current_info(gicode) :
    url = f'https://finance.naver.com/item/main.naver?code={str(gicode)}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rate_info = soup.find('div', {'class': 'rate_info'})
    no_today = rate_info.find('p', {'class': 'no_today'}).text.strip()
    no_today = no_today.split('\n')[0]
    no_today = int(no_today.replace(',', ''))

    now = datetime.now()
    formatted_date = now.strftime("%Y/%m/%d %H:%M")

    return {
        'current_price': no_today,
        'base_date': formatted_date
    }


# 업종 PER 추출
def get_same_per(gicode) :
    # NAVER
    nv_url = f'https://finance.naver.com/item/main.naver?code={str(gicode)}'
    nv_response = requests.get(nv_url)
    nv_soup = BeautifulSoup(nv_response.text, 'html.parser')

    # NAVER 동일업종 PER 정보
    nv_same_per = None
    table = nv_soup.find('table', {'summary': '동일업종 PER 정보'})
    table_em = table.find('em').get_text(strip=True)

    nv_a = table.find('a')['href']
    nv_main = 'https://finance.naver.com'
    nv_url = f'{nv_main}{nv_a}'
    
    try :
        nv_same_per = float(table_em)
    except :
        nv_same_per = None

    # Company Guide
    cg_soup = get_snapshot_soup(gicode)
    cg_same_per = None
    dl = cg_soup.find('div', {'id': 'corp_group2'}).findChildren(recursive=False)[2]
    dd = dl.find_all('dd')[-1]
    try :
        cg_same_per = float(dd.get_text(strip=True))
    except :
        cg_same_per = None

    cg_url = f'http://comp.fnguide.com/SVO2/ASP/SVD_ujanal.asp?pGB=1&gicode=A{gicode}&cID=&MenuYn=Y&ReportGB=&NewMenuID=110&stkGb=701'

    return {
        'naver': nv_same_per,
        'naver_url': nv_url,
        'company': cg_same_per,
        'company_url': cg_url
    }
    

# 등급별금리스프레드 추출
def get_spread() :
  url = 'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')

  table = soup.find('div', {'id': 'con_tab1'}).find('table')
  rows = table.find_all('tr')

  bbb = None

  for row in rows:
      columns = row.find_all('td')
      if len(columns) > 0 and columns[0].text.strip() == 'BBB-':
          bbb = columns[-1].text.strip()
          break

  return bbb

def get_all_spread() :
    url = 'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('div', {'id': 'con_tab1'}).find('table')
    rows = table.find_all('tr')
    ths = table.find_all('th')

    rate = {}

    for th in ths :
        rate[th.get_text(strip=True)] = []

    for row in rows:
        columns = row.find_all('td')
        if not columns :
            continue
        for idx, key in enumerate(list(rate.keys())) :
            bef_data = rate[key].copy()
            rdata = columns[idx].get_text(strip=True)
            if '.' in rdata : 
                rdata = float(rdata)
            else :
                if rdata.isdigit() :
                    rdata = int(rdata)
            bef_data.append(rdata)
            rate[key] = bef_data


    gubun = rate['구분']
    month = [g for g in list(rate.keys()) if g != '구분']
    spread = {}
    for idx, g in enumerate(gubun) :
        data = {m : rate[m][idx] for m in month}
        spread[g] = data

    date_input = soup.find('input', {'id': 'startDt'})['value']

    return {'date': date_input, 'rate': spread}


# 모든 아이템 출력
def get_stock_items(gicode) :
  soup = get_snapshot_soup(gicode)

  # 종목명, 업종
  info = get_stock_info(soup)

  # 발행 주식수, 시가총액
  common = get_common_stock(soup)


  # 재무상태표, 현금흐름표
  dc = get_cash_table(gicode)

  return {
    'name': info['name'],
    'stxt': info['stxt'],
    'current' : get_current_info(gicode),
    'summary' : get_summary(soup),
    'common' : common['common_stock'],
    'market_capacity' : common['market_capa'],
    'treasury' : get_treasury_stock(soup),
    'year' : get_year_fh(soup),
    'quarter' : get_quarter_fh(soup),
    'rate': get_stock_rate(gicode),
    'cash_table': dc['cash_table'],
    'daecha_table': dc['daecha_table'],
    'same_per': get_same_per(gicode),
    'bbb' : get_spread(),
    'spread' : get_all_spread()
  }




##############################
# 가중평균 계산
def set_weight_aver(*values) :
    n = len(values)
    denominator = (n * (n + 1))//2 # 분모
    weight_values = []
    weight = 1 # 초기 가중치
    for v in values :
        weight_values.append(v*weight)
        weight+=1
    
    molecule = sum(weight_values)
    try :
        result = molecule/denominator
        result = round(result, 2)
        return result
    except :
        return None

# SRIM Calculator
def SRIM(gicode, bbb=None) :
    stock = get_stock_items(gicode)

    # 연결재무제표(연간)
    cfs = stock['year']

    # 작년말 지배주주지분 ✅
    interest = cfs['지배주주지분']['c3']

    # ROE ✅
    roe = None
    ce_roe = cfs['ROE']['c4'] 

    # 추정 ROE : 가중 평균
    ys = [float(cfs['ROE'][y]) for y in ['c1', 'c2', 'c3'] if not cfs['ROE'][y] == None]
    w_roe = set_weight_aver(*ys)

    if not ce_roe == None :
        ce_roe = float(ce_roe)

    ws = {
        'w1' : 1,
        'w2' : float(0.9),
        'w3' : float(0.8),
        'w4' : float(0.7),
        'w5' : float(0.6),
        'w6' : float(0.5),
    }

    # BBB- 할인율 ✅
    if bbb == None :
        bbb = float(stock['bbb'])

    # SRIM 최종 결과 ✅
    return_values = {}

    for key, roe in [('ce', ce_roe), ('we', w_roe)] :
        final_values = {}
        if roe != None :
            # 기업가치(시가총액) ✅
            numerator = interest*(roe - bbb)
            b0 = interest + (numerator/bbb)

            # 주식수 ✅
            # 발행주식수
            shares_number = int(stock['common'])
            # 자사주
            treasury_number = int(stock['treasury'])
            stock_cnt = shares_number - treasury_number

            # 적정주가 ✅
            fair_value = (b0*100000000)/stock_cnt

            # 초과이익 ✅
            excess_profit = interest*((roe/100) - (bbb/100))

            for k, w in ws.items() :
                denominator = (1+float(bbb/100))-w
                w_calc = w/denominator
                svalue = interest + (excess_profit*w_calc)
                sprice = (svalue/stock_cnt)*100000000
                final_values[k] = {'svalue': round(svalue), 'sprice': round(sprice)}

            # 투자 여부
            w1 = final_values['w1']
            w3 = final_values['w3']

            flag = True
            if w1['sprice'] <= w3['sprice'] :
                flag = False
            
            if fair_value < 0 :
                flag = False

            return_values[key] = {
                'roe': roe,
                'flag': flag,
                'w': final_values
            }

    return {
        '지배주주지분': interest,
        '유통주식수': f'{format(stock_cnt, ",")}주',
        '할인율': round(bbb, 2),
        'srim': return_values
    }


# Market PER로 계산한 적정 주가 * 추정 영업이익으로 적정주가 계산
def MPER(gicode) :
    stock = get_stock_items(gicode)

    quarter = stock['quarter']
    cnt = stock['common'] # 주식수
    mcapa = stock['market_capacity'] # 현재 시가총액
    e_value = quarter['영업이익']
    find_none = [value for key, value in e_value.items() if not value == None]

    if not find_none :
        # 추정 영업이익 자체가 없음. 분석 불가
       return {
            '영업이익추정합': None,
            '적정주가': None,
            'flag': False,
        }
    # 예상 추정치가 없는 경우 평균치로 변환
    if not len(find_none) == len(e_value) :
        mean = int(sum(find_none)/len(find_none))
        for key, value in e_value.items() :
            if value == None :
                e_value[key] = mean

    # 올해 영업이익의 합산
    # 예상 영업이익이 없는 경우 평균값으로 계산
    e_sum = sum(e_value.values())*100000000

    # Market PER : 평균 10~12를 기준. 10 기준으로 작성
    market_per = 10

    # 10년 동안 일하면 원금회수를 할 수 있나?
    e_per = e_sum*market_per

    # 적정 주가
    fair_price = round(e_per/cnt)

    return_e_sum = f'{format(round(e_sum/100000000), ",")}억원'
    if e_sum < 0 :
        return {
            '영업이익추정합': return_e_sum,
            '적정주가': fair_price,
            'flag': False,
        }

    flag = True
    if mcapa > e_per :
        flag = False

    return {
        '영업이익추정합': return_e_sum,
        '적정주가': fair_price,
        'flag': flag,
    }




##### GET HTML
def chk_int(value) :
    if type(value) == int or type(value) == float :
        return True
    else :
        return False

def comma(value, rd=1, decimal=False) :
    if type(value) == int :
        return format(round(value, rd), ',')
    elif type(value) == float :
        if rd == 1 :
            if decimal :
                return "{:,.1f}".format(value, rd)
            else :
                return format(round(value), ',')
        else :
            return "{:,.{}f}".format(value, rd)
    else :
        return ''
    
def int_cond(value) :
    if chk_int(value) :
        return True
    else :
        return False
    
# ROE 기준값
def roe_value(value) :
    if not chk_int(value) :
        return ''

    if value >= 15 :
        return ' class="good-value"'
    else :
        if value <= 5 :
            return ' class="bad-value"'
        else :
            return ''
        

# PER 기준값
def per_value(value) :
    if not chk_int(value) :
        return ''

    if value <= 10 :
        return ' class="good-value"'
    else :
        if value >= 20 :
            return ' class="bad-value"'
        else :
            return ''

# PBR 기준값
def pbr_value(value) :
    if not chk_int(value) :
        return ''

    if value < 1 :
        return ' class="good-value"'
    else :
        if value >= 1.5 :
            return ' class="bad-value"'
        else :
            return ''

# 가중치 계산 여부 튜플 생성
def chk_weight(fs_value_dict) :
    return {key: [value, False] for key, value in fs_value_dict.items()}

def int_or_float(s):
    # 문자열이 실수를 나타내는지 확인
    if '.' in s:
        # 실수로 변환
        return float(s)
    else:
        # 정수로 변환
        return int(s)


# HTML 재무제표(연간/분기)
def fs_table(base, txt) :
    base = base.copy()
    table_head = list(base['year_chk'].values())
    sales = chk_weight(base['매출액'])
    profit = chk_weight(base['영업이익'])
    real_profit = chk_weight(base['당기순이익'])
    interest = chk_weight(base['지배주주지분'])
    roe = chk_weight(base['ROE'])
    per = chk_weight(base['PER수정주가'])
    pbr = chk_weight(base['PBR수정주가'])
    cpt_total = chk_weight(base['자본총계'])
    cpt = chk_weight(base['자본금'])
        
    chart_class = 'fs-y-chart' if txt == '연간' else 'fs-q-chart'

    # 3년 연속 적자인지?
    pm_flag = False
    for pl in [list(profit.values())[:3], list(profit.values())[1:]] :
        pm_cnt = 1
        for p, w in pl :
            if p != None :
                if p < 0 :
                    pm_cnt+=1
        
        if pm_cnt >= 3:
            pm_flag = True
        else :
            pm_flag = False

    # 올해 예상이 없는 경우 가중평균으로 계산
    for metr in [sales, profit, real_profit, interest, roe, per, pbr, cpt_total, cpt] :
        nones = [v for v, w in list(metr.values()) if v == None]
        
        if len(nones) >= 3 :
            continue

        while nones :
            for key, val in metr.items() :
                if val[0] == None :
                    values = [v for v, w in list(metr.values()) if v != None]
                    wavg = set_weight_aver(*values)
                    metr[key] = [wavg, True]
                    break
            nones = [v for v, w in list(metr.values()) if v == None]

    final_values = [list(metr.values()) for metr in [sales, profit, real_profit, interest, roe, per, pbr, cpt_total, cpt]]
    none_data_flag = []
   
    for value in final_values :
        if all(v == None for v, w in value) : # or len([v for v, w in value if v != None]) == 1
            none_data_flag.append(True)
        else :
            none_data_flag.append(False)
    
    if all(none_data_flag) :
        return f'''
            <!-- {txt} -->
            <div class="fs-head">
                <div class="fs-title">{txt}</div>
            </div>
            <div class="none-data">{txt} 데이터가 아직 없습니다.</div>
            <!-- {txt} END -->'''

    # 영업이익률
    profit_ratio = [round(((profit[key][0])/(value[0]))*100, 2) if all([profit[key][0] != None, value[0] != None]) else None for key, value in sales.items()]
    profit_ratio_txt = ['' if i == None else comma(i, 2) for i in profit_ratio]
    # 순이익률
    real_profit_ratio = [round(((real_profit[key][0])/(value[0]))*100, 2) if all([real_profit[key][0] != None, value[0] != None]) else None for key, value in sales.items()]
    real_profit_ratio_txt = ['' if i == None else comma(i, 2) for i in real_profit_ratio]

    # 자본잠식 계산
    zip_cpt = zip(list(cpt_total.values()), list(cpt.values()))
    # 자본잠식률
    erosion_rate = []
    for tot, cpv in list(zip_cpt) :
        t_v, t_w = tot
        c_v, c_w = cpv
        if not t_v == None and not c_v == None :
            av = c_v - t_v
            bv = (av/c_v)*100
            er_ratio = round(bv, 2)
            erosion_rate.append(er_ratio)
        else :
            erosion_rate.append(None)

    # 분기재무제표 요약
    summary = '''<div class="goto-summary">
    <a title="분기재무제표 요약 바로가기" href="#fs-summary-2">분기재무제표 요약 바로가기</a>
    </div>'''

    html_fs = f'''
            <!-- {txt} -->
            <div class="fs-head">
                <div class="fs-title" id="fs-table-{1 if txt == '연간' else 2}">{txt}</div>
                <div class="fs-unit">단위: 억원, %, 배</div>
            </div>
            <div class="fs-div">
                <table class="fs-data">
                    <thead>
                        <th>IFRS(연결)</th>
                        <th>{table_head[0]}</th>
                        <th>{table_head[1]}</th>
                        <th>{table_head[2]}</th>
                        <th>{table_head[3]}</th>
                    </thead>
                    <tbody>
                        <tr>
                            <th>매출액</th>
                            <td{' class="weight-value"' if sales['c1'][1] else ''}><span{' class="bad-value"' if int_cond(sales['c1'][0]) and (sales['c1'][0] < 50) and (txt=='연간') else ''}>{comma(sales['c1'][0])}</span></td>
                            <td{' class="weight-value"' if sales['c2'][1] else ''}><span{' class="bad-value"' if int_cond(sales['c2'][0]) and (sales['c2'][0] < 50) and (txt=='연간') else ''}>{comma(sales['c2'][0])}</span></td>
                            <td{' class="weight-value"' if sales['c3'][1] else ''}><span{' class="bad-value"' if int_cond(sales['c3'][0]) and (sales['c3'][0] < 50) and (txt=='연간') else ''}>{comma(sales['c3'][0])}</span></td>
                            <td{' class="weight-value"' if sales['c4'][1] else ''}><span{' class="bad-value"' if int_cond(sales['c4'][0]) and (sales['c4'][0] < 50) and (txt=='연간') else ''}>{comma(sales['c4'][0])}</span></td>
                        </tr>
                        <tr>
                            <th><span{' class="bad-value"' if pm_flag and txt=='연간' else ''}>영업이익</span></th>
                            <td{' class="weight-value"' if profit['c1'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c1'][0]) and (profit['c1'][0] < 0) else ''}>{comma(profit['c1'][0])}</span></td>
                            <td{' class="weight-value"' if profit['c2'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c2'][0]) and (profit['c2'][0] < 0) else ''}>{comma(profit['c2'][0])}</span></td>
                            <td{' class="weight-value"' if profit['c3'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c3'][0]) and (profit['c3'][0] < 0) else ''}>{comma(profit['c3'][0])}</span></td>
                            <td{' class="weight-value"' if profit['c4'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c4'][0]) and (profit['c4'][0] < 0) else ''}>{comma(profit['c4'][0])}</span></td>
                        </tr>
                        <tr>
                            <th>영업이익률</th>
                            <td{' class="weight-value"' if profit['c1'][1] else ''}><span{(' class="good-value"' if profit_ratio[0] >= 15 else ' class="bad-value"' if profit_ratio[0] < 5 else '') if type(profit_ratio[0]) in [float, int] else ''}>{profit_ratio_txt[0]}</span></td>
                            <td{' class="weight-value"' if profit['c2'][1] else ''}><span{(' class="good-value"' if profit_ratio[1] >= 15 else ' class="bad-value"' if profit_ratio[1] < 5 else '') if type(profit_ratio[1]) in [float, int] else ''}>{profit_ratio_txt[1]}</span></td>
                            <td{' class="weight-value"' if profit['c3'][1] else ''}><span{(' class="good-value"' if profit_ratio[2] >= 15 else ' class="bad-value"' if profit_ratio[2] < 5 else '') if type(profit_ratio[2]) in [float, int] else ''}>{profit_ratio_txt[2]}</span></td>
                            <td{' class="weight-value"' if profit['c4'][1] else ''}><span{(' class="good-value"' if profit_ratio[3] >= 15 else ' class="bad-value"' if profit_ratio[3] < 5 else '') if type(profit_ratio[3]) in [float, int] else ''}>{profit_ratio_txt[3]}</span></td>
                        </tr>
                        <tr>
                            <th>당기순이익</th>
                            <td{' class="weight-value"' if real_profit['c1'][1] else ''}><span{' class="bad-value"' if int_cond(real_profit['c1'][0]) and (real_profit['c1'][0] < 0) else ''}>{comma(real_profit['c1'][0])}</span></td>
                            <td{' class="weight-value"' if real_profit['c2'][1] else ''}><span{' class="bad-value"' if int_cond(real_profit['c2'][0]) and (real_profit['c2'][0] < 0) else ''}>{comma(real_profit['c2'][0])}</span></td>
                            <td{' class="weight-value"' if real_profit['c3'][1] else ''}><span{' class="bad-value"' if int_cond(real_profit['c3'][0]) and (real_profit['c3'][0] < 0) else ''}>{comma(real_profit['c3'][0])}</span></td>
                            <td{' class="weight-value"' if real_profit['c4'][1] else ''}><span{' class="bad-value"' if int_cond(real_profit['c4'][0]) and (real_profit['c4'][0] < 0) else ''}>{comma(real_profit['c4'][0])}</span></td>
                        </tr>
                        <tr>
                            <th>당기순이익률</th>
                            <td{' class="weight-value"' if real_profit['c1'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[0] >= 10 else ' class="bad-value"' if real_profit_ratio[0] < 3 else '') if type(real_profit_ratio[0]) in [float, int] else ''}>{real_profit_ratio_txt[0]}</span></td>
                            <td{' class="weight-value"' if real_profit['c2'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[1] >= 10 else ' class="bad-value"' if real_profit_ratio[1] < 3 else '') if type(real_profit_ratio[1]) in [float, int] else ''}>{real_profit_ratio_txt[1]}</span></td>
                            <td{' class="weight-value"' if real_profit['c3'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[2] >= 10 else ' class="bad-value"' if real_profit_ratio[2] < 3 else '') if type(real_profit_ratio[2]) in [float, int] else ''}>{real_profit_ratio_txt[2]}</span></td>
                            <td{' class="weight-value"' if real_profit['c4'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[3] >= 10 else ' class="bad-value"' if real_profit_ratio[3] < 3 else '') if type(real_profit_ratio[3]) in [float, int] else ''}>{real_profit_ratio_txt[3]}</span></td>
                        </tr>
                        <tr><!--
                            <th>지배주주지분</th>
                            <td{' class="weight-value"' if interest['c1'][1] else ''}>{comma(interest['c1'][0])}</td>
                            <td{' class="weight-value"' if interest['c2'][1] else ''}>{comma(interest['c2'][0])}</td>
                            <td{' class="weight-value"' if interest['c3'][1] else ''}>{comma(interest['c3'][0])}</td>
                            <td{' class="weight-value"' if interest['c4'][1] else ''}>{comma(interest['c4'][0])}</td>
                            -->
                        </tr>
                        <tr>
                            <th>자본총계</th>
                            <td{' class="weight-value"' if cpt_total['c1'][1] else ''}>{comma(cpt_total['c1'][0])}</td>
                            <td{' class="weight-value"' if cpt_total['c2'][1] else ''}>{comma(cpt_total['c2'][0])}</td>
                            <td{' class="weight-value"' if cpt_total['c3'][1] else ''}>{comma(cpt_total['c3'][0])}</td>
                            <td{' class="weight-value"' if cpt_total['c4'][1] else ''}>{comma(cpt_total['c4'][0])}</td>
                        </tr>
                        <tr>
                            <th>자본금</th>
                            <td{' class="weight-value"' if cpt['c1'][1] else ''}>{comma(cpt['c1'][0])}</td>
                            <td{' class="weight-value"' if cpt['c2'][1] else ''}>{comma(cpt['c2'][0])}</td>
                            <td{' class="weight-value"' if cpt['c3'][1] else ''}>{comma(cpt['c3'][0])}</td>
                            <td{' class="weight-value"' if cpt['c4'][1] else ''}>{comma(cpt['c4'][0])}</td>
                        </tr>
                        <tr>
                            <th>자본잠식률</th>
                            <td{' class="weight-value"' if (cpt_total['c1'][1] or cpt['c1'][1]) else ''}><span{' class="bad-value"' if erosion_rate[0] != None and erosion_rate[0] >= 0 else ''}>{'' if erosion_rate[0] == None else comma(erosion_rate[0], 2) if erosion_rate[0] >= 0 else '정상'}</span></td>
                            <td{' class="weight-value"' if (cpt_total['c2'][1] or cpt['c2'][1]) else ''}><span{' class="bad-value"' if erosion_rate[1] != None and erosion_rate[1] >= 0 else ''}>{'' if erosion_rate[1] == None else comma(erosion_rate[1], 2) if erosion_rate[1] >= 0 else '정상'}</span></td>
                            <td{' class="weight-value"' if (cpt_total['c3'][1] or cpt['c3'][1]) else ''}><span{' class="bad-value"' if erosion_rate[2] != None and erosion_rate[2] >= 0 else ''}>{'' if erosion_rate[2] == None else comma(erosion_rate[2], 2) if erosion_rate[2] >= 0 else '정상'}</span></td>
                            <td{' class="weight-value"' if (cpt_total['c4'][1] or cpt['c4'][1]) else ''}><span{' class="bad-value"' if erosion_rate[3] != None and erosion_rate[3] >= 0 else ''}>{'' if erosion_rate[3] == None else comma(erosion_rate[3], 2) if erosion_rate[3] >= 0 else '정상'}</span></td>
                        </tr>
                        <tr>
                            <th>ROE</th>
                            <td{' class="weight-value"' if roe['c1'][1] else ''}><span{roe_value(roe['c1'][0])}>{comma(roe['c1'][0], 2)}</span></td>
                            <td{' class="weight-value"' if roe['c2'][1] else ''}><span{roe_value(roe['c2'][0])}>{comma(roe['c2'][0], 2)}</span></td>
                            <td{' class="weight-value"' if roe['c3'][1] else ''}><span{roe_value(roe['c3'][0])}>{comma(roe['c3'][0], 2)}</span></td>
                            <td{' class="weight-value"' if roe['c4'][1] else ''}><span{roe_value(roe['c4'][0])}>{comma(roe['c4'][0], 2)}</span></td>
                        </tr>
                        <tr>
                            <th>PER</th>
                            <td{' class="weight-value"' if per['c1'][1] else ''}><span{per_value(per['c1'][0])}>{comma(per['c1'][0], 2)}</span></td>
                            <td{' class="weight-value"' if per['c2'][1] else ''}><span{per_value(per['c2'][0])}>{comma(per['c2'][0], 2)}</span></td>
                            <td{' class="weight-value"' if per['c3'][1] else ''}><span{per_value(per['c3'][0])}>{comma(per['c3'][0], 2)}</span></td>
                            <td{' class="weight-value"' if per['c4'][1] else ''}><span{per_value(per['c4'][0])}>{comma(per['c4'][0], 2)}</span></td>
                        </tr>
                        <tr>
                            <th>PBR</th>
                            <td{' class="weight-value"' if pbr['c1'][1] else ''}><span{pbr_value(pbr['c1'][0])}>{comma(pbr['c1'][0], 2)}</span></td>
                            <td{' class="weight-value"' if pbr['c2'][1] else ''}><span{pbr_value(pbr['c2'][0])}>{comma(pbr['c2'][0], 2)}</span></td>
                            <td{' class="weight-value"' if pbr['c3'][1] else ''}><span{pbr_value(pbr['c3'][0])}>{comma(pbr['c3'][0], 2)}</span></td>
                            <td{' class="weight-value"' if pbr['c4'][1] else ''}><span{pbr_value(pbr['c4'][0])}>{comma(pbr['c4'][0], 2)}</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <!-- {txt} END -->
            <!-- {txt} Chart -->
            <div class="fs-chard-div">
                <canvas class="{chart_class}"></canvas>
                <script>
                    financeSetChart('.{chart_class}', {table_head}, [
                        {['null' if v == None else v for v, f in sales.values()]},
                        {['null' if v == None else v for v, f in profit.values()]},
                        {['null' if v == None else v for v, f in real_profit.values()]},
                        {['null' if v == None else v for v in profit_ratio]},
                        {['null' if v == None else v for v in real_profit_ratio]},
                    ]);
                </script>
            </div>
            <!-- {txt} Chart END -->
            {summary if txt == '분기' else ''}
'''

    return html_fs

# 구분 good / bad 
def cash_gubun(comb) :
    if comb in ['+/-/-', '+/-/+'] :
        return f'<span class="good-value">{comb}</span>'
    
    if comb in ['-/+/-', '-/+/+'] :
        return f'<span class="bad-value">{comb}</span>'
    
    return comb

# 적정주가 계산
def cp_value(vprofit, vper, vcommon) :
    if vper == None :
        return {
            'value': '',
            'price': '',
        }
    else :
        value = float(int(vprofit)*float(vper))
        value = round(value)
        price = (value/vcommon)*100000000
        price = round(price)

        return {
            'value': value,
            'price': price
        }


# 등급별금리스트페리드 아코디언 아이템
def rate_acco_item(rate_data) :
    acco_item_txt = '''
                        <div class="fs-accordion-item">
                            <button class="fs-accordion-btn">{name}</button>
                            <div class="fs-accordion-content fs-spread-list">
                            {items}
                            </div>
                        </div>'''

    spre_item_txt = '''
                            <div class="fs-spread-item">
                                <div class="fs-spread-month">{month}</div>
                                <button class="fs-spread-value">{rate}</button>
                            </div>'''


    spread_html = []
    for key, value in rate_data.items() :
        spre_txt = [spre_item_txt.format(month=vk, rate=vv) for vk, vv in value.items()]
        acco_txt = acco_item_txt.format(name=key, items=''.join(spre_txt))
        spread_html.append(acco_txt)

    spread_html = ''.join(spread_html)

    return spread_html


def get_html(gicode, bbb=None) :
    web_data = get_stock_items(gicode)

    sname = web_data['name'] # 종목이름
    stxt = ' | '.join(web_data['stxt']) # 종목 정보
    sdate = web_data['current']['base_date'] # 기준 날짜
    current_price = web_data['current']['current_price'] # 현재 주가
    ssummary = web_data['summary'][0] # summary
    scommon = web_data['common'] # 발행주식수
    streasury = web_data['treasury'] # 자사주
    scapa = web_data['market_capacity'] # 시가총액

    sfsy = web_data['year'] # 연간연결재무제표
    sfsq = web_data['quarter'] # 분기연결재무제표

    srate = web_data['rate'] # 재무비율
    scash = web_data['cash_table'] # 현금흐름표
    sdeacha = web_data['daecha_table'] # 재무상태표

    same_pers = web_data['same_per'] # 업종 PER

    if bbb == None :
        bbb = float(web_data['bbb']) # BBB- 할인율 (기본값)

    spread = web_data['spread'] # 등급별금리스프레드
    spread_date = spread['date']
    spread_rate = spread['rate'] 

    # HTML HEAD
    html_head = '''
    <link rel="stylesheet/less" type="text/css" href="https://tistory1.daumcdn.net/tistory/6187703/skin/images/analyze.less" />
    <script src="https://cdn.jsdelivr.net/npm/less"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@latest/dist/chartjs-plugin-annotation.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chartist-plugin-legend/0.6.2/chartist-plugin-legend.min.js" integrity="sha512-J82gmCXFu+eMIvhK2cCa5dIiKYfjFY4AySzCCjG4EcnglcPQTST/nEtaf5X6egYs9vbbXpttR7W+wY3Uiy37UQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script>
    // 연간/분기 차트 생성
    const financeSetChart = (className, labels, datas) => {{
        const ctx = document.querySelector(className).getContext('2d');
        const myChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: '매출액',
                    data: datas[0],
                    backgroundColor: 'rgba(16, 163, 127, 0.2)',
                    borderColor: 'rgba(16, 163, 127, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1',
                    type: 'bar'
                }}, {{
                    label: '영업이익',
                    data: datas[1],
                    backgroundColor: 'rgba(0, 0, 128, 0.2)',
                    borderColor: 'rgba(0, 0, 128, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1',
                    type: 'bar'
                }}, {{
                    label: '당기순이익',
                    data: datas[2],
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1',
                    type: 'bar'
                }}, {{
                    label: '영업이익률',
                    data: datas[3],
                    backgroundColor: 'rgba(255, 223, 0, 0.2)',
                    borderColor: 'rgba(255, 223, 0, 1)',
                    borderWidth: 2,
                    yAxisID: 'y2',
                }}, {{
                    label: '당기순이익률',
                    data: datas[4],
                    backgroundColor: 'rgba(135, 206, 250, 0.2)',
                    borderColor: 'rgba(135, 206, 250, 1)',
                    borderWidth: 2,
                    yAxisID: 'y2',
                }}]
            }},
            options: {{
                scales: {{
                    y1: {{
                        position: 'left',
                        ticks: {{
                            callback: function(value, index, ticks) {{
                                return `${{value.toLocaleString()}}억원`;
                            }}
                        }}
                    }},
                    y2: {{
                        beginAtZero: true,
                        position: 'right',
                        grid: {{
                            drawOnChartArea: false,
                        }},
                        ticks: {{
                            callback: function(value, index, ticks) {{
                                return `${{value.toLocaleString()}}%`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    }}
    </script>
    <!-- START -->
    <!-- Head -->
    <h1>{sname}:주식 재무 분석 & 적정주가 계산</h1>
    <div class="a-line"></div>
    <!-- Head END -->
    <!-- 안내사항 -->
    <div class="before-start">
        <ul>
            <li>FnGuide/NAVER 증권에서 <b>웹스크래핑한 데이터</b>입니다.</li>
            <li>모바일에서도 확인은 가능하지만 PC가 더 편리할 수 있습니다.</li>
            <li>티스토리 <b>모바일 앱</b>에서는 <span class="bad-value"><b>일부 기능이 작동하지 않습니다.</b></span></li>
            <li>이 포스트는 <b>{sdate} 기준</b>입니다. <b>재무 데이터는 이후 변경될 수 있습니다.</b></li>
            <li><b>요약은 AI가 작성</b>했습니다.</li>
            <li><b>긍정적인 수치</b>는 <span class="good-value"><b>초록색 폰트</b></span>로 표시됩니다.</li>
            <li><b>부정적인 수치</b>는 <span class="bad-value"><b>빨간색 폰트</b></span>로 표시됩니다.</li>
            <li><span class="weight-value"><b>노란색 배경</b></span>은 <span class="weight-value"><b>가중 평균</b></span>으로 계산된 수치입니다.</li>
            <li>재무정보 중 <span class="weight-value"><b>가중 평균</b></span>으로 계산된 케이스는 <b>AI분석에서 제외</b>됩니다.</li>
            <li>재무정보의 차트는 범례를 클릭하면 해당 범례를 숨기거나 나타낼 수 있습니다.</li>
            <li><b>SRIM 적정주가 계산에서는 회사채 수익률을 변경해서 적용 가능합니다.</b></li>
            <li><b>SRIM 적정주가 계산의 요약</b>은 <b>BBB- 5년 회사채 수익률 기준</b>입니다.</li>
            <li><b>자료는 참고용 정보</b>일 뿐입니다. <b>투자 결과에 대한 책임은 본인</b>에게 있습니다.</li>
        </ul>
    </div>
    <div class="a-line"></div>
    <div class="a-line"></div>
    <div class="fs-mypost-list">
        <div class="fs-mypost">🚀 바로가기</div>
        <div class="fs-mypost-link">
            <a href="#finance-datas">
                <div>재무정보</div>
            </a>
        </div>
        <div class="fs-mypost-link">
            <a href="#fs-calc-result">
                <div>적정주가 계산 (영업이익*PER & SRIM)</div>
            </a>
        </div>
        <div class="fs-mypost-link">
            <a href="#fs-summary-ai">
                <div>요약 (From. AI)</div>
            </a>
        </div>
    </div>
    <div class="a-line"></div>
    '''.format(sname=sname, sdate=sdate.split(' ')[0])

    # HTML 종목 기본 정보
    html_info = f'''
    <!-- 종목 기본 정보 -->
    <div class="report-title">기본 정보</div>
    <div class="standard-info">
        <div class="info">
            <div class="info-cell">
                <div class="cell-head">종목 이름</div>
                <div class="cell-desc">{sname}</div>
            </div>

            <div class="info-cell">
                <div class="cell-head">종목 코드</div>
                <div class="cell-desc">{gicode}</div>
            </div>

            <div class="info-cell">
                <div class="cell-head">현재 주가</div>
                <div class="cell-desc">{comma(current_price)}원</div>
            </div>

            <div class="info-cell">
                <div class="cell-head">기준 날짜</div>
                <div class="cell-desc">{sdate}</div>
            </div>
        </div>

        <div class="info-one">
            <div class="cell-head">시가 총액</div>
            <div class="cell-desc">{comma(scapa)}</div>
        </div>

        <div class="info-one">
            <div class="cell-head">발행주식수</div>
            <div class="cell-desc">{comma(scommon)}</div>
        </div>

        <div class="info-one">
            <div class="cell-head">자사주</div>
            <div class="cell-desc">{comma(streasury)}</div>
        </div>

        <div class="info-summary">
            <div class="cell-head">개요</div>
            <div class="cell-desc">
                <div class="info-industry">{stxt}</div>
                <div class="info-detail">{ssummary}</div>
            </div>
        </div>
    </div>
    <div class="fs-btn-a">
        <a title="NAVER 증권:{sname}" target="_blank" href="https://finance.naver.com/item/main.nhn?code={gicode}">NAVER 증권 바로가기</a>
        <a title="FnGuide:{sname}" target="_blank" href="http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{gicode}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=&strResearchYN=">FnGuide 바로가기</a>
    </div>
    <!-- 종목 기본 정보 END-->
    <div class="a-line"></div>
    '''

    # HTML 재무제표(연간/분기)
    html_fs_table = f'''
    {fs_table(sfsy, '연간')}
    <div class="goto-summary">
        <a title="연간재무제표 요약 바로가기" href="#fs-summary-1">연간재무제표 요약 바로가기</a>
    </div>
    {fs_table(sfsq, '분기')}
    '''

    # HTML 재무상태표
    deacha_head = [date for date, value in list(sdeacha.values())[0]]
    deacha_value = {key:[val[1] for val in value] for key, value in sdeacha.items()}

    # 부채 비율
    deacha_ratio = [round((deacha_value['부채'][idx]/v)*100, 2) for idx, v in enumerate(deacha_value['자본'])]

    step_size = '0'*len(str(max(deacha_value['자산'])))
    step_size = int('1' + step_size[1:])

    html_daecha = f'''
            <!-- 재무상태표 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title">재무상태표</div>
                <div class="fs-unit">단위: 억원, %</div>
            </div>
            <div class="fs-div">
                <table class="fs-data">
                    <thead>
                        <th>IFRS(연결)</th>
                        <th>{deacha_head[0]}</th>
                        <th>{deacha_head[1]}</th>
                        <th>{deacha_head[2]}</th>
                        <th>{deacha_head[3]}</th>
                    </thead>
                    <tbody>
                        <tr>
                            <th>자산</th>
                            <td>{comma(deacha_value['자산'][0])}</td>
                            <td>{comma(deacha_value['자산'][1])}</td>
                            <td>{comma(deacha_value['자산'][2])}</td>
                            <td>{comma(deacha_value['자산'][3])}</td>
                        </tr>
                        <tr>
                            <th>부채</th>
                            <td>{comma(deacha_value['부채'][0])}</td>
                            <td>{comma(deacha_value['부채'][1])}</td>
                            <td>{comma(deacha_value['부채'][2])}</td>
                            <td>{comma(deacha_value['부채'][3])}</td>
                        </tr>
                        <tr>
                            <th>자본</th>
                            <td>{comma(deacha_value['자본'][0])}</td>
                            <td>{comma(deacha_value['자본'][1])}</td>
                            <td>{comma(deacha_value['자본'][2])}</td>
                            <td>{comma(deacha_value['자본'][3])}</td>
                        </tr>
                        <!--
                        <tr>
                            <th>부채비율</th>
                            <td><span{' class="good-value"' if deacha_ratio[0] <= 150 else ' class="bad-value"' if deacha_ratio[0] >= 200 else ''}>{comma(deacha_ratio[0])}</span></td>
                            <td><span{' class="good-value"' if deacha_ratio[1] <= 150 else ' class="bad-value"' if deacha_ratio[1] >= 200 else ''}>{comma(deacha_ratio[1])}</span></td>
                            <td><span{' class="good-value"' if deacha_ratio[2] <= 150 else ' class="bad-value"' if deacha_ratio[2] >= 200 else ''}>{comma(deacha_ratio[2])}</span></td>
                            <td><span{' class="good-value"' if deacha_ratio[3] <= 150 else ' class="bad-value"' if deacha_ratio[3] >= 200 else ''}>{comma(deacha_ratio[3])}</span></td>
                        </tr>
                        -->
                    </tbody>
                </table>
            </div>
            <!-- 재무상태표 END -->
'''

    # HTML 재무비율
    rate_head = [date for date, value in list(srate.values())[0]]
    rate_value = {key:[val[1] for val in value] for key, value in srate.items()}

    html_fs_ratio = f'''
            <!-- 재무비율 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title" id="fs-table-3">재무비율</div>
                <div class="fs-unit">단위: %, 억원</div>
            </div>
            <div class="fs-div">
                <table class="fs-data">
                    <thead>
                        <th>IFRS(연결)</th>
                        <th>{rate_head[0]}</th>
                        <th>{rate_head[1]}</th>
                        <th>{rate_head[2]}</th>
                        <th>{rate_head[3]}</th>
                    </thead>
                    <tbody>
                        <tr>
                            <th>유동비율</th>
                            <td><span{' class="good-value"' if rate_value['유동비율'][0] >= 200 else ' class="bad-value"' if rate_value['유동비율'][0] < 100 else ''}>{comma(rate_value['유동비율'][0], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['유동비율'][1] >= 200 else ' class="bad-value"' if rate_value['유동비율'][1] < 100 else ''}>{comma(rate_value['유동비율'][1], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['유동비율'][2] >= 200 else ' class="bad-value"' if rate_value['유동비율'][2] < 100 else ''}>{comma(rate_value['유동비율'][2], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['유동비율'][3] >= 200 else ' class="bad-value"' if rate_value['유동비율'][3] < 100 else ''}>{comma(rate_value['유동비율'][3], decimal=True)}</span></td>
                        </tr>
                        <tr>
                            <th>당좌비율</th>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][0] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][0] < 100 else ''}>{comma(rate_value['당좌비율'][0], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][1] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][1] < 100 else ''}>{comma(rate_value['당좌비율'][1], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][2] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][2] < 100 else ''}>{comma(rate_value['당좌비율'][2], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][3] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][3] < 100 else ''}>{comma(rate_value['당좌비율'][3], decimal=True)}</span></td>
                        </tr>
                        <tr>
                            <th>부채비율</th>
                            <td><span{' class="good-value"' if rate_value['부채비율'][0] <= 150 else ' class="bad-value"' if rate_value['부채비율'][0] >= 200 else ''}>{comma(rate_value['부채비율'][0], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['부채비율'][1] <= 150 else ' class="bad-value"' if rate_value['부채비율'][1] >= 200 else ''}>{comma(rate_value['부채비율'][1], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['부채비율'][2] <= 150 else ' class="bad-value"' if rate_value['부채비율'][2] >= 200 else ''}>{comma(rate_value['부채비율'][2], decimal=True)}</span></td>
                            <td><span{' class="good-value"' if rate_value['부채비율'][3] <= 150 else ' class="bad-value"' if rate_value['부채비율'][3] >= 200 else ''}>{comma(rate_value['부채비율'][3], decimal=True)}</span></td>
                        </tr>
                        <tr>
                            <th>유보율</th>
                            <td>{comma(rate_value['유보율'][0], decimal=True)}</td>
                            <td>{comma(rate_value['유보율'][1], decimal=True)}</td>
                            <td>{comma(rate_value['유보율'][2], decimal=True)}</td>
                            <td>{comma(rate_value['유보율'][3], decimal=True)}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="fs-comment-text">유보율은 높을수록 좋다.</div>
            <!-- 재무비율 END -->
            <!-- 재무상태표/재무비율 Chart -->
            <div class="fs-chard-div">
                <canvas class="fs-bar-chart"></canvas>
                <script>
                    const fsBarChart = document.querySelector('.fs-bar-chart').getContext('2d');
                    const deptRatio = {deacha_ratio};
                    const fsBarCanvas = new Chart(fsBarChart, {{
                        type: 'bar',
                        data: {{
                            labels: ['2020/12', '2021/12', '2022/12', '2023/03'],
                            datasets: [{{
                                    label: '자본',
                                    data: {deacha_value['자본']},
                                    backgroundColor: 'rgba(16, 163, 127, 0.2)',
                                    borderColor: 'rgba(16, 163, 127, 1)',
                                    borderWidth: 1,
                                    stack: 'combined',
                                    yAxisID: 'y1',
                                }},
                                {{
                                    label: '부채',
                                    data: {deacha_value['부채']},
                                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                    borderColor: 'rgba(255, 99, 132, 1)',
                                    borderWidth: 1,
                                    stack: 'combined',
                                    yAxisID: 'y1',
                                }}, {{
                                    label: '부채비율',
                                    data: deptRatio,
                                    backgroundColor: 'rgba(0, 0, 128, 0.2)',
                                    borderColor: 'rgba(0, 0, 128, 1)',
                                    borderWidth: 1,
                                    type: 'line',
                                    yAxisID: 'y2',
                                }}
                            ]
                        }},
                        options: {{
                            scales: {{
                                y1: {{
                                    beginAtZero: true,
                                    stacked: true,
                                    position: 'left',
                                    ticks: {{
                                        stepSize: {step_size},
                                        callback: function(value, index, ticks) {{
                                            return `${{value.toLocaleString()}}억원`;
                                        }}
                                    }}
                                }},
                                y2: {{
                                    beginAtZero: true,
                                    position: 'right',
                                    grid: {{
                                        drawOnChartArea: false,
                                    }},
                                    ticks: {{
                                        callback: function(value, index, ticks) {{
                                            return `${{value.toLocaleString()}}%`;
                                        }}
                                    }},
                                    min: Math.round((Math.min(...deptRatio) / 5) * 5) - 5,
                                    max: Math.round((Math.max(...deptRatio) / 5) * 5) + 5,
                                    stepSize: 5
                                }}
                            }},
                        }}
                    }});
                </script>
            </div>
            <div class="goto-summary">
                <a title="재무비율 요약 바로가기" href="#fs-summary-3">재무비율 요약 바로가기</a>
            </div>
            <!-- 재무상태표/재무비율 Chart END -->'''
    
    # HTML 현금흐름표
    cash_head = [date for date, value in list(scash.values())[0]]
    cash_value = {key:[val[1] for val in value] for key, value in scash.items()}

    # 영업활동
    sales_act = cash_value['영업활동으로인한현금흐름']
    # 투자활동
    invest_act = cash_value['투자활동으로인한현금흐름']
    # 재무활동
    finance_act = cash_value['재무활동으로인한현금흐름']

    # 구분 조합
    sales_pm = ['+' if i > 0 else '-' for i in sales_act]
    invest_pm = ['+' if i > 0 else '-' for i in invest_act]
    finance_pm = ['+' if i > 0 else '-' for i in finance_act]

    pms = zip(sales_pm, invest_pm, finance_pm)
    pms_tx = ['/'.join(i) for i in list(pms)]

    cash_comb_name = {
        '+/-/-' : '<span class="good-value">우량</span>',
        '+/-/+' : '<span class="good-value">성장</span>',
        '+/+/+' : '과도기',
        '+/+/-' : '과도기',
        '-/-/-' : '재활',
        '-/-/+' : '재활',
        '-/+/-' : '<span class="bad-value">위험</span>',
        '-/+/+' : '<span class="bad-value">접근금지</span>',
    }


    html_cash = f'''
            <!-- 현금흐름표 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title" id="fs-table-4">현금흐름표</div>
                <div class="fs-unit">단위: 억원</div>
            </div>
            <div class="fs-div">
                <table class="fs-data">
                    <thead>
                        <th>IFRS(연결)</th>
                        <th>{cash_head[0]}</th>
                        <th>{cash_head[1]}</th>
                        <th>{cash_head[2]}</th>
                        <th>{cash_head[3]}</th>
                    </thead>
                    <tbody>
                        <tr>
                            <th>영업활동</th>
                            <td><span{' class="minus-value"' if sales_act[0] < 0 else ''}>{comma(sales_act[0])}</span></td>
                            <td><span{' class="minus-value"' if sales_act[1] < 0 else ''}>{comma(sales_act[1])}</span></td>
                            <td><span{' class="minus-value"' if sales_act[2] < 0 else ''}>{comma(sales_act[2])}</span></td>
                            <td><span{' class="minus-value"' if sales_act[3] < 0 else ''}>{comma(sales_act[3])}</span></td>
                        </tr>
                        <tr>
                            <th>투자활동</th>
                            <td><span{' class="minus-value"' if invest_act[0] < 0 else ''}>{comma(invest_act[0])}</span></td>
                            <td><span{' class="minus-value"' if invest_act[1] < 0 else ''}>{comma(invest_act[1])}</span></td>
                            <td><span{' class="minus-value"' if invest_act[2] < 0 else ''}>{comma(invest_act[2])}</span></td>
                            <td><span{' class="minus-value"' if invest_act[3] < 0 else ''}>{comma(invest_act[3])}</span></td>
                        </tr>
                        <tr>
                            <th>재무활동</th>
                            <td><span{' class="minus-value"' if finance_act[0] < 0 else ''}>{comma(finance_act[0])}</span></td>
                            <td><span{' class="minus-value"' if finance_act[1] < 0 else ''}>{comma(finance_act[1])}</span></td>
                            <td><span{' class="minus-value"' if finance_act[2] < 0 else ''}>{comma(finance_act[2])}</span></td>
                            <td><span{' class="minus-value"' if finance_act[3] < 0 else ''}>{comma(finance_act[3])}</span></td>
                        </tr>
                        <tr>
                            <th rowspan="2">구분</th>
                            <td>{cash_gubun(pms_tx[0])}</td>
                            <td>{cash_gubun(pms_tx[1])}</td>
                            <td>{cash_gubun(pms_tx[2])}</td>
                            <td>{cash_gubun(pms_tx[3])}</td>
                        </tr>
                        <tr>
                            <td>{cash_comb_name[pms_tx[0]]}</td>
                            <td>{cash_comb_name[pms_tx[1]]}</td>
                            <td>{cash_comb_name[pms_tx[2]]}</td>
                            <td>{cash_comb_name[pms_tx[3]]}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="goto-summary">
                <a title="현금흐름표 요약 바로가기" href="#fs-summary-4">현금흐름표 요약 바로가기</a>
            </div>
            <!-- 현금흐름표 END -->
            <div class="a-line"></div>
            <br/>
            <div style="max-width: 600px;margin-bottom: 30px;">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5461323615661647"
                crossorigin="anonymous"></script>
            <!-- POSTAD -->
            <ins class="adsbygoogle"
                style="display:block"
                data-ad-client="ca-pub-5461323615661647"
                data-ad-slot="3674534741"
                data-ad-format="auto"
                data-full-width-responsive="true"></ins>
            <script>
                (adsbygoogle = window.adsbygoogle || []).push({{}});
            </script>
            </div>
            <br/>
            '''

    # 적정주가 PER 기준으로 계산 
    # 기준 날짜
    ydate = sfsy['year_chk']['c4']

    # 영업이익
    yprofit = sfsy['영업이익']['c4']
    yp_flag = False
    # 올해 예상치가 없는 경우
    if yprofit == None :
        # 가중평균으로 계산
        yvs = [v for v in sfsy['영업이익'].values() if v != None]
        yprofit = set_weight_aver(*yvs)
        yp_flag = True

    # 예상영업이익이 적자라면? 그냥 이건 패스
    if yprofit < 0 :
        html_per = f'''
            <!-- 적정주가 계산 파트 -->
            <div class="report-title" id="fs-calc-result">적정주가 계산</div>
            <!-- 영업이익*PER 적정 주가 계산 -->
            <div class="fs-head fs-with-q" style="margin-top: 20px;margin-bottom: 10px">
                <div class="fs-with-q">
                    <div class="fs-title" id="fs-table-5">영업이익*PER</div>
                    <div>
                        <a target="_blank" href="https://waymond.tistory.com/40" title="적정주가 간단하게 계산해보기">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                        </svg>                  
                        </a>
                    </div>
                </div>
            </div>
            <div class="none-data">예상되는 영업이익이 적자이므로 적정주가 계산을 진행하지 않습니다.</div>
            <!-- 영업이익*PER END -->
        '''
    # 필요한 PER
    # 예상 PER
    yper = sfsy['PER수정주가']['c4']
    # Company Guide의 예상 PER / 없으면 가중 PER만
    # 가중 PER
    # 최근 3년 가중평균으로 계산
    ywvp = [v for v in list(sfsy['PER수정주가'].values())[:3] if v != None]

    # 가중 PER
    ywper = set_weight_aver(*ywvp)

    # 업종 PER (NAVER/CG 따로)
    nv_per = same_pers['naver']
    nv_url = same_pers['naver_url']
    cg_per = same_pers['company']
    cg_url = same_pers['company_url']

    # 발행 주식수
    sc = scommon

    html_per = f'''
            <!-- 적정주가 계산 파트 -->
            <div class="report-title" id="fs-calc-result">적정주가 계산</div>
            <!-- 영업이익*PER 적정 주가 계산 -->
            <div class="fs-head fs-with-q" style="margin-top: 20px;margin-bottom: 10px">
                <div class="fs-with-q">
                    <div class="fs-title" id="fs-table-5">영업이익*PER</div>
                    <div>
                        <a target="_blank" href="https://waymond.tistory.com/40" title="적정주가 간단하게 계산해보기">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                        </svg>                  
                        </a>
                    </div>
                </div>
            </div>
            <div class="standard-info">
                <div class="info">
                    <div class="info-cell">
                        <div class="cell-head">영업이익</div>
                        <div class="cell-desc{' weight-value' if yp_flag else ''}">{comma(yprofit, decimal=True)}억원</div>
                    </div>

                    <div class="info-cell">
                        <div class="cell-head">기준</div>
                        <div class="cell-desc">{ydate}</div>
                    </div>
                </div>
                <div class="info-one">
                    <div class="cell-head">현재주가</div>
                    <div class="cell-desc">{comma(current_price)}원</div>
                </div>
                <div class="info-one">
                    <div class="cell-head">발행주식수</div>
                    <div class="cell-desc">{comma(sc)}</div>
                </div>
            </div>
            <div class="fs-div" style="margin-top: 10px">
                <table class="fs-data">
                    <thead>
                        <th>구분</th>
                        <th>PER</th>
                        <th>기업가치</th>
                        <th>적정주가</th>
                    </thead>
                    <tbody>
                        <tr>
                            <th>올해 예상</th>
                            <td>{comma(yper, 2)}</td>
                            <td>{comma(cp_value(yprofit, yper, sc)['value'])}{'억원' if cp_value(yprofit, yper, sc)['value'] != '' else ''}</td>
                            <td>{comma(cp_value(yprofit, yper, sc)['price'])}{'원' if cp_value(yprofit, yper, sc)['price'] != '' else ''}</td>
                        </tr>
                        <tr>
                            <th>가중 평균</th>
                            <td>{comma(ywper, 2) if ywper != None else ''}</td>
                            <td>{comma(cp_value(yprofit, ywper, sc)['value']) if ywper != None else ''}{'억원' if ywper != None else ''}</td>
                            <td>{comma(cp_value(yprofit, ywper, sc)['price']) if ywper != None else ''}{'원' if ywper != None else ''}</td>
                        </tr>
                        <tr>
                            <th><a target="_blank" href="{nv_url}">업종 (NV)</a></th>
                            <td>{comma(nv_per, 2)}</td>
                            <td>{comma(cp_value(yprofit, nv_per, sc)['value'])}억원</td>
                            <td>{comma(cp_value(yprofit, nv_per, sc)['price'])}원</td>
                        </tr>
                        <tr>
                            <th><a target="_blank" href="{cg_url}">업종 (FG)</a></th>
                            <td>{comma(cg_per, 2)}</td>
                            <td>{comma(cp_value(yprofit, cg_per, sc)['value'])}억원</td>
                            <td>{comma(cp_value(yprofit, cg_per, sc)['price'])}원</td>
                        </tr>
                        <tr>
                            <th>별도 조정</th>
                            <td class="per-input">
                                <div>
                                    <input class="custom-input" value="10" type="number" min="0" max="100" step="1" />
                                </div>
                                <div>
                                    PER 입력
                                </div>
                            </td>
                            <td><span class="custom-value per-fair-value"></span></td>
                            <td><span class="custom-value per-fair-price"></span></td>
                        </tr>
                    </tbody>
                </table>
                
            </div>
            <div class="fs-comment-text">
                <div><b>별도 조정의 PER은 직접 수정 가능합니다.</b></div>
                <div>NV=NAVER 증권 기준 동일 업종 PER</div>
                <div>FG=FnGuide 기준 동일 업종 PER</div>
            </div>
            <!-- 영업이익*PER END -->
            <!-- 영업이익*PER Chart -->
            <div class="fs-chard-div">
                <canvas class="fs-per-chart"></canvas>
                <script>
                    const perCanvas = document.querySelector('.fs-per-chart').getContext('2d');
                    const nowValue = {current_price};
                    let calcPer = 0;
                    const perChart = new Chart(perCanvas, {{
                        type: 'line',
                        data: {{
                            labels: ['올해 예상', '가중 평균', '업종 PER(NV)', '업종 PER(CG)', '별도 조정'],
                            datasets: [{{
                                label: '적정주가',
                                data: [{'null' if cp_value(yprofit, yper, sc)['price'] == '' else cp_value(yprofit, yper, sc)['price']}, {cp_value(yprofit, ywper, sc)['price']  if ywper != None else 'null'}, {cp_value(yprofit, nv_per, sc)['price']}, {cp_value(yprofit, cg_per, sc)['price']}, calcPer],
                                backgroundColor: 'rgba(16, 163, 127, 0.2)',
                                borderColor: 'rgba(16, 163, 127, 1)',
                                borderWidth: 1,
                                type: 'bar'
                            }}]
                        }},
                        options: {{
                            scales: {{
                                y: {{
                                    beginAtZero: true,
                                    position: 'left',
                                    ticks: {{
                                        callback: function(value, index, ticks) {{
                                            return `${{value.toLocaleString()}}원`;
                                        }}
                                    }}
                                }}
                            }},
                            plugins: {{
                                legend: {{
                                    onClick: (e) => e.stopPropagation()
                                }},
                                annotation: {{
                                    annotations: {{
                                        currentValue: {{
                                            type: 'line',
                                            mode: 'horizontal',
                                            scaleID: 'y',
                                            value: nowValue,
                                            borderColor: 'rgba(255, 127, 80, 1)',
                                            borderWidth: 1.5,
                                            label: {{
                                                content: '현재 주가',
                                                enabled: true,
                                                position: 'top',
                                            }}
                                        }},
                                        label1: {{
                                            type: 'label',
                                            yValue: nowValue,
                                            content: [`현재 주가 ${{nowValue.toLocaleString()}}원`, ''],
                                            color: 'rgba(255, 127, 80, 1)',
                                            font: {{
                                                size: 13,
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }});

                    const perInput = document.querySelector('.per-input');
                    const perHandler = (perValue) => {{
                        const fairValue = document.querySelector('.per-fair-value');
                        const fairPrice = document.querySelector('.per-fair-price');

                        if (parseInt(perValue) > 100) {{
                            perValue = 100;
                        }}

                        const earning = {yprofit}; // 영업이익
                        const stockCnt = {sc}; // 발행주식수
                        const per = parseFloat(perValue);

                        // 기업가치
                        let calcEarning = earning * per;
                        let calcPrice = (calcEarning / stockCnt) * 100000000;

                        calcEarning = calcEarning.toFixed(1);
                        calcPrice = calcPrice.toFixed(0);

                        if (isNaN(calcEarning)) {{
                            fairValue.innerHTML = '';
                            fairPrice.innerHTML = '';
                            calcPrice = 0;
                        }} else {{
                            fairValue.innerHTML = `${{parseFloat(calcEarning).toLocaleString()}}억원`;
                            fairPrice.innerHTML = `${{parseInt(calcPrice).toLocaleString()}}원`;
                        }}

                        calcPer = calcPrice;
                        perChart.data.datasets[0].data[4] = calcPer;

                        perChart.update();
                    }};

                    perInput.addEventListener('input', (event) => {{
                        perHandler(event.target.value);
                    }});
                    perHandler(10);
                </script>
            </div>
            <div class="goto-summary">
                <a title="영업이익*PER 요약 바로가기" href="#fs-summary-5">적정주가 계산 요약 바로가기</a>
            </div>
            <!-- 영업이익*PER Chart END -->'''

    # HTML SRIM
    srim = SRIM(gicode, bbb)

    # 지배주주지분
    srim_jibun = srim['지배주주지분']
    srim_result = srim['srim']
    # 예상 ROE
    e_roe = srim_result['ce']['roe'] if 'ce' in srim_result else None
    e_chk = e_roe >= bbb if 'ce' in srim_result else None
    e_value = srim_result['ce']['w'] if 'ce' in srim_result else None
    e_price = [val['sprice'] for val in e_value.values()] if e_value != None else None

    # 가중 ROE
    w_roe = srim_result['we']['roe']
    w_chk = w_roe >= bbb
    w_value = srim_result['we']['w']
    w_price = [val['sprice'] for val in w_value.values()] if w_value != None else None

    html_srim = f'''
            <!-- SRIM 계산 -->
            <div class="fs-head fs-with-q" style="margin-top: 20px;margin-bottom: 10px">
                <div class="fs-with-q">
                    <div class="fs-title" id="fs-table-6">SRIM</div>
                    <div>
                        <a target="_blank" href="https://waymond.tistory.com/41" title="주식투자 전략:SRIM으로 적정주가 계산">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                        </svg>                  
                        </a>
                    </div>
                </div>
            </div>
            <div class="standard-info">
                <div class="info-one">
                    <div class="cell-head">발행주식수</div>
                    <div class="cell-desc">{comma(scommon)}</div>
                </div>
                <div class="info-one">
                    <div class="cell-head">자사주</div>
                    <div class="cell-desc">{comma(streasury)}</div>
                </div>

                <div class="info-one">
                    <div class="cell-head">지배주주지분</div>
                    <div class="cell-desc">{comma(srim_jibun)}</div>
                </div>

                <div class="info-one">
                    <div class="cell-head">회사채 할인율</div>
                    <div class="cell-desc fs-flex">
                        <div class="fs-disc-rate">{bbb}%</div>
                        <div>
                            <div class="srim-ratio-btn">변경</div>
                        </div>
                    </div>
                </div>

                <div class="info">
                    <div class="info-cell">
                        <div class="cell-head">예상 ROE</div>
                        <div class="cell-desc">{comma(e_roe, 2) if e_roe != None else ''}</div>
                    </div>
                    <div class="info-cell">
                        <div class="cell-head">가중 ROE</div>
                        <div class="cell-desc">{comma(w_roe, 2)}</div>
                    </div>
                </div>
            </div>
            <div class="fs-comment-text">
                회사채 수익률의 기본값은 BBB- 등급의 5년 수익률입니다.
            </div>
            <div id="myModal" class="fs-modal">
                <div class="modal-content">
                    <div class="close">&times;</div>
                    <div class="fs-spread-head">등급별금리스프레드</div>
                    <div class="fs-spread-date">기준일: {spread_date} / 단위:%</div>
                    <div class="fs-accordion">
                        {rate_acco_item(spread_rate)}
                    </div>
                </div>
            </div>
            <script>
// SRIM Calculator
const srimCalculator = (ipROE, ipStockCnt, ipSelf, ipInter, ipRate)=>{{
    if( ipROE == null) return;
    const dan = 100000000;
    // 기업가치
    const numerator = ipInter*(ipROE - ipRate);
    const b0 = ipInter + (numerator/ipRate);
    
    // 주식수
    const realCnt = ipStockCnt - ipSelf;

    // 적정주가
    const fairValue = (b0*dan)/realCnt;
    //console.log(Math.round(fairValue));

    // 초과이익
    const excessProfit = ipInter*((ipROE/100) - (ipRate/100));
    // 초과이익, 초과손실
    const excessFlag = excessProfit > 0 ? true : false;

    let ws = {{
        w1 : 1,
        w2 : 0.9,
        w3 : 0.8,
        w4 : 0.7,
        w5 : 0.6,
        w6 : 0.5,
    }}

    Object.entries(ws).forEach(([key, value]) => {{
        const deno = (1+(ipRate/100)) - value;
        const wCalc = value/deno;
        const svalue = ipInter + (excessProfit*wCalc);
        const sprice = (svalue/realCnt)*dan;
        ws[key] = {{
            svalue: Math.round(svalue),
            sprice: Math.round(sprice)
        }}
    }});

    return {{
        flag : excessFlag,
        srim: ws
    }}
}}

const setSrimResult = (tableClass, ipROE, ipRate)=>{{
    if( ipROE == null ){{
        return [];
    }}
    const ws = srimCalculator(ipROE, {scommon}, {streasury}, {srim_jibun}, ipRate);
    // SRIM Table
    const srimTable = document.querySelector(tableClass);
    if( srimTable == undefined ){{
        return [];
    }};
    if( ws == null ){{
        return [];
    }};

    const flagTH = srimTable.querySelector('.srim-flag span');
    if( ws.flag ){{       
        flagTH.innerHTML = '초과이익';
        flagTH.classList.remove('bad-value');
    }} else {{
        flagTH.innerHTML = '초과손실';
        flagTH.classList.add('bad-value');
    }}

    const srimValueCell = srimTable.querySelectorAll('.srim-value');
    const srimPriceCell = srimTable.querySelectorAll('.srim-price');

    const srims = ws.srim;
    let resultList = [];
    Object.entries(srims).forEach(([key, srim], index)=>{{
        srimValueCell[index].innerHTML = `${{srim.svalue.toLocaleString()}}억`;
        srimPriceCell[index].innerHTML = `${{srim.sprice.toLocaleString()}}원`;
        resultList.push(srim.sprice);
    }});

    return resultList;
}}

document.addEventListener('DOMContentLoaded', (event) => {{
    const modal = document.querySelector('#myModal');
    const btn = document.querySelector(".srim-ratio-btn");
    const span = modal.querySelector(".close");

    btn.onclick = function() {{
        modal.style.display = "block";
    }}

    span.onclick = function() {{
        modal.style.display = "none";
    }}

    window.onclick = function(event) {{
        if (event.target == modal) {{
            modal.style.display = "none";
        }}
    }}


    const accordionButtons = document.querySelectorAll('.fs-accordion-btn');

    accordionButtons.forEach(function (button) {{
    button.addEventListener('click', function () {{
        const accordionContent = this.nextElementSibling.querySelector('.fs-accordion-content');
        const accordionItem = this.parentElement;
        const openItem = document.querySelector('.fs-accordion-item.open');

        if (openItem && openItem !== accordionItem) {{
            closeAccordion(openItem);
        }}

        if (accordionItem.classList.contains('open')) {{
            closeAccordion(accordionItem);
        }} else {{
            openAccordion(accordionItem);
        }}
        }});
    }});

    function openAccordion(accordionItem) {{
        const content = accordionItem.querySelector('.fs-accordion-content');
        accordionItem.classList.add('open');
        content.style.maxHeight = content.scrollHeight + 'px';
    }}

    function closeAccordion(accordionItem) {{
        const content = accordionItem.querySelector('.fs-accordion-content');
        accordionItem.classList.remove('open');
        content.style.maxHeight = null;
    }}
}});
            </script>
            <div class="srim-page">
                <div class="srim-roe-head">
                    <div class="srim-roe {'roe-selected' if e_roe != None else 'fs-hidden'}">예상 ROE</div>
                    <div class="srim-roe {'roe-selected' if e_roe == None else ''}">가중 ROE</div>
                    <div class="srim-roe-info">{'예상 ROE가 없습니다. 가중 ROE로만 제공됩니다.' if e_roe == None else '기준 ROE 선택'}</div>
                </div>
                <div class="fs-comment-text" style="margin-top: 5px">
                    <b>ROE가 회사채 수익률보다 낮은 경우</b>에는 <b>'초과이익'이 아닌</b> <span class="bad-value"><b>'초과손실' 기준</b></span>으로 판단합니다.
                </div>
                <div class="fs-div srim-result" style="margin-top: 10px">
                    <table class="srim-e-roe fs-data srim-table{' post-fs-hidden' if e_value == None else ''}">
                        <thead>
                            <th class="srim-flag"><span></span></th>
                            <th>기업가치</th>
                            <th>적정주가</th>
                        </thead>
                        <tbody>
                            <tr>
                                <th>지속</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>10% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>20% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>30% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>40% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>50% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                        </tbody>
                    </table>

                    <table class="srim-w-roe fs-data srim-table{' post-fs-hidden' if e_value != None else ''}">
                        <thead>
                            <th class="srim-flag"><span></span></th>
                            <th>기업가치</th>
                            <th>적정주가</th>
                        </thead>
                        <tbody>
                            <tr>
                                <th>지속</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>10% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>20% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>30% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>40% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                            <tr>
                                <th>50% 감소</th>
                                <td class="srim-value"></td>
                                <td class="srim-price"></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <!-- SRIM END -->
            <!-- SRIM Chart -->
            <div class="fs-chard-div">
                <canvas class="fs-srim-chart"></canvas>
            </div>
            <script>
            // SRIM CHART
            const srimCanvas = document.querySelector('.fs-srim-chart').getContext('2d');
            let srimResults = [
                setSrimResult('.srim-e-roe', {'null' if e_roe == None else e_roe}, {bbb}),
                setSrimResult('.srim-w-roe', {w_roe}, {bbb}),
            ];
            const srimNowValue = {current_price};
            let setSRIM = srimResults[{0 if e_value != None else 1}];
            const srimChart = new Chart(srimCanvas, {{
                type: 'line',
                data: {{
                    labels: ['지속', '10% 감소', '20% 감소', '30% 감소', '40% 감소', '50% 감소'],
                    datasets: [{{
                        label: '적정주가',
                        data: setSRIM,
                        backgroundColor: 'rgba(16, 163, 127, 0.2)',
                        borderColor: 'rgba(16, 163, 127, 1)',
                        borderWidth: 1,
                        type: 'bar'
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            position: 'left',
                            ticks: {{
                                callback: function(value, index, ticks) {{
                                    return `${{value.toLocaleString()}}원`;
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            onClick: (e) => e.stopPropagation()
                        }},
                        annotation: {{
                            annotations: {{
                                currentValue: {{
                                    type: 'line',
                                    mode: 'horizontal',
                                    scaleID: 'y',
                                    value: srimNowValue,
                                    borderColor: 'rgba(255, 127, 80, 1)',
                                    borderWidth: 1.5,
                                    label: {{
                                        content: '현재 주가',
                                        enabled: true,
                                        position: 'top',
                                    }}
                                }},
                                label1: {{
                                    type: 'label',
                                    yValue: srimNowValue,
                                    content: [`현재 주가 ${{srimNowValue.toLocaleString()}}원`, ''],
                                    color: 'rgba(255, 127, 80, 1)',
                                    font: {{
                                        size: 13,
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            // ROE 선택 기능
            const roeBtn = document.querySelectorAll('.srim-roe');
            const roeSelected = 'roe-selected';
            const roeHandler = (index) => {{
                const roeHead = document.querySelector('.srim-roe-head');
                const selectedRoe = roeHead.querySelector(`.${{roeSelected}}`);
                const roeTables = document.querySelectorAll('.srim-table');
                selectedRoe.classList.remove(roeSelected);

                roeBtn[index].classList.add(roeSelected);
                roeTables.forEach((table) => {{
                    table.classList.add('post-fs-hidden');
                }});
                roeTables[index].classList.remove('post-fs-hidden');

                // Chart update
                setSRIM = srimResults[index];
                srimChart.data.datasets[0].data = setSRIM;

                srimChart.update();
            }};

            roeBtn.forEach((roe, index) => {{
                roe.addEventListener('click', () => {{
                    roeHandler(index);
                }});
            }});


            const setSrimValue = (tableClass, ipRoe, ipRate) => {{
                const srimTable = document.querySelector(tableClass);
                if( srimTable == undefined || srimTable == null ) return;

                const srimResult = setSrimResult(tableClass, ipRoe, ipRate);
                
                const resultIndex = tableClass === '.srim-e-roe' ? 0 : 1;
                srimResults[resultIndex] = srimResult
                setSRIM = srimResults[resultIndex];
                // Chart update
                srimChart.data.datasets[0].data = srimResult;
                srimChart.update();
            }}

            document.addEventListener('DOMContentLoaded', ()=>{{
                const accoValues = document.querySelectorAll('.fs-spread-value');
                const modal = document.querySelector('#myModal');
                accoValues.forEach((acco)=>{{
                    acco.addEventListener('click', ()=>{{
                        document.querySelector('.fs-disc-rate').innerHTML = `${{acco.innerHTML}}%`;
                        const accoFloat = parseFloat(acco.innerHTML);
                        modal.style.display = "none";

                        setSrimValue('.srim-e-roe', {'null' if e_roe == None else e_roe}, accoFloat);
                        setSrimValue('.srim-w-roe', {w_roe}, accoFloat);
                        const roes = document.querySelectorAll('.srim-roe');

                        if( !roes[0].classList.contains('fs-hidden') ){{
                            roes[0].click();
                        }}else{{
                            roes[1].click();
                        }}
                    }})
                }});
            }});
        </script>
        <!-- SRIM Chart END -->
        <div class="goto-summary">
            <a title="SRIM 요약 바로가기" href="#fs-summary-6">SRIM 계산 요약 바로가기</a>
        </div>
        <div class="a-line"></div>'''
    # HTML Body (END)
    html_fs_body = f'''
    {html_head}
    {html_info}
    <div class="report-title" id="finance-datas">재무정보</div>
    <div class="financial-statements">
        <div class="fs-table">
    {html_fs_table}
    {html_daecha}
    {html_fs_ratio}
    {html_cash}
    {html_per}
    {html_srim}
        </div>
    </div>
    <script type="text/javascript">
    const links = document.querySelectorAll('.goto-summary a');

    links.forEach(link => {{
    link.addEventListener('click', function(e) {{
        e.preventDefault();

        const target = document.querySelector(this.getAttribute('href'));
        if( target === null || target === undefined ){{
            return;
        }}

        target.scrollIntoView({{ behavior: 'smooth' }});

        target.classList.add('summary-focus');

        setTimeout(() => {{
            target.classList.remove('summary-focus');
        }}, 2000);
    }});
    }});
    </script>
    <!-- END -->
    <!-- AI 분석 -->
    <div style="display: hidden;" id="fs-summary-ai"></div>

    <!-- 여기에 ChatGPT 내용 삽입 -->
    <!-- AI 분석 END -->
    <div class="a-line"></div>
    <div class="fs-news-report">
        <div class="fs-mypost-list">
            <div class="fs-mypost">📰 뉴스/공시</div>
            <div class="fs-mypost-link">
                <a target="_blank" href="https://finance.naver.com/item/news.naver?code={gicode}">
                    <div>네이버</div>
                </a>
            </div>
            <div class="fs-mypost-link">
                <a target="_blank" href="https://finance.daum.net/quotes/A{gicode}#news/stock">
                    <div>다음</div>
                </a>
            </div>
            <div class="fs-mypost-link">
                <a target="_blank" href="http://comp.fnguide.com/SVO2/ASP/SVD_Disclosure.asp?pGB=1&gicode=A{gicode}&cID=&MenuYn=Y&ReportGB=&NewMenuID=107&stkGb=701">
                    <div>FnGuide</div>
                </a>
            </div>
        </div>
        <div class="fs-mypost-list">
            <div class="fs-mypost">📋 리포트</div>
            <div class="fs-mypost-link">
                <a target="_blank" href="https://finance.naver.com/research/company_list.naver?keyword=&brokerCode=&writeFromDate=&writeToDate=&searchType=itemCode&itemName=%BB%EF%BC%BA%C0%FC%C0%DA&itemCode={gicode}&x=10&y=12">
                    <div>네이버</div>
                </a>
            </div>
            <div class="fs-mypost-link">
                <a target="_blank" href="https://finance.daum.net/quotes/A{gicode}#investments/report">
                    <div>다음</div>
                </a>
            </div>
            <div class="fs-mypost-link">
                <a target="_blank" href="http://comp.fnguide.com/SVO2/ASP/SVD_Report_Trend.asp?pGB=1&gicode=A{gicode}&cID=&MenuYn=Y&ReportGB=&NewMenuID=801&stkGb=701">
                    <div>FnGuide</div>
                </a>
            </div>
        </div>
    </div>
    <div class="a-line"></div>
    <!-- BUY ME A COFFEE -->
    <div class="coffee-div">
        <div class="coffee-script" style="display: flex;flex-direction: column;align-items: center;">
            <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="duron7456a" data-color="#40DCA5" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#ffffff" data-coffee-color="#FFDD00" ></script>
            <div class="coffee-text">
                커피 한 잔으로<br/>저를 응원해주세요!
            </div>
        </div>
    </div>
    <!-- BUY ME A COFFEE END -->
    <div class="fs-mypost-list">
        <div class="fs-mypost">📗 관련 포스트</div>
        <div class="fs-mypost-link">
            <a target="_blank" href="https://waymond.tistory.com/14">
                <div>주식 초보자 마인드 셋</div>
            </a>
        </div>
        <div class="fs-mypost-link">
            <a target="_blank" href="https://waymond.tistory.com/16">
                <div>상장폐지 조건</div>
            </a>
        </div>
        <div class="fs-mypost-link">
            <a target="_blank" href="https://waymond.tistory.com/22">
                <div>기본적 분석/기술적 분석</div>
            </a>
        </div>
        <div target="_blank" class="fs-mypost-link">
            <a href="https://waymond.tistory.com/23">
                <div>재무제표에 대해서</div>
            </a>
        </div>
        <div target="_blank" class="fs-mypost-link">
            <a href="https://waymond.tistory.com/27">
                <div>재무제표에서 꼭 확인해야 하는 것들</div>
            </a>
        </div>
        <div target="_blank" class="fs-mypost-link">
            <a href="https://waymond.tistory.com/85">
                <div>주식 지표 PER/PBR/ROE 알아보기</div>
            </a>
        </div>
        <div target="_blank" class="fs-mypost-link">
            <a href="https://waymond.tistory.com/86">
                <div>재무비율 알아보기</div>
            </a>
        </div>
        <div target="_blank" class="fs-mypost-link">
            <a href="https://waymond.tistory.com/40">
                <div>간단한 적정주가 계산:영업이익*PER</div>
            </a>
        </div>
        <div target="_blank" class="fs-mypost-link">
            <a href="https://waymond.tistory.com/41">
                <div>SRIM으로 적정주가 계산/저평가 주식</div>
            </a>
        </div>
    </div>
    '''
    re_date = sdate.split(' ')[0]
    file_date = re_date
    file_date = file_date.replace('/', '')
    file_name = f'{file_date}_{gicode}_{sname}.html'
    with open(file_name, 'w') as f :
        f.write(html_fs_body)
    print(f'{file_name} file has been created.')
    post_name = f'[A.I] {sname}:주식 재무 분석 & 적정주가 계산_{re_date}'
    print(post_name)
    return {
        'file_name': file_name,
        'stock_name': sname,
        'post_name': post_name
    }



### AI Generator
def for_chatgpt(gicode) :
    fs = get_stock_items(gicode)
    current_price = fs['current']['current_price']
    
    # 연간재무제표
    stock_name = fs['name']
    fsy = pd.DataFrame(fs['year'])
    fsy.set_index('year_chk', inplace=True)
    fsy['영업이익률'] = (fsy['영업이익']/fsy['매출액'])*100
    fsy['당기순이익률'] = (fsy['당기순이익']/fsy['매출액'])*100
    fsy['자본잠식률'] = ((fsy['자본금']-fsy['자본총계'])/fsy['자본금'])*100
    fsy.rename(columns={'PER수정주가': 'PER', 'PBR수정주가': 'PBR'}, inplace=True)

    # 분기재무제표
    fsq = pd.DataFrame(fs['quarter'])
    fsq.set_index('year_chk', inplace=True)
    fsq['영업이익률'] = (fsq['영업이익']/fsq['매출액'])*100
    fsq['당기순이익률'] = (fsq['당기순이익']/fsq['매출액'])*100
    fsq['자본잠식률'] = ((fsq['자본금']-fsq['자본총계'])/fsq['자본금'])*100
    fsq.rename(columns={'PER수정주가': 'PER', 'PBR수정주가': 'PBR'}, inplace=True)

    # 기준 컬럼
    columns = ['매출액', '영업이익','영업이익률', '당기순이익', 'ROE', 'PER', 'PBR']

    # 연간재무제표
    annual_financial_statements = fsy[columns]
    # 분기별재무제표
    quarterly_financial_statements = fsq[columns]


    # 재무상태표
    ftable = fs['daecha_table']
    col_name = [date for date, value in ftable['자산']]
    row_data = {key: [v for d, v in values] for key, values in ftable.items()}
    row_data['year_chk'] = col_name
    financial_statements = pd.DataFrame(row_data)
    financial_statements.set_index('year_chk', inplace=True)
    financial_statements['부채비율'] = (financial_statements['부채']/financial_statements['자본'])*100
    
    # 재무비율
    ftable = fs['rate']
    col_name = [date for date, value in ftable['유보율']]
    row_data = {key: [v for d, v in values] for key, values in ftable.items()}
    row_data['year_chk'] = col_name
    financial_ratio = pd.DataFrame(row_data)
    financial_ratio.set_index('year_chk', inplace=True)
    

    # 현금흐름표
    cash_table = fs['cash_table']
    col_name = [date for date, value in cash_table['영업활동으로인한현금흐름']]
    row_data = {key: [v for d, v in values] for key, values in cash_table.items()}
    row_data['year_chk'] = col_name
    statement_of_cash_flows = pd.DataFrame(row_data)
    statement_of_cash_flows.set_index('year_chk', inplace=True)
    

    # PER 계산
    # 올해 예상 PER
    estimated_per = annual_financial_statements.iloc[3]['PER']
    if estimated_per == None :
        estimated_per = np.nan
    # 최근 가중 PER
    before_per = list(annual_financial_statements.iloc[:3]['PER'].values)
    before_per = [i for i in before_per if i != None and not np.isnan(i)]
    
    # 가중 PER
    weighted_per = set_weight_aver(*before_per)
    
    if weighted_per == None :
        weighted_per = np.nan
    
    # 영업이익
    estimated_profit = annual_financial_statements.iloc[3]['영업이익']

    # 영업이익 구분
    profit_flag = '올해 예상 영업이익'
    if np.isnan(estimated_profit) :
        profit_flag = '가중평균 영업이익'
        before_profit = list(annual_financial_statements.iloc[:3]['영업이익'].values)
        before_profit = [i for i in before_profit if i != None]
        estimated_profit = set_weight_aver(*before_profit)

    estimated_profit = estimated_profit*100000000

    # 발행주식수
    common = fs['common']
    # 적정주가 계산 (PER)
    compare_price = {
        '현재주가': [current_price],
        '영업이익': [estimated_profit/100000000],
        '영업이익_구분': [profit_flag],
        '예상PER_적정주가' : [round((estimated_profit*estimated_per)/common) if not (np.isnan(estimated_per)) else None],
        '가중PER_적정주가' : [round((estimated_profit*weighted_per)/common) if not (np.isnan(weighted_per))  else None],
    }

    # PER 적정주가 데이터
    calc_fair_value_use_per = pd.DataFrame(compare_price)

    # SRIM
    bbb = float(fs['bbb'])
    srim_result = SRIM(gicode, bbb)['srim']
    ce_roe = None
    if 'ce' in srim_result :
        ce_srim = srim_result['ce']
        ce_roe = ce_srim['roe']
        # 예상 ROE가 있는 경우
        if ce_roe != None :
            ce_result = pd.DataFrame(ce_srim['w'])
            ce_result.drop(index='svalue', inplace=True)
            ce_result['현재 주가'] = current_price
            ce_result['ROE'] = ce_roe
            ce_result['구분'] = '초과이익' if ce_roe>=bbb else '초과손실'
            ce_result.rename(index={
                'sprice': '올해예상_ROE'
            }, columns={
                'w1': '지속_적정주가',
                'w2': '10%감소_적정주가',
                'w3': '20%감소_적정주가',
                'w4': '30%감소_적정주가',
                'w5': '40%감소_적정주가',
                'w6': '50%감소_적정주가',
            }, inplace=True)

    we_srim = srim_result['we']
    we_roe = we_srim['roe']
    we_result = pd.DataFrame(we_srim['w'])
    we_result.drop(index='svalue', inplace=True)
    we_result['현재 주가'] = current_price
    we_result['ROE'] = we_roe
    we_result['구분'] = '초과이익' if we_roe>=bbb else '초과손실'
    we_result.rename(index={
        'sprice': '가중평균_ROE'
    }, columns={
        'w1': '지속_적정주가',
        'w2': '10%감소_적정주가',
        'w3': '20%감소_적정주가',
        'w4': '30%감소_적정주가',
        'w5': '40%감소_적정주가',
        'w6': '50%감소_적정주가',
    }, inplace=True)

    # SRIM 분석결과
    SRIM_analysis_results = pd.DataFrame()
    if ce_roe != None :
        SRIM_analysis_results = pd.concat([ce_result, we_result])
    else :
        SRIM_analysis_results = we_result

    return {
        '연간재무제표': annual_financial_statements,
        '분기재무제표': quarterly_financial_statements,
        '재무상태표': financial_statements,
        '재무비율': financial_ratio,
        '현금흐름표': statement_of_cash_flows,
        'PER_적정주가_계산_결과': calc_fair_value_use_per,
        'SRIM_적정주가_계산_결과': SRIM_analysis_results
    }
    


def create_post(post_info, cate_name='Little Investment') :
    ACCESS_TOKEN = '3ea02f9b4ad8cb71e53023d8195d6436_e5ec86f3a2b9d824d735bb4f4d025389'

    # 블로그 정보
    BLOG_NAME = 'waymond'

    # 글 작성에 필요한 정보
    title = post_info['post_name']
    stock_name = post_info['stock_name']
    tags = [
        stock_name, 
        f'{stock_name} 투자'
        f'{stock_name} 재무제표', 
        f'{stock_name} 재무제표 웹스크래핑', 
        f'{stock_name} 적정주가', 
        f'{stock_name} SRIM',
        f'{stock_name} 분석',
        f'AI 주식 분석',
        f'주식투자'
    ]
    tags = ', '.join(tags)

    # API 요청 URL
    url = f'https://www.tistory.com/apis/post/write'

    # 카테고리 목록 받아오기
    cate_url = "https://www.tistory.com/apis/category/list"
    params = {
        'access_token': ACCESS_TOKEN,
        'output': 'json',
        'blogName': BLOG_NAME
    }
    response = requests.get(cate_url, params=params)
    data = response.json()

    # 원하는 카테고리 찾기
    for category in data['tistory']['item']['categories']:
        if category['name'] == cate_name :
            category_id = category['id']
            break

    # 요청 파라미터
    params = {
        'access_token': ACCESS_TOKEN,
        'output': 'json',
        'blogName': BLOG_NAME,
        'title': title,
        'content': '<!-- 웹스크래핑 자료 붙여 넣기 -->',
        'tag': tags,
        'category': category_id,
        'visibility': 0  # 0: 비공개, 1: 보호, 3: 발행
    }

    # API 요청
    response = requests.post(url, params=params)

    url = response.json()['tistory']['url']
    status = response.json()['tistory']['status']
    print(f'''
Create Post
Response status : {status}''')
    return url

