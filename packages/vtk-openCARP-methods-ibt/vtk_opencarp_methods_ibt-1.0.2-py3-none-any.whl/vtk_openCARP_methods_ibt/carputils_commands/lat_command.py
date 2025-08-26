import re
from .abstract_command import BaseCommand

class LATCommand(BaseCommand):
    def __init__(self, threshold, id_name="ACTs", positional_index=0, all_flag=0, measurand=0, mode=0):
        self.positional_index = positional_index
        self.id_name = id_name
        self.all = all_flag
        self.measurand = measurand
        self.mode = mode
        self.threshold = threshold

    def to_cmd(self):
        """Convert LAT object to list format."""
        return [
            '-num_LATs', 1,
            f'-lats[{self.positional_index}].ID', self.id_name,
            f'-lats[{self.positional_index}].all', self.all,
            f'-lats[{self.positional_index}].measurand', self.measurand,
            f'-lats[{self.positional_index}].mode', self.mode,
            f'-lats[{self.positional_index}].threshold', self.threshold
        ]

    @classmethod
    def create_from_cmd_list(cls, lat_list):
        """Create LAT object from list format."""
        lat_dict = {}
        for i in range(0, len(lat_list), 2):
            key = lat_list[i]
            value = lat_list[i + 1]
            match = re.search(r'\[(\d+)\]', key)
            if '.ID' in key:
                lat_dict['id_name'] = value
            elif '.all' in key:
                lat_dict['all_flag'] = value
            elif '.measurand' in key:
                lat_dict['measurand'] = value
            elif '.mode' in key:
                lat_dict['mode'] = value
            elif '.threshold' in key:
                lat_dict['threshold'] = value
            if match:
                lat_dict['positional_index'] = int(match.group(1))

        return cls(**lat_dict)

    def __str__(self):
        """String representation of LAT object."""
        return (f"LAT(id='{self.id_name}', all={self.all}, "
                f"measurand={self.measurand}, mode={self.mode}, "
                f"threshold={self.threshold})")
