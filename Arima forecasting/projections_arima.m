% Copyright (C) 2023 Michal Orzolek

% The model is a sales projection of a small grocery shop using autoregressive integrated moving average model.
% This specification was chosen after carefully examining the data and identifying 
% weekly cyclicality. Other datasets might prove this specification to be wrong.


clear all
% Specify the ARIMA model order:
p = 8; % Autoregressive (AR) order
d = 1; % Differencing order
q = 7; % Moving average (MA) order
train_frac = 0.8;   % 0.8 of the data is used for training
profit_margin = 0.15; % percentage of revenue withheld as profit
avg_revenue = 23; % avg revenue per customer 

% read cvs file with dates in the first column and values in the second column
t = readtable('data_matlab_wdays.csv');
dates = datetime(t.Var1, 'InputFormat', 'dd-MM-yyyy');
values = t.Var2;
tt = timetable(dates,values);

% Split data into training and testing sets
n = height(tt);
n_train = round(n * train_frac);
train_tt = tt(1:n_train, :);
test_tt = tt(n_train+1:end, :); %number of testing samles n+1:end

% Fit the ARIMA model to the training data
model = arima(p, d, q);
estModel = estimate(model, train_tt.values);

% Forecast 
num_periods = numel(test_tt.dates);
[forecast, forecast_ci] = forecast(estModel, num_periods, 'Y0', train_tt.values);

% Calculate Mean Squared Error (MSE)
mse = mean((test_tt.values - forecast).^2);
% Calculate Mean Absolute Error (MAE)
mae = mean(abs(test_tt.values - forecast));

% Plot the results
figure
hold on
plot(tt.dates, tt.values, 'k', 'LineWidth', 1.5, 'DisplayName', 'Original Data')
plot(train_tt.dates, train_tt.values, 'b', 'LineWidth', 1.5, 'DisplayName', 'Training Data')
plot(test_tt.dates, forecast, 'r', 'LineWidth', 1.5, 'DisplayName', 'Forecast')
legend('show')
xlabel('Time')
ylabel('Value')
title('Time Series Forecasting using ARIMA')
hold off

% Revenue and profit calculation
revenue = avg_revenue*tt.values;
profit=revenue*profit_margin;
sales_tt=timetable(tt.dates,revenue,profit);
% Group sales by month
monthly_tt = retime(sales_tt, 'monthly', 'sum');

% Create a bar chart of the monthly Revenue and Profit
figure;
bar(monthly_tt.Time, [monthly_tt.Var1, monthly_tt.Var2]);
xlabel('Month');
ylabel('Amount');
title('Monthly Revenue and Profit');
legend({'Revenue', 'Profit'});
