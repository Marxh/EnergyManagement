select LineDetection_energy.id, round(LineDetection_energy.energy,1) as energy, LineDetection_energy.energy_date, LineDetection_facility.facility_name
from LineDetection_energy, LineDetection_facility where LineDetection_energy.facility_id = LineDetection_facility.id and LineDetection_energy.facility_id = ### ORDER BY -LineDetection_energy.energy_date