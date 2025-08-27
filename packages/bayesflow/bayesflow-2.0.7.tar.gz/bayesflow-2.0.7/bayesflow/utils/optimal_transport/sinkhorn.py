import keras

from bayesflow.types import Tensor

from .. import logging

from .euclidean import euclidean


def sinkhorn(x1: Tensor, x2: Tensor, seed: int = None, **kwargs) -> (Tensor, Tensor):
    """
    Matches elements from x2 onto x1 using the Sinkhorn-Knopp algorithm.

    Sinkhorn-Knopp is an iterative algorithm that repeatedly normalizes the cost matrix into a
    transport plan, containing assignment probabilities.
    The permutation is then sampled randomly according to the transport plan.

    :param x1: Tensor of shape (n, ...)
        Samples from the first distribution.

    :param x2: Tensor of shape (m, ...)
        Samples from the second distribution.

    :param kwargs:
        Additional keyword arguments that are passed to :py:func:`sinkhorn_plan`.

    :param seed: Random seed to use for sampling indices.
        Default: None, which means the seed will be auto-determined for non-compiled contexts.

    :return: Tensor of shape (n,)
        Assignment indices for x2.

    """
    plan = sinkhorn_plan(x1, x2, **kwargs)

    # we sample from log(plan) to receive assignments of length n, corresponding to indices of x2
    # such that x2[assignments] matches x1
    assignments = keras.random.categorical(keras.ops.log(plan), num_samples=1, seed=seed)
    assignments = keras.ops.squeeze(assignments, axis=1)

    return assignments


def sinkhorn_plan(
    x1: Tensor,
    x2: Tensor,
    regularization: float = 1.0,
    max_steps: int = None,
    rtol: float = 1e-5,
    atol: float = 1e-8,
) -> Tensor:
    """
    Computes the Sinkhorn-Knopp optimal transport plan.

    :param x1: Tensor of shape (n, ...)
        Samples from the first distribution.

    :param x2: Tensor of shape (m, ...)
        Samples from the second distribution.

    :param regularization: Regularization parameter.
        Controls the standard deviation of the Gaussian kernel.

    :param max_steps: Maximum number of iterations, or None to run until convergence.
        Default: None

    :param rtol: Relative tolerance for convergence.
        Default: 1e-5.

    :param atol: Absolute tolerance for convergence.
        Default: 1e-8.

    :return: Tensor of shape (n, m)
        The transport probabilities.
    """
    cost = euclidean(x1, x2)
    cost_scaled = -cost / regularization

    # initialize transport plan from a gaussian kernel
    # (more numerically stable version of keras.ops.exp(-cost/regularization))
    plan = keras.ops.exp(cost_scaled - keras.ops.max(cost_scaled))
    n, m = keras.ops.shape(cost)

    def contains_nans(plan):
        return keras.ops.any(keras.ops.isnan(plan))

    def is_converged(plan):
        # for convergence, the target marginals must match
        conv0 = keras.ops.all(keras.ops.isclose(keras.ops.sum(plan, axis=0), 1.0 / m, rtol=rtol, atol=atol))
        conv1 = keras.ops.all(keras.ops.isclose(keras.ops.sum(plan, axis=1), 1.0 / n, rtol=rtol, atol=atol))
        return conv0 & conv1

    def cond(_, plan):
        # break the while loop if the plan contains nans or is converged
        return ~(contains_nans(plan) | is_converged(plan))

    def body(steps, plan):
        # Sinkhorn-Knopp: repeatedly normalize the transport plan along each dimension
        plan = plan / keras.ops.sum(plan, axis=0, keepdims=True) * (1.0 / m)
        plan = plan / keras.ops.sum(plan, axis=1, keepdims=True) * (1.0 / n)

        return steps + 1, plan

    steps = 0
    steps, plan = keras.ops.while_loop(cond, body, (steps, plan), maximum_iterations=max_steps)

    def do_nothing():
        pass

    def log_steps():
        msg = "Sinkhorn-Knopp converged after {} steps."

        logging.debug(msg, max_steps)

    def warn_convergence():
        msg = "Sinkhorn-Knopp did not converge after {}."

        logging.warning(msg, max_steps)

    def warn_nans():
        msg = "Sinkhorn-Knopp produced NaNs after {} steps."
        logging.warning(msg, steps)

    keras.ops.cond(contains_nans(plan), warn_nans, do_nothing)
    keras.ops.cond(is_converged(plan), log_steps, warn_convergence)

    return plan
