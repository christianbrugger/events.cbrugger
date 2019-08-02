
.\env\Scripts\activate && python get_all_events.py || exit /b

.\env\Scripts\activate && python get_event_times.py || exit /b

.\env\Scripts\activate && python parse_events_from_file.py || exit /b
