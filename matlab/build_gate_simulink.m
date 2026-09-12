% BUILD_GATE_SIMULINK  Auto-build the Simulink twin of gate_gearbox_pid_sim.m
%
%   Run this in MATLAB (Simulink required):  >> build_gate_simulink
%   It creates, saves and opens gate_gearbox_pid.slx, then you press Run.
%
%   The diagram is a 1:1 block twin of the .m simulation:
%     trapezoidal profile (From Workspace) -> error -> PID (P + gated-I with
%     output clamp + filtered D) + feedforward (gravity/inertia/friction) ->
%     motor conversion -> current-limit saturation -> driver lag ->
%     gearbox+arm plant (output side) with gravity/viscous/Coulomb load.
%   All numbers come from gate_params.m (same single source of truth).
%
%   Acceptance: ScopeAngle should match Figure 1 of the .m sim
%     (overshoot < 2 deg, steady error < 0.3 deg, peak torque ~1.2 N m).
%   Blocks are placed on a grid; drag them into a tidy layout if you wish -
%   layout does not affect results.

clearvars -except gate_prof;   % keep workspace clean (gate_prof rebuilt below)
close all;

%% 0. Parameters + reference profile table -------------------------------
P = gate_params();

dt = P.sim.dt;
tv = (0:dt:P.prof.T_end)';
prof = zeros(numel(tv), 3);
for k = 1:numel(tv)
    [th_d, w_d, a_d] = profile_at(tv(k), P);
    prof(k,:) = [th_d, w_d, a_d];
end
gate_prof = [tv, prof];   %#ok<NASGU>  % From Workspace source: [t th_d w_d a_d]
assignin('base', 'gate_prof', gate_prof);

%% 1. Fresh model ----------------------------------------------------------
mdl = 'gate_gearbox_pid';
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end
try
    new_system(mdl);
catch ME
    error('BUILD_GATE_SIMULINK:noSimulink', ...
        ['Could not create a Simulink model (%s).\n' ...
         'Is Simulink installed and licensed? The .m simulation needs no Simulink.'], ME.message);
end
open_system(mdl);

% Grid placement helper: GP(col,row,w,h) -> [left top right bottom]
GP = @(c,r,w,h) [20+c*175, 40+r*90, 20+c*175+w, 40+r*90+h];
S  = @(c,r)   GP(c,r,36,52);    % sums / small
Gn = @(c,r)   GP(c,r,110,36);   % gains, transfer fcns, trig
Ct = @(c,r)   GP(c,r,70,32);    % constants
Lg = @(c,r)   GP(c,r,70,44);    % logic / relational
NT = @(v) num2str(v, '%.10g');  % full-precision numbers

% --- profile / reference --------------------------------------------------
add_block('simulink/Sources/From Workspace', [mdl '/Profile'], ...
    'Position', GP(0,2,140,44), 'VariableName', 'gate_prof');
add_block('simulink/Signal Routing/Demux', [mdl '/Demux'], ...
    'Position', GP(1,2,30,120), 'Outputs', '3');

% --- error sums ------------------------------------------------------------
add_block('simulink/Math Operations/Sum', [mdl '/ErrSum'], ...
    'Position', S(2,1), 'Inputs', '+-');
add_block('simulink/Math Operations/Sum', [mdl '/VelErrSum'], ...
    'Position', S(2,3), 'Inputs', '+-');

% --- P branch ---------------------------------------------------------------
add_block('simulink/Math Operations/Gain', [mdl '/Kp'], ...
    'Position', Gn(3,1), 'Gain', NT(P.ctrl.Kp));

% --- I branch with anti-windup gate ------------------------------------------
add_block('simulink/Sources/Constant', [mdl '/Tpeak_pos'], ...
    'Position', Ct(3,4), 'Value', NT(P.motor.T_peak_m));
add_block('simulink/Sources/Constant', [mdl '/Tpeak_neg'], ...
    'Position', Ct(3,5), 'Value', NT(-P.motor.T_peak_m));
add_block('simulink/Sources/Constant', [mdl '/Zero'], ...
    'Position', Ct(3,3), 'Value', '0');
add_block('simulink/Sources/Constant', [mdl '/Zero2'], ...
    'Position', Ct(3,0), 'Value', '0');
add_block('simulink/Logic and Bit Operations/Relational Operator', [mdl '/GT_hi'], ...
    'Position', Lg(4,4), 'Operator', '>');
add_block('simulink/Logic and Bit Operations/Relational Operator', [mdl '/E_pos'], ...
    'Position', Lg(4,1), 'Operator', '>');
add_block('simulink/Logic and Bit Operations/Logical Operator', [mdl '/AND_hi'], ...
    'Position', Lg(5,2), 'Operator', 'AND', 'Inputs', '2');
