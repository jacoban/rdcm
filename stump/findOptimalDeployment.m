function [m_opt, T_opt] = findOptimalDeployment(vMin, tMin, M_2, Te, x)
    m_opt = M_2(tMin, (vMin-1) * x + 1 : vMin * x);
    T_opt = Te((tMin-1) * x + 1 : tMin * x, : );
end
