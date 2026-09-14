function P = gate_params()
% GATE_PARAMS  Every number for the Iron-Watch gate drive, in ONE place.
%
%   Used by:  gate_sim.m            (plain MATLAB / Octave simulation)
%             build_gate_simulink.m (builds the Simulink model)
%
%   Simplified model: the arm is treated as a pure inertia + viscous
%   friction load. No gravity term, no Coulomb friction, no worst-case
%   plant. Edit values here only.

%% 1. Gear train  (from the SolidWorks BOM, 3 stages)
P.i1 = 68/17;                 % stage 1: pinion 17T -> gear 68T  = 4.000
P.i2 = 70/16;                 % stage 2: pinion 16T -> gear 70T  = 4.375
P.i3 = 64/16;                 % stage 3: pinion 16T -> arm gear 64T = 4.000
P.N  = P.i1*P.i2*P.i3;        % total ratio = 70 : 1
P.eta = 0.96^3;               % 3 meshes @ 96 % each  = 0.885

%% 2. Inertia of the gears, reflected to the OUTPUT (arm) shaft
rho    = 7850;                          % kg/m^3 steel
pitchD = [51 204  64 280  80 320]/1000; % m  [P1 G1 P2 G2 P3 G3]
bore   = [28  20  20  30  30  90]/1000; % m
face   = [25  25  32  32  40  40]/1000; % m
Ro = pitchD/2;  Ri = bore/2;
mass  = rho*pi.*(Ro.^2 - Ri.^2).*face;
gearJ = 0.5*mass.*(Ro.^2 + Ri.^2);      % hollow disc, kg*m^2
speedRatio = [P.N, P.N/P.i1, P.N/P.i1, P.N/(P.i1*P.i2), P.N/(P.i1*P.i2), 1];
P.J_gearbox = sum(gearJ .* speedRatio.^2);   % ~13.7 kg*m^2 at the arm shaft

%% 3. Boom arm
P.m_arm = 13.5;                         % kg
P.L_arm = 1.0;                          % m
P.J_arm = (1/3)*P.m_arm*P.L_arm^2;      % slender rod about pivot = 4.5 kg*m^2

%% 4. Motor  (24 V 500 W brushed DC, MY1020 class)
P.motor.V      = 24;                    % V supply
P.motor.n_rated= 2500;                  % rpm
P.motor.w_rated= P.motor.n_rated*2*pi/60;
P.motor.I_rated= 27;                    % A
P.motor.R      = 0.15;                  % ohm   (assumed - measure if possible)
P.motor.L      = 0.5e-3;                % H     (assumed)
P.motor.Kt     = (P.motor.V - P.motor.I_rated*P.motor.R)/P.motor.w_rated; % N*m/A
P.motor.Ke     = P.motor.Kt;            % V*s/rad
P.motor.J_rot  = 6e-4;                  % kg*m^2
P.motor.I_max  = 30;                    % A, H-bridge current limit (BTS7960)
P.motor.T_rated= 500/P.motor.w_rated;   % ~1.91 N*m

%% 5. Total inertia seen at the arm shaft
P.J_eff = P.J_arm + P.J_gearbox + P.motor.J_rot*P.N^2;   % ~21.1 kg*m^2
P.b_fric = 1.2;                         % N*m*s/rad viscous friction (assumed)

%% 6. Motion profile: trapezoidal, 0 deg (closed) -> 90 deg (open)
P.theta_target = pi/2;                  % rad
P.T_acc  = 0.6;                         % s accelerate / decelerate
P.T_move = 2.5;                         % s total move
P.v_pk   = P.theta_target/(P.T_move - P.T_acc);   % rad/s cruise speed
P.a_pk   = P.v_pk/P.T_acc;              % rad/s^2
P.T_sim  = 6;                           % s simulation length

%% 7. PID gains  (2nd-order pole placement: wn, zeta)
wn   = 5;                               % rad/s closed-loop bandwidth
zeta = 0.9;                             % damping ratio
P.Kp = P.J_eff*wn^2;                    % ~528 N*m/rad
P.Kd = 2*zeta*wn*P.J_eff;               % ~190 N*m*s/rad
P.Ki = P.Kp*wn/10;                      % ~264 N*m/(rad*s)
P.I_clamp = 300;                        % N*m integral term clamp (anti-windup)

%% 8. Reference profile as a function handle:  [theta_ref, omega_ref] = P.ref(t)
P.ref = @(t) trap_ref(t, P.T_acc, P.T_move, P.v_pk, P.a_pk, P.theta_target);
end

%% ---- trapezoidal reference (local function) -----------------------------
function [th, w] = trap_ref(t, ta, Tm, vp, ap, D)
if t <= 0
    th = 0;                          w = 0;
elseif t < ta                        % accelerate
    th = 0.5*ap*t^2;                 w = ap*t;
elseif t < Tm - ta                   % cruise
    th = 0.5*ap*ta^2 + vp*(t-ta);    w = vp;
elseif t < Tm                        % decelerate
    td = Tm - t;
    th = D - 0.5*ap*td^2;            w = vp - ap*(t-(Tm-ta));
else                                 % hold at 90 deg
    th = D;                          w = 0;
end
end
