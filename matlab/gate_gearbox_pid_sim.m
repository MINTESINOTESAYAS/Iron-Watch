% GATE_GEARBOX_PID_SIM  90-degree gate drive: 3-stage 70:1 gearbox + PID control
%
%   Models YOUR SolidWorks assembly (gear BOM below) driving a 1.0 m / 13.5 kg
%   boom arm with a 24 V 500 W DC motor, and moves it 0 -> 90 deg (OPEN) and
%   back (CLOSE) on a trapezoidal motion profile under PID + feedforward.
%
%   HOW TO RUN: open this file in MATLAB, press F5 (Run). No toolboxes needed.
%   Octave users:  octave gate_gearbox_pid_sim.m
%
%   WHAT YOU GET:
%     1. Console: gear inertia table, torque/current sizing report, PID gains
%     2. Console: OPEN/CLOSE metrics (overshoot, settling, RMS error) + PASS/FAIL
%     3. Figure 1: nominal response (angle, error, velocity, torque, current, voltage)
%     4. Figure 2: robustness run (detuned plant, same controller)
%     5. File gate_tuning.mat: gains + profile for Simulink / hardware
%
%   Conventions: theta = 0 CLOSED (horizontal) | theta = +90 deg OPEN (vertical)

clear; clc; close all;

%% 0. Parameters (single source of truth - edit ONLY gate_params.m)
P = gate_params();

%% 1. Design report -------------------------------------------------------
print_report(P);

%% 2. Simulate nominal plant + worst-case plant ---------------------------
fprintf('\nSimulating (fixed-step RK4 @ 1 kHz, 16 s full cycle) ...\n');
tic;
[log_nom]   = simulate_case(P, 'nominal');
[log_worst] = simulate_case(P, 'worst');
fprintf('  done in %.1f s.\n', toc);

%% 3. Acceptance tests ----------------------------------------------------
fprintf('\n==================== ACCEPTANCE TESTS ====================\n');
ok_nom   = check_case(P, log_nom,   'nominal',    0.3);
ok_worst = check_case(P, log_worst, 'worst-case', 0.5);
fprintf('========================================================\n');
if ok_nom && ok_worst
    fprintf('RESULT: ALL CHECKS PASSED\n');
else
    fprintf('RESULT: FAILURES PRESENT - see [FAIL] lines above\n');
end

%% 4. Plots ----------------------------------------------------------------
make_plots(P, log_nom, log_worst);

%% 5. Export tuning for Simulink / hardware --------------------------------
tuning = struct('Kp', P.ctrl.Kp, 'Ki', P.ctrl.Ki, 'Kd', P.ctrl.Kd, ...
    'lam_d', P.ctrl.lam_d, 'int_max', P.ctrl.int_max, ...
    'N', P.N, 'eta', P.eta, 'T_peak_m', P.motor.T_peak_m, ...
    'Kt', P.motor.Kt, 'm_arm', P.m_arm, 'Lc', P.Lc, 'J_eff', P.J_eff, ...
    'b', P.fric.b, 'tc', P.fric.tc, 'T_move', P.prof.T_move, ...
    'T_acc', P.prof.T_acc, 'dt', P.sim.dt);
save('gate_tuning.mat', 'tuning');
fprintf('\nExported gate_tuning.mat (gains + profile for Simulink/hardware).\n');

%==========================================================================
% LOCAL FUNCTIONS
%==========================================================================

