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
    years = ['y3', 'y2', 'y1', 'ce']

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
        
    # 각 value를 ['q1', 'q2', 'q3', 'q4']와 매칭
    qts = ['q1', 'q2', 'q3', 'q4']

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

    result['qts_chk'] = dict(zip(qts, qts_text))

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
                tds =[t.get_text(strip=True) for t in t.find_all('td')[1:]]
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


# 현재가 추출 (NAVER 금융) + 업종 PER
def get_current_info(gicode) :
    url = f'https://finance.naver.com/item/main.naver?code={str(gicode)}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rate_info = soup.find('div', {'class': 'rate_info'})
    no_today = rate_info.find('p', {'class': 'no_today'}).text.strip()
    no_today = no_today.split('\n')[0]

    now = datetime.now()
    formatted_date = now.strftime("%Y/%m/%d %H:%M")

    return {
        'current_price': no_today,
        'base_date': formatted_date
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
    'bbb' : get_spread()
  }




##############################

# SRIM Calculator
def SRIM(gicode) :
    stock = get_stock_items(gicode)

    # 연결재무제표(연간)
    cfs = stock['year']

    # 작년말 지배주주지분 ✅
    interest = cfs['지배주주지분']['y1']

    # ROE ✅
    roe = None
    ce_roe = cfs['ROE']['ce'] 

    # 예상 ROE가 없는 경우 추정 ROE로 계산 ✅
    use_roe = '예상 ROE'

    if ce_roe == None :
        # 추정 ROE : 가중 평균
        y3 = cfs['ROE']['y3']*1
        y2 = cfs['ROE']['y2']*2
        y1 = cfs['ROE']['y1']*3

        sum_y = y3 + y2 + y1
        roe = float(sum_y/6)

        use_roe = '가중 평균 ROE'
    else :
        # 예상 ROE
        roe = float(ce_roe)

    # BBB- 할인율 ✅
    bbb = float(stock['bbb'])

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

    ## TEST ##
    # roe = float(15.16)
    # bbb = float(7.92)
    # interest = 48809
    # numerator = interest*(roe - bbb)
    # b0 = b0 = interest + (numerator/bbb)
    # stock_cnt = 15054186 - 357302
    # fair_value = (b0*100000000)/stock_cnt
    # excess_profit = interest*((roe/100) - (bbb/100))
    #####

    ws = {
        'w1' : 1,
        'w2' : float(0.9),
        'w3' : float(0.8)
    }

    # SRIM 최종 결과 ✅
    final_values = {}

    # w1 = 2차 매도가(적정주가)
    # w2 = 1차 매도가
    # w3 = 적정매수가

    for key, w in ws.items() :
        denominator = (1+float(bbb/100))-w
        w_calc = w/denominator
        m_calc = interest + (excess_profit*w_calc)
        profit = (m_calc/stock_cnt)*100000000
        final_values[key] = profit

    # 투자 여부
    w1 = final_values['w1']
    w2 = final_values['w2']
    w3 = final_values['w3']

    # % 비율
    w3_w1 = (w1 - w3)
    w3_w1 = round((w3_w1/w3)*100, 2)

    w3_w2 = (w2 - w3)
    w3_w2 = round((w3_w2/w3)*100, 2)

    flag = True
    if w1 <= w3 :
        flag = False
    
    if fair_value < 0 :
        flag = False

    return {
        '지배주주지분': interest,
        '유통주식수': f'{format(stock_cnt, ",")}주',
        'ROE': round(roe, 2),
        '기준ROE': use_roe,
        '할인율': round(bbb, 2),
        '기업가치': f'{round(b0)}억원',
        '적정주가': f'{format(round(fair_value), ",")}원',
        '이익_지속': round(w1),
        '10%_감소': round(w2),
        '20%_감소': round(w3),
        'flag': flag,
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

