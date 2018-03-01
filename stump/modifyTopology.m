function [Te] = modifyTopology(G)
    Te = [];
    for i = 2 : length(G)
        for j = 1 : (i-1)
            if G(i,j) == 1
                T = buildTopology(tril(G), i, j);
                Te = [Te; T];
            end
        end
    end
end
