function P = gate_params()
% GATE_PARAMS  Single source of truth for the gate-gearbox project.
%
%   P = gate_params() returns struct P with every parameter used by:
%       gate_gearbox_pid_sim.m   (main simulation, no toolboxes)
%       build_gate_simulink.m    (auto-builds the Simulink twin)
%
%   Array/angle conventions:
%       theta = 0 rad      CLOSED (arm horizontal, worst-case gravity torque)
%       theta = +pi/2 rad  OPEN   (arm vertical, zero gravity torque)
%
%   Parameter provenance flags (see comments):
%       [GIVEN]  measured/supplied by the designer (SolidWorks / scale / tape)
%       [DS]     motor nameplate/datasheet value
%       [EST]    engineering estimate - flagged wherever used; replacing an
%                [EST] value with a measured one only requires editing it here.
%
%   No toolboxes required. MATLAB R2016b+ or Octave 4.4+.

%% ---------------------------------------------------------------- 0. Units
P.g         = 9.81;     % gravity, m/s^2
P.rho_steel = 7850;     % gear steel density, kg/m^3

%% ------------------------------------------------- 1. Gear train [GIVEN]
% name | stage | teeth | module | pitch_dia | OD | root_dia | bore | face (mm)
G = { 'P1', 1, 17, 3,  51,  57,  43.5,  28, 25 ; ...
      'G1', 1, 68, 3, 204, 210, 196.5,  20, 25 ; ...
      'P2', 2, 16, 4,  64,  72,  54.0,  20, 32 ; ...
      'G2', 2, 70, 4, 280, 288, 270.0,  30, 32 ; ...
      'P3', 3, 16, 5,  80,  90,  67.5,  30, 40 ; ...
      'G3', 3, 64, 5, 320, 330, 307.5,  90, 40 };

for k = 1:size(G,1)
    P.gear(k).name   = G{k,1};
    P.gear(k).stage  = G{k,2};
    P.gear(k).teeth  = G{k,3};
    P.gear(k).module = G{k,4};
    P.gear(k).pitch  = G{k,5} / 1000;   % m
    P.gear(k).od     = G{k,6} / 1000;   % m
    P.gear(k).root   = G{k,7} / 1000;   % m
    P.gear(k).bore   = G{k,8} / 1000;   % m
    P.gear(k).face   = G{k,9} / 1000;   % m
    % Hollow-cylinder inertia about the gear axis, outer radius = PITCH
    % radius (standard reference: addendum/dedendum tooth mass ~cancels).
    Ro = P.gear(k).pitch / 2;
    Ri = P.gear(k).bore  / 2;
    w  = P.gear(k).face;
    P.gear(k).mass = P.rho_steel * pi * (Ro^2 - Ri^2) * w;
    P.gear(k).J    = 0.5 * P.gear(k).mass * (Ro^2 + Ri^2);
end

% Stage ratios and mesh centre distances (verify against SolidWorks sketch)
P.i1 = 68/17;               % 4.000
P.i2 = 70/16;               % 4.375
P.i3 = 64/16;               % 4.000
P.N  = P.i1 * P.i2 * P.i3;  % 70.000 total motor->arm reduction
P.cd_mm = [3*(17+68)/2, 4*(16+70)/2, 5*(16+64)/2];  % [127.5 172 200]

% Mesh efficiency [EST]: 0.96 per spur mesh (greased steel, this size/speed)
P.eta_mesh = 0.96;
P.eta      = P.eta_mesh^3;  % 0.8847 motor -> arm

%% ------------------------------------------------------- 2. Arm [GIVEN]
P.m_arm = 13.5;     % kg, arm + its shaft (weighed together)
P.L_arm = 1.0;      % m, shaft centre -> tip
% Centre of mass [EST-until-measured]: uniform rod => L/2. The shaft sits ON
% the pivot axis so it adds mass but ~zero gravity moment; if you can, weigh
% the arm alone and balance it on a knife edge to measure Lc exactly.
P.Lc    = 0.5;      % m, pivot -> centre of mass
P.J_arm = (1/3) * P.m_arm * P.L_arm^2;   % rod about one end
P.T_grav_max = P.m_arm * P.g * P.Lc;     % worst case, arm horizontal

%% ---------------------- 3. Reflected inertia (all shafts -> output shaft)
J = @(nm) P.gear(strcmp({P.gear.name}, nm)).J;   % lookup helper
P.J_shaftA = J('G1') + J('P2');     % spins (i2*i3) = 17.5x output speed
P.J_shaftB = J('G2') + J('P3');     % spins  i3     = 4x   output speed
P.J_G3     = J('G3');               % on the output shaft
P.J_P1     = J('P1');               % on the motor shaft (below)

