function [finalList] = refineList(list, G)
    finalList = list;
    midList = [];
    k = length(finalList);
    j=0;
    while(j < k)
        midList = generateList(G, finalList(j+1));
        
        for i = 1:length(midList)
            if ismember(midList(i), finalList) == 0
                finalList = [finalList midList(i)];
            end
        end
        
        k = length(finalList);
        j = j+1;
    end
end
