%% GATE_SIM  Iron-Watch boom gate: 70:1 gearbox + DC motor + PID (simplified)
%
%   Moves the arm 0 deg (CLOSED) -> 90 deg (OPEN) along a trapezoidal
%   speed profile using a PID controller. Plant = inertia + viscous friction.
%
%   RUN:   open in MATLAB and press F5   (Octave: octave gate_sim.m)
%   NEEDS: gate_params.m in the same folder. No toolboxes.
%
%   Outputs: console sizing report, Figure 1 (angle / error / current).

clear; clc; close all;
P = gate_params();

%% ---- console report -----------------------------------------------------
fprintf('=========== IRON-WATCH GATE DRIVE ===========\n');
fprintf('Gear ratio N            : %.1f : 1  (eta = %.3f)\n', P.N, P.eta);
fprintf('Inertia at arm shaft    : %.2f kg*m^2\n', P.J_eff);
fprintf('   arm %.2f + gearbox %.2f + rotor %.2f\n', ...
        P.J_arm, P.J_gearbox, P.motor.J_rot*P.N^2);
T_acc_req = P.J_eff*P.a_pk + P.b_fric*P.v_pk;           % torque to accelerate
fprintf('Peak torque needed @ arm: %.1f N*m  -> @ motor %.3f N*m (rated %.2f)\n', ...
        T_acc_req, T_acc_req/(P.N*P.eta), P.motor.T_rated);
fprintf('PID gains  Kp=%.1f  Ki=%.1f  Kd=%.1f\n', P.Kp, P.Ki, P.Kd);

%% ---- simulation (Euler, 1 ms) --------------------------------------------
dt = 1e-3;
t  = 0:dt:P.T_sim;
n  = numel(t);

theta = zeros(1,n);  omega = zeros(1,n);  current = zeros(1,n);
theta_ref = zeros(1,n);  omega_ref = zeros(1,n);  volt = zeros(1,n);
e_int = 0;

for k = 1:n-1
    % 1. reference
    [th_r, w_r] = P.ref(t(k));
    theta_ref(k) = th_r;  omega_ref(k) = w_r;

    % 2. PID  (torque demand at the arm shaft)
    e  = th_r - theta(k);
    de = w_r  - omega(k);
    e_int = max(min(e_int + e*dt, P.I_clamp/P.Ki), -P.I_clamp/P.Ki); % clamp
    tau_cmd = P.Kp*e + P.Ki*e_int + P.Kd*de;

    % 3. torque -> motor current command, limited by the H-bridge
    i_cmd = tau_cmd/(P.N*P.eta*P.motor.Kt);
    i_cmd = max(min(i_cmd, P.motor.I_max), -P.motor.I_max);

    % 4. motor electrical loop (voltage = Ri + back-EMF, limited by supply)
    V = i_cmd*P.motor.R + P.motor.Ke*P.N*omega(k);
    V = max(min(V, P.motor.V), -P.motor.V);
    volt(k) = V;
    didt = (V - P.motor.R*current(k) - P.motor.Ke*P.N*omega(k))/P.motor.L;
    current(k+1) = current(k) + didt*dt;

    % 5. mechanics:  J*alpha = T_gear - b*omega
    tau_out   = P.N*P.eta*P.motor.Kt*current(k+1);
    alpha     = (tau_out - P.b_fric*omega(k))/P.J_eff;
    omega(k+1) = omega(k) + alpha*dt;
    theta(k+1) = theta(k) + omega(k+1)*dt;
end
theta_ref(n) = P.theta_target;  volt(n) = volt(n-1);

%% ---- results --------------------------------------------------------------
theta_deg = theta*180/pi;
err_deg   = (theta_ref - theta)*180/pi;
settle    = t(find(abs(err_deg) > 0.5, 1, 'last'));
fprintf('\nFinal angle   : %.2f deg (target 90)\n', theta_deg(end));
fprintf('Peak error    : %.2f deg\n', max(abs(err_deg)));
fprintf('Settled <0.5deg at t = %.2f s\n', settle);
fprintf('Peak current  : %.1f A (limit %.0f A)\n', max(abs(current)), P.motor.I_max);
fprintf('Peak voltage  : %.1f V (supply %.0f V)\n', max(abs(volt)), P.motor.V);

figure('Name','Iron-Watch gate: PID response');
subplot(3,1,1);
plot(t, theta_ref*180/pi, 'r--', t, theta_deg, 'b', 'LineWidth', 1.3);
ylabel('\theta [deg]'); legend('reference','actual','Location','SouthEast'); grid on;
title('Gate arm angle: 0 (closed) \rightarrow 90 deg (open)');
subplot(3,1,2);
plot(t, err_deg, 'k'); ylabel('Error [deg]'); grid on;
subplot(3,1,3);
plot(t, current, 'm'); ylabel('Motor current [A]'); xlabel('Time [s]'); grid on;