function print_report(P)
    fprintf('=========== GATE GEARBOX PID SIM - DESIGN REPORT ===========\n');
    fprintf('Gear geometry cross-check (full-depth teeth: OD=m(z+2), root=m(z-2.5)):\n');
    for k = 1:numel(P.gear)
        g = P.gear(k);
        th_od = g.module*(g.teeth+2);  th_rt = g.module*(g.teeth-2.5);
        th_p  = g.module*g.teeth;
        ok = abs(th_od-g.od*1000)<1e-9 && abs(th_rt-g.root*1000)<1e-9 ...
             && abs(th_p-g.pitch*1000)<1e-9;
        s = 'OK'; if ~ok, s = 'MISMATCH!!'; end
        fprintf('  %s: pitch %6.1f OD %6.1f root %6.1f -> %s\n', ...
            g.name, g.pitch*1000, g.od*1000, g.root*1000, s);
    end
    fprintf('\nMass / inertia (hollow cylinder @ pitch radius, steel %.0f kg/m^3):\n', P.rho_steel);
    mtot = 0;
    for k = 1:numel(P.gear)
        fprintf('  %s: mass = %7.3f kg   J = %.6f kg m^2\n', ...
            P.gear(k).name, P.gear(k).mass, P.gear(k).J);
        mtot = mtot + P.gear(k).mass;
    end
    fprintf('  TOTAL gear mass = %.2f kg  (compare with SolidWorks Mass Properties!)\n', mtot);
    fprintf('\nRatios: i1=%.4f i2=%.4f i3=%.4f N_total=%.4f\n', P.i1, P.i2, P.i3, P.N);
    fprintf('Centre distances (verify in SolidWorks sketch): %.1f / %.1f / %.1f mm\n', P.cd_mm);
    fprintf('\nArm: m=%.1f kg L=%.1f m Lc=%.2f m -> J_arm=%.4f kg m^2\n', ...
        P.m_arm, P.L_arm, P.Lc, P.J_arm);
    fprintf('Worst-case gravity torque (horizontal) = %.2f N m\n', P.T_grav_max);
    fprintf('Efficiency: %.2f^3 = %.4f | J_eff @ output = %.4f kg m^2\n', ...
        P.eta_mesh, P.eta, P.J_eff);
    fprintf('  (arm %.3f + G3 %.4f + shaftB %.4f + shaftA %.4f + motor %.4f)\n', ...
        P.J_arm, P.J_G3, P.J_shaftB*P.i3^2, ...
        P.J_shaftA*(P.i2*P.i3)^2, P.J_mshaft*P.N^2);
    m = P.motor;
    fprintf('\nMotor: %s\n', m.name);
    fprintf('  %.0f V %.0f W %.0f rpm: T_rated=%.3f N m I_rated=%.1f A\n', ...
        m.V_sup, m.P_rated, m.n_rated, m.T_rated, m.I_rated);
    fprintf('  R=%.2f ohm L=%.2f mH Ke=Kt=%.6f J_rotor=%.1e (R,L,Jrot = estimates)\n', ...
        m.R, m.L*1000, m.Ke, m.J_rotor);
    fprintf('  Holding torque @ motor = %.3f N m = %.1f%% of rated (peak avail %.2f N m)\n', ...
        m.T_hold_m, 100*m.T_hold_m/m.T_rated, m.T_peak_m);
    fprintf('\nProfile: 90 deg in %.1f s, t_acc=%.1f s -> v_pk=%.4f rad/s (%.2f deg/s)\n', ...
        P.prof.T_move, P.prof.T_acc, P.prof.v_pk, rad2deg(P.prof.v_pk));
    fprintf('Gains (wn=%.0f, zeta=%.1f): Kp=%.1f Ki=%.1f Kd=%.1f\n', ...
        P.ctrl.wn, P.ctrl.zeta, P.ctrl.Kp, P.ctrl.Ki, P.ctrl.Kd);
end

function [p, v, a] = trap_prog(s, P)
    % Trapezoidal reference for move progress s in [0,1] -> (pos, vel, acc)
    D = P.prof.move; T = P.prof.T_move; ta = P.prof.T_acc;
    vv = P.prof.v_pk; aa = P.prof.a_pk;
    t = s * T;
    if t <= 0
        p = 0; v = 0; a = 0;
    elseif t < ta
        p = 0.5*aa*t*t; v = aa*t; a = aa;
    elseif t < T - ta
        p = 0.5*aa*ta*ta + vv*(t-ta); v = vv; a = 0;
    elseif t < T
        td = T - t;
        p = D - 0.5*aa*td*td; v = vv - aa*(t-(T-ta)); a = -aa;
    else
        p = D; v = 0; a = 0;
    end
end

function [th_d, w_d, a_d] = ref_at(t, P)
    % Full-cycle reference: dwell | OPEN | dwell | CLOSE | dwell
    if t < P.prof.t0_open
        th_d = 0; w_d = 0; a_d = 0;
    elseif t < P.prof.t1_open
        [p, v, a] = trap_prog((t - P.prof.t0_open)/P.prof.T_move, P);
        th_d = p; w_d = v; a_d = a;
    elseif t < P.prof.t0_close
        th_d = P.prof.move; w_d = 0; a_d = 0;
    elseif t < P.prof.t1_close
        [p, v, a] = trap_prog((t - P.prof.t0_close)/P.prof.T_move, P);
        th_d = P.prof.move - p; w_d = -v; a_d = -a;
    else
        th_d = 0; w_d = 0; a_d = 0;
    end
end

