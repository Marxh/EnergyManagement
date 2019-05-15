select T2.id, T2.install_date, T2.production_line, T2.brand, T2.facility_name, T2.total_energy, 
T3.anomaly_comments, T3.anomaly_date, T3.anomaly_type, T3.facility_id
from (select LineDetection_facility.id, LineDetection_facility.install_date, LineDetection_facility.production_line, 
LineDetection_facility.brand, LineDetection_facility.facility_name, ROUND(sum(T1.energy), 0) as total_energy 
from (select energy, facility_id, energy_date from LineDetection_energy 
where month(LineDetection_energy.energy_date) = 3 and day(LineDetection_energy.energy_date) = 8) as T1
left join LineDetection_facility on LineDetection_facility.id = T1.facility_id 
GROUP BY LineDetection_facility.id ) as T2
left join (select * from LineDetection_anomaly where month(LineDetection_anomaly.anomaly_date)=3 and day(LineDetection_anomaly.anomaly_date) = 8) as T3
on T3.facility_id = T2.id

/*
select T2.id, T2.install_date, T2.production_line, T2.brand, T2.facility_name, T2.total_energy, 
LineDetection_anomaly.anomaly_comments, LineDetection_anomaly.anomaly_date, LineDetection_anomaly.anomaly_type, LineDetection_anomaly.facility_id
from (select LineDetection_facility.id, LineDetection_facility.install_date, LineDetection_facility.production_line, 
LineDetection_facility.brand, LineDetection_facility.facility_name, ROUND(sum(T1.energy), 0) as total_energy 
from (select energy, facility_id, energy_date from LineDetection_energy 
where month(LineDetection_energy.energy_date) = 3 and day(LineDetection_energy.energy_date) = 8) as T1
left join LineDetection_facility on LineDetection_facility.id = T1.facility_id 
GROUP BY LineDetection_facility.id ) as T2
left join (select * from LineDetection_anomaly where month(LineDetection_anomaly.anomaly_date)=3 and day(LineDetection_anomaly.anomaly_date) = 8) as T3
on T3.facility_id = T2.id


update LineDetection_anomaly set anomaly_date = ADDDATE(anomaly_date, -62) where year(anomaly_date) = 2019
*/