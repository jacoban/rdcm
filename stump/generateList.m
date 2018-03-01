function [list] = generateList(G,n)
    list = [];
    
    for i = n:length(G)
        if G(i,n) == 1
            list = [list i];  
        end
    end
    for j = 1:n
        if G(n,j) == 1
            list = [list j];
        end
    end
    
    list = [n list];
end
