%% BUILD_GATE_SIMULINK  Programmatically builds gate_gearbox_pid.slx
%
%   Run in MATLAB (Simulink required):   >> build_gate_simulink
%
%   Same block diagram as before, but every block now has a descriptive
%   name (no more "IntE", "DiDtSum" etc.) and the canvas is divided into
%   four labelled sections so it reads top-to-bottom like a textbook
%   block diagram: REFERENCE -> CONTROLLER -> MOTOR -> MECHANICAL PLANT.
%   Good for showing a supervisor without a live explanation.
%
%   NOTE: written and syntax-reviewed carefully but not executed against
%   real Simulink on my end. The underlying wiring is unchanged from the
%   version you already ran successfully -- this pass only renames
%   blocks and adds text annotations (wrapped in try/catch so a version
%   mismatch on the annotation API cannot break the model build).

clear; clc; close all;
P = gate_params();

%% Build the reference-signal table (same trap_ref.m used by gate_sim.m)
dt = 1e-3;
tv = (0:dt:8)';
ref = zeros(numel(tv), 2);
for k = 1:numel(tv)
    [th, w] = trap_ref(tv(k), P);
    ref(k,:) = [th, w];
end
gate_ref = [tv, ref];              % columns: [t, theta_ref, omega_ref]
assignin('base', 'gate_ref', gate_ref);

%% Fresh model
mdl = 'gate_gearbox_pid';
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end
try
    new_system(mdl);
catch ME
    error(['Could not create a Simulink model (%s).\n' ...
        'Is Simulink installed and licensed? gate_sim.m needs no Simulink.'], ME.message);
end
open_system(mdl);

% grid helper: GP(col,row) -> a [left top right bottom] box
GP = @(c,r,w,h) [30+c*160, 60+r*90, 30+c*160+w, 60+r*90+h];
G  = @(c,r) GP(c,r,120,32);
B  = @(c,r,w,h) GP(c,r,w,h);
NT = @(v) num2str(v, '%.10g');

%% ================= SECTION 1: REFERENCE ================================
add_block('simulink/Sources/From Workspace', [mdl '/Reference profile (trapezoidal)'], ...
    'Position', B(0,3,140,40), 'VariableName', 'gate_ref');
add_block('simulink/Signal Routing/Demux', [mdl '/Split angle and speed refs'], ...
    'Position', B(1,3,20,70), 'Outputs', '2');

%% ================= SECTION 2: CONTROLLER (PID + gravity feedforward) ===
add_block('simulink/Math Operations/Sum', [mdl '/Position error'], ...
    'Position', G(2,1), 'Inputs', '+-');
add_block('simulink/Math Operations/Sum', [mdl '/Speed error'], ...
    'Position', G(2,3), 'Inputs', '+-');

add_block('simulink/Math Operations/Trigonometric Function', [mdl '/cos of arm angle'], ...
    'Position', G(2,6), 'Operator', 'cos');
add_block('simulink/Math Operations/Gain', [mdl '/Gravity feedforward mgLc'], ...
    'Position', G(3,6), 'Gain', NT(P.m_arm*P.g*P.Lc));

add_block('simulink/Math Operations/Gain', [mdl '/Kp proportional gain'], ...
    'Position', G(3,1), 'Gain', NT(P.Kp));
add_block('simulink/Math Operations/Gain', [mdl '/Ki integral gain'], ...
    'Position', G(3,2), 'Gain', NT(P.Ki));
add_block('simulink/Continuous/Integrator', [mdl '/Integral of error, clamped'], ...
    'Position', G(4,2), 'InitialCondition', '0', 'LimitOutput', 'on', ...
    'UpperSaturationLimit', '300', 'LowerSaturationLimit', '-300');
    % This block's own +-300 Nm output clamp IS the anti-windup - no
    % extra logic blocks needed.
add_block('simulink/Math Operations/Gain', [mdl '/Kd derivative gain'], ...
    'Position', G(3,3), 'Gain', NT(P.Kd));
add_block('simulink/Math Operations/Sum', [mdl '/Sum P plus I plus D'], ...
    'Position', G(5,2), 'Inputs', '+++');

add_block('simulink/Math Operations/Sum', [mdl '/Total torque command'], ...
    'Position', G(6,3), 'Inputs', '++');
add_block('simulink/Math Operations/Gain', [mdl '/Torque to motor current command'], ...
    'Position', G(7,3), 'Gain', NT(1/(P.N*P.eta*P.motor.Kt)));
add_block('simulink/Discontinuities/Saturation', [mdl '/Driver current limit'], ...
    'Position', G(8,3), 'UpperLimit', NT(P.motor.I_max), ...
    'LowerLimit', NT(-P.motor.I_max));

