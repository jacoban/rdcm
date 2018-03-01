function [costMin, vMin, tMin] = findMinCosts(costs)
     [vec, indeces] = min(costs);
     [costMin, index] = min(vec);
     vMin = index;
     tMin = indeces(index);
end
