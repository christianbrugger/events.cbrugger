
.\env\Scripts\activate ^
	&& python get_all_events.py ^
	&& python get_event_times.py ^
	&& python parse_events_from_file.py
