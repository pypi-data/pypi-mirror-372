import pytest
from collections.abc import Sequence

from bayesflow.networks import MLP, Sequential
from bayesflow.utils.tensor_utils import concatenate_valid
from bayesflow.utils.serialization import serializable, serialize


@pytest.fixture()
def diffusion_model_edm_F():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 250},
        noise_schedule="edm",
        prediction_type="F",
    )


@serializable("test", disable_module_check=True)
class ConcatenateMLP(Sequential):
    def __init__(
        self,
        widths: Sequence[int] = (256, 256),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.widths = widths
        self.mlp = MLP(widths)

    def call(self, x, t, conditions=None, training=False):
        con = concatenate_valid([x, t, conditions], axis=-1)
        return self.mlp(con)

    def compute_output_shape(self, x_shape, t_shape, conditions_shape=None):
        concatenate_input_shapes = tuple(
            (
                x_shape[0],
                x_shape[-1] + t_shape[-1] + (conditions_shape[-1] if conditions_shape is not None else 0),
            )
        )
        return self.mlp.compute_output_shape(concatenate_input_shapes)

    def build(self, x_shape, t_shape, conditions_shape=None):
        if self.built:
            return

        concatenate_input_shapes = tuple(
            (
                x_shape[0],
                x_shape[-1] + t_shape[-1] + (conditions_shape[-1] if conditions_shape is not None else 0),
            )
        )
        self.mlp.build(concatenate_input_shapes)

    def get_config(self):
        config = {"widths": self.widths}

        return serialize(config)


@pytest.fixture()
def diffusion_model_edm_F_subnet_separate_inputs():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=ConcatenateMLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 4},
        noise_schedule="edm",
        prediction_type="F",
        concatenate_subnet_input=False,
    )


@pytest.fixture()
def diffusion_model_edm_velocity():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 250},
        noise_schedule="edm",
        prediction_type="velocity",
    )


@pytest.fixture()
def diffusion_model_edm_noise():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 250},
        noise_schedule="edm",
        prediction_type="noise",
    )


@pytest.fixture()
def diffusion_model_cosine_F():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 250},
        noise_schedule="cosine",
        prediction_type="F",
    )


@pytest.fixture()
def diffusion_model_cosine_velocity():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 250},
        noise_schedule="cosine",
        prediction_type="velocity",
    )


@pytest.fixture()
def diffusion_model_cosine_noise():
    from bayesflow.networks import DiffusionModel

    return DiffusionModel(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 250},
        noise_schedule="cosine",
        prediction_type="noise",
    )


@pytest.fixture()
def flow_matching():
    from bayesflow.networks import FlowMatching

    return FlowMatching(
        subnet=MLP([8, 8]),
        integrate_kwargs={"method": "rk45", "steps": 100},
    )


@pytest.fixture()
def flow_matching_subnet_separate_inputs():
    from bayesflow.networks import FlowMatching

    return FlowMatching(
        subnet=ConcatenateMLP([8, 8]), integrate_kwargs={"method": "rk45", "steps": 4}, concatenate_subnet_input=False
    )


@pytest.fixture()
def consistency_model():
    from bayesflow.networks import ConsistencyModel

    return ConsistencyModel(total_steps=100, subnet=MLP([8, 8]))


@pytest.fixture()
def consistency_model_subnet_separate_inputs():
    from bayesflow.networks import ConsistencyModel

    return ConsistencyModel(total_steps=4, subnet=ConcatenateMLP([8, 8]), concatenate_subnet_input=False)


@pytest.fixture()
def affine_coupling_flow():
    from bayesflow.networks import CouplingFlow

    return CouplingFlow(
        depth=2, subnet="mlp", subnet_kwargs=dict(widths=[8, 8]), transform="affine", transform_kwargs=dict(clamp=1.8)
    )


@pytest.fixture()
def spline_coupling_flow():
    from bayesflow.networks import CouplingFlow

    return CouplingFlow(
        depth=2, subnet="mlp", subnet_kwargs=dict(widths=[8, 8]), transform="spline", transform_kwargs=dict(bins=8)
    )


@pytest.fixture()
def free_form_flow():
    from bayesflow.experimental import FreeFormFlow

    return FreeFormFlow(encoder_subnet=MLP([16, 16]), decoder_subnet=MLP([16, 16]))