add_block('simulink/Logic and Bit Operations/Relational Operator', [mdl '/LT_lo'], ...
    'Position', Lg(4,5), 'Operator', '<');
add_block('simulink/Logic and Bit Operations/Relational Operator', [mdl '/E_neg'], ...
    'Position', Lg(4,0), 'Operator', '<');
add_block('simulink/Logic and Bit Operations/Logical Operator', [mdl '/AND_lo'], ...
    'Position', Lg(5,4), 'Operator', 'AND', 'Inputs', '2');
add_block('simulink/Logic and Bit Operations/Logical Operator', [mdl '/OR_fr'], ...
    'Position', Lg(6,3), 'Operator', 'OR', 'Inputs', '2');
add_block('simulink/Signal Routing/Switch', [mdl '/IntGate'], ...
    'Position', GP(4,2,70,70), 'Criteria', 'u2 >= Threshold', 'Threshold', '0.5');
add_block('simulink/Math Operations/Gain', [mdl '/Ki'], ...
    'Position', Gn(5,1), 'Gain', NT(P.ctrl.Ki));
add_block('simulink/Continuous/Integrator', [mdl '/IntE'], ...
    'Position', Gn(6,1), 'InitialCondition', '0', 'LimitOutput', 'on', ...
    'UpperSaturationLimit', NT(P.ctrl.int_max), ...
    'LowerSaturationLimit', NT(-P.ctrl.int_max));

% --- D branch (filtered velocity error) ---------------------------------------
add_block('simulink/Continuous/Transfer Fcn', [mdl '/Dfilt'], ...
    'Position', Gn(3,3), 'Numerator', ['[' NT(P.ctrl.lam_d) ']'], ...
    'Denominator', ['[1 ' NT(P.ctrl.lam_d) ']']);
add_block('simulink/Math Operations/Gain', [mdl '/Kd'], ...
    'Position', Gn(4,3), 'Gain', NT(P.ctrl.Kd));

% --- PID + feedforward sums ----------------------------------------------------
add_block('simulink/Math Operations/Sum', [mdl '/PIDSum'], ...
    'Position', S(7,1), 'Inputs', '+++');
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/CosTh'], ...
    'Position', Gn(5,6), 'Operator', 'cos');
add_block('simulink/Math Operations/Gain', [mdl '/GravFF'], ...
    'Position', Gn(6,6), 'Gain', NT(P.m_arm*P.g*P.Lc));
add_block('simulink/Math Operations/Gain', [mdl '/InertFF'], ...
    'Position', Gn(2,5), 'Gain', NT(P.J_eff));
add_block('simulink/Math Operations/Gain', [mdl '/ViscFF'], ...
    'Position', Gn(2,4), 'Gain', NT(P.fric.b));
add_block('simulink/Math Operations/Gain', [mdl '/CoulNorm'], ...
    'Position', Gn(3,6), 'Gain', '20');   % 1/0.05 smoothing
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/TanhWd'], ...
    'Position', Gn(4,6), 'Operator', 'tanh');
add_block('simulink/Math Operations/Gain', [mdl '/CoulFF'], ...
    'Position', Gn(5,5), 'Gain', NT(P.fric.tc));
add_block('simulink/Math Operations/Sum', [mdl '/FFSum'], ...
    'Position', S(7,5), 'Inputs', '++++');
add_block('simulink/Math Operations/Sum', [mdl '/OutTauSum'], ...
    'Position', S(8,3), 'Inputs', '++');

% --- motor interface: conversion -> limit -> driver lag -------------------------
add_block('simulink/Math Operations/Gain', [mdl '/ToMotor'], ...
    'Position', Gn(9,3), 'Gain', NT(1/(P.N*P.eta)));
add_block('simulink/Discontinuities/Saturation', [mdl '/CurLim'], ...
    'Position', Gn(10,3), 'UpperLimit', NT(P.motor.T_peak_m), ...
    'LowerLimit', NT(-P.motor.T_peak_m));
add_block('simulink/Continuous/Transfer Fcn', [mdl '/Driver'], ...
    'Position', Gn(11,3), 'Numerator', '[1]', ...
    'Denominator', ['[' NT(P.ctrl.tau_drv) ' 1]']);

% --- plant (output side) ---------------------------------------------------------
add_block('simulink/Math Operations/Gain', [mdl '/ToOutput'], ...
    'Position', Gn(12,3), 'Gain', NT(P.N*P.eta));
add_block('simulink/Math Operations/Sum', [mdl '/PlantSum'], ...
    'Position', S(13,3), 'Inputs', '+---');
add_block('simulink/Math Operations/Gain', [mdl '/InvJ'], ...
    'Position', Gn(14,3), 'Gain', NT(1/P.J_eff));
