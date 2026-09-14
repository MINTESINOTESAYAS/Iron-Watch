function [th, w] = trap_ref(t, P)
    ta = P.T_acc; Tm = P.T_move; vp = P.v_pk; ap = P.a_pk; D = P.theta_target;
    if t <= 0
        th = 0; w = 0;
    elseif t < ta
        th = 0.5*ap*t^2; w = ap*t;
    elseif t < Tm - ta
        th = 0.5*ap*ta^2 + vp*(t-ta); w = vp;
    elseif t < Tm
        td = Tm - t;
        th = D - 0.5*ap*td^2; w = vp - ap*(t-(Tm-ta));
    else
        th = D; w = 0;
    end
end
