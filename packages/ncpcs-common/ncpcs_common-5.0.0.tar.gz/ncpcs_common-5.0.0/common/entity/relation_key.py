from dataclasses import dataclass

from common.util.date_util import convert_standard_timestamp_to_compact


@dataclass
class RelationKey:
    medical_institution_code: str
    medical_record_no: str
    discharge_time: str
    admission_time: str

    def __repr__(self):
        return self.medical_institution_code + '|' + self.medical_record_no + '|' + convert_standard_timestamp_to_compact(self.discharge_time)

    def __eq__(self, other):
        return self.medical_institution_code == other.medical_institution_code and self.medical_record_no \
               == other.medical_record_no and self.discharge_time == other.discharge_time

    def __hash__(self):
        return hash((self.medical_institution_code, self.medical_record_no, self.discharge_time))