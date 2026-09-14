function P = gate_params()
% GATE_PARAMS  All the numbers for the gate project, in one place.
%   Edit values here; gate_sim.m and the Simulink model both read this.

%% Constants
P.g = 9.81;              % m/s^2
P.rho = 7850;             % kg/m^3, steel (for gear mass estimate)

%% Gear train (from SolidWorks BOM)
% columns: teeth, module(mm), pitch dia(mm), bore(mm), face width(mm)
%           P1     G1      P2     G2      P3     G3(arm)
% teeth  = [17,     68,     16,    70,     16,    64  ];
% module = [3,      3,      4,     4,      5,     5   ];
pitchD = [51,    204,     64,   280,     80,   320  ];
bore   = [28,     20,     20,    30,     30,    90  ];
face   = [25,     25,     32,    32,     40,    40  ];

for k = 1:6
    Ro = (pitchD(k)/1000)/2;
    Ri = (bore(k)/1000)/2;
    w  = face(k)/1000;
    mass = P.rho*pi*(Ro^2-Ri^2)*w;
    P.gearJ(k) = 0.5*mass*(Ro^2+Ri^2);   % solid-disk inertia at pitch dia
end
% P.gearJ = [J_P1 J_G1 J_P2 J_G2 J_P3 J_G3]

P.i1 = 68/17;                % stage 1 ratio = 4.000
P.i2 = 70/16;                % stage 2 ratio = 4.375
P.i3 = 64/16;                % stage 3 ratio = 4.000
P.N  = P.i1*P.i2*P.i3;       % total ratio = 70.00 (matches spec)

P.eta_mesh = 0.96;           % efficiency per gear mesh, assumed
P.eta = P.eta_mesh^3;        % 3 meshes total

%% Boom arm (measured)
P.m_arm = 13.5;              % kg, arm + shaft it carries
P.L_arm = 1.0;                % m, shaft centre to tip
P.Lc    = P.L_arm/2;          % m, centre of mass (uniform arm assumed)
P.J_arm = (1/3)*P.m_arm*P.L_arm^2;   % slender rod about the pivot end
P.T_grav_max = P.m_arm*P.g*P.Lc;      % worst case torque, arm horizontal

%% Reflect every gear + the arm to the OUTPUT (arm) shaft
% Shaft speeds relative to output: P1&motor spin N times faster, G1&P2
% spin N/i1 times faster, G2&P3 spin N/(i1*i2) times faster, G3+arm = 1x
Ne_A = P.N;              % P1 + motor
Ne_B = P.N/P.i1;         % G1 + P2
Ne_C = P.N/(P.i1*P.i2);  % G2 + P3
%              P1            G1            P2            G2            P3            G3
J_own   = P.gearJ;
Ne_each = [Ne_A,          Ne_B,         Ne_B,         Ne_C,         Ne_C,         1  ];
P.J_gearbox_reflected = sum(J_own .* Ne_each.^2);

%% Motor: 24V 500W brushed DC gearmotor (e.g. MY1020-class, common in
% scooters/e-bikes and widely used in DIY boom-gate/barrier projects).
% This size was picked because its CONTINUOUS torque covers the worst-case
% holding torque at the motor shaft with roughly 3x margin (see console
% report when you run gate_sim.m) -- edit freely if you have a different
% motor on hand, that is the point of keeping everything in this file.
P.motor.V      = 24;         % V, supply
P.motor.P_rated= 500;        % W
P.motor.n_rated= 2500;       % rpm
P.motor.w_rated= P.motor.n_rated*2*pi/60;
P.motor.T_rated= P.motor.P_rated/P.motor.w_rated;  % ~1.91 N*m
P.motor.I_rated= 27;         % A, approx nameplate
P.motor.R      = 0.15;       % ohm, ASSUMED -- measure with a multimeter if you have the real motor
P.motor.L      = 0.5e-3;     % H, ASSUMED
P.motor.Kt     = (P.motor.V - P.motor.I_rated*P.motor.R)/P.motor.w_rated; % N*m/A
P.motor.Ke     = P.motor.Kt; % V*s/rad (same constant, SI units)
P.motor.J_rot  = 6e-4;       % kg*m^2, rotor inertia, ASSUMED (small vs. gearbox)
P.motor.I_max  = 30;         % A, driver current limit (e.g. BTS7960 H-bridge)

P.J_eff = P.J_arm + P.J_gearbox_reflected + P.motor.J_rot*P.N^2;

%% Friction (lumped, output side) -- a single viscous term is enough for
% a first design; add Coulomb/stiction later if you measure it.
P.b_fric = 1.2;   % N*m*s/rad, ASSUMED

%% Motion profile: trapezoidal, 0 -> 90 deg
P.theta_target = pi/2;
P.T_acc  = 0.6;    % s, acceleration (and, symmetric, deceleration) time
P.T_move = 2.5;    % s, total move time
P.v_pk = P.theta_target/(P.T_move - P.T_acc);
P.a_pk = P.v_pk/P.T_acc;

%% PID gains: standard 2nd-order design (natural frequency / damping),
% the same method used in most undergrad controls courses, plus a small
% Ki for zero steady-state error.
wn = 5;        % rad/s, desired closed-loop bandwidth -- retune this
zeta = 0.9;    % damping ratio, ~critically damped
P.Kp = P.J_eff*wn^2;
P.Kd = 2*zeta*wn*P.J_eff;
P.Ki = P.Kp*wn/10;         % rule of thumb: small compared to Kp
end
