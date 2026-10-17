import datetime as dt


class Scheduler:
    """Weekly schedule: entries are (weekday 0=Mon, 'HH:MM')."""

    def __init__(self):
        self.entries = set()
        self._last_fired = None

    def add(self, weekday, hhmm):
        self.entries.add((weekday, hhmm))

    def remove(self, weekday, hhmm):
        self.entries.discard((weekday, hhmm))

    def due(self, now: dt.datetime):
        key = (now.weekday(), now.strftime("%H:%M"))
        if key in self.entries and self._last_fired != (now.date(), key[1]):
            self._last_fired = (now.date(), key[1])
            return True
        return False

    def as_list(self):
        return sorted(self.entries)
