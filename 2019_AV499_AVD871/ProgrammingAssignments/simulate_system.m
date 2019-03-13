function reward = simulate_system(action)
if action == 1
    reward = 10 * rand(1);
elseif action == 2
    reward = exprnd(5);
elseif action == 3
    reward = exprnd(2.5);
end
        