@pytest.fixture()
def typical_point_inference_network():
    from bayesflow.networks import PointInferenceNetwork
    from bayesflow.scores import MeanScore, MedianScore, QuantileScore, MultivariateNormalScore

    return PointInferenceNetwork(
        scores=dict(
            mean=MeanScore(),
            median=MedianScore(),
            quantiles=QuantileScore([0.1, 0.2, 0.5, 0.65]),
            mvn=MultivariateNormalScore(),  # currently not stable
        )
    )


@pytest.fixture()
def typical_point_inference_network_subnet():
    from bayesflow.networks import PointInferenceNetwork
    from bayesflow.scores import MeanScore, MedianScore, QuantileScore, MultivariateNormalScore

    subnet = MLP([16, 8])

    return PointInferenceNetwork(
        scores=dict(
            mean=MeanScore(subnets=dict(value=subnet)),
            median=MedianScore(subnets=dict(value=subnet)),
            quantiles=QuantileScore(subnets=dict(value=subnet)),
            mvn=MultivariateNormalScore(subnets=dict(mean=subnet, covariance=subnet)),
        ),
        subnet=subnet,
    )


@pytest.fixture(
    params=[
        "typical_point_inference_network",
        "affine_coupling_flow",
        "spline_coupling_flow",
        "flow_matching",
        "free_form_flow",
        "consistency_model",
        pytest.param("diffusion_model_edm_F"),
        pytest.param("diffusion_model_edm_noise", marks=pytest.mark.slow),
        pytest.param("diffusion_model_cosine_velocity", marks=pytest.mark.slow),
        pytest.param("diffusion_model_cosine_F", marks=pytest.mark.slow),
        pytest.param("diffusion_model_cosine_noise", marks=pytest.mark.slow),
        pytest.param("diffusion_model_cosine_velocity", marks=pytest.mark.slow),
    ],
    scope="function",
)
def inference_network(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(
    params=[
        "typical_point_inference_network_subnet",
        "coupling_flow_subnet",
        "flow_matching_subnet",
        "free_form_flow_subnet",
    ],
    scope="function",
)
def inference_network_subnet(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(
    params=[
        "affine_coupling_flow",
        "spline_coupling_flow",
        "flow_matching",
        "free_form_flow",
        "consistency_model",
        pytest.param("diffusion_model_edm_F"),
        pytest.param(
            "diffusion_model_edm_noise",
            marks=[
                pytest.mark.slow,
                pytest.mark.skip("noise prediction not testable without prior training for numerical reasons."),
            ],
        ),
        pytest.param("diffusion_model_cosine_velocity", marks=pytest.mark.slow),
        pytest.param(
            "diffusion_model_cosine_F",
            marks=[
                pytest.mark.slow,
                pytest.mark.skip("skip to reduce load on CI."),
            ],
        ),
        pytest.param(
            "diffusion_model_cosine_noise",
            marks=[
                pytest.mark.slow,
                pytest.mark.skip("noise prediction not testable without prior training for numerical reasons."),
            ],
        ),
        pytest.param(
            "diffusion_model_cosine_velocity",
            marks=[
                pytest.mark.slow,
                pytest.mark.skip("skip to reduce load on CI."),
            ],
        ),
    ],
    scope="function",
)
def generative_inference_network(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(
    params=[
        pytest.param("flow_matching_subnet_separate_inputs"),
        pytest.param("consistency_model_subnet_separate_inputs"),
        pytest.param("diffusion_model_edm_F_subnet_separate_inputs"),
    ],
    scope="function",
)
def inference_network_subnet_separate_inputs(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def time_series_network(summary_dim):
    from bayesflow.networks import TimeSeriesNetwork

    return TimeSeriesNetwork(summary_dim=summary_dim)


@pytest.fixture(scope="function")
def time_series_transformer(summary_dim):
    from bayesflow.networks import TimeSeriesTransformer

    return TimeSeriesTransformer(summary_dim=summary_dim)


@pytest.fixture(scope="function")
def fusion_transformer(summary_dim):
    from bayesflow.networks import FusionTransformer

    return FusionTransformer(summary_dim=summary_dim)


@pytest.fixture(scope="function")
def set_transformer(summary_dim):
    from bayesflow.networks import SetTransformer

    return SetTransformer(summary_dim=summary_dim)


@pytest.fixture(scope="function")
def deep_set(summary_dim):
    from bayesflow.networks import DeepSet

    return DeepSet(summary_dim=summary_dim)


@pytest.fixture(
    params=[
        None,
        "time_series_network",
        "time_series_transformer",
        "fusion_transformer",
        "set_transformer",
        "deep_set",
    ],
    scope="function",
)
def summary_network(request, summary_dim):
    if request.param is None:
        return None
    return request.getfixturevalue(request.param)
