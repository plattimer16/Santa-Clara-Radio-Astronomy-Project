% Time vs Angle Plotter
% The purpose of this script is to evaluate how the rotation system
% is performing in terms of its ability to orient itself towards the target
% angle
% Variable to represent the target angle
target_angle = 15;
% Plot the angle of radio telescope against time
plot(time_array, angle_array, ’LineWidth’, 2, ’Color’, ’b’);
title(’Angle of Radio Telescope vs Time’);
xlabel(’Time (s)’);
ylabel(’Angle of Radio Telescope’);
yline(target_angle + 2, ’Color’, ’r’, ’LineStyle’,’--’, ’LineWidth’, 2);
yline(target_angle, ’Color’, ’r’, ’LineWidth’, 2);
62
yline(target_angle - 2, ’Color’, ’r’,’LineStyle’, ’--’, ’LineWidth’, 2);