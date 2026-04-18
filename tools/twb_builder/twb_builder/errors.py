class TwbBuilderError(Exception):
    pass


class PlanError(TwbBuilderError):
    pass


class RenderError(TwbBuilderError):
    pass


class ValidationError(TwbBuilderError):
    pass


class SourceReadError(TwbBuilderError):
    pass
