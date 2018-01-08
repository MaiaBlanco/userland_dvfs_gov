data = csvread('matlab_temp_sys_identification.csv',1);
thermal_inputs = data(:,2:5);
power_inputs = data(:,8:15);
thermal_outputs = data(:,16:19);
time_data = iddata(thermal_outputs, [thermal_inputs, power_inputs], 0.2);
% therm_sys = armax(time_data, [zeros(4)])