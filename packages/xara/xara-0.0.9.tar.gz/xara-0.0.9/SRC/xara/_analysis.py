from xara import Model


class Pattern:   pass # Acceleration, Element, Boundary, Constraint

class Sequence:  pass


class Search:    pass
class Algorithm: pass
class Test:      pass

class ConstraintHandler: pass


class EigenSolver: pass
class LinearSolver: pass


_EquilibriumResponse = [
    "residual",
    "tangent",

    "position",
    "rotation",
    "velocity",
    "acceleration",

    "resistance", # "force",
    "reaction"
]

_SpectralResponse = [
    "frequency",
    "period",
    "mode"
]

class Analysis:
    Success = 0
    Failure = 1
    Partial = 2 # in progress


    _status: int
    _constraints: ConstraintHandler

    def _analysis_cached(self, model):
        
        if not hasattr(self._model, "_last_analysis") or \
            model._last_analysis is not self:
            model._last_analysis = self 
            return False 
        
        return True


    def solution(self,
                 response: str, 
                 node=None, dof=None, 
                 element=None, material=None, section=None,
                 **kwds):
        
        if node is None and element is None:
            return self._solution_vector()
        
        if element is not None and node is not None:
            raise ValueError("Cannot specify both element and node for solution retrieval.")

        if element is not None:
            return self._element_solution(
                response, element=element, material=material, section=section
            )
        
        if node is not None:
            return self._node_solution(
                response, node=node, dof=dof
            )

    def gradient(self, response, parameter, **loc):
        pass

    def jacobian(self, response, parameters):
        pass


class StabilityAnalysis(Analysis):
    def __init__(self,
                 constraints=None,
                 solver: "EigenSolver" = None):
        self._status = Analysis.Partial
        self._constraints = constraints


class FrequencyAnalysis(Analysis):
    def __init__(self, highest, unorm:float):
        self._status = Analysis.Partial


    def analyze(self, model):
        model.modalProperties()

        self._status = Analysis.Success

        return self._status



class SpectrumAnalysis(Analysis):
    def __init__(self, 
                 model, sequence, 
                 modes: FrequencyAnalysis,
                 highest=None, unorm:float=None,
                 solver: EigenSolver=None):
        pass




class _EquilibriumAnalysis(Analysis):
    _algorithm : Algorithm
    _solver    : LinearSolver
    _test      : Test
    _search    : Search
    _response = [
        *_EquilibriumResponse
    ]

    def __init__(self):
        self._patterns = []
        self._time = 0.0

    def _add_pattern(self, pattern, type):
        self._patterns.append((pattern, type))

    def _start_equilibrium(self,model):
        if not self._analysis_cached(model):
            model.wipeAnalysis()
            if self._constraints is not None:
                model.constraints(self._constraints)
            if self._test is not None:
                model.test(self._test)
            if self._solver is not None:
                model.solver(self._solver)
                

        # Patterns
        model.setTime(self._time)
        for i,(pattern, type) in enumerate(self._patterns):
            pattern._activate(model, pattern=i+1)

        # Algorithm
        if self._algorithm is None:
            model.algorithm("Newton")
        else:
            model.algorithm(*self._algorithm)



class StaticAnalysis(_EquilibriumAnalysis):
    # Simplified LoadControl
    def __init__(self, 
                 model, 
                 pattern: Pattern,
                 step:    float=1.0,
                 # Analysis
                 constraints=None,
                 # EquilibriumAnalysis
                 test: Test = None,
                 algorithm: Algorithm=None,
                 search=None,
                 solver:    LinearSolver=None,
                 ):

        self._model = model
        self._status = Analysis.Partial
        self._constraints = constraints

        self._algorithm = algorithm
        self._solver    = solver
        self._test      = test

        super().__init__()

        if isinstance(pattern, list):
            for p in pattern:
                self._add_pattern(p, "Linear")
        else:
            self._add_pattern(pattern, "Linear")

    def analyze(self, model):
        status = Analysis.Partial
        # add our patterns
        self._start_equilibrium(model)


        # analyze
        self._model.analysis("Static")
        self._model.analyze(1)

        # clean up
        self._status = status
        self._model.wipeAnalysis()
        self._model.loadConst(time=self._time)
        return status



class DynamicAnalysis(_EquilibriumAnalysis):
    class Integrator: pass 


    def __init__(self, model,
                 pattern: Pattern=None,
                 step=None, step_scale=None,
                 integrator: "DynamicAnalysis.Integrator"=None,
                 # Analysis
                 constraints=None,
                 # EquilibriumAnalysis
                 test: Test = None,
                 algorithm: Algorithm=None,
                 search=None,
                 solver:    LinearSolver=None,
                ):

        self._status = Analysis.Partial
        self._constraints = constraints

        self._algorithm = algorithm
        self._solver    = solver
        self._test      = test

        super().__init__()

        self._add_pattern(pattern, "Constant")

        self._integrator = integrator
        # self._add_series(series)


    def analyze(self, model):
        pass 


class ControlAnalysis(_EquilibriumAnalysis):
    # DispControl, LoadControl, ArcLength
    def __init__(self,
                 model,
                 pattern,
                 step,
                 control=None,
                 min_step: float=None,
                 max_step: float=None,
                 # Analysis
                 constraints=None,
                 # EquilibriumAnalysis
                 test: Test=None,
                 algorithm: Algorithm=None,
                 search=None,
                 solver: LinearSolver=None,
                 #
                 **kwds):

        self._model = model
        self._status = Analysis.Partial
        self._constraints = constraints

        self._algorithm = algorithm
        self._solver    = solver
        self._test      = test

        super().__init__()
        self._add_pattern(pattern, "Linear")

        self._control = control
        self._step = step
        self._control_kwds = kwds

    def update(self, **integrator):
        pass

    def analyze(self, model, repeat:int=1)->int:
        self._start_equilibrium(model)
        status = Analysis.Partial
        self._model.loadConst(time=self._time)

        # add our patterns

        # analyze

        self._time = self._model.getTime()
        self._model.loadConst(time=self._time)



def Objective(builder:  callable, # | Model,
              analysis: callable, # | Analysis | Pattern, 
              response):

    # if analysis is a pattern, create a basic static analysis

    def evaluate(self):
        pass

    def gradient(self):
        pass


class AnalysisSequence:
    pass


if __name__ == "__main__":
    import sys
    import xara

    model = xara.Model()


    options = {
        "algorithm": {"type": "NewtonRaphson"},
        "test":      {"type": "Residual",  "tolerance": 1e-6,  "iterate": 10 },
        "solver":    "Umfpack",
        "constraints": "Transformation"
    }

    StaticAnalysis(pattern="SelfWeight", **options).analyze(model)


    ma = FrequencyAnalysis(model, 3)
    ma.analyze()
    model.damping(ma, {1: 0.05, 2: 0.05, 3: 0.05}) # TODO


    motion = Pattern(persist=False)
    rha = DynamicAnalysis(pattern=motion, step=0.01, **options)



    rha.analyze(model)

    g = Objective(model,  rha,  "u", node=1, dof=1)

    K = rha.jacobian("p", "u")
    M = rha.jacobian("p", "a")
    C = rha.jacobian("p", "v")

    u = rha.solution("u", node=1, dof=1)

    s = rha.solution("s", element=1, material=1)