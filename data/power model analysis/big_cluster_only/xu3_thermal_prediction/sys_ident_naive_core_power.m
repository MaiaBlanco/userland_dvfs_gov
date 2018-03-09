%% Parameteric Knobs...
SKIP_FACTOR = 1;
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
thermal_inputs_noavg = data(1:end,11:15);
thermal_inputs = movmean(thermal_inputs_noavg, [AVG_WINDOW 0], 1);
thermal_inputs = thermal_inputs(1:SKIP_FACTOR:end, :);
thermal_inputs_next = [thermal_inputs_noavg(4:end,:); 
    thermal_inputs_noavg(end, :); thermal_inputs_noavg(end, :); thermal_inputs_noavg(end, :)];
power_big_cluster_naive_split = data(1:end,16:19);
% power_big_cluster_naive_split = movmean(power_big_cluster_naive_split, [AVG_WINDOW 0],1);
power_big_cluster_naive_split = power_big_cluster_naive_split(1:SKIP_FACTOR:end,:);

%% Read test data:
verification_data = csvread('xu3_power_thermal_test_blackscholes.csv',2);
v_thermal_inputs_noavg = verification_data(1:end,11:15);
v_thermal_inputs = movmean(v_thermal_inputs_noavg, [AVG_WINDOW 0], 1);
v_thermal_inputs = v_thermal_inputs(1:SKIP_FACTOR:end, :);
v_thermal_inputs_next = [v_thermal_inputs_noavg(4:end,:); 
    v_thermal_inputs_noavg(end, :); v_thermal_inputs_noavg(end, :); v_thermal_inputs_noavg(end, :)];
v_power_big_cluster_naive_split = verification_data(1:SKIP_FACTOR:end,16:19);
v_power_big_cluster_naive_split = movmean(v_power_big_cluster_naive_split, [AVG_WINDOW 0],1);
% Create train data objects for system identficiation using naive split for
% power on the big cluster:
time_data_naive_split = iddata(thermal_inputs, power_big_cluster_naive_split, scaled_period);
time_data_naive_split.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
time_data_naive_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7', 'tempGPU'};
time_data_naive_split.InputUnit = {'Watts','Watts','Watts','Watts'};
time_data_naive_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius', 'Celcius'};
% Create test data objects for system identficiation using naive big
% cluster power split based on usage:
v_time_data_naive_split = iddata(v_thermal_inputs, v_power_big_cluster_naive_split, scaled_period);
v_time_data_naive_split.InputName = {'watt4', 'watt5', 'watt6', 'watt7'};
v_time_data_naive_split.OutputName = {'temp4', 'temp5', 'temp6', 'temp7', 'tempGPU'};
v_time_data_naive_split.InputUnit = {'Watts','Watts','Watts','Watts'};
v_time_data_naive_split.OutputUnit = {'Celcius','Celcius','Celcius','Celcius', 'Celcius'};

%% Create state-space models
A_naive = A_init;
B_naive = A_init(:, 1:4);
C = eye(5);
D = zeros(5,4); 
K = zeros(5,5);
x0 = thermal_inputs(1,:);
v_x0 = v_thermal_inputs(1,:);
% Create naive split state space model:
m_naive = idss(A_naive,B_naive,C,D,K,x0',scaled_period);
% Set model constraints:
m_naive.Structure.c.Free = false;
m_naive.Structure.a.Minimum = 0;
m_naive.Structure.a.Maximum = 1;
m_naive.Structure.b.Maximum = 1;
m_naive.Structure.b.Minimum = 0;
m_naive.Structure.b.Free = true;
m_naive.Structure.c.Free = false;
m_naive.Structure.d.Free = false;
m_naive.Structure.k.Free = false;
opt_naive = ssestOptions;
opt_naive.InitialState = x0';
mp_naive_split = ssest(time_data_naive_split, m_naive, 'Ts', scaled_period, 'DisturbanceModel', 'none', opt_naive);

%% Validate the model:
temp_labels = ["CPU4"; "CPU5"; "CPU6"; "CPU7"; "GPU"];
% Lookahead three iterations:
pw=power_big_cluster_naive_split(3000:end,:);
ti = thermal_inputs(3000:end,:);
ti_n = thermal_inputs_next(3000:end,:);
est_temp = mp_naive_split.a * ti' + mp_naive_split.b * pw';
est_temp = mp_naive_split.a * est_temp + mp_naive_split.b * pw';
est_temp = mp_naive_split.a * est_temp + mp_naive_split.b * pw';
figure('Name', '0.6s Naive Power Split prediction (Round Robin Training Data)');
for i=1:4
    subplot(2,2,i);
    t = 1:size(ti,1);
    plot( t, ti(:,i) );
    hold on;
    plot( t, est_temp(i,:)' );
    title(sprintf('%s',temp_labels(i,:)));
    legend('Source data','Predicted data');
    hold off;
end
%% plot max temp over training data:
figure('Name', '0.6s Naive Power Split prediction (Round Robin Training Data) Max Temps');
t = 1:size(ti,1);
plot( t, max(ti,[], 2));
hold on;
plot( t, max(est_temp,[], 1)' );
title('Max Temp over CPUs and GPU');
legend('Source data','Predicted data');
hold off;
error = mean(abs(ti_n - est_temp')./ti_n)*100;
fprintf('Training error is %d\n', mean(error(1:4)));

%% Plot verification data
% Lookahead three iterations:
v_pw=v_power_big_cluster_naive_split(1:end,:);
v_ti = v_thermal_inputs(1:end,:);
v_ti_n = v_thermal_inputs_next(1:end,:);
v_est_temp = mp_naive_split.a * v_ti' + mp_naive_split.b * v_pw';
v_est_temp = mp_naive_split.a * v_est_temp + mp_naive_split.b * v_pw';
v_est_temp = mp_naive_split.a * v_est_temp + mp_naive_split.b * v_pw';
figure('Name', '0.6s Naive Power Split prediction (4 Threaded Blackscholes)');
for i=1:4
    subplot(2,2,i);
    t = 1:size(v_ti,1);
    plot( t, v_ti(:,i) );
    hold on;
    plot( t, v_est_temp(i,:)' );
    legend('Source data','Predicted data');
    title(sprintf('%s',temp_labels(i,:)));
    hold off;
end
%% Plot max temps for verification data
figure('Name', '0.6s Naive Power Split prediction (4 Threaded Blackscholes) Max Temps');
t = 1:size(v_ti,1);
plot( t, max(v_ti,[],2) );
hold on;
plot( t, max(v_est_temp,[],1)' );
legend('Source data','Predicted data');
title('Max Temp over CPUs and GPU');
hold off;
v_error = mean(abs(v_ti_n - v_est_temp')./v_ti_n)*100;
fprintf('Verification error is %d\n', mean(v_error(1:4)));