add_block('simulink/Continuous/Integrator', [mdl '/W'], ...
    'Position', Gn(15,3), 'InitialCondition', '0');
add_block('simulink/Continuous/Integrator', [mdl '/TH'], ...
    'Position', Gn(16,3), 'InitialCondition', '0');
add_block('simulink/Math Operations/Gain', [mdl '/ViscPlant'], ...
    'Position', Gn(14,5), 'Gain', NT(P.fric.b));
add_block('simulink/Math Operations/Gain', [mdl '/CoulNormP'], ...
    'Position', Gn(13,6), 'Gain', '50');   % 1/0.02 smoothing
add_block('simulink/Math Operations/Trigonometric Function', [mdl '/TanhW'], ...
    'Position', Gn(14,6), 'Operator', 'tanh');
add_block('simulink/Math Operations/Gain', [mdl '/CoulPlant'], ...
    'Position', Gn(15,6), 'Gain', NT(P.fric.tc));

% --- electrical monitor ------------------------------------------------------------
add_block('simulink/Math Operations/Gain', [mdl '/ToCurrent'], ...
    'Position', Gn(12,1), 'Gain', NT(1/P.motor.Kt));
add_block('simulink/Math Operations/Gain', [mdl '/Rdrop'], ...
    'Position', Gn(13,1), 'Gain', NT(P.motor.R));
add_block('simulink/Math Operations/Gain', [mdl '/EMF'], ...
    'Position', Gn(13,0), 'Gain', NT(P.motor.Ke*P.N));
add_block('simulink/Math Operations/Sum', [mdl '/VoltSum'], ...
    'Position', S(14,1), 'Inputs', '++');

% --- scopes / logging ----------------------------------------------------------------
add_block('simulink/Signal Routing/Mux', [mdl '/MuxAngle'], ...
    'Position', GP(16,1,30,80), 'Inputs', '2');
add_block('simulink/Sinks/Scope', [mdl '/ScopeAngle'], ...
    'Position', GP(17,1,90,80));
add_block('simulink/Signal Routing/Mux', [mdl '/MuxTau'], ...
    'Position', GP(12,5,30,110), 'Inputs', '3');
add_block('simulink/Sinks/Scope', [mdl '/ScopeTorque'], ...
    'Position', GP(13,4,90,80));
add_block('simulink/Sinks/To Workspace', [mdl '/TW_thd'], ...
    'Position', GP(1,0,110,36), 'VariableName', 'th_d_log', 'SaveFormat', 'Array');
add_block('simulink/Sinks/To Workspace', [mdl '/TW_th'], ...
    'Position', GP(17,3,110,36), 'VariableName', 'th_log', 'SaveFormat', 'Array');
add_block('simulink/Sinks/To Workspace', [mdl '/TW_tau'], ...
    'Position', GP(17,4,110,36), 'VariableName', 'tau_log', 'SaveFormat', 'Array');
add_block('simulink/Sinks/To Workspace', [mdl '/TW_i'], ...
    'Position', GP(14,2,110,36), 'VariableName', 'i_log', 'SaveFormat', 'Array');
add_block('simulink/Sinks/To Workspace', [mdl '/TW_v'], ...
    'Position', GP(15,1,110,36), 'VariableName', 'v_log', 'SaveFormat', 'Array');

