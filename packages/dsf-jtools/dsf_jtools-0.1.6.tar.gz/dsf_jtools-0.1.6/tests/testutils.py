import sys
sys.path.append('F:/projects/jtools')

from jtools.utils import *

td = datetime.today().strftime("%Y%m%d")

assert len(get_trading_dates('SH', '20240101', '20250821')) == 397

trddts1 = ['20250102', '20250103', '20250106', '20250107', '20250108', '20250109', '20250110', '20250113', '20250114', '20250115', '20250116', '20250117', '20250120', '20250121', '20250122', '20250123', '20250124', '20250127']
assert trddts1 == get_trading_dates('SH', '20250101', '20250131')
assert trddts1 == get_trading_dates('DF', '20250101', '20250131')

trddts2 = ['20250428', '20250429', '20250430', '20250506', '20250507', '20250508', '20250509', '20250512', '20250513', '20250514', '20250515', '20250516']
assert trddts2 == get_trading_dates('SH', trddts2[0], trddts2[-1])
assert trddts2 == get_trading_dates('SH', '20250426', '20250518')
assert trddts2 == get_trading_dates('DF', '20250428', '20250518')

trddts3 = ['20240910', '20240911', '20240912', '20240913', '20240918', '20240919', '20240920', '20240923', '20240924', '20240925', '20240926', '20240927', '20240930', '20241008', '20241009', '20241010', '20241011', '20241014', '20241015', '20241016', '20241017', '20241018', '20241021', '20241022', '20241023', '20241024', '20241025']
assert trddts3 == get_trading_dates('SH', trddts3[0], trddts3[-1])
assert trddts3 == get_trading_dates('DF', trddts3[0], trddts3[-1])
assert trddts3 == get_trading_dates('DF', trddts3[0], '20241026')

print(len(get_trading_dates('SH', '20050223', td)))

# 一般交易日跑测试
lasttrddt = get_last_trddt()
assert lasttrddt == datetime.today().strftime("%Y%m%d")  # '20250825'
latesttrddt = get_latest_trddt()
assert lasttrddt == datetime.today().strftime("%Y%m%d")  # '20250825'

# is_trading_date
assert is_trading_date(td)
assert is_trading_date('20250825')
assert is_trading_date('20041231')
assert is_trading_date('20241231')
assert not is_trading_date('20250824')
assert is_trading_date(1747929600000)
assert is_trading_date(datetime(2025, 8, 22))
assert is_trading_date(1755792000000)
assert is_trading_date(1755792000)