function dx = state_deriv(x, t, P, PL)
    % Full state: x = [theta; omega; tau_driver; int_e; ed_filt]
    % P  = design parameters (controller uses these)
    % PL = plant parameters  (reality; differs in robustness run)
    th = x(1); w = x(2); tau_drv = x(3); int_e = x(4); ed_f = x(5);
    [th_d, w_d, a_d] = ref_at(t, P);
    e = th_d - th;
    ed_raw = w_d - w;
    % PID + feedforward (output side, N m)
    tau_pid = P.ctrl.Kp*e + P.ctrl.Ki*int_e + P.ctrl.Kd*ed_f;
    ff = P.m_arm*P.g*P.Lc*cos(th) + P.J_eff*a_d ...
       + P.fric.b*w_d + P.fric.tc*tanh(w_d/0.05);
    tau_m_cmd = (tau_pid + ff) / (P.N * P.eta);
    tau_sat = max(-P.motor.T_peak_m, min(P.motor.T_peak_m, tau_m_cmd));
    % Anti-windup: freeze integrator when saturated and pushing further
    frozen = (tau_m_cmd >  P.motor.T_peak_m && e > 0) || ...
             (tau_m_cmd < -P.motor.T_peak_m && e < 0);
    if frozen
        int_dot = 0;
    else
        int_dot = e;
    end
    if P.ctrl.Ki*int_e >  P.ctrl.int_max && int_dot > 0, int_dot = 0; end
    if P.ctrl.Ki*int_e < -P.ctrl.int_max && int_dot < 0, int_dot = 0; end
    % Plant (output side)
    tau_out = tau_drv * P.N * P.eta;
    w_dot = (tau_out - PL.m*P.g*PL.Lc*cos(th) - PL.b*w ...
             - PL.tc*tanh(w/0.02)) / PL.J;
    dx = [w; w_dot; (tau_sat - tau_drv)/P.ctrl.tau_drv; int_dot; ...
          P.ctrl.lam_d*(ed_raw - ed_f)];
end

function lg = simulate_case(P, which)
    if strcmp(which, 'worst')
        PL = P.plant_worst;
    else
        PL = struct('m', P.m_arm, 'Lc', P.Lc, 'J', P.J_eff, ...
                    'b', P.fric.b, 'tc', P.fric.tc);
    end
    dt = P.sim.dt;
    n = round(P.prof.T_end/dt) + 1;
    T = zeros(n,1); X = zeros(n,5); RE = zeros(n,3);
    for k = 1:n-1
        t = (k-1)*dt;
        T(k) = t;
        x = X(k,:)';
        k1 = state_deriv(x, t, P, PL);
        k2 = state_deriv(x + 0.5*dt*k1, t + 0.5*dt, P, PL);
        k3 = state_deriv(x + 0.5*dt*k2, t + 0.5*dt, P, PL);
        k4 = state_deriv(x + dt*k3, t + dt, P, PL);
        X(k+1,:) = (x + dt*(k1 + 2*k2 + 2*k3 + k4)/6)';
    end
    T(n) = P.prof.T_end;
    for k = 1:n
        [th_d, w_d, a_d] = ref_at(T(k), P);
        RE(k,:) = [th_d, w_d, a_d];
    end
    lg.T = T; lg.X = X; lg.REF = RE;
    lg.tau_m = X(:,3);
    lg.cur   = X(:,3) / P.motor.Kt;
    lg.volt  = lg.cur*P.motor.R + P.motor.Ke*P.N*X(:,2);
    lg.which = which;
end

function [over, settle, rms, mx] = move_metrics(P, lg, t0, t1, target)
    T = lg.T; TH = lg.X(:,1); RE = lg.REF(:,1);
    m  = (T >= t0) & (T <= t1 + 2.0);
    me = (T >= t0) & (T <= t1);
    err = RE(m) - TH(m);
    if target > 0
        over = max(0, max(TH(m)) - target);
    else
        over = max(0, target - min(TH(m)));
    end
    outs = T(m & (abs(RE - TH) > deg2rad(0.5)));
    if isempty(outs)
        settle = 0;
    else
        settle = max(outs) - t0;
    end
    e_move = RE(me) - TH(me);
    rms = sqrt(mean(e_move.^2));
    mx  = max(abs(e_move));
end

