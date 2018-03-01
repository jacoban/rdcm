function [list] = findNeighbours(G, v)
    list = [];
    
    for i = v:length(G)
        if G(i,v) == 1
            list = [list i];  
        end
    end
    for j = 1:v
        if G(v,j) == 1
            list = [list j];
        end
    end
end
