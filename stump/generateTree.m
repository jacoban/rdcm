function [T] = generateTree(Te, x, k)
    T = [];
    m = 1;
    for i = (k-1)*x+1 : k*x
        T(m,:) = Te(i,:);
        m = m+1;
    end
end
