% Parameters and variables for the system
horizon = 1000;
action_space = [1,2,3];
Qt = 1 * ones(1, length(action_space));
Nt = zeros(1, length(action_space));
epsilon = 0.1;

optimal_value = 5; % please note that this is not known to the agent
regret = zeros(1, horizon);
mean_rewards = [5, 5, 2.5];
for t = 1:horizon
    if rand < epsilon
        action = randi(length(action_space));
        % action = action_space(action);
    else
        [~, action] = max(Qt);
        % action = action_space(action);
    end
    reward = simulate_system(action);
    % update the Qt estimate and the Nt count
    Nt(action) = Nt(action) + 1;
    Qt(action) = ((Nt(action) - 1) * Qt(action) + reward)/ Nt(action);
    if t == 1
        regret(1) = optimal_value - mean_rewards(action);
    else
        regret(t) = regret(t - 1) + optimal_value - mean_rewards(action);
    end
end
plot(1:horizon, regret);
        
    