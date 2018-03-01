function [m_2] = generateOutput(C_beta, V_beta, V)
    m_2 = [];
    for i = 1:length(V)
        if ismember(V(i),V_beta)
            for k = 1:length(V_beta)
                if V(i) == V_beta(k)
                    m_2 = [m_2 C_beta(k)];
                end
            end
        else
            m_2 = [m_2 0];
        end
    end
end
