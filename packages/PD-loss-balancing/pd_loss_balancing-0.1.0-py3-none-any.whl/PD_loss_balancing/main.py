import torch

from abc import ABC, abstractmethod


class Target(ABC):
    """Abstract base class for defining target values in loss balancing.

    Subclasses must implement get_target() to specify how the target
    is computed based on two loss values.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_target(self, target_input: None | float) -> float:
        """Compute target value based on two loss values.

        Args:
            target_input: input to calculate target from

        Returns:
            Target value for loss balancing
        """
        pass


class RelativeTarget(Target):
    """Target that returns a scaled version of the second loss.

    Sets target = ratio * loss2, allowing you to specify the desired
    relationship between loss1 and loss2.
    """

    def __init__(self, ratio: float = 1):
        """Initialize relative target.

        Args:
            ratio: How much bigger loss2 should be relative to loss1.
                  ratio=1 means equal losses, ratio=2 means loss2 should be 2x loss1.
        """
        self.ratio = ratio

    def get_target(self, target_input: None | float) -> float:
        """Return ratio * target_input as the target for loss1.

        Args:
            target_input: value to be relative to (ei other loss values)

        Returns:
            Target value as ratio * target_input
        """
        return self.ratio * target_input


class ConstantTarget(Target):
    """Target that's constant"""

    def __init__(self, value: float):
        """Initialize constant trajectory target.

        Args:
            value: target value

        """
        self.target = value

    def get_target(self, target_input: None | float) -> float:
        """Return target value.

        Args:
            target_input: value to get target from, should be none

        Returns:
            Target value.
        """
        assert target_input is None

        return self.target


class LinearTrajectoryTarget(Target):
    """Target that changes linearly from an initial to final value over time.

    Useful when you want the target to evolve during training, starting
    at one value and gradually moving to another over num_steps calls.
    """

    def __init__(self, initial: float, final: float, num_steps: int):
        """Initialize linear trajectory target.

        Args:
            initial: Starting target value
            final: Target value after num_steps calls
            num_steps: Number of get_target() calls to reach final value
        """
        self.target = initial
        self.num_steps = num_steps
        self.cur_step = 0
        self.step = (final - initial) / (1.0 * num_steps)

    def get_target(self, target_input: None | float) -> float:
        """Return current target value and advance along trajectory.

        Args:
            target_input: value to get target from, should be none

        Returns:
            Current target value. Increments internally for next call.
        """
        assert target_input is None
        self.cur_step += 1
        if self.cur_step <= self.num_steps:
            self.target += self.step
        return self.target


class LossBalancer:
    """PD controller for automatically balancing two losses.

    Adjusts a mixing parameter (alpha) to keep loss1 close to a target value.
    The combined loss becomes: alpha * loss1 + (1 - alpha) * loss2.
    Uses PD control to adjust alpha based on how far loss1 is from target.
    """

    def __init__(
        self,
        target: Target,
        kp: float = 0.001,
        kd: float = 0.02,
        initial_balance: float = 0.5,
        len_errors: int = 5,
        min_alpha: float = 0,
        max_alpha: float = 1,
        arithmetic_error: bool = False,
        error_min: float = -4,
        error_max: float = 4,
        derivative_min: float = -0.5,
        derivative_max: float = 0.5,
    ):
        """Initialize loss balancer.

        Args:
            target: Strategy for computing the target value for loss1
            kp: Proportional gain - how strongly to react to current error
            kd: Derivative gain - how strongly to react to error trend
            initial_balance: Starting alpha value (0=only loss2, 1=only loss1)
            len_errors: How many recent errors to keep for derivative calculation
            min_alpha: Minimum allowed alpha value
            max_alpha: Maximum allowed alpha value
            arithmetic_error: If True, error = loss1 - target.
                            If False, uses geometric error (ratio-based)
            error_min: Minimum error for clipping (currently unused)
            error_max: Maximum error for clipping (currently unused)
            derivative_min: Minimum derivative value (clips large negative changes)
            derivative_max: Maximum derivative value (clips large positive changes)
        """
        assert min_alpha <= initial_balance <= max_alpha
        assert 0 <= min_alpha <= max_alpha <= 1
        assert error_min < 0
        assert error_max > 0
        assert derivative_min < 0
        assert derivative_max > 0

        self.target = target
        self.alpha = initial_balance
        self.kp = kp
        self.kd = kd
        self.len_errors = len_errors
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.errors = []
        self.arithmetic_error = arithmetic_error
        self.error_min = error_min
        self.error_max = error_max
        self.derivative_min = derivative_min
        self.derivative_max = derivative_max

    def get_error_and_deriv(
        self, target_input: None | float, target_reference: float
    ) -> tuple[float, float]:
        """Compute error and derivative for PD control.

        Args:
            target_input: value to compute target from
            target_reference: value to compare to target

        Returns:
            Tuple of (error, derivative) where:
            - error: How far target_reference is from target (computed with target_input) (clipped to bounds)
            - derivative: Rate of change of error (clipped to bounds)
        """
        target = self.target.get_target(target_input)
        if isinstance(target_reference, torch.Tensor):
            target_reference = target_reference.detach().cpu().item()

        if self.arithmetic_error:
            # Simple difference: positive when loss1 > target
            error = target_reference - target
        else:
            # Geometric error: captures relative differences better for varied loss scales
            error = (
                -target / (target_reference + 1e-6)
                if target > target_reference
                else target_reference / (target + 1e-6)
            )
        error = np.clip(error, self.error_min, self.error_max)

        if len(self.errors) > 0:
            derivative = np.clip(
                error - self.errors[-1],
                self.derivative_min,
                self.derivative_max,
            )
        else:
            derivative = 0

        self.errors.append(error)
        if len(self.errors) > self.len_errors:
            self.errors.pop(0)

        return error, derivative

    def get_combined_loss(
        self,
        loss1: float,
        loss2: float,
        target_input: None | float,
        target_reference: float,
    ) -> tuple[float, float]:
        """Update balance parameter and return combined loss.

        Uses PD control: alpha += kp * error + kd * derivative
        Then computes: combined_loss = alpha * loss1 + (1 - alpha) * loss2

        Args:
            loss1: First loss value
            loss2: Second loss value

        Returns:
            Tuple of (combined_loss, alpha) where:
            - combined_loss: Weighted combination of the two losses
            - alpha: Updated balance parameter (clipped to [min_alpha, max_alpha])
        """
        error, derivative = self.get_error_and_deriv(target_input, target_reference)
        self.alpha = self.alpha + (self.kp * error) + (self.kd * derivative)
        self.alpha = np.clip(self.alpha, self.min_alpha, self.max_alpha)
        combined_loss = self.alpha * loss1 + (1 - self.alpha) * loss2
        return combined_loss, self.alpha
