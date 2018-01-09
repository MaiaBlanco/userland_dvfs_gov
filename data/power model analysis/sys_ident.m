data = csvread('matlab_temp_sys_identification.csv',1);
verification_data = csvread('matlab_temp_sys_identification_verification_blackscholes.csv',1);
v_thermal_inputs = verification_data(:,2:5);
v_power_inputs = verification_data(:,10:17);
thermal_inputs = data(:,2:5);
power_inputs = data(:,8:15);
time_data = iddata(thermal_inputs, power_inputs, 0.2);
time_data.InputName = {'watt0', 'watt1', 'watt2', 'watt3', 'watt4', 'watt5', 'watt6', 'watt7'};
time_data.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
time_data.InputUnit = {'Watts','Watts','Watts','Watts','Watts','Watts','Watts','Watts'};
time_data.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
v_time_data = iddata(v_thermal_inputs, v_power_inputs, 0.2);
v_time_data.InputName = {'watt0', 'watt1', 'watt2', 'watt3', 'watt4', 'watt5', 'watt6', 'watt7'};
v_time_data.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
v_time_data.InputUnit = {'Watts','Watts','Watts','Watts','Watts','Watts','Watts','Watts'};
v_time_data.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
nx=4;%1:10;

mp = ssest(time_data, nx, 'Ts', 0.2);%, 'DisturbanceModel', 'none');

% initial_system = idss(0.9 * eye(4), 0.9 * ones(4,8), eye(4), zeros(4,8) );
% initial_system.Structure.C.Free = false;
% initial_system.Structure.A.Maximum = 1;
% initial_system.Structure.A.Minimum = 0;
% initial_system.Structure.B.Minimum = 0;
% opts_sys = ssestOptions('EnforceStability',true);
% mp = ssest(time_data, initial_system, opts_sys);

A_s = mp.C*(mp.A*0.2+eye(4))*mp.C^(-1);
A_s = A_s / norm(A_s, inf);
B_s = mp.C * mp.B * 0.2;

tp = zeros(size(v_thermal_inputs));
for i = 1:size(v_thermal_inputs, 1)
    tp(i, :) = A_s * v_thermal_inputs(i, :)' + B_s * v_power_inputs(i, :)'; 
end
