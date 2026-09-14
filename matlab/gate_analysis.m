%% GATE_ANALYSIS  Open-loop and closed-loop analysis of the simplified gate
%
%   Linear model (arm shaft, current-controlled motor, no gravity):
%
%        J_eff * theta''  =  tau  -  b * theta'
%
%   Open loop  G(s) = theta/tau = 1 / (J s^2 + b s)
%   PID        C(s) = Kp + Ki/s + Kd s   (D acts on speed error, so the
%                                          closed loop is exactly 3rd order)
%   Closed loop  T(s) = (Kd s^2 + Kp s + Ki) / (J s^3 + (b+Kd) s^2 + Kp s + Ki)
%
%   RUN:  >> gate_analysis      (no toolbox needed for the numbers;
%          the Bode / step plots use Control System Toolbox if present)

clear; clc; close all;
P = gate_params();
J = P.J_eff;  b = P.b_fric;  Kp = P.Kp;  Ki = P.Ki;  Kd = P.Kd;

%% 1. Open-loop plant
fprintf('================ OPEN LOOP  G(s) = 1/(J s^2 + b s) ================\n');
fprintf('J_eff = %.2f kg*m^2   b = %.2f N*m*s/rad\n', J, b);
fprintf('Poles: s = 0 (integrator, arm drifts), s = %.4f (friction)\n', -b/J);
fprintf('-> marginally stable: needs feedback to hold a position.\n\n');

%% 2. Closed-loop characteristic polynomial and poles
den = [J, b+Kd, Kp, Ki];
num = [Kd, Kp, Ki];
p   = roots(den);
fprintf('================ CLOSED LOOP with PID ================\n');
fprintf('Kp = %.1f  Ki = %.1f  Kd = %.1f\n', Kp, Ki, Kd);
fprintf('Closed-loop poles:\n');
for k = 1:numel(p)
    if abs(imag(p(k))) < 1e-9
        fprintf('   s = %8.3f\n', real(p(k)));
    else
        wn_k = abs(p(k));  z_k = -real(p(k))/wn_k;
        fprintf('   s = %8.3f %+8.3fj   (wn = %.2f rad/s, zeta = %.2f)\n', ...
            real(p(k)), imag(p(k)), wn_k, z_k);
    end
end
if all(real(p) < 0)
    fprintf('All poles in LHP -> STABLE.\n');
else
    fprintf('WARNING: unstable pole!\n');
end
fprintf('Slowest pole time constant: %.2f s  (settling ~ %.1f s)\n\n', ...
    1/min(abs(real(p))), 4/min(abs(real(p))));

%% 3. Controllability (state x = [theta; omega], input tau)
A = [0 1; 0 -b/J];  Bm = [0; 1/J];  C = [1 0];
Co = [Bm, A*Bm];    Ob = [C; C*A];
fprintf('rank(Co) = %d of 2 -> %s\n', rank(Co), pick(rank(Co)==2,'controllable','NOT controllable'));
fprintf('rank(Ob) = %d of 2 -> %s\n\n', rank(Ob), pick(rank(Ob)==2,'observable','NOT observable'));

%% 4. Steady-state torque / current budget for the motion profile
tau_acc = J*P.a_pk + b*P.v_pk;                 % during acceleration
i_acc   = tau_acc/(P.N*P.eta*P.motor.Kt);
w_motor = P.v_pk*P.N*60/(2*pi);                % rpm at cruise
fprintf('================ SIZING CHECK ================\n');
fprintf('Cruise speed   : %.1f deg/s arm -> %.0f rpm motor (rated %d)\n', ...
    P.v_pk*180/pi, w_motor, P.motor.n_rated);
fprintf('Accel torque   : %.1f N*m arm -> %.3f N*m motor (%.0f%% of rated)\n', ...
    tau_acc, tau_acc/(P.N*P.eta), 100*tau_acc/(P.N*P.eta)/P.motor.T_rated);
fprintf('Accel current  : %.1f A (driver limit %d A)\n\n', i_acc, P.motor.I_max);

%% 5. Plots (Control System Toolbox, optional)
if exist('tf', 'file') == 2
    G = tf(1, [J b 0]);
    T = tf(num, den);
    figure('Name', 'Open-loop plant');   bode(G);  grid on;  title('Open-loop G(s)');
    figure('Name', 'Closed-loop step');  step(T, 6); grid on;
    title('Closed-loop step response (1 rad step)');
    S = stepinfo(T);
    fprintf('Step: rise %.2f s  settle %.2f s  overshoot %.1f %%\n', ...
        S.RiseTime, S.SettlingTime, S.Overshoot);
    figure('Name', 'Pole-zero');  pzmap(T); grid on;
else
    fprintf('(Control System Toolbox not found - plots skipped, numbers above are valid.)\n');
end

function s = pick(cond, a, b)
if cond, s = a; else, s = b; end
end
