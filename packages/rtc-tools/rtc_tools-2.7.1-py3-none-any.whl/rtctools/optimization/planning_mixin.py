from rtctools.optimization.optimization_problem import OptimizationProblem


class PlanningMixin(OptimizationProblem):
    """
    Uses default discretization logic for planning variables, but uses
    dedicated per-ensemble-member decision variables for other, non-planning control
    variables.
    """

    # Planning variables
    planning_variables = []

    def discretize_control(self, variable, ensemble_member, times, offset):
        if variable not in self.planning_variables:
            # Non-planning variables are never shared between ensemble members
            return slice(offset, offset + len(times))
        else:
            return super().discretize_control(variable, ensemble_member, times, offset)
