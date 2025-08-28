import qutip
import qutip.solver.integrator as qode
from qutip.solver.mcsolve import MCSolver, MCIntegrator
from qutip.solver.mesolve import MESolver
from qutip.solver.sesolve import SESolver
from qutip.solver.result import Result as qt_Result

from .state import CuState
from .qobjevo import CuQobjEvo


__all__ = []


class Result(qt_Result):
    def _e_op_func(self, e_op):
        if isinstance(e_op, (qutip.Qobj, qutip.QobjEvo)):
            gpu_caller = CuQobjEvo(qutip.QobjEvo(e_op))
            return gpu_caller.expect
        raise NotImplementedError


class CuIntegratorVern7(qode.IntegratorVern7):
    supports_blackbox: bool = False  # No feedback support
    method = "vern7"

    def __init__(self, system, options):
        self.system = CuQobjEvo(system)
        super().__init__(self.system, options)
        self.name = f"vern7 with cuDensity"

    def set_state(self, t, state):
        state = CuState(state, self.system.hilbert_space_dims)
        self._ode_solver.set_initial_value(state, t)
        self._is_set = True


class CuIntegratorVern9(qode.IntegratorVern9):
    supports_blackbox: bool = False  # No feedback support
    method = "vern9"

    def __init__(self, system, options):
        self.system = CuQobjEvo(system)
        super().__init__(self.system, options)
        self.name = f"vern9 with cuDensity"

    def set_state(self, t, state):
        state = CuState(state, self.system.hilbert_space_dims)
        self._ode_solver.set_initial_value(state, t)
        self._is_set = True


class CuIntegratorTsit5(qode.IntegratorTsit5):
    supports_blackbox: bool = False  # No feedback support
    method = "tsit5"

    def __init__(self, system, options):
        self.system = CuQobjEvo(system)
        super().__init__(self.system, options)
        self.name = f"tsit5 with cuDensity"

    def set_state(self, t, state):
        state = CuState(state, self.system.hilbert_space_dims)
        self._ode_solver.set_initial_value(state, t)
        self._is_set = True


class CuMCIntegrator(MCIntegrator):
    def __init__(self, integrator, system, options=None):
        self._integrator = integrator
        self.system = system
        self._c_ops = [CuQobjEvo(op) for op in system.c_ops]
        self._n_ops = [CuQobjEvo(op) for op in system.n_ops]
        self.options = options
        self._generator = None
        self.method = f"{self.name} {self._integrator.method}"
        self._is_set = False
        self.issuper = self._c_ops[0].issuper



MCSolver.add_integrator(CuIntegratorVern7, "CuVern7")
MESolver.add_integrator(CuIntegratorVern7, "CuVern7")
SESolver.add_integrator(CuIntegratorVern7, "CuVern7")

MCSolver.add_integrator(CuIntegratorVern9, "CuVern9")
MESolver.add_integrator(CuIntegratorVern9, "CuVern9")
SESolver.add_integrator(CuIntegratorVern7, "CuVern9")

MCSolver.add_integrator(CuIntegratorTsit5, "CuTsit5")
MESolver.add_integrator(CuIntegratorTsit5, "CuTsit5")
SESolver.add_integrator(CuIntegratorTsit5, "CuTsit5")
