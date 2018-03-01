% solves a single instance with the stump algorithm

function [costMin, m_opt, D_opt] = solveInstance(root_folder, logs_folder, instance)
best_cost = Inf;

    try
        D = importdata(strcat(root_folder, [instance '_D.txt']),'\t');
        G = importdata(strcat(root_folder, [instance '_G.txt']),'\t');
        m_1 = importdata(strcat(root_folder, [instance '_m_1.txt']),'\t');
        V_beta = importdata(strcat(root_folder, [instance '_V_beta.txt']),'\t');
        w_p = importdata(strcat(root_folder, [instance '_w_p.txt']),'\t');
        C = 1:size(w_p,1);
        V = 1:size(m_1,2);
        mu=0.001;
        R=1;
        C_beta = m_1(V_beta);
    catch e
        disp(getReport(e,'basic'))
        return
    end
        
    fid = fopen([logs_folder filesep instance '.log'], 'w');
    fprintf(fid,'---\n');
    fclose(fid);
    
    startTime = tic;
    
    Te = modifyTopology(tril(D));
    Te = [D; Te];
    
    [y, x] = size(Te);
    c = y/x;
    
    w = buildWeights(G,R,C,w_p);
    
    Q = [];
    M_2 = [];
    costs = [];
    m_opt = [];
    D_opt = [];
    
    for i = 1:c % for each tree topology
        
        T = generateTree(Te, x, i);        
        Q_2 = []; 
        M_2_fin = [];
        
        for j = 1:length(V) % for each agent and robot
            
            q = [];
            q_2 = [];
            m_2 = [];
            m_2_fin = [];
            
            V_v = V(j); % 1 2 3 ... 20
            V_a = V_v;            
            q = initializeRedeployment(m_1, C_beta, w_p, C, V, V_beta);
            q_2 = redeployment(q, w, T, mu, V_v, V_a, C);
            Q_2 = [Q_2 q_2];            
            m_2 = generateOutput(C_beta, V_beta, V);         
            m_2_fin = buildLocations(m_2, q_2, w, T, mu, V_v, V_a, C);
            M_2_fin = [M_2_fin m_2_fin];            
            %costs(i,j) = totalRedeploymentCosts(m_2_fin, q_2, w, T, mu, V_v, V_a, C);
            costs(i,j) = min(q_2(V_v,:));
            
            mgain = best_cost - costs(i,j);
            
            if(mgain>0.5) % edges are unitary
                % incumbent solution: m2_fin, of cost costs(i,j)
                curComputeTime = toc(startTime);
                fid = fopen([logs_folder filesep instance '.log'], 'a');
                fprintf(fid,'Runtime=%e\n', curComputeTime);
                fprintf(fid,'Objval=%e\n', costs(i,j));
                fprintf(fid,'MarginalGain=%e\n', mgain);
                fprintf(fid,['Allocation=[' sprintf('%d, ', m_2_fin(1:end-1) ) num2str(m_2_fin(end))  ']\n']);
                fprintf(fid,'---\n');
                fclose(fid);
                best_cost = costs(i,j);
            end
        end        
        
        Q = [Q; Q_2];        
        M_2 = [M_2; M_2_fin];        
    end
    [costMin, vMin, tMin] = findMinCosts(costs);
    
    if costMin == inf
        %fprintf('Non è stata trovata alcuna struttura che permetta di collegare i target indicati. \n');
        costMin = 1e+100;
        %m_opt = NaN(1,numel(m_1));
        m_opt = -1*ones(1,numel(m_1));
        
        curComputeTime = toc(startTime);
        fid = fopen([logs_folder filesep instance '.log'], 'a');
        fprintf(fid,'Runtime=%e\n', curComputeTime);
        fprintf(fid,'Objval=%e\n', costMin);
        fprintf(fid,'MarginaGain=%e\n', 0);
        fprintf(fid,['Allocation=[' sprintf('%d, ', m_opt(1:end-1) ) num2str(m_opt(end))  ']\n']);
        fprintf(fid,'---\n');
        fclose(fid);       
        
    else
        [m_opt, D_opt] = findOptimalDeployment(vMin, tMin, M_2, Te, x);       
    end
end