function ok = check_case(P, lg, tag, steady_lim_deg)
    [o1, s1, r1, ~] = move_metrics(P, lg, P.prof.t0_open, P.prof.t1_open, P.prof.move);
    [o2, s2, r2, ~] = move_metrics(P, lg, P.prof.t0_close, P.prof.t1_close, 0);
    steady = mean(abs(lg.REF(lg.T >= P.prof.T_end-1, 1) - lg.X(lg.T >= P.prof.T_end-1, 1)));
    pk_tq = max(abs(lg.tau_m)); pk_i = max(abs(lg.cur)); pk_v = max(abs(lg.volt));
    fprintf('--- %s plant ---\n', tag);
    fprintf('  OPEN : overshoot=%.3f deg settle=%.2f s RMS=%.3f deg\n', ...
        rad2deg(o1), s1, rad2deg(r1));
    fprintf('  CLOSE: overshoot=%.3f deg settle=%.2f s RMS=%.3f deg\n', ...
        rad2deg(o2), s2, rad2deg(r2));
    fprintf('  steady err=%.3f deg peakT=%.3f Nm peakI=%.2f A peakV=%.2f V\n', ...
        rad2deg(steady), pk_tq, pk_i, pk_v);
    C = {'overshoot OPEN<=2deg',  rad2deg(o1)<=2.0; ...
         'overshoot CLOSE<=2deg', rad2deg(o2)<=2.0; ...
         'settle OPEN<=move+2s',  s1<=P.prof.T_move+2; ...
         'settle CLOSE<=move+2s', s2<=P.prof.T_move+2; ...
         sprintf('steady<=%.1fdeg',steady_lim_deg), rad2deg(steady)<=steady_lim_deg; ...
         'peakTq<90%limit',  pk_tq<0.9*P.motor.T_peak_m; ...
         'peakI<limit',      pk_i<P.motor.I_peak; ...
         'peakV headroom',   pk_v<20.0; ...
         'RMS<1deg',         max(rad2deg(r1),rad2deg(r2))<1.0};
    ok = true;
    for k = 1:size(C,1)
        if C{k,2}, s = 'PASS'; else s = 'FAIL'; ok = false; end
        fprintf('  [%s] [%s] %s\n', s, tag, C{k,1});
    end
end

function make_plots(P, ln, lw)
    t = ln.T;
    figure('Name', 'Gate response - nominal plant', 'NumberTitle', 'off');
    subplot(3,2,1);
    plot(t, rad2deg(ln.REF(:,1)), 'r--', t, rad2deg(ln.X(:,1)), 'b-', 'LineWidth', 1.2);
    grid on; xlabel('time (s)'); ylabel('angle (deg)');
    title('Arm angle: reference vs actual'); legend('reference', 'actual');
    subplot(3,2,2);
    plot(t, rad2deg(ln.REF(:,1)-ln.X(:,1)), 'b-', 'LineWidth', 1.2);
    grid on; xlabel('time (s)'); ylabel('error (deg)');
    title('Tracking error');
    subplot(3,2,3);
    plot(t, rad2deg(ln.REF(:,2)), 'r--', t, rad2deg(ln.X(:,2)), 'b-', 'LineWidth', 1.2);
    grid on; xlabel('time (s)'); ylabel('speed (deg/s)');
    title('Arm speed: reference vs actual'); legend('reference', 'actual');
    subplot(3,2,4);
    plot(t, ln.tau_m, 'b-', 'LineWidth', 1.2); hold on;
    plot([t(1) t(end)], [P.motor.T_peak_m P.motor.T_peak_m], 'r--');
    plot([t(1) t(end)], [-P.motor.T_peak_m -P.motor.T_peak_m], 'r--');
    hold off; grid on; xlabel('time (s)'); ylabel('torque (N m)');
    title('Motor torque + driver limits'); legend('torque', 'limits');
    subplot(3,2,5);
    plot(t, ln.cur, 'b-', 'LineWidth', 1.2); hold on;
    plot([t(1) t(end)], [P.motor.I_peak P.motor.I_peak], 'r--');
    plot([t(1) t(end)], [-P.motor.I_peak -P.motor.I_peak], 'r--');
    hold off; grid on; xlabel('time (s)'); ylabel('current (A)');
    title('Motor current + limit'); legend('current', 'limit');
    subplot(3,2,6);
    plot(t, ln.volt, 'b-', 'LineWidth', 1.2); hold on;
    plot([t(1) t(end)], [P.motor.V_sup P.motor.V_sup], 'r--');
    plot([t(1) t(end)], [-P.motor.V_sup -P.motor.V_sup], 'r--');
    hold off; grid on; xlabel('time (s)'); ylabel('voltage (V)');
    title('Implied voltage + supply'); legend('voltage', 'supply');

    figure('Name', 'Gate response - worst-case plant', 'NumberTitle', 'off');
    subplot(2,1,1);
    plot(lw.T, rad2deg(lw.REF(:,1)-lw.X(:,1)), 'b-', 'LineWidth', 1.2);
    grid on; xlabel('time (s)'); ylabel('error (deg)');
    title('Robustness run: tracking error (plant +15% mass, +20% J, 2x friction)');
    subplot(2,1,2);
    plot(lw.T, lw.tau_m, 'b-', 'LineWidth', 1.2); hold on;
    plot([lw.T(1) lw.T(end)], [P.motor.T_peak_m P.motor.T_peak_m], 'r--');
    plot([lw.T(1) lw.T(end)], [-P.motor.T_peak_m -P.motor.T_peak_m], 'r--');
    hold off; grid on; xlabel('time (s)'); ylabel('torque (N m)');
    title('Robustness run: motor torque + limits'); legend('torque', 'limits');
end
