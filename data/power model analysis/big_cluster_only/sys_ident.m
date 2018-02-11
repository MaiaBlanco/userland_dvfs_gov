SKIP_FACTOR = 2;    % Based on characteristic time of system
PREDICT_HORIZON = 3;
data = csvread('matlab_temp_sys_identification_big_only.csv',1);
verification_data = csvread('matlab_temp_sys_identification_verification_blackscholes_big_only.csv',1);
v_thermal_inputs = verification_data(1:SKIP_FACTOR:end,2:5);
v_power_inputs = verification_data(1:SKIP_FACTOR:end,10:13);
thermal_inputs = data(1:SKIP_FACTOR:end,2:5);
power_inputs = data(1:SKIP_FACTOR:end,7:10);
time_data = iddata(thermal_inputs, power_inputs, 0.2*SKIP_FACTOR);
time_data.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
time_data.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
time_data.InputUnit = {'Watts','Watts','Watts','Watts'};
time_data.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
v_time_data = iddata(v_thermal_inputs, v_power_inputs, 0.2*SKIP_FACTOR);
v_time_data.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
v_time_data.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
v_time_data.InputUnit = {'Watts','Watts','Watts','Watts'};
v_time_data.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
nx=4;%1:10;

mp = ssest(time_data, nx, 'Ts', 0.2*SKIP_FACTOR);%, 'DisturbanceModel', 'none');

% initial_system = idss(0.9 * eye(4), 0.9 * ones(4,8), eye(4), zeros(4,8) );
% initial_system.Structure.C.Free = false;
% initial_system.Structure.A.Maximum = 1;
% initial_system.Structure.A.Minimum = 0;
% initial_system.Structure.B.Minimum = 0;
% opts_sys = ssestOptions('EnforceStability',true);
% mp = ssest(time_data, initial_system, opts_sys);

figure();
compare(v_time_data, mp);
P = predict(mp, v_time_data, PREDICT_HORIZON);
figure();
plot(v_time_data, P);
legend('Estimation data','Predicted data');

A_s = mp.C*(mp.A*0.2+eye(4))*mp.C^(-1);
A_s = A_s / norm(A_s, inf);
B_s = mp.C * mp.B * 0.2;

tp = zeros(size(v_thermal_inputs));
for i = 1:size(v_thermal_inputs, 1)
    tp(i, :) = A_s * v_thermal_inputs(i, :)' + B_s * v_power_inputs(i, :)'; 
end

predicted_validation = iddata(tp, v_power_inputs, 0.2*SKIP_FACTOR);
predicted_validation.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
predicted_validation.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
predicted_validation.InputUnit = {'Watts','Watts','Watts','Watts'};
predicted_validation.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
figure();
plot(v_time_data, predicted_validation);
legend('True data','Predicted data');

