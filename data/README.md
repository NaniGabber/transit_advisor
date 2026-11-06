# Input Data: GTFS Archive

The system accepts transit schedules in the form of a **ZIP archive**.
Inside the archive, at the root level (no nested folders), there must be the following text files in CSV format:

- `agency.txt` — transit agency information;
- `routes.txt` — routes;
- `stops.txt` — stops;
- `trips.txt` — trips;
- `stop_times.txt` — arrival and departure times at stops.

**Requirements:**
- All files must be encoded in **UTF-8**.
- The first line of each file must contain column headers (e.g., `agency_id,agency_name`).
- The delimiter is a comma (`,`).