%% -------------------------------------- 4. Motor (primary): 24 V 500 W DC
% Brushed DC, MY1020 class (e-bike/scooter standard frame). Chosen because it
% is the smallest widely stocked 24 V motor whose CONTINUOUS rating covers the
% worst-case holding torque (1.07 N m, see report) with margin. [DS]/[EST] mix.
P.motor.name    = '24V 500W brushed DC (MY1020 class)';
P.motor.V_sup   = 24;       % V [DS]
P.motor.P_rated = 500;      % W [DS]
P.motor.n_rated = 2500;     % rpm [DS]
P.motor.w_rated = P.motor.n_rated * 2*pi/60;
P.motor.T_rated = P.motor.P_rated / P.motor.w_rated;  % 1.910 N m
P.motor.I_rated = 27.4;     % A [DS typical, Unite/MY1020]
P.motor.R       = 0.15;     % ohm [EST - measure: locked-rotor V/I at low V]
P.motor.L       = 0.35e-3;  % H   [EST - LCR meter across terminals]
% Back-EMF/torque constant from the rated operating point (SI: Ke = Kt)
P.motor.Ke = (P.motor.V_sup - P.motor.I_rated*P.motor.R) / P.motor.w_rated;
P.motor.Kt = P.motor.Ke;    % N m/A
P.motor.J_rotor = 0.6e-3;   % kg m^2 [EST - dominates nothing; see report]
% Driver: BTS7960-class H-bridge, 43 A hardware max -> 40 A configured limit
P.motor.I_peak   = 40;                    % A, current limit
P.motor.T_peak_m = P.motor.Kt * P.motor.I_peak;
P.motor.T_hold_m = P.T_grav_max / (P.N * P.eta);  % motor torque to hold arm

% --- Alternative (drop-in, uncomment to use): 24 V 500 W BLDC, 3000 rpm ---
% Same averaged model (FOC current loop behaves like the DC loop below).
% P.motor.name='24V 500W BLDC (D5BLD500 class)+BLD-750 driver';
% P.motor.n_rated=3000; P.motor.w_rated=P.motor.n_rated*2*pi/60;
% P.motor.T_rated=500/P.motor.w_rated; P.motor.I_rated=26.0;
% P.motor.R=0.09; P.motor.L=0.25e-3;
% P.motor.Ke=(24-P.motor.I_rated*P.motor.R)/P.motor.w_rated; P.motor.Kt=P.motor.Ke;
% P.motor.J_rotor=0.4e-3; P.motor.I_peak=40;
% P.motor.T_peak_m=P.motor.Kt*P.motor.I_peak;
% P.motor.T_hold_m=P.T_grav_max/(P.N*P.eta);

P.J_mshaft = P.J_P1 + P.motor.J_rotor;    % spins N = 70x output speed
P.J_eff = P.J_arm + P.J_G3 ...
        + P.J_shaftB * P.i3^2 ...
        + P.J_shaftA * (P.i2*P.i3)^2 ...
        + P.J_mshaft * P.N^2;             % ~21.1 kg m^2 @ output

%% ------------------------------------ 5. Friction model [EST both terms]
% Output-side equivalent incl. 3 meshes + bearings + seals. Measure by
% back-driving the arm with a spring scale, or identify from a coast-down test.
P.fric.b  = 1.5;    % N m s/rad, viscous
P.fric.tc = 2.5;    % N m, Coulomb (smoothed by tanh in code)

%% ------------------------------------ 6. Trapezoidal motion profile [GIVEN]
P.prof.move   = pi/2;   % rad, 90 deg
P.prof.T_move = 6.0;    % s per move
P.prof.T_acc  = 1.5;    % s accel = decel (symmetric trapezoid)
P.prof.v_pk   = P.prof.move / (P.prof.T_move - P.prof.T_acc);
P.prof.a_pk   = P.prof.v_pk / P.prof.T_acc;
% Full-cycle timeline: dwell | OPEN | dwell | CLOSE | dwell
P.prof.t0_open  = 1.0;
P.prof.t1_open  = P.prof.t0_open + P.prof.T_move;
P.prof.t0_close = 9.0;
P.prof.t1_close = P.prof.t0_close + P.prof.T_move;
P.prof.T_end    = 16.0;

%% ----------------------- 7. Controller (position PID + feedforward, 1 kHz)
% 3rd-order pole placement on the rigid plant 1/(J_eff s^2):
%   (s^2 + 2*z*wn*s + wn^2)(s + p3), p3 = wn/3  => critically damped, no overshoot
P.ctrl.wn   = 8.0;
P.ctrl.zeta = 1.0;
P.ctrl.p3   = P.ctrl.wn/3;
P.ctrl.Kp = P.J_eff * (P.ctrl.wn^2 + 2*P.ctrl.zeta*P.ctrl.wn*P.ctrl.p3);
P.ctrl.Kd = P.J_eff * (2*P.ctrl.zeta*P.ctrl.wn + P.ctrl.p3);
P.ctrl.Ki = P.J_eff * (P.ctrl.wn^2 * P.ctrl.p3);
P.ctrl.lam_d   = 2*pi*30;   % D-term (velocity-error) filter, rad/s
P.ctrl.tau_drv = 4e-3;      % s, driver current-loop lag (1st order)
P.ctrl.int_max = 25;        % N m @ output, integrator authority cap

%% ------------------------------------------------------- 8. Solver / test
P.sim.dt = 1e-3;            % s, fixed step (RK4), = controller sample time
% Worst-case plant used for the robustness run (controller stays nominal):
% +15% arm mass, +10% CoM, +20% inertia, 2x friction.
P.plant_worst = struct('m', 15.5, 'Lc', 0.55, 'J', P.J_eff*1.2, ...
                       'b', P.fric.b*2, 'tc', P.fric.tc*2);
end
