%% BUILD_GATE_SIMULINK  Builds gate_pid.slx programmatically (simplified)
%
%   RUN in MATLAB (Simulink required):   >> build_gate_simulink
%
%   Block diagram, left to right:
%     REFERENCE -> PID CONTROLLER -> MOTOR (electrical) -> GEARBOX + ARM
%   Plant is inertia + viscous friction only (no gravity term).
%
%   Blocks : 22    Lines : 30    Solver : ode4 fixed step 1 ms, 6 s
%   Same equations as gate_sim.m, so the scopes should match its Figure 1.

clear; clc; close all;
P = gate_params();

%% 1. Reference table for the From Workspace block  [t theta_ref omega_ref]
dt = 1e-3;
tv = (0:dt:P.T_sim)';
ref = zeros(numel(tv), 2);
for k = 1:numel(tv)
    [ref(k,1), ref(k,2)] = P.ref(tv(k));
end
gate_ref = [tv, ref];
assignin('base', 'gate_ref', gate_ref);

%% 2. New model
mdl = 'gate_pid';
if bdIsLoaded(mdl), close_system(mdl, 0); end
new_system(mdl);
open_system(mdl);

% grid helpers -> [left top right bottom]
B  = @(c,r,w,h) [30+c*150, 60+r*90, 30+c*150+w, 60+r*90+h];
G  = @(c,r) B(c,r,110,32);
NT = @(v) num2str(v, '%.10g');

%% ---- REFERENCE ----------------------------------------------------------
add_block('simulink/Sources/From Workspace', [mdl '/Reference (trapezoid)'], ...
    'Position', B(0,2,130,40), 'VariableName', 'gate_ref');
add_block('simulink/Signal Routing/Demux', [mdl '/Split'], ...
    'Position', B(1,2,15,60), 'Outputs', '2');

%% ---- PID CONTROLLER -----------------------------------------------------
add_block('simulink/Math Operations/Sum',  [mdl '/Position error'], 'Position', G(2,1), 'Inputs', '+-');
add_block('simulink/Math Operations/Sum',  [mdl '/Speed error'],    'Position', G(2,3), 'Inputs', '+-');
add_block('simulink/Math Operations/Gain', [mdl '/Kp'], 'Position', G(3,1), 'Gain', NT(P.Kp));
add_block('simulink/Math Operations/Gain', [mdl '/Ki'], 'Position', G(3,2), 'Gain', NT(P.Ki));
add_block('simulink/Continuous/Integrator', [mdl '/Integrator (clamped)'], ...
    'Position', G(4,2), 'LimitOutput', 'on', ...
    'UpperSaturationLimit', NT(P.I_clamp), 'LowerSaturationLimit', NT(-P.I_clamp));
add_block('simulink/Math Operations/Gain', [mdl '/Kd'], 'Position', G(3,3), 'Gain', NT(P.Kd));
add_block('simulink/Math Operations/Sum',  [mdl '/P+I+D = torque cmd'], 'Position', G(5,2), 'Inputs', '+++');
add_block('simulink/Math Operations/Gain', [mdl '/Torque to current'], ...
    'Position', G(6,2), 'Gain', NT(1/(P.N*P.eta*P.motor.Kt)));
add_block('simulink/Discontinuities/Saturation', [mdl '/Current limit'], ...
    'Position', G(7,2), 'UpperLimit', NT(P.motor.I_max), 'LowerLimit', NT(-P.motor.I_max));

%% ---- MOTOR (electrical:  L di/dt = V - R i - Ke N w) --------------------
add_block('simulink/Math Operations/Gain', [mdl '/R x i_cmd'], 'Position', G(8,2), 'Gain', NT(P.motor.R));
add_block('simulink/Math Operations/Gain', [mdl '/Back-EMF feedforward'], 'Position', G(8,4), 'Gain', NT(P.motor.Ke*P.N));
add_block('simulink/Math Operations/Sum',  [mdl '/Voltage cmd'], 'Position', G(9,2), 'Inputs', '++');
add_block('simulink/Discontinuities/Saturation', [mdl '/Supply limit'], ...
    'Position', G(10,2), 'UpperLimit', NT(P.motor.V), 'LowerLimit', NT(-P.motor.V));
add_block('simulink/Math Operations/Gain', [mdl '/R x i'], 'Position', G(11,1), 'Gain', NT(P.motor.R));
add_block('simulink/Math Operations/Gain', [mdl '/Back-EMF'], 'Position', G(11,4), 'Gain', NT(P.motor.Ke*P.N));
add_block('simulink/Math Operations/Sum',  [mdl '/V - Ri - EMF'], 'Position', G(12,2), 'Inputs', '+--');
add_block('simulink/Math Operations/Gain', [mdl '/1 over L'], 'Position', G(13,2), 'Gain', NT(1/P.motor.L));
add_block('simulink/Continuous/Integrator', [mdl '/Motor current i'], 'Position', G(14,2));

