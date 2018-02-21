SKIP_FACTOR = 1;
PREDICT_HORIZON = 3;
base_period = 0.2;
scaled_period = base_period*SKIP_FACTOR;
% Read train data:
data = csvread('xu3_power_thermal_train.csv',2);
thermal_inputs = data(1:SKIP_FACTOR:end,11:14);
power_big_cluster_naive_split = data(1:SKIP_FACTOR:end,16:19);
power_components = data(1:SKIP_FACTOR:end,3:6);
% Read test data:
verification_data = csvread('xu3_power_thermal_test_blackscholes.csv',2);
v_thermal_inputs = verification_data(1:SKIP_FACTOR:end,11:14);
v_power_big_cluster_naive_split = verification_data(1:SKIP_FACTOR:end,16:19);
v_power_components = verification_data(1:SKIP_FACTOR:end,3:6);
% Create train data objects for system identficiation using naive split for
% power on the big cluster:
time_data_naive_split = iddata(thermal_inputs, power_big_cluster_naive_split, 0.2*SKIP_FACTOR);
time_data_naive_split.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
time_data_naive_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
time_data_naive_split.InputUnit = {'Watts','Watts','Watts','Watts'};
time_data_naive_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
% Create train data objects for system identficiation using componentwise split for
% power on the entire board:
time_data_pwr_comps = iddata(thermal_inputs, power_components, 0.2*SKIP_FACTOR);
time_data_pwr_comps.InputName = {'watt_big', 'watt_little', 'watt_gpu', 'watt_mem'};
time_data_pwr_comps.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
time_data_pwr_comps.InputUnit = {'Watts','Watts','Watts','Watts'};
time_data_pwr_comps.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
% Create test data objects for system identficiation using naive big
% cluster power split based on usage:
v_time_data_naive_split = iddata(v_thermal_inputs, v_power_big_cluster_naive_split, 0.2*SKIP_FACTOR);
v_time_data_naive_split.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
v_time_data_naive_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
v_time_data_naive_split.InputUnit = {'Watts','Watts','Watts','Watts'};
v_time_data_naive_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
% Create test data objects for system identficiation using componentwise split for
% power on the entire board:
v_time_data_comp_split = iddata(v_thermal_inputs, v_power_components, 0.2*SKIP_FACTOR);
v_time_data_comp_split.InputName = {'watt_big', 'watt_little', 'watt_gpu', 'watt_mem'};
v_time_data_comp_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
v_time_data_comp_split.InputUnit = {'Watts','Watts','Watts','Watts'};
v_time_data_comp_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
nx=4;%1:10;
% Create state space models:
mp_naive_split = ssest(time_data_naive_split, nx, 'Ts', 0.2*SKIP_FACTOR);%, 'DisturbanceModel', 'none');
mp_comp_split = ssest(time_data_pwr_comps, nx, 'Ts', 0.2*SKIP_FACTOR);%, 'DisturbanceModel', 'none');

% Currently unused constraints on state space matrices:
% initial_system = idss(0.9 * eye(4), 0.9 * ones(4,8), eye(4), zeros(4,8) );
% initial_system.Structure.C.Free = false;
% initial_system.Structure.A.Maximum = 1;
% initial_system.Structure.A.Minimum = 0;
% initial_system.Structure.B.Minimum = 0;
% opts_sys = ssestOptions('EnforceStability',true);
% mp = ssest(time_data, initial_system, opts_sys);

% Prediction plots:
P_naive = predict(mp_naive_split, v_time_data_naive_split, PREDICT_HORIZON);
figure('Name','Naive Split Prediction');
plot(v_time_data_naive_split, P_naive);
legend('Verification data','Predicted data');
P_comp = predict(mp_comp_split, v_time_data_comp_split, PREDICT_HORIZON);
figure('Name','Component Split Prediction');
plot(v_time_data_comp_split, P_comp);
legend('Verification data','Predicted data');