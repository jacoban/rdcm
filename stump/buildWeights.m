function [w] = buildWeights(G,R,C,w_p)
    
    for i = 1:length(G)
        for j = 1:i
            if G(C(i),C(j)) == 1 
                %Ipotizzo che: ||C(i) - C(j)|| = w_p(i,j)
                w(C(i),C(j)) = norm(w_p(i,j)) + R;
            else
                w(C(i),C(j)) = inf;
            end
        end
    end
    
    w = w + w' - diag(diag(w));

end
