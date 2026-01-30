% Angle Comparison Script
% The purpose of this scrip tis to manually compare the rounded reported
% angles by the angle sensor to the angles reported by the analog angle
% protractor
% By Nicholas Alva
% Clear everything
clc
close all
clear
% Create an array with the angles (in degrees) read from the analog
% protractor
analog_protractor = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90];
% Create an array with the angles (in degrees) read from the angle sensor
angle_sensor = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90];
% Plot the angle protractor’s values against the angle sensor’s value
plot(analog_protractor, analog_protractor, ’LineWidth’, 2);
hold;
plot(analog_protractor, angle_sensor, ’LineWidth’, 3, ’LineStyle’, ’--’, ’Color’, ’r’);
xlabel(’Angle Read by Analog Protractor (Degrees)’);
ylabel(’Angle Read by Angle Sensor (Degrees)’);
title(’Plot Comparing Angle Read By Sensor and Protractor’);
legend(’Analog Protractor Reading’, ’Angle Sensor Reading’);