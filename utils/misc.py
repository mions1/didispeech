def time_2_ms(start: str="00:00:00", end: str="00:00:00") -> [int,int]:
	""" It converts start and end from "hh:mm:ss" in ms
	"""
	h_start = start[0:2]
	m_start = start[3:5]
	s_start = start[6:]

	h_end = end[0:2]
	m_end = end[3:5]
	s_end = end[6:]

	s = int(h_start)*(60*60*1000) + int(m_start)*(60*1000) + int(s_start)*(1000)
	e = int(h_end)*(60*60*1000) + int(m_end)*(60*1000) + int(s_end)*(1000)

	return s, e

def ms_2_time(ms: int) -> str:
	""" It converts milliseconds to time in format:
	    "hh:mm:ss"

	Args:
		ms (int): time in ms

	Returns:
		str: time in str hh:mm:ss
	"""

	ss = int(ms/1000)%60
	if ss < 10:
		ss = "0"+str(ss)
	mm = int((ms/(60*1000)) % 60)
	if mm < 10:
		mm = "0"+str(mm)
	hh = int(ms/(60*60*1000)%24)
	if hh < 10:
		hh = "0"+str(hh)

	return str(hh)+":"+str(mm)+":"+str(ss)

def s_2_time(s: float) -> str:
	""" It converts seconds to time in format:
	    "hh:mm:ss"

	Args:
		s (int): time in s

	Returns:
		str: time in str hh:mm:ss
	"""
	ms = int(s*1000)

	return ms_2_time(ms)