%% ================= SECTION 3: MOTOR (electrical) ========================
add_block('simulink/Math Operations/Gain', [mdl '/icmd times R feedforward'], ...
    'Position', G(9,2), 'Gain', NT(P.motor.R));
add_block('simulink/Math Operations/Gain', [mdl '/Back-EMF feedforward'], ...
    'Position', G(9,4), 'Gain', NT(P.motor.Ke*P.N));
add_block('simulink/Math Operations/Sum', [mdl '/Voltage command'], ...
    'Position', G(10,3), 'Inputs', '++');
add_block('simulink/Discontinuities/Saturation', [mdl '/Supply voltage limit'], ...
    'Position', G(11,3), 'UpperLimit', NT(P.motor.V), ...
    'LowerLimit', NT(-P.motor.V));

add_block('simulink/Math Operations/Gain', [mdl '/Resistive drop, actual current'], ...
    'Position', G(12,2), 'Gain', NT(P.motor.R));
add_block('simulink/Math Operations/Gain', [mdl '/Back-EMF, actual speed'], ...
    'Position', G(12,4), 'Gain', NT(P.motor.Ke*P.N));
add_block('simulink/Math Operations/Sum', [mdl '/Electrical equation V-Ri-EMF'], ...
    'Position', G(13,3), 'Inputs', '+--');
add_block('simulink/Math Operations/Gain', [mdl '/Divide by inductance L'], ...
    'Position', G(14,3), 'Gain', NT(1/P.motor.L));
add_block('simulink/Continuous/Integrator', [mdl '/Motor current'], ...
    'Position', G(15,3), 'InitialCondition', '0');

%% ================= SECTION 4: MECHANICAL PLANT (gearbox + arm) =========
add_block('simulink/Math Operations/Gain', [mdl '/Output shaft torque via gearbox'], ...
    'Position', G(16,3), 'Gain', NT(P.N*P.eta*P.motor.Kt));
add_block('simulink/Math Operations/Gain', [mdl '/Viscous friction torque'], ...
    'Position', G(16,5), 'Gain', NT(P.b_fric));
add_block('simulink/Math Operations/Sum', [mdl '/Net torque, Newtons 2nd law'], ...
    'Position', G(17,3), 'Inputs', '+--');
add_block('simulink/Math Operations/Gain', [mdl '/Divide by effective inertia'], ...
    'Position', G(18,3), 'Gain', NT(1/P.J_eff));
add_block('simulink/Continuous/Integrator', [mdl '/Arm angular speed omega'], ...
    'Position', G(19,3), 'InitialCondition', '0');
add_block('simulink/Continuous/Integrator', [mdl '/Arm angle theta'], ...
    'Position', G(20,3), 'InitialCondition', '0');

%% ================= SCOPES ================================================
add_block('simulink/Math Operations/Gain', [mdl '/theta to degrees'], ...
    'Position', G(21,1), 'Gain', '180/pi');
add_block('simulink/Math Operations/Gain', [mdl '/ref to degrees'], ...
    'Position', G(21,0), 'Gain', '180/pi');
add_block('simulink/Signal Routing/Mux', [mdl '/Combine for scope'], ...
    'Position', B(22,0,20,60), 'Inputs', '2');
add_block('simulink/Sinks/Scope', [mdl '/SCOPE Angle ref vs actual deg'], ...
    'Position', B(23,0,90,60));
add_block('simulink/Sinks/Scope', [mdl '/SCOPE Motor current A'], ...
    'Position', B(16,0,90,50));

