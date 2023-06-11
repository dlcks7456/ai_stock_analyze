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

    return {
        'naver': nv_same_per,
        'company': cg_same_per
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
    'bbb' : get_spread()
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
    result = molecule/denominator
    result = round(result, 2)
    return result

# SRIM Calculator
def SRIM(gicode) :
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

def comma(value, rd=1) :
    if type(value) == int :
        return format(round(value, rd), ',')
    elif type(value) == float :
        return "{:,.2f}".format(value)
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

    chart_class = 'fs-y-chart' if txt == '연간' else 'fs-q-chart'

    # 올해 예상이 없는 경우 가중평균으로 계산
    for metr in [sales, profit, real_profit, interest, roe, per, pbr] :
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

    final_values = [list(metr.values()) for metr in [sales, profit, real_profit, interest, roe, per, pbr]]
    none_data_flag = []
   
    for value in final_values :
        if all(v == None for v, w in value) or len([v for v, w in value if v != None]) == 1 :
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
    profit_ratio = [round(((profit[key][0])/(value[0]))*100, 2) if all([profit[key][0] != None, value[0] != None]) else '' for key, value in sales.items()]
    # 순이익률
    real_profit_ratio = [round(((real_profit[key][0])/(value[0]))*100, 2) if all([real_profit[key][0] != None, value[0] != None]) else '' for key, value in sales.items()]

    html_fs = f'''
            <!-- {txt} -->
            <div class="fs-head">
                <div class="fs-title">{txt}</div>
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
                            <th>영업이익</th>
                            <td{' class="weight-value"' if profit['c1'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c1'][0]) and (profit['c1'][0] < 0) else ''}>{comma(profit['c1'][0])}</span></td>
                            <td{' class="weight-value"' if profit['c2'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c2'][0]) and (profit['c2'][0] < 0) else ''}>{comma(profit['c2'][0])}</span></td>
                            <td{' class="weight-value"' if profit['c3'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c3'][0]) and (profit['c3'][0] < 0) else ''}>{comma(profit['c3'][0])}</span></td>
                            <td{' class="weight-value"' if profit['c4'][1] else ''}><span{' class="bad-value"' if int_cond(profit['c4'][0]) and (profit['c4'][0] < 0) else ''}>{comma(profit['c4'][0])}</span></td>
                        </tr>
                        <tr>
                            <th>영업이익률</th>
                            <td{' class="weight-value"' if profit['c1'][1] else ''}><span{(' class="good-value"' if profit_ratio[0] >= 15 else ' class="bad-value"' if profit_ratio[0] < 5 else '') if type(profit_ratio[0]) in [float, int] else ''}>{comma(profit_ratio[0])}</span></td>
                            <td{' class="weight-value"' if profit['c2'][1] else ''}><span{(' class="good-value"' if profit_ratio[1] >= 15 else ' class="bad-value"' if profit_ratio[1] < 5 else '') if type(profit_ratio[1]) in [float, int] else ''}>{comma(profit_ratio[1])}</span></td>
                            <td{' class="weight-value"' if profit['c3'][1] else ''}><span{(' class="good-value"' if profit_ratio[2] >= 15 else ' class="bad-value"' if profit_ratio[2] < 5 else '') if type(profit_ratio[2]) in [float, int] else ''}>{comma(profit_ratio[2])}</span></td>
                            <td{' class="weight-value"' if profit['c4'][1] else ''}><span{(' class="good-value"' if profit_ratio[3] >= 15 else ' class="bad-value"' if profit_ratio[3] < 5 else '') if type(profit_ratio[3]) in [float, int] else ''}>{comma(profit_ratio[3])}</span></td>
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
                            <td{' class="weight-value"' if real_profit['c1'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[0] >= 10 else ' class="bad-value"' if real_profit_ratio[0] < 3 else '') if real_profit_ratio[0] in [float, int] else ''}>{comma(real_profit_ratio[0])}</span></td>
                            <td{' class="weight-value"' if real_profit['c2'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[1] >= 10 else ' class="bad-value"' if real_profit_ratio[1] < 3 else '') if real_profit_ratio[1] in [float, int] else ''}>{comma(real_profit_ratio[1])}</span></td>
                            <td{' class="weight-value"' if real_profit['c3'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[2] >= 10 else ' class="bad-value"' if real_profit_ratio[2] < 3 else '') if real_profit_ratio[2] in [float, int] else ''}>{comma(real_profit_ratio[2])}</span></td>
                            <td{' class="weight-value"' if real_profit['c4'][1] else ''}><span{(' class="good-value"' if real_profit_ratio[3] >= 10 else ' class="bad-value"' if real_profit_ratio[3] < 3 else '') if real_profit_ratio[3] in [float, int] else ''}>{comma(real_profit_ratio[3])}</span></td>
                        </tr>
                        <tr>
                            <th>지배주주지분</th>
                            <td{' class="weight-value"' if interest['c1'][1] else ''}>{comma(interest['c1'][0])}</td>
                            <td{' class="weight-value"' if interest['c2'][1] else ''}>{comma(interest['c2'][0])}</td>
                            <td{' class="weight-value"' if interest['c3'][1] else ''}>{comma(interest['c3'][0])}</td>
                            <td{' class="weight-value"' if interest['c4'][1] else ''}>{comma(interest['c4'][0])}</td>
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
                        {[v for v, f in sales.values()]},
                        {profit_ratio},
                        {real_profit_ratio},
                    ]);
                </script>
            </div>
            <!-- {txt} Chart END -->
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



def get_html(gicode) :
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

    bbb = web_data['bbb'] # BBB- 할인율

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
                    label: '영업이익률',
                    data: datas[1],
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    yAxisID: 'y2',
                }}, {{
                    label: '당기순이익률',
                    data: datas[2],
                    backgroundColor: 'rgba(0, 0, 128, 0.2)',
                    borderColor: 'rgba(0, 0, 128, 1)',
                    borderWidth: 1,
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
    <h1>주식종목 간단 분석:{sname}_{sdate} 기준</h1>
    <div class="a-line"></div>
    <!-- Head END -->
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
    <!-- 종목 기본 정보 END-->
    <div class="a-line"></div>
    '''

    # HTML 재무제표(연간/분기)
    html_fs_table = f'''
    {fs_table(sfsy, '연간')}
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
                        <tr>
                            <th>부채비율</th>
                            <td><span{' class="good-value"' if deacha_ratio[0] <= 100 else ' class="bad-value"' if deacha_ratio[0] >= 150 else ''}>{comma(deacha_ratio[0])}</span></td>
                            <td><span{' class="good-value"' if deacha_ratio[1] <= 100 else ' class="bad-value"' if deacha_ratio[1] >= 150 else ''}>{comma(deacha_ratio[1])}</span></td>
                            <td><span{' class="good-value"' if deacha_ratio[2] <= 100 else ' class="bad-value"' if deacha_ratio[2] >= 150 else ''}>{comma(deacha_ratio[2])}</span></td>
                            <td><span{' class="good-value"' if deacha_ratio[3] <= 100 else ' class="bad-value"' if deacha_ratio[3] >= 150 else ''}>{comma(deacha_ratio[3])}</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <!-- 재무상태표 END -->
            <!-- 재무상태표 Chart -->
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
            <!-- 재무상태표 Chart END -->'''

    # HTML 재무비율
    rate_head = [date for date, value in list(srate.values())[0]]
    rate_value = {key:[val[1] for val in value] for key, value in srate.items()}

    html_fs_ratio = f'''
            <!-- 재무비율 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title">재무비율</div>
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
                            <td><span{' class="good-value"' if rate_value['유동비율'][0] >= 200 else ' class="bad-value"' if rate_value['유동비율'][0] < 100 else ''}>{comma(rate_value['유동비율'][0])}</span></td>
                            <td><span{' class="good-value"' if rate_value['유동비율'][1] >= 200 else ' class="bad-value"' if rate_value['유동비율'][1] < 100 else ''}>{comma(rate_value['유동비율'][1])}</span></td>
                            <td><span{' class="good-value"' if rate_value['유동비율'][2] >= 200 else ' class="bad-value"' if rate_value['유동비율'][2] < 100 else ''}>{comma(rate_value['유동비율'][2])}</span></td>
                            <td><span{' class="good-value"' if rate_value['유동비율'][3] >= 200 else ' class="bad-value"' if rate_value['유동비율'][3] < 100 else ''}>{comma(rate_value['유동비율'][3])}</span></td>
                        </tr>
                        <tr>
                            <th>당좌비율</th>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][0] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][0] < 100 else ''}>{comma(rate_value['당좌비율'][0])}</span></td>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][1] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][1] < 100 else ''}>{comma(rate_value['당좌비율'][1])}</span></td>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][2] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][2] < 100 else ''}>{comma(rate_value['당좌비율'][2])}</span></td>
                            <td><span{' class="good-value"' if rate_value['당좌비율'][3] >= 150 else ' class="bad-value"' if rate_value['당좌비율'][3] < 100 else ''}>{comma(rate_value['당좌비율'][3])}</span></td>
                        </tr>
                        <tr>
                            <th>부채비율</th>
                            <td><span{' class="good-value"' if rate_value['부채비율'][0] < 150 else ' class="bad-value"' if rate_value['부채비율'][0] >= 200 else ''}>{comma(rate_value['부채비율'][0])}</span></td>
                            <td><span{' class="good-value"' if rate_value['부채비율'][1] < 150 else ' class="bad-value"' if rate_value['부채비율'][1] >= 200 else ''}>{comma(rate_value['부채비율'][1])}</span></td>
                            <td><span{' class="good-value"' if rate_value['부채비율'][2] < 150 else ' class="bad-value"' if rate_value['부채비율'][2] >= 200 else ''}>{comma(rate_value['부채비율'][2])}</span></td>
                            <td><span{' class="good-value"' if rate_value['부채비율'][3] < 150 else ' class="bad-value"' if rate_value['부채비율'][3] >= 200 else ''}>{comma(rate_value['부채비율'][3])}</span></td>
                        </tr>
                        <tr>
                            <th>유보율</th>
                            <td>{comma(rate_value['유보율'][0])}</td>
                            <td>{comma(rate_value['유보율'][1])}</td>
                            <td>{comma(rate_value['유보율'][2])}</td>
                            <td>{comma(rate_value['유보율'][3])}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="fs-comment-text">유보율은 높을수록 좋다.</div>
            <!-- 재무비율 END -->'''
    
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
        '+/+/-' : '과도기',
        '-/-/-' : '재활',
        '-/-/+' : '재활',
        '-/+/-' : '<span class="bad-value">위험</span>',
        '-/+/+' : '<span class="bad-value">접근금지</span>',
    }


    html_cash = f'''
            <!-- 현금흐름표 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title">현금흐름표</div>
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
            <!-- 현금흐름표 END -->
            <div class="a-line"></div>'''

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
            <div class="report-title">적정주가 계산</div>
            <!-- 영업이익*PER 적정 주가 계산 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title">영업이익*PER</div>
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
    cg_per = same_pers['company']

    # 발행 주식수
    sc = scommon

    html_per = f'''
            <!-- 적정주가 계산 파트 -->
            <div class="report-title">적정주가 계산</div>
            <!-- 영업이익*PER 적정 주가 계산 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title">영업이익*PER</div>
            </div>
            <div class="standard-info">
                <div class="info">
                    <div class="info-cell">
                        <div class="cell-head">영업이익</div>
                        <div class="cell-desc{' weight-value' if yp_flag else ''}">{comma(yprofit)}억원</div>
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
                            <td>{comma(yper)}</td>
                            <td>{comma(cp_value(yprofit, yper, sc)['value'])}{'억원' if cp_value(yprofit, yper, sc)['value'] != '' else ''}</td>
                            <td>{comma(cp_value(yprofit, yper, sc)['price'])}{'원' if cp_value(yprofit, yper, sc)['price'] != '' else ''}</td>
                        </tr>
                        <tr>
                            <th>가중 평균</th>
                            <td>{comma(ywper)}</td>
                            <td>{comma(cp_value(yprofit, ywper, sc)['value'])}억원</td>
                            <td>{comma(cp_value(yprofit, ywper, sc)['price'])}원</td>
                        </tr>
                        <tr>
                            <th>업종 PER(NV)</th>
                            <td>{comma(nv_per)}</td>
                            <td>{comma(cp_value(yprofit, nv_per, sc)['value'])}억원</td>
                            <td>{comma(cp_value(yprofit, nv_per, sc)['price'])}원</td>
                        </tr>
                        <tr>
                            <th>업종 PER(CG)</th>
                            <td>{comma(cg_per)}</td>
                            <td>{comma(cp_value(yprofit, cg_per, sc)['value'])}억원</td>
                            <td>{comma(cp_value(yprofit, cg_per, sc)['price'])}원</td>
                        </tr>
                        <tr>
                            <th>별도 조정</th>
                            <td>
                                <input class="custom-input per-input" value="10" type="number" min="0" max="100" step="1" />
                            </td>
                            <td><span class="custom-value per-fair-value"></span></td>
                            <td><span class="custom-value per-fair-price"></span></td>
                        </tr>
                    </tbody>
                </table>
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
                                data: [{'null' if cp_value(yprofit, yper, sc)['price'] == '' else cp_value(yprofit, yper, sc)['price']}, {cp_value(yprofit, ywper, sc)['price']}, {cp_value(yprofit, nv_per, sc)['price']}, {cp_value(yprofit, cg_per, sc)['price']}, calcPer],
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
                                            content: ['현재 주가', `${{nowValue.toLocaleString()}}원`],
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
            <!-- 영업이익*PER Chart END -->'''

    # HTML SRIM
    srim = SRIM(gicode)

    # 지배주주지분
    srim_jibun = srim['지배주주지분']
    srim_result = srim['srim']
    # 예상 ROE
    e_roe = srim_result['ce']['roe'] if 'ce' in srim_result else None
    e_value = srim_result['ce']['w'] if 'ce' in srim_result else None
    e_price = [val['sprice'] for val in e_value.values()] if e_value != None else None

    # 가중 ROE
    w_roe = srim_result['we']['roe']
    w_value = srim_result['we']['w']
    w_price = [val['sprice'] for val in w_value.values()] if w_value != None else None

    html_srim = f'''
            <!-- SRIM 계산 -->
            <div class="fs-head" style="margin-top: 20px">
                <div class="fs-title">SRIM</div>
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

                <div class="info" style="margin-top: 15px;">
                    <div class="info-cell">
                        <div class="cell-head">지배주주지분</div>
                        <div class="cell-desc">{comma(srim_jibun)}</div>
                    </div>

                    <div class="info-cell">
                        <div class="cell-head">BBB-</div>
                        <div class="cell-desc">{bbb}%</div>
                    </div>
                    <div class="info-one">
                        <div class="cell-head">예상 ROE</div>
                        <div class="cell-desc">{comma(e_roe) if e_roe != None else ''}</div>
                    </div>
                    <div class="info-one">
                        <div class="cell-head">가중 ROE</div>
                        <div class="cell-desc">{comma(w_roe)}</div>
                    </div>
                </div>
            </div>
            <div class="srim-page">
                <div class="srim-roe-head">
                    <div class="srim-roe {'roe-selected' if e_roe != None else 'fs-hidden'}">예상 ROE</div>
                    <div class="srim-roe {'roe-selected' if e_roe == None else ''}">가중 ROE</div>
                    <div class="srim-roe-info">기준 ROE 선택</div>
                </div>
                <div class="fs-div srim-result" style="margin-top: 10px">
                    <table class="fs-data srim-table{' post-fs-hidden' if e_value == None else ''}">
                        <thead>
                            <th>초과이익</th>
                            <th>기업가치</th>
                            <th>적정주가</th>
                        </thead>
                        <tbody>
                            <tr>
                                <th>이익 지속</th>
                                <td>{'%s억'%(comma(e_value['w1']['svalue'])) if e_roe != None else ''}</td>
                                <td>{'%s원'%(comma(e_value['w1']['sprice'])) if e_roe != None else ''}</td>
                            </tr>
                            <tr>
                                <th>10% 감소</th>
                                <td>{'%s억'%(comma(e_value['w2']['svalue'])) if e_roe != None else ''}</td>
                                <td>{'%s원'%(comma(e_value['w2']['sprice'])) if e_roe != None else ''}</td>
                            </tr>
                            <tr>
                                <th>20% 감소</th>
                                <td>{'%s억'%(comma(e_value['w3']['svalue'])) if e_roe != None else ''}</td>
                                <td>{'%s원'%(comma(e_value['w3']['sprice'])) if e_roe != None else ''}</td>
                            </tr>
                            <tr>
                                <th>30% 감소</th>
                                <td>{'%s억'%(comma(e_value['w4']['svalue'])) if e_roe != None else ''}</td>
                                <td>{'%s원'%(comma(e_value['w4']['sprice'])) if e_roe != None else ''}</td>
                            </tr>
                            <tr>
                                <th>40% 감소</th>
                                <td>{'%s억'%(comma(e_value['w5']['svalue'])) if e_roe != None else ''}</td>
                                <td>{'%s원'%(comma(e_value['w5']['sprice'])) if e_roe != None else ''}</td>
                            </tr>
                            <tr>
                                <th>50% 감소</th>
                                <td>{'%s억'%(comma(e_value['w6']['svalue'])) if e_roe != None else ''}</td>
                                <td>{'%s원'%(comma(e_value['w6']['sprice'])) if e_roe != None else ''}</td>
                            </tr>
                        </tbody>
                    </table>

                    <table class="fs-data srim-table{' post-fs-hidden' if e_value != None else ''}">
                        <thead>
                            <th>초과이익</th>
                            <th>기업가치</th>
                            <th>적정주가</th>
                        </thead>
                        <tbody>
                            <tr>
                                <th>이익 지속</th>
                                <td>{'%s억'%(comma(w_value['w1']['svalue']))}</td>
                                <td>{'%s원'%(comma(w_value['w1']['sprice']))}</td>
                            </tr>
                            <tr>
                                <th>10% 감소</th>
                                <td>{'%s억'%(comma(w_value['w2']['svalue']))}</td>
                                <td>{'%s원'%(comma(w_value['w2']['sprice']))}</td>
                            </tr>
                            <tr>
                                <th>20% 감소</th>
                                <td>{'%s억'%(comma(w_value['w3']['svalue']))}</td>
                                <td>{'%s원'%(comma(w_value['w3']['sprice']))}</td>
                            </tr>
                            <tr>
                                <th>30% 감소</th>
                                <td>{'%s억'%(comma(w_value['w4']['svalue']))}</td>
                                <td>{'%s원'%(comma(w_value['w4']['sprice']))}</td>
                            </tr>
                            <tr>
                                <th>40% 감소</th>
                                <td>{'%s억'%(comma(w_value['w5']['svalue']))}</td>
                                <td>{'%s원'%(comma(w_value['w5']['sprice']))}</td>
                            </tr>
                            <tr>
                                <th>50% 감소</th>
                                <td>{'%s억'%(comma(w_value['w6']['svalue']))}</td>
                                <td>{'%s원'%(comma(w_value['w6']['sprice']))}</td>
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
            const srimResults = [
                {e_price if e_price != None else []},
                {w_price if w_price != None else []}
            ];
            const srimNowValue = {current_price};
            let setSRIM = srimResults[{0 if e_value != None else 1}];
            const srimChart = new Chart(srimCanvas, {{
                type: 'line',
                data: {{
                    labels: ['이익 지속', '10% 감소', '20% 감소', '30% 감소', '40% 감소', '50% 감소'],
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
                                    content: ['현재 주가', `${{srimNowValue.toLocaleString()}}원`],
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
        </script>
        <!-- SRIM Chart END -->
        <div class="a-line"></div>'''
    # HTML Body (END)
    html_fs_body = f'''
    {html_head}
    {html_info}
    <div class="report-title">재무정보</div>
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
    <!-- END -->
    '''
    file_date = sdate.split(' ')[0]
    file_date = file_date.replace('/', '')
    with open(f'{gicode}_{sname}_{file_date}.html', 'w') as f :
        f.write(html_fs_body)