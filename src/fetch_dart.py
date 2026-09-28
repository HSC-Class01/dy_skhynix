"""Build an SK hynix financial time series from Open DART.

Uses consolidated statements when disclosed.  It asks for every annual, half-year,
and first/third-quarter report for 2010 onward.  Rows unavailable in Open DART's
structured-account endpoint are logged rather than fabricated.
"""
from __future__ import annotations
import argparse, json, os, re, time
from pathlib import Path
from datetime import date
import pandas as pd
import requests
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'data'
CORP_CODE='00164779'  # SK hynix Inc.
ENDPOINT='https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
# Open DART report codes: annual, half-year, Q1, Q3 respectively.
REPORTS={'annual':'11011','half_year':'11012','quarterly_q1':'11013','quarterly_q3':'11014'}
ACCOUNTS={
 'revenue':[r'^매출액$',r'^수익\(매출액\)$',r'^수익$'],
 'gross_profit':[r'^매출총이익$'],
 'operating_profit':[r'^영업이익$',r'^영업이익\(손실\)$'],
 'net_income':[r'^당기순이익$',r'^당기순이익\(손실\)$'],
 'total_assets':[r'^자산총계$'], 'current_assets':[r'^유동자산$'],
 'cash':[r'^현금및현금성자산$'], 'inventory':[r'^재고자산$'],
 'total_liabilities':[r'^부채총계$'], 'current_liabilities':[r'^유동부채$'],
 'total_equity':[r'^자본총계$'],
 'cfo':[r'^영업활동으로 인한 현금흐름$'],
 'capex':[r'^유형자산의 취득$',r'^유형자산 취득$',r'^무형자산의 취득$',r'^무형자산 취득$'],
}
def num(v):
    s=str(v or '').replace(',','').strip()
    return None if s in ('','-','nan') else float(s.replace('(','-').replace(')',''))
def find(rows, pats, summ=False):
    vs=[num(r.get('thstrm_amount')) for r in rows if any(re.search(p,r.get('account_nm','')) for p in pats)]
    vs=[v for v in vs if v is not None]
    return (sum(vs) if summ else vs[0]) if vs else None
def fetch(key,year,kind,code):
    p={'crtfc_key':key,'corp_code':CORP_CODE,'bsns_year':year,'reprt_code':code,'fs_div':'CFS'}
    r=requests.get(ENDPOINT,params=p,timeout=45); r.raise_for_status(); j=r.json()
    if j.get('status')!='000': return None,j.get('message','unknown DART error')
    row={'year':year,'category':kind,'report_code':code,'source':'Open DART / consolidated (CFS)'}
    for name,pats in ACCOUNTS.items(): row[name]=find(j['list'],pats,name=='capex')
    if row['capex'] is not None: row['capex']=abs(row['capex'])
    return row,None
def ratios(df):
    d=df.copy()
    for c in ['revenue','gross_profit','operating_profit','net_income','cfo','capex','total_assets','current_assets','cash','inventory','total_liabilities','current_liabilities','total_equity']:
        if c not in d: d[c]=None
    d['gross_margin_pct']=d.gross_profit/d.revenue*100
    d['operating_margin_pct']=d.operating_profit/d.revenue*100
    d['net_margin_pct']=d.net_income/d.revenue*100
    d['current_ratio_pct']=d.current_assets/d.current_liabilities*100
    d['debt_to_equity_pct']=d.total_liabilities/d.total_equity*100
    d['equity_ratio_pct']=d.total_equity/d.total_assets*100
    d['fcf']=d.cfo-d.capex
    # Only annual statements are appropriate for annual growth/return metrics.
    annual=d[d.category=='annual'].sort_values('year').copy()
    annual['revenue_growth_pct']=annual.revenue.pct_change()*100
    annual['avg_assets']=(annual.total_assets+annual.total_assets.shift())/2
    annual['avg_equity']=(annual.total_equity+annual.total_equity.shift())/2
    annual['roa_pct']=annual.net_income/annual.avg_assets*100
    annual['roe_pct']=annual.net_income/annual.avg_equity*100
    d=d.merge(annual[['year','revenue_growth_pct','roa_pct','roe_pct']],on='year',how='left')
    return d
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--start-year',type=int,default=2010); ap.add_argument('--end-year',type=int,default=date.today().year)
    a=ap.parse_args(); load_dotenv(ROOT/'.env'); key=os.getenv('DART_API_KEY')
    if not key or key.startswith('PASTE_'): raise SystemExit('Set DART_API_KEY in environment or .env first.')
    rows=[]; unavailable=[]
    for y in range(a.start_year,a.end_year+1):
      for kind,code in REPORTS.items():
        try:
          row,err=fetch(key,y,kind,code)
          if row: rows.append(row)
          else: unavailable.append({'year':y,'category':kind,'reason':err})
        except Exception as e: unavailable.append({'year':y,'category':kind,'reason':str(e)})
        time.sleep(.15)
    OUT.mkdir(parents=True,exist_ok=True)
    d=ratios(pd.DataFrame(rows)) if rows else pd.DataFrame()
    d.to_json(OUT/'financials.json',orient='records',force_ascii=False,indent=2)
    d.to_csv(OUT/'financials.csv',index=False,encoding='utf-8-sig')
    (OUT/'unavailable_reports.json').write_text(json.dumps(unavailable,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Published {len(d)} report rows; logged {len(unavailable)} unavailable rows.')
if __name__=='__main__': main()