%% ================= WIRING (unchanged logic, new names) ==================
L = {
    'Reference profile (trapezoidal)/1',   'Split angle and speed refs/1';
    'Split angle and speed refs/1',        'Position error/1';
    'Split angle and speed refs/1',        'ref to degrees/1';
    'Split angle and speed refs/2',        'Speed error/1';
    'Arm angle theta/1',                   'Position error/2';
    'Arm angle theta/1',                   'cos of arm angle/1';
    'Arm angle theta/1',                   'theta to degrees/1';
    'Arm angular speed omega/1',           'Speed error/2';
    'Arm angular speed omega/1',           'Back-EMF feedforward/1';
    'Arm angular speed omega/1',           'Back-EMF, actual speed/1';
    'Arm angular speed omega/1',           'Viscous friction torque/1';
    'cos of arm angle/1',                  'Gravity feedforward mgLc/1';
    'Gravity feedforward mgLc/1',          'Total torque command/2';
    'Position error/1',                    'Kp proportional gain/1';
    'Position error/1',                    'Ki integral gain/1';
    'Kp proportional gain/1',              'Sum P plus I plus D/1';
    'Ki integral gain/1',                  'Integral of error, clamped/1';
    'Integral of error, clamped/1',        'Sum P plus I plus D/2';
    'Speed error/1',                       'Kd derivative gain/1';
    'Kd derivative gain/1',                'Sum P plus I plus D/3';
    'Sum P plus I plus D/1',               'Total torque command/1';
    'Total torque command/1',              'Torque to motor current command/1';
    'Torque to motor current command/1',   'Driver current limit/1';
    'Driver current limit/1',              'icmd times R feedforward/1';
    'Back-EMF feedforward/1',              'Voltage command/2';
    'icmd times R feedforward/1',          'Voltage command/1';
    'Voltage command/1',                   'Supply voltage limit/1';
    'Supply voltage limit/1',              'Electrical equation V-Ri-EMF/1';
    'Resistive drop, actual current/1',    'Electrical equation V-Ri-EMF/2';
    'Back-EMF, actual speed/1',            'Electrical equation V-Ri-EMF/3';
    'Electrical equation V-Ri-EMF/1',      'Divide by inductance L/1';
    'Divide by inductance L/1',            'Motor current/1';
    'Motor current/1',                     'Resistive drop, actual current/1';
    'Motor current/1',                     'Output shaft torque via gearbox/1';
    'Motor current/1',                     'SCOPE Motor current A/1';
    'Output shaft torque via gearbox/1',   'Net torque, Newtons 2nd law/1';
    'Viscous friction torque/1',           'Net torque, Newtons 2nd law/2';
    'Gravity feedforward mgLc/1',          'Net torque, Newtons 2nd law/3';
    'Net torque, Newtons 2nd law/1',       'Divide by effective inertia/1';
    'Divide by effective inertia/1',       'Arm angular speed omega/1';
    'Arm angular speed omega/1',           'Arm angle theta/1';
    'theta to degrees/1',                  'Combine for scope/1';
    'ref to degrees/1',                    'Combine for scope/2';
    'Combine for scope/1',                 'SCOPE Angle ref vs actual deg/1';
    };
for k = 1:size(L,1)
    add_line(mdl, L{k,1}, L{k,2}, 'autorouting', 'on');
end

%% ================= SECTION HEADER ANNOTATIONS ===========================
% Purely cosmetic labels for a supervisor demo. Wrapped in try/catch: if
% the Simulink.Annotation API differs slightly on your release, the model
% still builds and simulates fine without these labels.
try
    hdr = @(txt, pos) set(Simulink.Annotation([mdl '/' txt]), 'Position', pos, ...
        'FontSize', 14, 'ForegroundColor', 'blue');
    hdr('1. REFERENCE (trapezoidal 0 to 90 deg profile)', [40, 20]);
    hdr('2. CONTROLLER (PID + gravity feedforward)',      [330, 20]);
    hdr('3. MOTOR (DC electrical model)',                  [1450, 20]);
    hdr('4. MECHANICAL PLANT (gearbox 70:1 + arm)',        [2500, 20]);
    note = @(txt, pos) set(Simulink.Annotation([mdl '/' txt]), 'Position', pos, ...
        'FontSize', 9, 'ForegroundColor', [0.4 0.4 0.4]);
    note('theta=0: CLOSED (horizontal). theta=90deg: OPEN (vertical).', [40, 700]);
    note('Anti-windup = this integrator''s own output clamp (+-300).', [500, 260]);
catch ME
    fprintf('(Section headers skipped -- annotation API mismatch: %s)\n', ME.message);
    fprintf('Model still built and wired correctly, this is cosmetic only.\n');
end

%% ================= SOLVER ================================================
set_param(mdl, 'Solver', 'ode4', 'FixedStep', num2str(dt), 'StopTime', '8');
save_system(mdl);
open_system(mdl);

fprintf('\nBuilt %s.slx (%d blocks, %d lines).\n', mdl, ...
    numel(find_system(mdl, 'Type', 'block')), size(L,1));
fprintf('\n=== CHECKLIST ===\n');
fprintf('1. Run. Open "SCOPE Angle ref vs actual deg": both traces 0->90 deg,\n');
fprintf('   actual tracking reference closely (matches gate_sim.m Figure 1).\n');
fprintf('2. Open "SCOPE Motor current A": peaks ~15-20 A, stays under 30 A.\n');
fprintf('3. If a block errors on Run, double-click it and re-enter the same\n');
fprintf('   value by hand -- every other block is unaffected.\n');
