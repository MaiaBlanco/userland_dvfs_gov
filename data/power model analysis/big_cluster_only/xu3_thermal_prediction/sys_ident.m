%% Parameteric Knobs...
SKIP_FACTOR = 1;
PREDICT_HORIZON = 1;
base_period = 0.2;
scaled_period = base_period*SKIP_FACTOR;
AVG_WINDOW = 3;
% From Ganapati Bhat (working at Arizona State University in Umit Ogras' team):
A_init =[0.9935    0.0015    0.0022    0.0014 0.0007;
    0.0070    0.9913    0.0001    0.0008 0;
    0.0017    0.0022    0.9911    0.0019 0.0030;
    0.0074         0         0    0.9904 0.0003
    0.0020    0.0019    0.0022    0.0015 0.9896];

B_init = [0.1229    0.0196         0    0.0472
    0.0659    0.0512         0    0.0079
    0.0611    0.0377    0.1448         0
    0.0708    0.0489         0    0.0226
    0.1299    0.0273         0    0.0519 ];

%% Read train data
data = csvread('xu3_power_thermal_train.csv',2);
thermal_inputs = data(1:end,11:15);
thermal_inputs = movmean(thermal_inputs, [AVG_WINDOW 0], 1);
thermal_inputs = thermal_inputs(1:SKIP_FACTOR:end, :);
thermal_inputs_next = [thermal_inputs(2:end,:); thermal_inputs(end, :)];
power_big_cluster_naive_split = data(1:end,16:19);
power_big_cluster_naive_split = movmean(power_big_cluster_naive_split, [AVG_WINDOW 0],1);
power_big_cluster_naive_split = power_big_cluster_naive_split(1:SKIP_FACTOR:end,:);
power_components = data(1:end,3:6);
power_components = movmean(power_components, [AVG_WINDOW 0],1);
power_components = power_components(1:SKIP_FACTOR:end,:);

%% Read test data:
verification_data = csvread('xu3_power_thermal_test_blackscholes.csv',2);
v_thermal_inputs = verification_data(1:end,11:15);
v_thermal_inputs = movmean(v_thermal_inputs, [AVG_WINDOW 0], 1);
v_thermal_inputs = v_thermal_inputs(1:SKIP_FACTOR:end, :);
v_thermal_inputs_next = [v_thermal_inputs(2:end,:); v_thermal_inputs(end, :)];
v_power_big_cluster_naive_split = movmean(verification_data(1:SKIP_FACTOR:end,16:19), [AVG_WINDOW 0],1);
v_power_components = movmean(verification_data(1:SKIP_FACTOR:end,3:6), [AVG_WINDOW 0], 1);
% Create train data objects for system identficiation using naive split for
% power on the big cluster:
% time_data_naive_split = iddata(thermal_inputs, power_big_cluster_naive_split, scaled_period);
% time_data_naive_split.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
% time_data_naive_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7', 'tempGPU'};
% time_data_naive_split.InputUnit = {'Watts','Watts','Watts','Watts'};
% time_data_naive_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius', 'Celcius'};
% Create train data objects for system identficiation using componentwise split for
% power on the entire board:
time_data_pwr_comps = iddata(thermal_inputs, power_components, scaled_period);
time_data_pwr_comps.InputName = {'watt_big', 'watt_little', 'watt_gpu', 'watt_mem'};
time_data_pwr_comps.OutputName = {'temp4', 'temp5', 'temp6', 'temp7', 'tempGPU'};
time_data_pwr_comps.InputUnit = {'Watts','Watts','Watts','Watts'};
time_data_pwr_comps.OutputUnit = {'Celcius','Celcius','Celcius','Celcius', 'Celcius'};
% Create test data objects for system identficiation using naive big
% cluster power split based on usage:
% v_time_data_naive_split = iddata(v_thermal_inputs, v_power_big_cluster_naive_split, scaled_period);
% v_time_data_naive_split.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
% v_time_data_naive_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7', 'tempGPU'};
% v_time_data_naive_split.InputUnit = {'Watts','Watts','Watts','Watts'};
% v_time_data_naive_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius', 'Celcius'};
% Create test data objects for system identficiation using componentwise split for
% power on the entire board:
v_time_data_comp_split = iddata(v_thermal_inputs, v_power_components, scaled_period);
v_time_data_comp_split.InputName = {'watt_big', 'watt_little', 'watt_gpu', 'watt_mem'};
v_time_data_comp_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7', 'tempGPU'};
v_time_data_comp_split.InputUnit = {'Watts','Watts','Watts','Watts'};
v_time_data_comp_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius', 'Celcius'};


%% Create state-space models
A_comp = A_init;
B_comp = B_init;
% A_naive = A_init;
% B_naive = A_init(:, 1:4);
C = eye(5);
D = zeros(5,4); 
K = zeros(5,5);
x0 = thermal_inputs(1,:);
v_x0 = v_thermal_inputs(1,:);
% Create naive split state space model:
% m_naive = idss(A_naive,B_naive,C,D,K,x0',scaled_period);
% Set model constraints:
% m_naive.Structure.c.Free = false;
% m_naive.Structure.a.Minimum = 0;
% m_naive.Structure.a.Maximum = 1;
% m_naive.Structure.b.Maximum = 1;
% m_naive.Structure.b.Minimum = 0;
% m_naive.Structure.b.Free = true;
% m_naive.Structure.c.Free = false;
% m_naive.Structure.d.Free = false;
% m_naive.Structure.k.Free = false;
% opt_naive = ssestOptions;
% opt_naive.InitialState = x0';
% mp_naive_split = ssest(time_data_naive_split, m_naive, 'Ts', scaled_period, 'DisturbanceModel', 'none', opt_naive);

% create components split state space model:
m_split = idss(A_comp,B_comp,C,D,K,x0',scaled_period);
m_split.Structure.c.Free = false;
m_split.Structure.a.Minimum = 0;
m_split.Structure.a.Maximum = 1;
m_split.Structure.b.Maximum = 1;
m_split.Structure.b.Minimum = 0;
m_split.Structure.b.Free = true;
m_split.Structure.c.Free = false;
m_split.Structure.d.Free = false;
m_split.Structure.k.Free = false;
opt_split = ssestOptions;
opt_split.InitialState = x0';
mp_comp_split = ssest(time_data_pwr_comps, m_split, 'Ts', scaled_period, 'DisturbanceModel', 'none', opt_split);

%% Validate the models:
% figure('Name','Naive split comparison');
% compare(v_time_data_naive_split, mp_naive_split);

% figure('Name','Componentwise split comparison');
% compare(v_time_data_comp_split, mp_comp_split);

% figure('Name', 'Naive Split Predition');
% P_naive = predict(mp_naive_split, time_data_naive_split, PREDICT_HORIZON);
% plot(v_time_data_naive_split, P_naive);
% legend('Verification data','Predicted data');

opt = predictOptions('InitialCondition',x0');
figure('Name', 'Power-Component split prediction TRAINING');
P_comp = predict(mp_comp_split , time_data_pwr_comps, PREDICT_HORIZON, opt);
plot(time_data_pwr_comps , P_comp);
legend('Verification data','Predicted data');

figure('Name', 'Power-Component split prediction VERIFICATION');
P_comp = predict(mp_comp_split , v_time_data_comp_split, PREDICT_HORIZON, opt);
plot(v_time_data_comp_split , P_comp);
legend('Verification data','Predicted data');

% tp = zeros(size(v_thermal_inputs));
% for i = 1:size(v_thermal_inputs, 1)
%     tp(i, :) = A_s * v_thermal_inputs(i, :)' + B_s * v_power_inputs(i, :)'; 
% end
% 
% predicted_validation = iddata(tp, v_power_inputs, scaled_period);
% predicted_validation.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
% predicted_validation.OutputName = {'temp4', 'temp5', 'temp6', 'temp7'};
% predicted_validation.InputUnit = {'Watts','Watts','Watts','Watts'};
% predicted_validation.OutputUnit = {'Celcius','Celcius','Celcius','Celcius'};
% figure();
% plot(v_time_data_naive_split, predicted_validation);
% legend('True data','Predicted data with A_s B_s Model');
% 