%% ---- GEARBOX + ARM (mechanical:  J dw/dt = N eta Kt i - b w) ------------
add_block('simulink/Math Operations/Gain', [mdl '/Gearbox torque N eta Kt'], ...
    'Position', G(15,2), 'Gain', NT(P.N*P.eta*P.motor.Kt));
add_block('simulink/Math Operations/Gain', [mdl '/Friction b'], 'Position', G(15,4), 'Gain', NT(P.b_fric));
add_block('simulink/Math Operations/Sum',  [mdl '/Net torque'], 'Position', G(16,2), 'Inputs', '+-');
add_block('simulink/Math Operations/Gain', [mdl '/1 over J_eff'], 'Position', G(17,2), 'Gain', NT(1/P.J_eff));
add_block('simulink/Continuous/Integrator', [mdl '/omega'], 'Position', G(18,2));
add_block('simulink/Continuous/Integrator', [mdl '/theta'], 'Position', G(19,2));

%% ---- SCOPES -------------------------------------------------------------
add_block('simulink/Math Operations/Gain', [mdl '/rad2deg ref'],   'Position', G(19,0), 'Gain', '180/pi');
add_block('simulink/Math Operations/Gain', [mdl '/rad2deg theta'], 'Position', G(20,1), 'Gain', '180/pi');
add_block('simulink/Signal Routing/Mux', [mdl '/Mux'], 'Position', B(21,0,15,60), 'Inputs', '2');
add_block('simulink/Sinks/Scope', [mdl '/Angle ref vs actual [deg]'], 'Position', B(22,0,80,50));
add_block('simulink/Sinks/Scope', [mdl '/Motor current [A]'],        'Position', B(15,0,80,50));

%% ---- WIRING ---------------------------------------------------------------
L = {
    'Reference (trapezoid)/1',  'Split/1';
    'Split/1',                  'Position error/1';
    'Split/1',                  'rad2deg ref/1';
    'Split/2',                  'Speed error/1';
    'theta/1',                  'Position error/2';
    'theta/1',                  'rad2deg theta/1';
    'omega/1',                  'Speed error/2';
    'omega/1',                  'Back-EMF feedforward/1';
    'omega/1',                  'Back-EMF/1';
    'omega/1',                  'Friction b/1';
    'Position error/1',         'Kp/1';
    'Position error/1',         'Ki/1';
    'Ki/1',                     'Integrator (clamped)/1';
    'Speed error/1',            'Kd/1';
    'Kp/1',                     'P+I+D = torque cmd/1';
    'Integrator (clamped)/1',   'P+I+D = torque cmd/2';
    'Kd/1',                     'P+I+D = torque cmd/3';
    'P+I+D = torque cmd/1',     'Torque to current/1';
    'Torque to current/1',      'Current limit/1';
    'Current limit/1',          'R x i_cmd/1';
    'R x i_cmd/1',              'Voltage cmd/1';
    'Back-EMF feedforward/1',   'Voltage cmd/2';
    'Voltage cmd/1',            'Supply limit/1';
    'Supply limit/1',           'V - Ri - EMF/1';
    'R x i/1',                  'V - Ri - EMF/2';
    'Back-EMF/1',               'V - Ri - EMF/3';
    'V - Ri - EMF/1',           '1 over L/1';
    '1 over L/1',               'Motor current i/1';
    'Motor current i/1',        'R x i/1';
    'Motor current i/1',        'Gearbox torque N eta Kt/1';
    'Motor current i/1',        'Motor current [A]/1';
    'Gearbox torque N eta Kt/1','Net torque/1';
    'Friction b/1',             'Net torque/2';
    'Net torque/1',             '1 over J_eff/1';
    '1 over J_eff/1',           'omega/1';
    'omega/1',                  'theta/1';
    'rad2deg theta/1',          'Mux/1';
    'rad2deg ref/1',            'Mux/2';
    'Mux/1',                    'Angle ref vs actual [deg]/1';
    };
for k = 1:size(L,1)
    add_line(mdl, L{k,1}, L{k,2}, 'autorouting', 'on');
end

%% ---- Section labels (cosmetic, safe to fail) ------------------------------
try
    hdr = @(txt, pos) set(Simulink.Annotation([mdl '/' txt]), 'Position', pos, ...
        'FontSize', 13, 'ForegroundColor', 'blue');
    hdr('1. REFERENCE',            [40,   20]);
    hdr('2. PID CONTROLLER',       [330,  20]);
    hdr('3. DC MOTOR (electrical)',[1230, 20]);
    hdr('4. GEARBOX 70:1 + ARM',   [2280, 20]);
catch
end

%% ---- Solver + save ----------------------------------------------------------
set_param(mdl, 'Solver', 'ode4', 'FixedStep', NT(dt), 'StopTime', NT(P.T_sim));
save_system(mdl);
fprintf('Built %s.slx  (%d blocks, %d lines). Press Run, then open the scopes.\n', ...
    mdl, numel(find_system(mdl, 'Type', 'block')), size(L,1));
