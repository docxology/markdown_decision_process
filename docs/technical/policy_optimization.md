# Policy optimization

`PolicyOptimizer` exposes two kinds of operations over Markdown structure. `value_iteration()` computes state values from the supplied graph, normalized outgoing weights, and discounted state rewards. `policy_improvement()` derives a policy from those values. `q_learning(episodes, max_steps)` updates state-transition values using sampled transitions. `set_reward_function(fn)` sets the graph reward callable.

For editing a complete document, `optimize(document, output_path=None)` evaluates candidate structural changes using its internal readability, information-density, and structure scores. It only accepts a candidate when its score exceeds the current one. The return value is a dictionary containing the resulting Markdown and reward history. `transform(path)` offers a file-to-text editing interface. A larger internal score describes the scoring function’s preference for that edit. Evaluating utility to readers requires separate observations.

See the [PolicyOptimizer API](../api/policy_optimizer.md) for the available methods and [manuscript verification](../manuscript-build.md) for the evaluation boundary.
