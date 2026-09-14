%% GATE_SIM  90-degree boom-gate: gearbox + DC motor + PID, plain and simple
%
%   Moves the arm from theta=0 (CLOSED, horizontal) to theta=90deg (OPEN,
%   vertical) using a trapezoidal speed profile tracked by a PID +
%   gravity-feedforward controller.
%
%   RUN: open in MATLAB, press F5 (or `octave gate_sim.m`). No toolboxes.
%
%   Files:
%     gate_params.m  <- all numbers live here, edit this one file
%     gate_sim.m     <- this file: simulation + plots (rarely needs editing)

clear; clc; close all;
P = gate_params();

%% ---- console report -----------------------------------------------------
fprintf('Total gear ratio       : %.3f : 1\n', P.N);
fprintf('Worst-case arm torque  : %.2f N*m (at theta=0, horizontal)\n', P.T_grav_max);
T_motor_needed = P.T_grav_max/(P.N*P.eta);
fprintf('Motor-side torque needed: %.3f N*m  (motor rated = %.3f N*m, %.0f%% used)\n', ...
    T_motor_needed, P.motor.T_rated, 100*T_motor_needed/P.motor.T_rated);
fprintf('Effective inertia @ output shaft: %.3f kg*m^2\n', P.J_eff);
fprintf('  (motor rotor reflected = %.3f, gearbox reflected = %.3f, arm = %.3f)\n', ...
    P.motor.J_rot*P.N^2, P.J_gearbox_reflected, P.J_arm);
fprintf('PID gains: Kp=%.2f  Ki=%.2f  Kd=%.2f\n', P.Kp, P.Ki, P.Kd);

%% ---- simulation (fixed-step, 1 ms) ---------------------------------------
dt = 1e-3;
t  = 0:dt:8;
n  = numel(t);

theta = zeros(1,n); omega = zeros(1,n); current = zeros(1,n);
theta_ref = zeros(1,n); omega_ref = zeros(1,n);
e_int = 0; e_prev = 0;

for k = 1:n-1
    % --- trapezoidal reference at time t(k) ---
    [th_r, w_r] = trap_ref(t(k), P);
    theta_ref(k) = th_r; omega_ref(k) = w_r;

    % --- PID + gravity feedforward (all torques at the OUTPUT/arm shaft) ---
    e  = th_r - theta(k);
    de = w_r  - omega(k);
    tau_ff = P.m_arm*P.g*P.Lc*cos(theta(k));   % cancel gravity at current angle
    tau_pid = P.Kp*e + P.Ki*e_int + P.Kd*de;
    tau_cmd = tau_ff + tau_pid;

    % --- refer to motor shaft, saturate at driver current limit ---
    i_cmd = tau_cmd/(P.N*P.eta*P.motor.Kt);
    i_cmd = max(min(i_cmd, P.motor.I_max), -P.motor.I_max);

    if abs(i_cmd) < P.motor.I_max          % simple anti-windup: don't
        e_int = e_int + e*dt;               % integrate while saturated
    end
    e_prev = e;

    % --- motor electrical + mechanical (Euler step) ---
    V_cmd = i_cmd*P.motor.R + P.motor.Ke*P.N*omega(k);   % back-EMF feedforward
    V_cmd = max(min(V_cmd, P.motor.V), -P.motor.V);
    didt = (V_cmd - P.motor.R*current(k) - P.motor.Ke*P.N*omega(k))/P.motor.L;
    current(k+1) = current(k) + didt*dt;

    tau_out = P.N*P.eta*P.motor.Kt*current(k+1);
    theta_ddot = (tau_out - P.b_fric*omega(k) - P.m_arm*P.g*P.Lc*cos(theta(k)))/P.J_eff;

    omega(k+1) = omega(k) + theta_ddot*dt;
    theta(k+1) = theta(k) + omega(k+1)*dt;
end
theta_ref(n) = P.theta_target; omega_ref(n) = 0;

%% ---- results --------------------------------------------------------------
theta_deg = theta*180/pi;
err_deg = (theta_ref - theta)*180/pi;
fprintf('\nFinal angle: %.2f deg (target 90 deg)\n', theta_deg(end));
fprintf('Peak error during move: %.2f deg\n', max(abs(err_deg)));
fprintf('Peak current: %.1f A (limit %.0f A)\n', max(abs(current)), P.motor.I_max);

figure('Name','Gate arm PID response');
subplot(3,1,1);
plot(t, theta_ref*180/pi, 'r--', t, theta_deg, 'b', 'LineWidth', 1.3);
ylabel('\theta [deg]'); legend('reference','actual','Location','SouthEast'); grid on;
title('Gate arm angle: 0 (closed) -> 90 deg (open)');
subplot(3,1,2);
plot(t, err_deg, 'k'); ylabel('Error [deg]'); grid on;
subplot(3,1,3);
plot(t, current, 'm'); ylabel('Motor current [A]'); xlabel('Time [s]'); grid on;