%% 2. Lines -----------------------------------------------------------------------
L = { % {from, to}
    'Profile/1',   'Demux/1';
    'Demux/1',     'ErrSum/1';
    'Demux/1',     'MuxAngle/1';
    'Demux/1',     'TW_thd/1';
    'Demux/2',     'VelErrSum/1';
    'Demux/2',     'ViscFF/1';
    'Demux/2',     'CoulNorm/1';
    'Demux/3',     'InertFF/1';
    'TH/1',        'ErrSum/2';
    'TH/1',        'CosTh/1';
    'TH/1',        'MuxAngle/2';
    'TH/1',        'TW_th/1';
    'W/1',         'VelErrSum/2';
    'W/1',         'ViscPlant/1';
    'W/1',         'CoulNormP/1';
    'W/1',         'EMF/1';
    'W/1',         'TH/1';
    'ErrSum/1',    'Kp/1';
    'ErrSum/1',    'E_pos/1';
    'ErrSum/1',    'E_neg/1';
    'ErrSum/1',    'IntGate/3';
    'Zero/1',      'E_pos/2';
    'Zero/1',      'E_neg/2';
    'Kp/1',        'PIDSum/1';
    'IntGate/1',   'Ki/1';
    'Ki/1',        'IntE/1';
    'IntE/1',      'PIDSum/2';
    'VelErrSum/1', 'Dfilt/1';
    'Dfilt/1',     'Kd/1';
    'Kd/1',        'PIDSum/3';
    'PIDSum/1',    'OutTauSum/1';
    'CosTh/1',     'GravFF/1';
    'GravFF/1',    'FFSum/1';
    'GravFF/1',    'PlantSum/2';
    'InertFF/1',   'FFSum/2';
    'ViscFF/1',    'FFSum/3';
    'CoulNorm/1',  'TanhWd/1';
    'TanhWd/1',    'CoulFF/1';
    'CoulFF/1',    'FFSum/4';
    'FFSum/1',     'OutTauSum/2';
    'OutTauSum/1', 'ToMotor/1';
    'ToMotor/1',   'GT_hi/1';
    'ToMotor/1',   'LT_lo/1';
    'ToMotor/1',   'CurLim/1';
    'Tpeak_pos/1', 'GT_hi/2';
    'Tpeak_pos/1', 'MuxTau/2';
    'Tpeak_neg/1', 'LT_lo/2';
    'Tpeak_neg/1', 'MuxTau/3';
    'GT_hi/1',     'AND_hi/1';
    'E_pos/1',     'AND_hi/2';
    'LT_lo/1',     'AND_lo/1';
    'E_neg/1',     'AND_lo/2';
    'AND_hi/1',    'OR_fr/1';
    'AND_lo/1',    'OR_fr/2';
    'OR_fr/1',     'IntGate/2';
    'Zero2/1',     'IntGate/1';
    'CurLim/1',    'Driver/1';
    'Driver/1',    'ToOutput/1';
    'Driver/1',    'ToCurrent/1';
    'Driver/1',    'MuxTau/1';
    'Driver/1',    'TW_tau/1';
    'ToOutput/1',  'PlantSum/1';
    'ViscPlant/1', 'PlantSum/3';
    'CoulNormP/1', 'TanhW/1';
    'TanhW/1',     'CoulPlant/1';
    'CoulPlant/1', 'PlantSum/4';
    'PlantSum/1',  'InvJ/1';
    'InvJ/1',      'W/1';
    'ToCurrent/1', 'Rdrop/1';
    'ToCurrent/1', 'TW_i/1';
    'Rdrop/1',     'VoltSum/1';
    'EMF/1',       'VoltSum/2';
    'VoltSum/1',   'TW_v/1';
    'MuxAngle/1',  'ScopeAngle/1';
    'MuxTau/1',    'ScopeTorque/1';
    };
for k = 1:size(L,1)
    add_line(mdl, L{k,1}, L{k,2});
end

%% 3. Solver: fixed-step RK4 @ 1 kHz (matches the .m sim) ---------------------------
set_param(mdl, 'Solver', 'ode4', 'FixedStep', '0.001', ...
    'StopTime', NT(P.prof.T_end));
save_system(mdl);
open_system(mdl);

fprintf('\nBuilt %s.slx (%d blocks, %d lines).\n', mdl, ...
    numel(find_system(mdl, 'Type', 'block')), size(L,1));
fprintf('Profile source "gate_prof" is in the base workspace (%d x %d).\n', ...
    size(gate_prof,1), size(gate_prof,2));
fprintf(['NEXT: press Run, then open ScopeAngle (should match Figure 1 of the\n' ...
    '.m sim: overshoot < 2 deg, steady error < 0.3 deg, peak torque ~1.2 N m).\n']);

%==========================================================================
% LOCAL FUNCTION (mirror of the .m sim profile - same equations)
%==========================================================================
function [th_d, w_d, a_d] = profile_at(t, P)
    if t < P.prof.t0_open
        th_d = 0; w_d = 0; a_d = 0;
    elseif t < P.prof.t1_open
        [p, v, a] = trap((t - P.prof.t0_open)/P.prof.T_move, P);
        th_d = p; w_d = v; a_d = a;
    elseif t < P.prof.t0_close
        th_d = P.prof.move; w_d = 0; a_d = 0;
    elseif t < P.prof.t1_close
        [p, v, a] = trap((t - P.prof.t0_close)/P.prof.T_move, P);
        th_d = P.prof.move - p; w_d = -v; a_d = -a;
    else
        th_d = 0; w_d = 0; a_d = 0;
    end
end

function [p, v, a] = trap(s, P)
    D = P.prof.move; T = P.prof.T_move; ta = P.prof.T_acc;
    vv = P.prof.v_pk; aa = P.prof.a_pk;
    tt = s * T;
    if tt <= 0
        p = 0; v = 0; a = 0;
    elseif tt < ta
        p = 0.5*aa*tt*tt; v = aa*tt; a = aa;
    elseif tt < T - ta
        p = 0.5*aa*ta*ta + vv*(tt-ta); v = vv; a = 0;
    elseif tt < T
        td = T - tt;
        p = D - 0.5*aa*td*td; v = vv - aa*(tt-(T-ta)); a = -aa;
    else
        p = D; v = 0; a = 0;
    end
end
