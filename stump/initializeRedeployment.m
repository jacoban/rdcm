function [q] = initializeRedeployment (m_1, C_beta, w_p, C, V, V_beta)
    q = [];
    
    for i = 1:length(V)
        if ismember(V(i), V_beta)
            for j = 1:length(C)
                if ismember(C(j), C_beta)
                    for k = 1:length(C_beta)
                        if C(j) == C_beta(k)
                            q(V_beta(k),C(j)) = 0;
                        else
                            q(V_beta(k),C(j)) = inf;
                        end
                    end
                else
                    q(V(i),C(j)) = inf;
                end
            end
        else
            for j=1:length(C)
                q(V(i),C(j)) = w_p(m_1(V(i)), C(j));
            end
        end
    end
end
