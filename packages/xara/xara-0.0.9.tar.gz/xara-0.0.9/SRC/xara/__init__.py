try:
    from opensees.openseespy import Model
except:
    Model = None

successful = 0

from ._analysis import StaticAnalysis 

# def __getattr__(name):
#     global successful
#     if name == "Model":
#         try:
#             from opensees.openseespy import Model
#         except:
#             Model = None
#         if Model is None:
#             raise ImportError("opensees is not installed or not available.")
#         return Model
# 
#     elif name == "successful":
#         return successful
#     else:
#         raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


try:
    from jax import tree_util
#   import opensees.openseespy as ops
# 1) Tell JAX that ops.Model is an opaque leaf
    def _flatten_model(model):
        # no children, carry the model object in aux_data
        return (), model

    def _unflatten_model(aux_data, _children):
        # aux_data *is* the original model
        return aux_data

    tree_util.register_pytree_node(Model, _flatten_model, _unflatten_model)
except:
    pass

